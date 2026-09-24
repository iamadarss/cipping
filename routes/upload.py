"""Upload route - handles video upload and metadata extraction."""

import config
from pathlib import Path

from flask import Blueprint, request, jsonify

from utils.video_utils import VideoLoader

upload_bp = Blueprint("upload", __name__, url_prefix="/upload")


@upload_bp.route("/video", methods=["POST"])
def upload_video():
    """Accept an uploaded video, save it, extract metadata and thumbnail."""

    if "video" not in request.files:
        return jsonify({"success": False, "error": "No video file provided"}), 400

    file = request.files["video"]

    if file.filename == "":
        return jsonify({"success": False, "error": "Empty filename"}), 400

    import re
    raw_name = Path(file.filename).name
    # Fix cp1252 / latin-1 decoding if Werkzeug misinterpreted UTF-8 filename
    for enc in ("cp1252", "latin-1", "iso-8859-1"):
        try:
            cand = raw_name.encode(enc).decode("utf-8")
            if cand and not any(c in cand for c in ('â', 'Ã', 'Â', 'ï')):
                raw_name = cand
                break
        except Exception:
            pass

    # Strip illegal characters (< > : " / \ | ? *) while preserving Unicode, spaces, and punctuation
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", raw_name).strip() or "uploaded_video.mp4"

    # Save to input directory
    config.INPUT_DIR.mkdir(parents=True, exist_ok=True)
    save_path = config.INPUT_DIR / filename

    file.save(str(save_path))

    # Extract metadata
    try:
        loader = VideoLoader(save_path)
        info = loader.metadata()

        # Generate thumbnail
        config.THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)
        thumb_name = f"{Path(filename).stem}_thumb.jpg"
        thumb_path = config.THUMBNAIL_DIR / thumb_name
        loader.thumbnail(thumb_path)
        loader.close()

        # Verify thumbnail file actually exists on disk
        if not thumb_path.exists() or thumb_path.stat().st_size == 0:
            from utils.ffmpeg_utils import generate_thumbnail
            generate_thumbnail(save_path, thumb_path)

        thumb_url = f"/download/thumbnail/{thumb_name}"

        # Register or update in SQLite Project database
        proj_id = None
        try:
            from extensions import db
            from models.project import Project
            from core.project_manager import project_manager

            dur = float(info.get("duration", 0.0) or 0.0)
            proj = Project.query.filter_by(source_path=filename).first()
            if not proj:
                proj = Project(
                    name=Path(filename).stem,
                    source_path=filename,
                    thumbnail_path=thumb_url,
                    duration=dur,
                    status="ready"
                )
                db.session.add(proj)
            else:
                proj.name = Path(filename).stem
                proj.thumbnail_path = thumb_url
                proj.duration = dur
                proj.status = "ready"
            db.session.commit()

            project_manager.record_recent_project(
                project_id=proj.id,
                name=proj.name,
                source_path=proj.source_path or "",
                thumbnail_path=proj.thumbnail_path or ""
            )
            proj_id = proj.id
        except Exception as db_err:
            from flask import current_app
            current_app.logger.warning("Failed to register project in DB: %s", db_err)

        return jsonify({
            "success": True,
            "filename": filename,
            "project_id": proj_id,
            "metadata": info,
            "thumbnail": thumb_url,
            "video_url": f"/download/input/{filename}"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@upload_bp.route("/subtitle", methods=["POST"])
@upload_bp.route("/transcript", methods=["POST"])
def upload_subtitle():
    """Accept an uploaded subtitle/transcript file (.srt, .vtt, .json, .txt), parse segments and cache."""
    file = None
    for field in ("subtitle", "transcript", "file"):
        if field in request.files:
            file = request.files[field]
            break

    if not file or file.filename == "":
        return jsonify({"success": False, "error": "No subtitle or transcript file provided"}), 400

    import re
    from ai.transcript import TranscriptManager
    from ai.subtitle_builder import SubtitleBuilder

    raw_name = Path(file.filename).name
    # Clean filename
    clean_name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", raw_name).strip() or "uploaded_subtitles.srt"
    ext = Path(clean_name).suffix.lower()

    if ext not in [".srt", ".vtt", ".json", ".txt"]:
        return jsonify({"success": False, "error": f"Unsupported subtitle format: '{ext}'. Please upload .srt, .vtt, .json, or .txt."}), 400

    config.SUBTITLE_DIR.mkdir(parents=True, exist_ok=True)
    config.TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    dest_path = config.SUBTITLE_DIR / clean_name
    file.save(str(dest_path))

    try:
        manager = TranscriptManager()
        manager.load(dest_path)

        segments = manager.segments
        segment_count = len(segments)
        duration = round(float(segments[-1]["end"]), 2) if segments else 0.0
        word_count = len(manager.full_text.split())
        preview = manager.full_text[:250] + ("..." if len(manager.full_text) > 250 else "")

        # Guarantee both .json transcript and .srt exist for downstream modules
        stem = Path(clean_name).stem
        json_path = config.TRANSCRIPT_DIR / f"{stem}.json"
        srt_path = config.SUBTITLE_DIR / f"{stem}.srt"
        vtt_path = config.SUBTITLE_DIR / f"{stem}.vtt"

        builder = SubtitleBuilder()
        if segments:
            builder.save_all(segments, srt_path, vtt_path)
            with open(json_path, "w", encoding="utf-8") as jf:
                import json
                json.dump(segments, jf, ensure_ascii=False, indent=2)

        return jsonify({
            "success": True,
            "filename": clean_name,
            "stem": stem,
            "format": ext.lstrip("."),
            "segment_count": segment_count,
            "segments_count": segment_count,
            "duration": duration,
            "word_count": word_count,
            "preview": preview,
            "text_preview": preview,
            "srt_url": f"/download/subtitle/{stem}.srt",
            "vtt_url": f"/download/subtitle/{stem}.vtt",
            "json_url": f"/download/transcript/{stem}.json",
            "message": f"Successfully loaded {segment_count} subtitle segments ({duration}s duration)."
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to parse subtitle file: {str(e)}"
        }), 500

