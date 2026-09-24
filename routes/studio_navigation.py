"""Cross-module navigation routes - connect YouTube Downloader, Clip Cutter, Caption Studio, and YouTube Automation."""

import config
from pathlib import Path
from typing import Dict, Optional
from flask import Blueprint, request, jsonify, render_template, redirect, url_for

from core.project_state import project_state, CaptionStyleConfig

studio_nav_bp = Blueprint("studio_navigation", __name__)


# ============================================================
# Media passing endpoints
# ============================================================

@studio_nav_bp.route("/studio/navigate", methods=["POST"])
def navigate_to_module():
    """Navigate from one module to another, passing media references."""
    data = request.get_json(silent=True) or {}
    target_module = data.get("target_module", "")
    project_id = data.get("project_id", "")
    media_type = data.get("media_type", "")
    filename = data.get("filename", "")
    caption_style = data.get("caption_style")

    if not target_module or not project_id:
        return jsonify({"success": False, "error": "target_module and project_id required"}), 400

    project = project_state.get_project(project_id)
    if not project:
        return jsonify({"success": False, "error": "Project not found"}), 404

    if caption_style:
        style = _parse_style_config(caption_style)
        project_state.set_caption_style(project_id, style)

    project_state.navigate_to(project_id, target_module, {
        "media_type": media_type,
        "filename": filename,
    })

    redirect_map = {
        "clip_cutter": "/dashboard",
        "caption_studio": "/caption-studio",
        "youtube_automation": "/youtube-desk",
        "home": "/",
        "yt_downloader": "/yt-downloader",
    }

    redirect_url = redirect_map.get(target_module, "/")
    return jsonify({
        "success": True,
        "redirect_url": redirect_url,
        "project_id": project_id,
        "module": target_module,
    })


@studio_nav_bp.route("/studio/open-in-clip-cutter", methods=["POST"])
def open_in_clip_cutter():
    """Open a video directly in Clip Cutter (the main studio pipeline)."""
    data = request.get_json(silent=True) or {}
    filename = data.get("filename", "")
    source = data.get("source", "youtube")  # youtube | upload | caption_studio

    if not filename:
        return jsonify({"success": False, "error": "filename required"}), 400

    video_path = config.INPUT_DIR / filename
    if not video_path.exists():
        return jsonify({"success": False, "error": "Video not found"}), 404

    project = project_state.create_project(filename, f"/download/input/{filename}")
    project_state.navigate_to(project.project_id, "clip_cutter", {
        "filename": filename,
        "source": source,
    })

    return jsonify({
        "success": True,
        "redirect_url": "/dashboard?file=" + filename,
        "project_id": project.project_id,
    })


@studio_nav_bp.route("/studio/open-in-caption-studio", methods=["POST"])
def open_in_caption_studio():
    """Open a clip or source video in Caption Studio."""
    data = request.get_json(silent=True) or {}
    filename = data.get("filename", "")
    project_id = data.get("project_id", "")
    source = data.get("source", "clip_cutter")

    if not filename and not project_id:
        return jsonify({"success": False, "error": "filename or project_id required"}), 400

    if not project_id:
        all_projects = project_state.list_all_projects()
        for summary in all_projects:
            if summary["source_video"] == filename:
                project_id = summary["project_id"]
                break
            for clip_fn in summary["clips"]:
                if clip_fn == filename:
                    project_id = summary["project_id"]
                    break
            if project_id:
                break

    if not project_id:
        video_path = config.INPUT_DIR / filename if filename else None
        if video_path and video_path.exists():
            project = project_state.create_project(filename, f"/download/input/{filename}")
            project_id = project.project_id
        else:
            return jsonify({"success": False, "error": "Project not found"}), 404

    project_state.navigate_to(project_id, "caption_studio", {
        "filename": filename,
        "source": source,
    })

    video_path = config.INPUT_DIR / filename if filename else None
    video_url = ""
    if video_path and video_path.exists():
        video_url = f"/download/input/{filename}"
    elif filename:
        video_url = f"/download/clip/{filename}"

    return jsonify({
        "success": True,
        "redirect_url": "/caption-studio?src=" + filename,
        "project_id": project_id,
        "video_url": video_url,
    })


@studio_nav_bp.route("/studio/send-to-youtube", methods=["POST"])
def send_to_youtube():
    """Send a final video to YouTube Automation."""
    data = request.get_json(silent=True) or {}
    filename = data.get("filename", "")
    project_id = data.get("project_id", "")

    if not filename:
        return jsonify({"success": False, "error": "filename required"}), 400

    if not project_id:
        all_projects = project_state.list_all_projects()
        for summary in all_projects:
            for clip_fn in summary["clips"]:
                if clip_fn == filename:
                    project_id = summary["project_id"]
                    break
            if project_id:
                break

    if not project_id:
        return jsonify({"success": False, "error": "Project not found. Send a clip from Clip Cutter first."}), 404

    project_state.navigate_to(project_id, "youtube_automation", {
        "filename": filename,
    })

    return jsonify({
        "success": True,
        "redirect_url": "/youtube-desk?file=" + filename,
        "project_id": project_id,
    })


@studio_nav_bp.route("/studio/caption-style", methods=["GET", "POST"])
def caption_style_api():
    """Get/set the pre-defined caption style for the current project."""
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        project_id = data.get("project_id", "")
        style_data = data.get("style", {})

        if not project_id:
            return jsonify({"success": False, "error": "project_id required"}), 400

        style = _parse_style_config(style_data)
        project_state.set_caption_style(project_id, style)
        return jsonify({"success": True, "style": _style_to_dict(style)})

    project_id = request.args.get("project_id", "")
    style = project_state.get_caption_style(project_id)
    if style:
        return jsonify({"success": True, "style": _style_to_dict(style)})
    return jsonify({"success": True, "style": None})


@studio_nav_bp.route("/studio/project/<project_id>", methods=["GET"])
def get_project_state(project_id):
    """Get the current state of a project including all media references."""
    project = project_state.get_project(project_id)
    if not project:
        # Fallback to database lookup
        try:
            import json
            from models.project import Project
            from core.project_state import MediaItem
            clean_id = int(str(project_id).replace("proj_", ""))
            db_proj = Project.query.get(clean_id)
            if db_proj:
                in_mem = project_state.create_project(
                    db_proj.source_path or "",
                    f"/download/input/{db_proj.source_path}" if db_proj.source_path else ""
                )
                in_mem.project_id = project_id
                if db_proj.editor_state:
                    try:
                        ed = json.loads(db_proj.editor_state)
                        for c in ed.get("clips", []):
                            cfn = c.get("filename") or c.get("name")
                            if cfn:
                                in_mem.clips.append(MediaItem(
                                    filename=cfn,
                                    media_type="clip",
                                    label=c.get("label", cfn),
                                    url=c.get("url", f"/download/clip/{cfn}")
                                ))
                    except Exception:
                        pass
                project_state._projects[project_id] = in_mem
                project = in_mem
        except Exception:
            pass

    if not project:
        return jsonify({"success": False, "error": "Project not found"}), 404

    return jsonify({
        "success": True,
        "project": {
            "project_id": project.project_id,
            "source_video": {
                "filename": project.source_video.filename if project.source_video else None,
                "url": project.source_video.url if project.source_video else None,
                "media_type": "source",
            } if project.source_video else None,
            "clips": [
                {
                    "filename": c.filename,
                    "url": c.url,
                    "media_type": c.media_type,
                    "label": c.label,
                }
                for c in project.clips
            ],
            "caption_files": [
                {
                    "filename": c.filename,
                    "url": c.url,
                    "media_type": c.media_type,
                }
                for c in project.caption_files
            ],
            "final_exports": [
                {
                    "filename": c.filename,
                    "url": c.url,
                    "media_type": c.media_type,
                }
                for c in project.final_exports
            ],
            "caption_style": _style_to_dict(project.caption_style) if project.caption_style else None,
            "current_module": project.current_module,
        },
    })


@studio_nav_bp.route("/studio/clip-captions/<project_id>/<clip_filename>", methods=["GET"])
def get_clip_caption_files(project_id, clip_filename):
    """Get caption files associated with a specific clip."""
    items = project_state.get_clip_caption_files(project_id, clip_filename)
    return jsonify({
        "success": True,
        "captions": [
            {
                "filename": item.filename,
                "url": item.url,
                "media_type": item.media_type,
            }
            for item in items
        ],
    })


# ============================================================
# Global jobs
# ============================================================

@studio_nav_bp.route("/studio/jobs", methods=["GET"])
def get_active_jobs():
    """Return active background jobs across all modules."""
    from routes.process import JOBS
    jobs_list = []
    for job_id, job in JOBS.items():
        if not job.finished:
            percent = round((job.steps_completed / job.total_steps) * 100) if job.total_steps else 0
            jobs_list.append({
                "job_id": job.job_id,
                "filename": job.filename,
                "status": job.status,
                "step": job.step,
                "progress": percent,
                "steps_completed": job.steps_completed,
                "total_steps": job.total_steps,
            })
    return jsonify({"success": True, "jobs": jobs_list, "count": len(jobs_list)})


@studio_nav_bp.route("/studio/jobs/cancel/<job_id>", methods=["POST"])
def cancel_job(job_id):
    """Cancel a running background job."""
    from routes.process import JOBS
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"success": False, "error": "Job not found"}), 404
    if job.finished:
        return jsonify({"success": False, "error": "Job already finished"}), 400
    job.status = "error"
    job.finished = True
    job.error = "Cancelled by user"
    job.add_log("Job cancelled by user.")
    return jsonify({"success": True})


# ============================================================
# Unified studio home / navigation hub
# ============================================================

@studio_nav_bp.route("/studio")
def studio_hub():
    """Unified studio hub showing all modules and recent projects."""
    return render_template("studio_hub.html")


def _style_to_dict(style: Optional[CaptionStyleConfig]) -> Optional[dict]:
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
        # CamelCase aliases for client compatibility
        "fontFamily": style.font_family,
        "fontSize": style.font_size,
        "fontWeight": style.font_weight,
        "textColor": style.text_color,
        "activeWordColor": style.active_word_color,
        "backgroundColor": style.background_color,
        "backgroundOpacity": style.background_opacity,
        "outlineColor": style.outline_color,
        "outlineWidth": style.outline_width,
        "shadowColor": style.shadow_color,
        "shadowBlur": style.shadow_blur,
        "shadowOffsetY": style.shadow_offset_y,
        "letterSpacing": style.letter_spacing,
        "lineHeight": style.line_height,
        "maxLines": style.max_lines,
    }


def _parse_style_config(caption_style: dict) -> CaptionStyleConfig:
    """Safely parse CaptionStyleConfig supporting both camelCase and snake_case keys."""
    if not isinstance(caption_style, dict):
        return CaptionStyleConfig(id="custom", name="Custom")

    def _to_int(val, default):
        try:
            return int(val) if val is not None and val != "" else default
        except (TypeError, ValueError):
            return default

    def _to_float(val, default):
        try:
            return float(val) if val is not None and val != "" else default
        except (TypeError, ValueError):
            return default

    font_family = caption_style.get("font_family") or caption_style.get("fontFamily") or "Arial Black"
    font_size = _to_int(caption_style.get("font_size") or caption_style.get("fontSize"), 34)
    font_weight = _to_int(caption_style.get("font_weight") or caption_style.get("fontWeight"), 800)
    text_color = caption_style.get("text_color") or caption_style.get("textColor") or "#FFFFFF"
    active_word_color = caption_style.get("active_word_color") or caption_style.get("activeWordColor") or "#fbbf24"
    background_color = caption_style.get("background_color") or caption_style.get("backgroundColor") or caption_style.get("bgColor") or "#000000"
    background_opacity = _to_float(caption_style.get("background_opacity") or caption_style.get("backgroundOpacity") or caption_style.get("bgOpacity"), 0.0)
    if background_opacity > 1.0:
        background_opacity = background_opacity / 100.0

    outline_color = caption_style.get("outline_color") or caption_style.get("outlineColor") or caption_style.get("strokeColor") or "#000000"
    outline_width = _to_int(caption_style.get("outline_width") or caption_style.get("outlineWidth") or caption_style.get("strokeWidth"), 3)
    shadow_color = caption_style.get("shadow_color") or caption_style.get("shadowColor") or "#000000"
    shadow_blur = _to_int(caption_style.get("shadow_blur") or caption_style.get("shadowBlur"), 4)
    shadow_offset_y = _to_int(caption_style.get("shadow_offset_y") or caption_style.get("shadowOffsetY") or caption_style.get("shadowY"), 2)
    position = caption_style.get("position") or "bottom"
    animation = caption_style.get("animation") or "pop"
    letter_spacing = _to_int(caption_style.get("letter_spacing") or caption_style.get("letterSpacing"), 0)
    line_height = _to_float(caption_style.get("line_height") or caption_style.get("lineHeight"), 1.2)
    max_lines = _to_int(caption_style.get("max_lines") or caption_style.get("maxLines"), 2)

    return CaptionStyleConfig(
        id=caption_style.get("id", "custom"),
        name=caption_style.get("name", "Custom"),
        font_family=font_family,
        font_size=font_size,
        font_weight=font_weight,
        text_color=text_color,
        active_word_color=active_word_color,
        background_color=background_color,
        background_opacity=background_opacity,
        outline_color=outline_color,
        outline_width=outline_width,
        shadow_color=shadow_color,
        shadow_blur=shadow_blur,
        shadow_offset_y=shadow_offset_y,
        position=position,
        animation=animation,
        letter_spacing=letter_spacing,
        line_height=line_height,
        max_lines=max_lines,
    )
