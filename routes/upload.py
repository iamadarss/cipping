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
