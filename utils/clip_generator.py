from pathlib import Path
import subprocess
import re

import config
from utils.video_utils import VideoLoader


class ClipGenerator:

    def __init__(self, video_path):
        self.video_path = Path(video_path)

    # ======================================================
    # Build FFmpeg filter for aspect-ratio smart crop
    # ======================================================

    def _build_crop_filter(self, target_width, target_height, reframe_x=None):
        """
        Build an ffmpeg scale + crop filter that does intelligent
        crop/reframe (center or subject-aware) instead of stretching.

        Returns None if no aspect change needed (original).
        """
        if target_width is None or target_height is None:
            return None

        # Ensure even pixel dimensions for libx264 encoding
        target_width = (int(target_width) // 2) * 2
        target_height = (int(target_height) // 2) * 2

        scale_part = f"scale={target_width}:{target_height}:force_original_aspect_ratio=increase"

        # Explicit center crop as reliable default
        crop_part = f"crop={target_width}:{target_height}:(in_w-{target_width})/2:(in_h-{target_height})/2"

        if reframe_x is not None:
            try:
                rx = float(reframe_x)
                if 0.05 <= rx <= 0.95:
                    # Subject center as ratio (e.g. 0.5 = center, 0.3 = left, 0.7 = right)
                    crop_part = f"crop={target_width}:{target_height}:max(0\\,min(in_w-{target_width}\\,in_w*{rx}-{target_width}/2)):(in_h-{target_height})/2"
                elif abs(rx) > 0.5:
                    # Pixel/canvas offset from center
                    crop_part = f"crop={target_width}:{target_height}:max(0\\,min(in_w-{target_width}\\,(in_w-{target_width})/2+({rx}))):(in_h-{target_height})/2"
            except (ValueError, TypeError):
                pass

        return f"{scale_part},{crop_part}"

    # ======================================================
    # Build FFmpeg scale filter for quality presets
    # ======================================================

    def _build_quality_filter(self, quality_key, target_w, target_h):
        """
        Build a scale filter enforcing a max resolution for the selected
        quality preset, preserving the target aspect ratio.

        Returns None if original quality or already within bounds.
        """
        preset = config.QUALITY_PRESETS.get(
            quality_key,
            config.QUALITY_PRESETS[config.DEFAULT_QUALITY]
        )
        max_w, max_h = preset[1], preset[2]
        if max_w is None or max_h is None:
            return None

        # If aspect crop already determines exact dimensions:
        if target_w and target_h:
            # For vertical/portrait formats (target_h > target_w):
            # The preset dimensions (e.g. 1920x1080 for 1080p, 1280x720 for 720p)
            # must align with vertical bounds: max vertical width = min(max_w, max_h),
            # max vertical height = max(max_w, max_h).
            if target_h > target_w:
                preset_limit_w = min(max_w, max_h)
                preset_limit_h = max(max_w, max_h)
            elif target_w > target_h:
                preset_limit_w = max(max_w, max_h)
                preset_limit_h = min(max_w, max_h)
            else:  # 1:1 square
                square_limit = min(max_w, max_h)
                preset_limit_w = square_limit
                preset_limit_h = square_limit

            # Calculate if scaling down is required
            scale_factor = min(1.0, preset_limit_w / float(target_w), preset_limit_h / float(target_h))
            if scale_factor >= 1.0:
                # Target dimensions already fit within quality preset bounds!
                return None

            out_w = (int(target_w * scale_factor) // 2) * 2
            out_h = (int(target_h * scale_factor) // 2) * 2
            return f"scale={out_w}:{out_h}"

        # Otherwise scale down to fit within (max_w, max_h), preserving ratio.
        return (
            f"scale={max_w}:{max_h}:force_original_aspect_ratio=decrease"
        )

    # ======================================================
    # Create Single Clip
    # ======================================================

    def create_clip(
        self,
        start_time,
        duration,
        output_file,
        aspect_key="original",
        fps=None,
        quality=config.DEFAULT_QUALITY,
        reframe_x=None,
    ):
        """
        Create one MP4 clip using FFmpeg.

        start_time  : float start (seconds)
        duration    : float duration (seconds)
        output_file : Path output file
        aspect_key  : config.ASPECT_OPTIONS key (e.g. 'original', '9:16')
        quality     : config.QUALITY_PRESETS key (e.g. 'original', '1080p')
        reframe_x   : optional horizontal subject offset or center ratio
        """

        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Resolve aspect ratio
        aspect = config.ASPECT_OPTIONS.get(
            aspect_key,
            config.ASPECT_OPTIONS["original"]
        )
        target_w, target_h = aspect[1], aspect[2]

        command = [
            config.FFMPEG_PATH,
            "-y",
            # Fast input seeking (before -i) for much faster start
            "-ss", str(start_time),
            "-i", str(self.video_path),
            "-t", str(duration),
        ]

        # Build combined video filter: aspect crop + quality scaling
        filters = []
        crop_filter = self._build_crop_filter(target_w, target_h, reframe_x=reframe_x)
        if crop_filter:
            filters.append(crop_filter)

        quality_filter = self._build_quality_filter(quality, target_w, target_h)
        if quality_filter:
            filters.append(quality_filter)

        if filters:
            command += ["-vf", ",".join(filters)]

        # Optional FPS (only when explicitly requested to avoid re-encode)
        if fps:
            command += ["-r", str(fps)]

        command += [
            "-c:v", config.VIDEO_CODEC,
            # Fast encoding preset + quality CRF
            "-preset", "veryfast",
            "-crf", "23",
            "-c:a", config.AUDIO_CODEC,
            str(output_file)
        ]

        try:
            subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            return output_file
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed : {output_file.name}")
            print(e)
            return None

    # ======================================================
    # Content-based clip naming
    # ======================================================

    def _slugify(self, text, max_len=40):
        """Convert arbitrary text to a safe filename slug."""
        text = (text or "").strip().lower()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[\s_]+", "_", text).strip("_")
        if not text:
            return None
        return text[:max_len]

    def _build_clip_name(
        self,
        index,
        naming,
        transcript=None,
        start_time=0,
        duration=0,
        existing_names=None,
    ):
        """
        Build a clip filename based on naming mode.

        naming         : config.NAME_SEQUENTIAL or config.NAME_CONTENT
        transcript     : optional list of {start,end,text} used for content names
        existing_names : optional set of already-used filenames to avoid duplicates
        """
        existing_names = existing_names or set()
        base_name = None

        if naming == config.NAME_CONTENT:
            base_name = self._get_content_name(transcript, start_time, duration, index)
        elif naming == config.NAME_SEQUENTIAL:
            base_name = f"AI_Spark_Clip_{index:03d}"

        if not base_name:
            base_name = f"AI_Spark_Clip_{index:03d}"

        # Ensure filesystem-safe filename
        safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", base_name).strip("._")
        if not safe_name:
            safe_name = f"AI_Spark_Clip_{index:03d}"

        # Handle duplicate names
        final_name = f"{safe_name}.mp4"
        counter = 1
        while final_name in existing_names:
            final_name = f"{safe_name}_{counter:02d}.mp4"
            counter += 1

        existing_names.add(final_name)
        return final_name

    def _get_content_name(self, transcript, start_time, duration, index):
        """Extract a meaningful content-based name from spoken transcript and topic."""
        clip_end = start_time + max(float(duration or 0), 1.0)
        collected_texts = []
        if transcript:
            for seg in transcript:
                s_start = float(seg.get("start", 0))
                s_end = float(seg.get("end", 0))
                if not (s_end < start_time or s_start > clip_end):
                    t = (seg.get("text") or "").strip()
                    if t:
                        collected_texts.append(t)

        full_clip_text = " ".join(collected_texts).strip()

        stop_words = {
            "this", "that", "with", "from", "have", "were", "been", "they", "will",
            "what", "when", "where", "which", "about", "there", "their", "would",
            "video", "clip", "shorts", "hindi", "kya", "aur", "hota", "hoti", "hote",
            "kare", "karna", "nahi", "islye", "lekin", "bahut", "raha", "rahe", "gaya",
            "said", "then", "into", "more", "some", "such", "than", "them", "these",
            "also", "just", "like", "know", "good", "well", "come", "time", "make"
        }

        # Extract words of 3+ alphanumeric chars
        words = re.findall(r"[A-Za-z0-9]{3,}", full_clip_text)
        filtered = [w for w in words if w.lower() not in stop_words]

        if len(filtered) >= 2:
            title_slug = "_".join(w.capitalize() for w in filtered[:4])
            return f"{title_slug}_{index:02d}"

        # Fallback to source video filename topic
        source_stem = Path(self.video_path).stem
        source_words = re.findall(r"[A-Za-z0-9]{3,}", source_stem)
        filtered_source = [w for w in source_words if w.lower() not in stop_words]

        if filtered_source:
            source_slug = "_".join(w.capitalize() for w in filtered_source[:3])
            return f"{source_slug}_Clip_{index:02d}"

        return f"Viral_Clip_{index:03d}"

    # ======================================================
    # Phase 3 - Split by Fixed Duration
    # ======================================================

    def split_video(
        self,
        clip_duration=None,
        aspect_key="original",
        naming=config.NAME_SEQUENTIAL,
        transcript=None,
        fps=None,
        quality=config.DEFAULT_QUALITY,
        reframe_x=None,
    ):

        if clip_duration is None:
            clip_duration = config.CLIP_DURATION

        loader = VideoLoader(self.video_path)
        info = loader.metadata()
        total_duration = int(info["duration"])
        loader.close()

        clips = []
        start = 0
        index = 1
        used_names = set()

        print("\nGenerating Fixed Clips...")
        print("-" * 50)

        while start < total_duration:

            duration = min(
                clip_duration,
                total_duration - start
            )

            filename = self._build_clip_name(
                index, naming, transcript, start, duration, used_names
            )
            output_file = config.CLIPS_DIR / filename

            clip = self.create_clip(
                start,
                duration,
                output_file,
                aspect_key=aspect_key,
                fps=fps,
                quality=quality,
                reframe_x=reframe_x,
            )

            if clip:
                clips.append(clip)
                print(
                    f"✅ Clip {index:03d} | "
                    f"{start:.1f}s → {start+duration:.1f}s"
                )

            start += clip_duration
            index += 1

        print("-" * 50)
        print(f"Total Fixed Clips : {len(clips)}")

        return clips

    # ======================================================
    # Build clips from scene segments with modes
    # ======================================================

    def generate_clips(
        self,
        scenes,
        mode=config.CLIPPING_AI,
        clip_duration=None,
        clip_count=None,
        aspect_key="original",
        naming=config.NAME_SEQUENTIAL,
        transcript=None,
        fps=None,
        quality=config.DEFAULT_QUALITY,
        reframe_x=None,
    ):
        """
        Generate clips from detected scenes according to user clipping mode.

        mode : config.CLIPPING_AI | CLIPPING_DURATION | CLIPPING_COUNT

        - AI mode: uses merged scenes as-is (AI decides count & duration)
        - DURATION mode: splits into fixed-duration clips, up to all possible
        - COUNT mode: picks N best scenes (evenly spaced) and adjusts duration
        """
        if mode == config.CLIPPING_DURATION:
            return self.split_video(
                clip_duration=clip_duration or config.CLIP_DURATION,
                aspect_key=aspect_key,
                naming=naming,
                transcript=transcript,
                fps=fps,
                quality=quality,
                reframe_x=reframe_x,
            )

        if mode == config.CLIPPING_COUNT:
            return self._generate_by_count(
                scenes,
                clip_count=clip_count or 1,
                aspect_key=aspect_key,
                naming=naming,
                transcript=transcript,
                fps=fps,
                quality=quality,
                reframe_x=reframe_x,
            )

        # Default: AI mode generates one unique edited clip per scene.
        # This keeps the output aligned with the final workflow: each detected
        # scene becomes a complete, stand-alone clip with no duplicate versions.
        return self.split_by_scenes(
            scenes,
            aspect_key=aspect_key,
            naming=naming,
            transcript=transcript,
            fps=fps,
            quality=quality,
            reframe_x=reframe_x,
        )

    # ======================================================
    # COUNT mode - pick N best scenes
    # ======================================================

    def _generate_by_count(
        self,
        scenes,
        clip_count,
        aspect_key="original",
        naming=config.NAME_SEQUENTIAL,
        transcript=None,
        fps=None,
        quality=config.DEFAULT_QUALITY,
        reframe_x=None,
    ):
        """Pick `clip_count` best scenes evenly spaced through the video."""
        clips = []
        if not scenes:
            return clips

        # We use merged-like scenes; pick evenly spaced indices
        n = len(scenes)
        if clip_count >= n:
            selected_indices = list(range(n))
        else:
            step = n / clip_count
            selected_indices = [int(i * step) for i in range(clip_count)]

        print("\nGenerating Clips by Count...")
        print("-" * 50)
        used_names = set()

        for pos, idx in enumerate(selected_indices, start=1):
            scene = scenes[idx]
            start = scene["start"]
            end = scene["end"]
            duration = end - start
            min_dur = getattr(config, "MIN_DURATION", 60.0)
            if len(scenes) > 1 and duration < min(min_dur * 0.7, 45.0):
                continue

            filename = self._build_clip_name(
                pos, naming, transcript, start, duration, used_names
            )
            output_file = config.CLIPS_DIR / filename

            clip = self.create_clip(
                start,
                duration,
                output_file,
                aspect_key=aspect_key,
                fps=fps,
                quality=quality,
                reframe_x=reframe_x,
            )

            if clip:
                clips.append(clip)
                print(
                    f"🎬 Clip {pos:03d} | "
                    f"{start:.2f}s → {end:.2f}s"
                )

        print("-" * 50)
        print(f"Total Count Clips : {len(clips)}")
        return clips

    # ======================================================
    # Split by Scene Detection (AI mode)
    # ======================================================

    def split_by_scenes(
        self,
        scenes,
        aspect_key="original",
        naming=config.NAME_SEQUENTIAL,
        transcript=None,
        fps=None,
        quality=config.DEFAULT_QUALITY,
        reframe_x=None,
    ):

        clips = []

        print("\nGenerating Scene Clips...")
        print("-" * 50)

        index = 1
        used_names = set()

        for scene in scenes:

            start = scene["start"]
            end = scene["end"]

            duration = end - start

            # Skip very small scenes (must be genuine clip duration floor >= 60s)
            min_dur = getattr(config, "MIN_DURATION", 60.0)
            if len(scenes) > 1 and duration < min(min_dur * 0.7, 45.0):
                continue

            # Cap very long scenes to max clip duration
            if duration > config.MAX_CLIP_DURATION:
                duration = config.MAX_CLIP_DURATION

            filename = self._build_clip_name(
                index, naming, transcript, start, duration, used_names
            )
            output_file = config.CLIPS_DIR / filename

            clip = self.create_clip(
                start,
                duration,
                output_file,
                aspect_key=aspect_key,
                fps=fps,
                quality=quality,
                reframe_x=reframe_x,
            )

            if clip:
                clips.append(clip)
                print(
                    f"🎬 Scene {index:03d} | "
                    f"{start:.2f}s → {end:.2f}s"
                )

            index += 1

        print("-" * 50)
        print(f"Total Scene Clips : {len(clips)}")

        return clips
