import os
from pathlib import Path
from flask import Blueprint, jsonify, current_app
from utils.video_utils import VideoLoader

media_thumbnail_bp = Blueprint('media_thumbnail', __name__)

@media_thumbnail_bp.route('/api/thumbnail/<path:media_path>')
def get_thumbnail(media_path):
    """Generate (or retrieve cached) thumbnail for a media file.
    `media_path` is relative to the project's media directory.
    Returns JSON with URL to the thumbnail image.
    """
    # Resolve absolute media path and guard against directory traversal
    media_root = current_app.config.get('MEDIA_ROOT', '')
    if not media_root:
        return jsonify({"error": "Media root not configured"}), 500

    try:
        root_resolved = Path(media_root).resolve()
        media_abs_path = (root_resolved / media_path).resolve()
        # Ensure target is strictly inside root_resolved
        if not str(media_abs_path).startswith(str(root_resolved)):
            return jsonify({"error": "Access denied"}), 403
    except Exception:
        return jsonify({"error": "Invalid path"}), 400

    if not media_abs_path.is_file():
        return jsonify({"error": "Media not found"}), 404

    # Ensure thumbnail cache directory exists inside static folder
    static_folder = current_app.static_folder or "static"
    thumb_dir = Path(static_folder) / 'cache' / 'thumbnails'
    thumb_dir.mkdir(parents=True, exist_ok=True)

    # Thumbnail filename based on media filename
    base_name = media_abs_path.stem
    thumb_path = thumb_dir / f"{base_name}_thumb.png"

    # Generate thumbnail if not cached
    if not thumb_path.is_file():
        loader = VideoLoader(media_abs_path)
        loader.thumbnail(thumb_path)  # uses existing thumbnail helper (captures first frame)
        loader.close()

    thumb_url = f"/static/cache/thumbnails/{base_name}_thumb.png"
    return jsonify({"thumbUrl": thumb_url})
