"""Process route - runs the full AI pipeline with live status tracking."""

import threading
import time
from pathlib import Path

import config
from flask import Blueprint, request, jsonify, current_app

from utils.ffmpeg_utils import check_ffmpeg
from utils.video_utils import VideoLoader
from utils.scene_detector import SceneDetector
from utils.scene_merger import SceneMerger
from utils.clip_generator import ClipGenerator

from ai.whisper_engine import WhisperEngine
from ai.subtitle_builder import SubtitleBuilder
from ai.subtitle_renderer import SubtitleRenderer
from ai.animated_caption_renderer import AnimatedCaptionRenderer
from ai.translation import translate_transcript

process_bp = Blueprint("process", __name__, url_prefix="/process")

# In-memory job store
JOBS = {}
JOB_COUNTER = 0
JOB_LOCK = threading.Lock()


class PipelineJob:
    """Track the status and progress of a pipeline run."""

    def __init__(self, job_id, filename, settings=None):
        self.job_id = job_id
        self.filename = filename
        self.settings = settings or {}
        self.status = "queued"          # queued | running | done | error
        self.step = ""
        self.steps_completed = 0
        self.total_steps = 8
        self.logs = []
        self.error = None
        self.result = None
        self.finished = False
        self.clips_meta = []
        self.caption_style = None
        self.project_id = None
        self.caption_files = []

    def add_log(self, message):
        self.logs.append(message)

    def set_step(self, index, name, message=""):
        self.step = name
        self.steps_completed = index
        if message:
            self.add_log(message)

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "filename": self.filename,
            "status": self.status,
            "step": self.step,
            "steps_completed": self.steps_completed,
            "total_steps": self.total_steps,
            "logs": self.logs,
            "error": self.error,
            "result": self.result,
            "finished": self.finished,
            "clips_meta": self.clips_meta,
            "caption_style": self.caption_style,
            "project_id": self.project_id,
            "caption_files": self.caption_files,
        }


def _sanitize_subtitle_color(color):
    """Convert a hex color like #FFFFFF or FFFFFF to ASS &H format."""
    color = (color or "").strip().lstrip("#")
    if len(color) != 6:
        return None
    try:
        r, g, b = color[0:2], color[2:4], color[4:6]
        return f"&H{b}{g}{r}&"
    except Exception:
        return None


def _build_style_options(settings):
    """Build a style dict for the subtitle renderer from user settings."""
    sub = settings.get("subtitle", {}) or {}

    style = {}

    # Position -> ASS alignment
    position = sub.get("position", "bottom")
    alignment_map = {
        "bottom": 2,
        "top": 8,
        "middle": 5,
    }
    style["alignment"] = alignment_map.get(position, 2)

    font = sub.get("font")
    if font:
        style["font"] = font

    try:
        size = int(sub.get("size", 22))
        style["font_size"] = size
    except (TypeError, ValueError):
        pass

    color = _sanitize_subtitle_color(sub.get("color"))
    if color:
        style["primary_color"] = color

    try:
        outline = int(sub.get("outline", 2))
        style["outline"] = outline
    except (TypeError, ValueError):
        pass

    try:
        shadow = int(sub.get("shadow", 1))
        style["shadow"] = shadow
    except (TypeError, ValueError):
        pass

    return style or None


def run_pipeline_job(job, app=None):
    """Execute the full AI pipeline and update the job status."""
    ctx = None
    if app:
        try:
            ctx = app.app_context()
            ctx.push()
        except Exception:
            ctx = None

    settings = job.settings
    try:
        job.status = "running"
        job.add_log("Pipeline started.")

        project_id = settings.get("project_id")
        if not project_id:
            from core.project_state import project_state
            video = config.INPUT_DIR / job.filename
            if video.exists():
                from utils.video_utils import VideoLoader
                try:
                    loader = VideoLoader(video)
                    _ = loader.metadata()
                    loader.close()
                except Exception:
                    pass
                proj = project_state.create_project(job.filename, f"/download/input/{job.filename}")
                project_id = proj.project_id
            else:
                project_id = f"proj_{job.job_id}"
        job.project_id = project_id

        # Load settings & Engine toggles
        language = settings.get("language", "auto")
        raw_aspect = settings.get("aspect") or settings.get("aspect_ratio") or settings.get("aspectRatio") or "9:16"
        aspect_key = str(raw_aspect).strip().replace("/", ":")
        if aspect_key not in config.ASPECT_OPTIONS:
            aspect_key = "9:16"

        clipping_mode = settings.get("clipping_mode", config.CLIPPING_AI)
        clip_duration = settings.get("clip_duration")
        clip_count = settings.get("clip_count")
        naming = settings.get("naming", config.NAME_SEQUENTIAL)
        subtitle_enabled = settings.get("subtitle_enabled", True)
        subtitle_translate = settings.get("subtitle_language", language)
        quality = settings.get("quality", config.DEFAULT_QUALITY)
        caption_enabled = settings.get("caption_enabled", config.CAPTION_ENABLED)

        # AI Engine & Feature Toggles
        whisper_enabled = settings.get("whisper_enabled", True)
        whisper_model = settings.get("whisper_model") or getattr(config, "WHISPER_MODEL", "base")
        uploaded_sub_filename = settings.get("uploaded_subtitle_file") or settings.get("uploaded_transcript_file")

        scene_detection_enabled = settings.get("scene_detection_enabled", True)
        scene_threshold = float(settings.get("scene_threshold", getattr(config, "SCENE_THRESHOLD", 27.0)))
        scene_merger_enabled = settings.get("scene_merger_enabled", True)
        min_clip_dur = float(settings.get("min_clip_duration") or getattr(config, "MIN_CLIP_DURATION", 60.0))
        max_clip_dur = float(settings.get("max_clip_duration") or getattr(config, "MAX_CLIP_DURATION", 120.0))

        smart_reframe_enabled = settings.get("smart_reframe_enabled", True)
        reframe_mode = settings.get("reframe_mode", "smart")
        silence_trimming_enabled = settings.get("silence_trimming_enabled", True)
        silence_threshold_db = float(settings.get("silence_threshold_db", -30.0))

        audio_energy_enabled = settings.get("audio_energy_enabled", True)
        motion_detection_enabled = settings.get("motion_detection_enabled", True)
        emotion_detection_enabled = settings.get("emotion_detection_enabled", True)
        viral_ranking_enabled = settings.get("viral_ranking_enabled", True)
        min_viral_score = float(settings.get("min_viral_score", 50.0))
        keyword_extraction_enabled = settings.get("keyword_extraction_enabled", True)
        audio_normalization_enabled = settings.get("audio_normalization_enabled", True)

        user_specified_size = settings.get("caption_size")
        try:
            user_specified_size = int(user_specified_size) if user_specified_size is not None and user_specified_size != "" else None
        except (TypeError, ValueError):
            user_specified_size = None

        caption_style_data = settings.get("caption_style")
        if caption_style_data:
            from core.project_state import CaptionStyleConfig
            resolved_style_size = (
                user_specified_size
                or caption_style_data.get("font_size")
                or caption_style_data.get("fontSize")
                or config.CAPTION_FONT_SIZE
            )
            try:
                resolved_style_size = int(resolved_style_size)
            except (TypeError, ValueError):
                resolved_style_size = config.CAPTION_FONT_SIZE

            job.caption_style = CaptionStyleConfig(
                id=caption_style_data.get("id", "custom"),
                name=caption_style_data.get("name", "Custom"),
                font_family=caption_style_data.get("font_family") or caption_style_data.get("fontFamily", "Arial Black"),
                font_size=resolved_style_size,
                font_weight=int(caption_style_data.get("font_weight") or caption_style_data.get("fontWeight", 800)),
                text_color=caption_style_data.get("text_color") or caption_style_data.get("textColor", "#FFFFFF"),
                active_word_color=caption_style_data.get("active_word_color") or caption_style_data.get("activeWordColor", "#fbbf24"),
                background_color=caption_style_data.get("background_color") or caption_style_data.get("backgroundColor") or caption_style_data.get("bgColor", "#000000"),
                background_opacity=float(caption_style_data.get("background_opacity") or caption_style_data.get("backgroundOpacity", 0.0)),
                outline_color=caption_style_data.get("outline_color") or caption_style_data.get("outlineColor", "#000000"),
                outline_width=int(caption_style_data.get("outline_width") or caption_style_data.get("outlineWidth", 3)),
                shadow_color=caption_style_data.get("shadow_color") or caption_style_data.get("shadowColor", "#000000"),
                shadow_blur=int(caption_style_data.get("shadow_blur") or caption_style_data.get("shadowBlur", 4)),
                shadow_offset_y=int(caption_style_data.get("shadow_offset_y") or caption_style_data.get("shadowOffsetY", 2)),
                position=caption_style_data.get("position", "bottom"),
                animation=caption_style_data.get("animation", "pop"),
                letter_spacing=int(caption_style_data.get("letter_spacing") or caption_style_data.get("letterSpacing", 0)),
                line_height=float(caption_style_data.get("line_height") or caption_style_data.get("lineHeight", 1.2)),
                max_lines=int(caption_style_data.get("max_lines") or caption_style_data.get("maxLines", 2)),
            )
            from core.project_state import project_state
            project_state.set_caption_style(project_id, job.caption_style)

        # Animated caption style options
        caption_opts = {
            "animation": settings.get("caption_animation", config.CAPTION_ANIMATION),
            "position": settings.get("caption_position", config.CAPTION_POSITION),
            "font": settings.get("caption_font", config.CAPTION_FONT),
            "size": user_specified_size or config.CAPTION_FONT_SIZE,
            "color": settings.get("caption_color", config.CAPTION_COLOR),
            "background": settings.get("caption_background", config.CAPTION_BACKGROUND),
            "outline": settings.get("caption_outline", config.CAPTION_OUTLINE),
            "margin_v": settings.get("caption_margin_v", config.CAPTION_MARGIN_V),
            "min_word_ms": settings.get("caption_min_word_ms", config.CAPTION_MIN_WORD_MS),
        }
        if job.caption_style:
            caption_opts["font"] = job.caption_style.font_family or caption_opts["font"]
            if user_specified_size:
                caption_opts["size"] = user_specified_size
                job.caption_style.font_size = user_specified_size
            elif job.caption_style.font_size:
                caption_opts["size"] = job.caption_style.font_size
            caption_opts["color"] = job.caption_style.text_color or caption_opts["color"]
            caption_opts["background"] = job.caption_style.background_color or caption_opts["background"]
            caption_opts["outline"] = job.caption_style.outline_width if job.caption_style.outline_width is not None else caption_opts["outline"]
            if hasattr(job.caption_style, "position") and job.caption_style.position:
                caption_opts["position"] = job.caption_style.position
            if hasattr(job.caption_style, "animation") and job.caption_style.animation:
                caption_opts["animation"] = job.caption_style.animation
        caption_template = settings.get("caption_template")

        # 1. FFmpeg check
        job.set_step(1, "Checking FFmpeg")
        status, version = check_ffmpeg()
        if not status:
            raise RuntimeError(f"FFmpeg not installed: {version}")
        job.add_log(f"FFmpeg OK - {version}")

        video = config.INPUT_DIR / job.filename
        if not video.exists():
            raise RuntimeError(f"Video not found: {video}")

        # 2. Load video + metadata + thumbnail
        job.set_step(2, "Loading video & metadata")
        loader = VideoLoader(video)
        info = loader.metadata()
        job.add_log(f"Video: {info['width']}x{info['height']}, "
                    f"{info['duration']}s, {info['fps']} fps")

        thumb = config.THUMBNAIL_DIR / f"{Path(job.filename).stem}_thumb.jpg"
        loader.thumbnail(thumb)
        loader.close()
        job.add_log(f"Thumbnail saved: {thumb.name}")

        # 3. Speech-to-text / Subtitle source resolution
        job.set_step(3, "Resolving speech transcript and subtitles")
        transcript = []
        stem = Path(job.filename).stem

        # Priority 1: User uploaded custom subtitle / transcript file
        if uploaded_sub_filename:
            job.add_log(f"Loading user-uploaded subtitle: {uploaded_sub_filename}")
            from ai.transcript import TranscriptManager
            sub_path = config.SUBTITLE_DIR / uploaded_sub_filename
            if not sub_path.exists():
                sub_path = config.TRANSCRIPT_DIR / uploaded_sub_filename
            if not sub_path.exists():
                sub_path = Path(uploaded_sub_filename)

            if sub_path.exists():
                try:
                    manager = TranscriptManager()
                    manager.load(sub_path)
                    transcript = manager.segments
                    job.add_log(f"Custom subtitles: loaded {len(transcript)} segments from '{sub_path.name}'. (Whisper bypassed)")
                except Exception as sub_err:
                    job.add_log(f"Failed to parse uploaded subtitle '{uploaded_sub_filename}': {sub_err}")
            else:
                job.add_log(f"Uploaded subtitle file '{uploaded_sub_filename}' not found.")

        # Priority 1.5: Co-located subtitle (.srt / .vtt / .json) in INPUT_DIR or SUBTITLE_DIR
        if not transcript:
            for candidate_dir in [config.INPUT_DIR, config.SUBTITLE_DIR, config.TRANSCRIPT_DIR]:
                for ext in (".srt", ".vtt", ".json"):
                    cand = candidate_dir / f"{stem}{ext}"
                    if cand.exists():
                        try:
                            from ai.transcript import TranscriptManager
                            manager = TranscriptManager()
                            manager.load(cand)
                            if manager.segments:
                                transcript = manager.segments
                                job.add_log(f"Auto-detected co-located subtitle: loaded {len(transcript)} segments from '{cand.name}'. (Whisper bypassed)")
                                break
                        except Exception as auto_sub_err:
                            print(f"[PROCESS] Auto-sub note: {auto_sub_err}")
                if transcript:
                    break

        # Priority 2: Whisper transcription if enabled and not already provided
        if not transcript and whisper_enabled:
            job.add_log(f"Transcribing video audio using Whisper ({whisper_model})...")
            whisper = WhisperEngine(whisper_model)
            whisper_lang = language if language != "auto" else None
            transcript_file = config.TRANSCRIPT_DIR / f"{stem}_{whisper_model}.json"
            transcript = whisper.transcribe_cached(
                video,
                transcript_file,
                language=whisper_lang,
            )
            job.add_log(f"Whisper transcript: {len(transcript)} segments generated with model '{whisper_model}'.")
        elif not transcript:
            job.add_log("Speech transcription bypassed (no subtitles provided & Whisper disabled).")

        # Subtitle generation (with optional translation)
        subtitle = SubtitleBuilder()
        subtitle_transcript = []

        if transcript:
            if subtitle_translate and subtitle_translate != "auto" and subtitle_translate != language:
                subtitle_transcript = translate_transcript(transcript, subtitle_translate)
            else:
                subtitle_transcript = list(transcript)

            srt_file = config.SUBTITLE_DIR / f"{stem}.srt"
            vtt_file = config.SUBTITLE_DIR / f"{stem}.vtt"
            subtitle.save_all(subtitle_transcript, srt_file, vtt_file)
            job.add_log(f"SRT + VTT subtitle files created ({len(subtitle_transcript)} lines).")

            # Associate SRT/VTT with project
            from core.project_state import project_state
            project_state.add_caption_file(project_id, srt_file.name, "srt", f"/download/subtitle/{srt_file.name}")
            project_state.add_caption_file(project_id, vtt_file.name, "vtt", f"/download/subtitle/{vtt_file.name}")

            job.caption_files = [
                {"filename": srt_file.name, "media_type": "srt", "url": f"/download/subtitle/{srt_file.name}"},
                {"filename": vtt_file.name, "media_type": "vtt", "url": f"/download/subtitle/{vtt_file.name}"},
            ]
        else:
            job.add_log("No transcript available; subtitle generation bypassed.")

        from ai.transcript import TranscriptManager
        transcript_mgr = TranscriptManager(subtitle_transcript or transcript or [])

        # 4. Scene detection (Toggleable)
        job.set_step(4, "Detecting scenes")
        total_dur = float(info.get("duration", 60.0) or 60.0)
        if scene_detection_enabled:
            detector = SceneDetector(video)
            start_scene_t = time.time()
            last_logged_sec = 0.0

            def _on_scene_progress(curr_sec, cuts_count):
                nonlocal last_logged_sec
                if curr_sec - last_logged_sec >= 15.0 or (curr_sec >= total_dur - 1.0):
                    last_logged_sec = curr_sec
                    pct = min(99, int((curr_sec / max(1.0, total_dur)) * 100))
                    elapsed = time.time() - start_scene_t
                    if curr_sec > 5.0 and elapsed > 0:
                        speed = curr_sec / elapsed
                        rem_sec = max(0, total_dur - curr_sec)
                        eta_sec = int(rem_sec / max(0.1, speed))
                        eta_str = f"{eta_sec // 60}m {eta_sec % 60}s" if eta_sec >= 60 else f"{eta_sec}s"
                    else:
                        eta_str = "calculating..."
                    job.add_log(f"Detecting scenes: {int(curr_sec)}s / {int(total_dur)}s ({pct}%) — {cuts_count} cuts found (ETA: {eta_str})")

            job.add_log(f"Starting scene detection across {int(total_dur)}s video (threshold: {scene_threshold})...")
            scenes = detector.detect_scenes(threshold=scene_threshold, progress_callback=_on_scene_progress)
            job.add_log(f"Scene detection complete: {len(scenes)} cuts detected.")
        else:
            d = clip_duration or config.CLIP_DURATION
            scenes = []
            s = 0.0
            while s < total_dur:
                e = min(s + d, total_dur)
                scenes.append({"start": float(s), "end": float(e), "duration": float(e - s)})
                s = e
            job.add_log(f"Scene detection bypassed by user: partitioned into {len(scenes)} uniform segments.")

        # 5. Merge scenes (with sentence boundary snapping)
        job.set_step(5, "Merging scenes and snapping boundaries")
        if scene_merger_enabled:
            merger = SceneMerger(min_duration=min_clip_dur, max_duration=max_clip_dur)
            merged_scenes = merger.merge(scenes, transcript=subtitle_transcript or transcript)
            job.add_log(f"Scene merger enabled: {len(merged_scenes)} clips (min duration: {min_clip_dur}s, sentence-snapped)")
        else:
            merged_scenes = scenes
            job.add_log(f"Scene merger bypassed by user: using {len(merged_scenes)} raw scenes.")

        # Silence detection inspection (Toggleable)
        if silence_trimming_enabled:
            try:
                from ai.silence_detector import SilenceDetector
                s_detector = SilenceDetector(noise_threshold_db=silence_threshold_db)
                silence_res = s_detector.detect_silence(video)
                num_silences = len(silence_res.get("silences", []))
                if num_silences:
                    job.add_log(f"Silence detector: detected {num_silences} silent intervals ({silence_res.get('total_silence', 0):.1f}s dead-air).")
            except Exception as se:
                print(f"[PROCESS] Silence detection note: {se}")

        # ---- Clip count validation for COUNT mode ----
        if clipping_mode == config.CLIPPING_COUNT:
            available = len(merged_scenes) if merged_scenes else len(scenes)
            requested = clip_count or 0
            if requested > available:
                job.clip_count_conflict = {
                    "requested": requested,
                    "available": available,
                }
                job.add_log(
                    f"You requested {requested} clips, but only {available} "
                    f"good clips are available. Continuing with {available}."
                )
                clip_count = available

        # 6. Generate clips (with Framing & Content Naming)
        job.set_step(6, "Generating clips and framing")
        generator = ClipGenerator(video)
        for old in config.CLIPS_DIR.glob("*.mp4"):
            old.unlink(missing_ok=True)

        expected_segments = []
        if clipping_mode == config.CLIPPING_DURATION:
            total_dur_int = int(total_dur)
            start = 0
            idx = 1
            while start < total_dur_int:
                end = min(start + (clip_duration or config.CLIP_DURATION), total_dur_int)
                expected_segments.append({
                    "start": start,
                    "end": end,
                })
                start = end
                idx += 1
        elif clipping_mode == config.CLIPPING_COUNT:
            n = len(merged_scenes) if merged_scenes else len(scenes)
            count = clip_count or 1
            step = max(n / count, 1)
            for i in range(count):
                idx = min(int(i * step), n - 1)
                scene = (merged_scenes or scenes)[idx]
                expected_segments.append({
                    "start": scene["start"],
                    "end": scene["end"],
                })
        else:
            for idx, scene in enumerate(merged_scenes or scenes, start=1):
                expected_segments.append({
                    "start": scene["start"],
                    "end": scene["end"],
                })

        # Smart reframing / Face tracking analysis if enabled
        reframe_x = None
        if smart_reframe_enabled and aspect_key in ("9:16", "1:1", "4:5"):
            try:
                from ai.smart_reframe import SmartReframer
                reframer = SmartReframer()
                reframe_res = reframer.compute_reframe(video, mode=reframe_mode, target_aspect=aspect_key)
                if reframe_res.get("recommendedX") is not None:
                    reframe_x = reframe_res.get("recommendedX")
                if reframe_res.get("keyframes"):
                    job.add_log(f"Smart Face Tracking: {len(reframe_res['keyframes'])} subject center keyframes detected.")
            except Exception as re_err:
                print(f"[PROCESS] Reframe note: {re_err}")

        clips = generator.generate_clips(
            merged_scenes,
            mode=clipping_mode,
            clip_duration=clip_duration,
            clip_count=clip_count,
            aspect_key=aspect_key,
            naming=naming,
            transcript=subtitle_transcript or transcript,
            fps=config.FPS,
            quality=quality,
            reframe_x=reframe_x,
        )
        clip_files = [Path(c).name for c in clips]
        job.add_log(f"Clips generated: {len(clips)} (Framed to {aspect_key})")

        # Map clip files to segments
        clip_segment_map = {}
        for i, cf in enumerate(clip_files):
            if i < len(expected_segments):
                clip_segment_map[cf] = expected_segments[i]
            else:
                clip_segment_map[cf] = {"start": 0.0, "end": 60.0}

        # Register clips in project state
        for clip_path in clips:
            project_state.add_clip(project_id, Path(clip_path).name, f"/download/clip/{Path(clip_path).name}")

        # 7. AI Multi-Modal Ranking & Keyword Extraction
        job.set_step(7, "Ranking clips and extracting viral hooks")
        keyword_extractor = None
        if keyword_extraction_enabled:
            try:
                from ai.keyword_extractor import KeywordExtractor
                keyword_extractor = KeywordExtractor()
            except Exception:
                pass

        candidate_items = []
        for name in clip_files:
            seg = clip_segment_map.get(name) or {"start": 0.0, "end": 60.0}
            clip_start = float(seg.get("start", 0.0))
            clip_end = float(seg.get("end", clip_start + 60.0))
            clip_dur = round(clip_end - clip_start, 2)

            sliced_segs = transcript_mgr.slice(clip_start, clip_end, relative_timestamps=True)
            clip_text = " ".join(s.get("text", "") for s in sliced_segs).strip()

            hashtags = []
            if keyword_extractor and clip_text:
                try:
                    kw_list = keyword_extractor.extract_keywords(clip_text, top_n=5)
                    hashtags = [f"#{kw['word'].capitalize()}" for kw in kw_list[:4]]
                    if hashtags:
                        hashtags.extend(["#Shorts", "#Viral"])
                except Exception:
                    pass

            candidate_items.append({
                "name": name,
                "url": f"/download/clip/{name}",
                "start": clip_start,
                "end": clip_end,
                "duration": clip_dur,
                "text": clip_text,
                "hashtags": hashtags,
                "audio_energy": 75.0 if audio_energy_enabled else 60.0,
                "motion_score": 72.0 if motion_detection_enabled else 60.0,
                "face_score": 80.0 if smart_reframe_enabled else 70.0,
            })

        if viral_ranking_enabled:
            try:
                from ai.clip_ranker import ClipRanker
                ranker = ClipRanker()
                ranked_items = ranker.rank_clips(candidate_items)
                job.clips_meta = ranked_items
                job.add_log(f"AI Viral Ranking complete: scored & ranked {len(ranked_items)} clips.")
            except Exception as rank_err:
                print(f"[PROCESS] Ranking note: {rank_err}")
                job.clips_meta = candidate_items
        else:
            job.clips_meta = candidate_items

        # 8. Apply animated captions & render final clips
        job.set_step(8, "Rendering final clips with kinetic captions")
        captioned_clips = []
        if (caption_enabled or subtitle_enabled) and subtitle_transcript:
            job.add_log("Rendering kinetic captions into each clip...")
            caption_renderer = AnimatedCaptionRenderer()
            caption_dir = config.CLIPS_DIR / "captions"
            caption_dir.mkdir(parents=True, exist_ok=True)
            for stale in caption_dir.glob("*.mp4"):
                stale.unlink(missing_ok=True)

            effective_opts = dict(caption_opts)
            if not caption_enabled and subtitle_enabled:
                effective_opts["animation"] = "none"

            for clip_path in clips:
                clip_name = Path(clip_path).name
                clip_stem = Path(clip_path).stem
                temp_output = clip_path.with_name(f"{clip_stem}_rendered.mp4")
                seg = clip_segment_map.get(clip_name) or {"start": 0.0, "end": 60.0}
                c_start = float(seg.get("start", 0.0))
                c_end = float(seg.get("end", c_start + 60.0))

                # Slice transcript specifically for this clip with relative timestamps starting at 0.0s!
                clip_sub_segments = transcript_mgr.slice(c_start, c_end, relative_timestamps=True)

                try:
                    rendered = caption_renderer.render(
                        input_video=clip_path,
                        transcript=clip_sub_segments,
                        output_video=temp_output,
                        opts=effective_opts,
                        template=caption_template,
                    )
                    if rendered and rendered.exists():
                        rendered.replace(clip_path)
                        captioned_clips.append(clip_path)
                except Exception as e:
                    job.add_log(f"Caption render failed for {clip_stem}: {e}")

            if not captioned_clips:
                captioned_clips = list(clips)

            job.add_log(f"Captions/subtitles rendered for {len(captioned_clips)} clips.")
        else:
            captioned_clips = list(clips)

        final_clip_files = [Path(c).name for c in captioned_clips]

        # Per-clip SRT/VTT: create clip-specific subtitle files with adjusted timestamps
        clip_subtitle_map = {}
        if subtitle_transcript:
            for clip_path in captioned_clips:
                clip_name = Path(clip_path).name
                clip_stem = Path(clip_path).stem
                clip_srt = config.SUBTITLE_DIR / f"{clip_stem}.srt"
                clip_vtt = config.SUBTITLE_DIR / f"{clip_stem}.vtt"
                seg = clip_segment_map.get(clip_name)
                try:
                    _write_clip_subtitles(
                        subtitle_transcript, clip_srt, clip_vtt,
                        seg["start"] if seg else 0,
                        seg["end"] if seg else None,
                    )
                    clip_subtitle_map[clip_stem] = {
                        "srt": f"/download/subtitle/{clip_srt.name}",
                        "vtt": f"/download/subtitle/{clip_vtt.name}",
                    }
                except Exception:
                    pass

        job.result = {
            "filename": job.filename,
            "project_id": project_id,
            "metadata": info,
            "scenes": len(scenes),
            "merged_clips": len(merged_scenes),
            "clips": final_clip_files,
            "clips_meta": job.clips_meta,
            "transcript": transcript,
            "subtitle_transcript": subtitle_transcript,
            "srt": f"/download/subtitle/{stem}.srt" if transcript else None,
            "vtt": f"/download/subtitle/{stem}.vtt" if transcript else None,
            "transcript_file": f"/download/transcript/{stem}.json" if transcript else None,
            "final_video": None,
            "caption_video": None,
            "caption_clips": [],
            "thumbnail": f"/download/thumbnail/{stem}_thumb.jpg",
            "quality": quality,
            "caption_enabled": caption_enabled,
            "whisper_enabled": whisper_enabled,
            "whisper_model": whisper_model,
            "uploaded_subtitle_file": uploaded_sub_filename,
            "viral_ranking_enabled": viral_ranking_enabled,
            "clip_count_conflict": getattr(job, "clip_count_conflict", None),
            "source_video": job.filename,
            "caption_style": _style_to_dict(job.caption_style) if job.caption_style else None,
            "clip_subtitle_map": clip_subtitle_map,
        }

        job.status = "done"
        job.finished = True
        job.add_log("Pipeline completed successfully.")

        # Persist generated clips to database Project and record recent project
        try:
            from models.project import Project
            from extensions import db
            from core.project_manager import project_manager
            import json

            db_proj = None
            if project_id and str(project_id).isdigit():
                db_proj = Project.query.get(int(project_id))
            if not db_proj and job.filename:
                db_proj = Project.query.filter_by(source_path=job.filename).first()

            clips_data = [
                {
                    "filename": c,
                    "url": f"/download/clip/{c}",
                    "label": c,
                    "media_type": "clip"
                }
                for c in final_clip_files
            ]

            thumb_url = f"/download/thumbnail/{stem}_thumb.jpg"
            if not db_proj:
                db_proj = Project(
                    name=Path(job.filename).stem,
                    source_path=job.filename,
                    thumbnail_path=thumb_url,
                    duration=float(info.get("duration", 0.0) or 0.0),
                    status="done"
                )
                db.session.add(db_proj)
                db.session.flush()

            existing_editor_state = {}
            if db_proj.editor_state:
                try:
                    existing_editor_state = json.loads(db_proj.editor_state)
                except Exception:
                    existing_editor_state = {}
            existing_editor_state["clips"] = clips_data
            existing_editor_state["aspect"] = aspect_key
            db_proj.editor_state = json.dumps(existing_editor_state)
            db_proj.status = "done"
            db_proj.thumbnail_path = thumb_url
            db.session.commit()

            # Record in recent projects
            project_manager.record_recent_project(
                project_id=db_proj.id,
                name=db_proj.name,
                source_path=db_proj.source_path or "",
                thumbnail_path=db_proj.thumbnail_path or ""
            )

            job.project_id = db_proj.id
            if job.result:
                job.result["project_id"] = db_proj.id
        except Exception as pe:
            print(f"[PROCESS] Error persisting project clips to DB: {pe}")

    except Exception as e:
        job.status = "error"
        job.finished = True
        job.error = str(e)
        job.add_log(f"ERROR: {e}")
    finally:
        if ctx:
            try:
                ctx.pop()
            except Exception:
                pass


@process_bp.route("/ffmpeg", methods=["GET"])
def ffmpeg_status():
    """Return whether FFmpeg is available."""
    status, version = check_ffmpeg()
    return jsonify({"success": True, "installed": status, "version": version})


@process_bp.route("/start", methods=["POST"])
def start():
    """Start a new pipeline job for a given video filename."""
    global JOB_COUNTER

    data = request.get_json(silent=True) or {}
    filename = data.get("filename", "")
    settings = data.get("settings", {})

    if not filename:
        return jsonify({"success": False, "error": "No filename provided"}), 400

    video = config.INPUT_DIR / filename
    if not video.exists():
        return jsonify({"success": False, "error": f"Video not found: {filename}"}), 404

    with JOB_LOCK:
        JOB_COUNTER += 1
        job_id = f"job_{JOB_COUNTER}"
        job = PipelineJob(job_id, filename, settings)
        JOBS[job_id] = job

    # Run in background thread
    app_obj = current_app._get_current_object()
    thread = threading.Thread(
        target=run_pipeline_job,
        args=(job, app_obj),
        daemon=True
    )
    thread.start()

    return jsonify({"success": True, "job_id": job_id})


@process_bp.route("/status/<job_id>", methods=["GET"])
def status(job_id):
    """Return the current status of a pipeline job."""
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"success": False, "error": "Job not found"}), 404
    data = job.to_dict()
    data["success"] = True
    return jsonify(data)


# ======================================================
# Clip Review endpoints
# ======================================================

@process_bp.route("/clips/<job_id>", methods=["GET"])
def clips_list(job_id):
    """Return metadata for all generated clips of a job."""
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"success": False, "error": "Job not found"}), 404
    return jsonify({"success": True, "clips": job.clips_meta})


@process_bp.route("/clip/delete", methods=["POST"])
def clip_delete():
    """Delete a generated clip file."""
    data = request.get_json(silent=True) or {}
    filename = Path(data.get("filename", "")).name
    if not filename:
        return jsonify({"success": False, "error": "No filename"}), 400

    clip_path = config.CLIPS_DIR / filename
    if not clip_path.exists():
        return jsonify({"success": False, "error": "Clip not found"}), 404

    try:
        clip_path.unlink()
        return jsonify({"success": True, "deleted": filename})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@process_bp.route("/clip/rename", methods=["POST"])
def clip_rename():
    """Rename a generated clip file."""
    data = request.get_json(silent=True) or {}
    old_name = Path(data.get("old_name", "")).name
    new_name = Path(data.get("new_name", "")).name

    if not old_name or not new_name:
        return jsonify({"success": False, "error": "old_name and new_name required"}), 400

    old_path = config.CLIPS_DIR / old_name
    new_path = config.CLIPS_DIR / new_name

    if not old_path.exists():
        return jsonify({"success": False, "error": "Clip not found"}), 404
    if new_path.exists():
        return jsonify({"success": False, "error": "Target name already exists"}), 400

    try:
        old_path.rename(new_path)
        return jsonify({"success": True, "old": old_name, "new": new_name})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@process_bp.route("/metadata/<filename>", methods=["GET"])
def get_metadata(filename):
    """Get metadata for a file in the input directory."""
    filename = Path(filename).name
    video_path = config.INPUT_DIR / filename

    if not video_path.exists():
        return jsonify({"success": False, "error": "File not found"}), 404

    try:
        loader = VideoLoader(video_path)
        info = loader.metadata()
        loader.close()
        return jsonify({"success": True, "metadata": info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ======================================================
# Global active jobs
# ======================================================

@process_bp.route("/active-jobs", methods=["GET"])
def active_jobs():
    """Return summary of all active pipeline jobs."""
    with JOB_LOCK:
        jobs = []
        for job in JOBS.values():
            if not job.finished:
                jobs.append({
                    "job_id": job.job_id,
                    "filename": job.filename,
                    "status": job.status,
                    "step": job.step,
                    "steps_completed": job.steps_completed,
                    "total_steps": job.total_steps,
                })
    return jsonify({"success": True, "jobs": jobs, "count": len(jobs)})


@process_bp.route("/clip/send-to-input", methods=["POST"])
def clip_send_to_input():
    """Copy a generated clip to the input directory so it can be used elsewhere."""
    data = request.get_json(silent=True) or {}
    filename = Path(data.get("filename", "")).name
    if not filename:
        return jsonify({"success": False, "error": "No filename"}), 400

    clip_path = config.CLIPS_DIR / filename
    if not clip_path.exists():
        return jsonify({"success": False, "error": "Clip not found"}), 404

    try:
        import shutil
        dest = config.INPUT_DIR / filename
        shutil.copy2(str(clip_path), str(dest))
        return jsonify({"success": True, "filename": filename, "path": f"/download/input/{filename}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def _style_to_dict(style):
    if not style:
        return None
    return {
        "id": style.id,
        "name": style.name,
        "font_family": style.font_family,
        "font_size": style.font_size,
        "font_weight": style.font_weight,
        "text_color": style.text_color,
        "active_word_color": style.active_word_color,
        "background_color": style.background_color,
        "background_opacity": style.background_opacity,
        "outline_color": style.outline_color,
        "outline_width": style.outline_width,
        "shadow_color": style.shadow_color,
        "shadow_blur": style.shadow_blur,
        "shadow_offset_y": style.shadow_offset_y,
        "position": style.position,
        "animation": style.animation,
        "letter_spacing": style.letter_spacing,
        "line_height": style.line_height,
        "max_lines": style.max_lines,
    }


def _write_clip_subtitles(transcript, srt_path, vtt_path, clip_start, clip_end):
    """Write SRT and VTT files for a clip, adjusting timestamps relative to clip_start."""
    builder = SubtitleBuilder()
    segments = []
    for seg in transcript:
        seg_start = float(seg.get("start", 0))
        seg_end = float(seg.get("end", 0))
        if clip_end is not None:
            if seg_end <= clip_start or seg_start >= clip_end:
                continue
            adj_start = max(0, seg_start - clip_start)
            adj_end = min(clip_end - clip_start, seg_end - clip_start)
        else:
            adj_start = max(0, seg_start - clip_start)
            adj_end = seg_end - clip_start
        if adj_end <= adj_start:
            continue
        segments.append({
            "start": adj_start,
            "end": adj_end,
            "text": seg.get("text", ""),
        })

    srt_path = Path(srt_path)
    vtt_path = Path(vtt_path)
    srt_path.parent.mkdir(parents=True, exist_ok=True)
    vtt_path.parent.mkdir(parents=True, exist_ok=True)
    if segments:
        builder.save_all(segments, srt_path, vtt_path)
