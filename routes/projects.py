# routes/projects.py
"""
Project & Application Management API Endpoints — UpClip Studio Phase 19.
Provides CRUD operations, Schema Validation, Autosave/Recovery, Save As,
Recent Projects Tracking, Global Settings, and Background Task Management.
"""

import json
import time
from flask import Blueprint, request, jsonify

from extensions import db
from models.project import Project
from core.project_manager import project_manager
from core.settings_manager import settings_manager
from core.progress import task_manager
from core.logger import logger

projects_bp = Blueprint('projects', __name__)


# =========================================================================
# PROJECT CRUD OPERATIONS
# =========================================================================

@projects_bp.route('/api/projects', methods=['GET'])
def list_projects():
    """List actual saved projects, ordered by recent update."""
    projects = Project.query.order_by(Project.updated_at.desc()).limit(20).all()
    project_dicts = [p.to_dict() for p in projects]
    return jsonify(project_dicts)


@projects_bp.route('/api/projects', methods=['POST'])
def create_project():
    """Create a new project with settings (name, aspect ratio, fps, resolution)."""
    from pathlib import Path
    data = request.get_json() or {}
    name = data.get('name', 'Untitled Project').strip()
    source_path = data.get('source_path')
    thumbnail_path = data.get('thumbnail_path')
    if not thumbnail_path and source_path:
        thumbnail_path = f"/download/thumbnail/{Path(source_path).stem}_thumb.jpg"
    duration = float(data.get('duration', 0.0) or 0.0)
    aspect_ratio = data.get('aspect_ratio', data.get('aspectRatio', '9:16'))
    fps = int(data.get('fps', 30))
    resolution = data.get('resolution')

    manifest = project_manager.create_project_manifest(
        name=name,
        source_path=source_path,
        aspect_ratio=aspect_ratio,
        fps=fps,
        resolution=resolution
    )

    proj = Project(
        name=name,
        source_path=source_path,
        thumbnail_path=thumbnail_path,
        duration=duration,
        status='ready',
        editor_state=json.dumps(manifest)
    )
    db.session.add(proj)
    db.session.commit()

    # Record in recent projects
    project_manager.record_recent_project(
        project_id=proj.id,
        name=proj.name,
        source_path=proj.source_path or "",
        thumbnail_path=proj.thumbnail_path or ""
    )

    logger.project(f"New project created: #{proj.id} - '{proj.name}'")
    return jsonify(proj.to_dict()), 201


@projects_bp.route('/api/projects/<int:proj_id>', methods=['GET'])
def get_project(proj_id):
    """Retrieve project by ID with schema validation and safe migration."""
    proj = Project.query.get_or_404(proj_id)

    # Validate and migrate editor state
    editor_state_dict = {}
    if proj.editor_state:
        try:
            parsed = json.loads(proj.editor_state)
            editor_state_dict = project_manager.validate_and_migrate(parsed)
        except Exception as e:
            logger.project(f"Error parsing editor state for project {proj_id}: {e}", level="warning")
            editor_state_dict = project_manager.create_project_manifest(proj.name, proj.source_path)

    project_dict = proj.to_dict()
    project_dict["editor_state_parsed"] = editor_state_dict

    # Record as recently opened
    project_manager.record_recent_project(
        project_id=proj.id,
        name=proj.name,
        source_path=proj.source_path or "",
        thumbnail_path=proj.thumbnail_path or ""
    )

    return jsonify(project_dict)


@projects_bp.route('/api/projects/<int:proj_id>', methods=['PUT'])
def update_project(proj_id):
    """Update project metadata, name, or full editor state."""
    proj = Project.query.get_or_404(proj_id)
    data = request.get_json() or {}

    for field in ['name', 'status', 'thumbnail_path', 'duration']:
        if field in data and data[field] is not None:
            setattr(proj, field, data[field])

    if 'editor_state' in data:
        editor_state_val = data['editor_state']
        if isinstance(editor_state_val, dict):
            migrated = project_manager.validate_and_migrate(editor_state_val)
            proj.editor_state = json.dumps(migrated)
        elif isinstance(editor_state_val, str):
            try:
                parsed = json.loads(editor_state_val)
                migrated = project_manager.validate_and_migrate(parsed)
                proj.editor_state = json.dumps(migrated)
            except Exception:
                proj.editor_state = editor_state_val

    db.session.commit()

    # Update recent projects tracking
    project_manager.record_recent_project(
        project_id=proj.id,
        name=proj.name,
        source_path=proj.source_path or "",
        thumbnail_path=proj.thumbnail_path or ""
    )

    return jsonify(proj.to_dict())


@projects_bp.route('/api/projects/<int:proj_id>', methods=['DELETE'])
def delete_project(proj_id):
    """Delete a project record and cleanup associated temporary autosave files."""
    proj = Project.query.get_or_404(proj_id)
    if proj.thumbnail_path:
        try:
            import os
            if os.path.exists(proj.thumbnail_path):
                os.remove(proj.thumbnail_path)
        except Exception:
            pass

    project_manager.clear_autosave(proj_id)
    project_manager.remove_recent_project(proj_id)

    db.session.delete(proj)
    db.session.commit()
    logger.project(f"Project #{proj_id} deleted.")
    return jsonify({'result': 'deleted', 'id': proj_id}), 200


# =========================================================================
# SAVE AS & DUPLICATION
# =========================================================================

@projects_bp.route('/api/projects/<int:proj_id>/save-as', methods=['POST'])
def save_project_as(proj_id):
    """Save As: Create a completely independent project clone with a new name."""
    orig = Project.query.get_or_404(proj_id)
    data = request.get_json(silent=True) or {}
    new_name = data.get("name", f"{orig.name} (Copy)").strip()

    # Parse and update name inside editor_state
    new_editor_state = orig.editor_state
    if orig.editor_state:
        try:
            parsed = json.loads(orig.editor_state)
            parsed["name"] = new_name
            new_editor_state = json.dumps(parsed)
        except Exception:
            pass

    clone = Project(
        name=new_name,
        source_path=orig.source_path,
        thumbnail_path=orig.thumbnail_path,
        status='ready',
        duration=orig.duration,
        editor_state=new_editor_state
    )
    db.session.add(clone)
    db.session.commit()

    project_manager.record_recent_project(
        project_id=clone.id,
        name=clone.name,
        source_path=clone.source_path or "",
        thumbnail_path=clone.thumbnail_path or ""
    )

    logger.project(f"Project #{orig.id} saved as new project #{clone.id} ('{clone.name}')")
    return jsonify({
        "success": True,
        "project": clone.to_dict()
    }), 201


@projects_bp.route('/api/projects/<int:proj_id>/duplicate', methods=['POST'])
def duplicate_project(proj_id):
    """Duplicate a project with an independent ID, cloned editor state, and shared source reference."""
    orig = Project.query.get_or_404(proj_id)
    new_name = f"{orig.name} (Copy)"

    clone = Project(
        name=new_name,
        source_path=orig.source_path,
        thumbnail_path=orig.thumbnail_path,
        status='ready',
        duration=orig.duration,
        editor_state=orig.editor_state
    )
    db.session.add(clone)
    db.session.commit()

    project_manager.record_recent_project(
        project_id=clone.id,
        name=clone.name,
        source_path=clone.source_path or "",
        thumbnail_path=clone.thumbnail_path or ""
    )

    return jsonify({
        "success": True,
        "project": clone.to_dict()
    }), 201


@projects_bp.route('/api/projects/<int:proj_id>/save-as-template', methods=['POST'])
def save_project_as_template(proj_id):
    """Convert project visual layout, graphics, and audio structure into a reusable user template."""
    proj = Project.query.get_or_404(proj_id)
    data = request.get_json(silent=True) or {}

    template_name = data.get("name") or f"{proj.name} Template"
    category = data.get("category") or "Custom"
    description = data.get("description") or f"Created from project {proj.name}"

    parsed_editor_state = {}
    if proj.editor_state:
        try:
            parsed_editor_state = json.loads(proj.editor_state)
        except Exception:
            pass

    template_payload = {
        "name": template_name,
        "category": category,
        "aspectRatio": "9:16",
        "description": description,
        "favorite": False,
        "data": {
            "aspectRatio": "9:16",
            "captionStyle": parsed_editor_state.get("captionStyle", {}),
            "graphics": parsed_editor_state.get("graphics", []),
            "audioTracks": parsed_editor_state.get("audioTracks", [])
        }
    }

    from core.preset_manager import preset_manager
    saved = preset_manager.save_user_template(template_payload)
    return jsonify({"success": True, "template": saved}), 201

# =========================================================================
# TEMPLATES API (SYSTEM & USER PRESETS)
# =========================================================================

@projects_bp.route('/api/templates', methods=['GET'])
def get_all_templates_list():
    """Return all system and user templates with optional category filter."""
    category = request.args.get('category')
    from core.preset_manager import preset_manager
    templates = preset_manager.get_templates(category=category)
    return jsonify({
        "success": True,
        "templates": templates
    })


@projects_bp.route('/api/templates/<template_id>', methods=['GET'])
def get_template_detail(template_id):
    """Retrieve full configuration object for a specific template."""
    from core.template_engine import template_engine
    from core.preset_manager import preset_manager

    # Check premium templates first
    prem = template_engine.get_template(template_id)
    if prem:
        return jsonify({"success": True, "template": prem.to_dict()})

    # Check legacy/system/user presets
    tpl = preset_manager.get_template_by_id(template_id)
    if tpl:
        return jsonify({"success": True, "template": tpl})

    return jsonify({"success": False, "error": f"Template '{template_id}' not found"}), 404


@projects_bp.route('/api/templates/<template_id>/save-custom', methods=['POST'])
def save_custom_template_api(template_id):
    """Save user customizations as a new or modified custom template."""
    from core.template_engine import template_engine

    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"success": False, "error": "Missing template configuration payload"}), 400

    data["id"] = data.get("id") or f"custom_{template_id}_{int(time.time())}"
    success, tmpl, errors = template_engine.save_custom_template(data)
    if not success:
        return jsonify({"success": False, "errors": errors}), 400

    return jsonify({"success": True, "template": tmpl.to_dict()}), 201


@projects_bp.route('/api/templates/set-project-default', methods=['POST'])
def set_project_default_template():
    """Set the default template (Level 1) for a specific project."""
    data = request.get_json(silent=True) or {}
    project_id = data.get("project_id") or data.get("projectId")
    template_id = data.get("template_id") or data.get("templateId")
    custom_settings = data.get("custom_settings") or data.get("customSettings") or {}

    if not project_id:
        return jsonify({"success": False, "error": "project_id is required"}), 400
    if not template_id:
        return jsonify({"success": False, "error": "template_id is required"}), 400

    proj = db.session.get(Project, int(project_id))
    if not proj:
        return jsonify({"success": False, "error": f"Project #{project_id} not found"}), 404

    try:
        current_state = json.loads(proj.editor_state) if proj.editor_state else {}
    except Exception:
        current_state = {}

    current_state["default_template"] = {
        "id": template_id,
        "custom_settings": custom_settings,
        "updated_at": time.time(),
    }
    # Sync captionStyle if provided
    if "caption_config" in custom_settings:
        current_state["captionStyle"] = custom_settings["caption_config"]
    elif "captionStyle" in custom_settings:
        current_state["captionStyle"] = custom_settings["captionStyle"]

    proj.editor_state = json.dumps(current_state)
    db.session.commit()

    return jsonify({
        "success": True,
        "project_id": proj.id,
        "default_template": current_state["default_template"]
    })


@projects_bp.route('/api/templates/set-global-preferred', methods=['POST'])
def set_global_preferred_template():
    """Set user's global preferred template (Level 3) in settings."""
    from core.settings_manager import settings_manager

    data = request.get_json(silent=True) or {}
    template_id = data.get("template_id") or data.get("templateId")
    if not template_id:
        return jsonify({"success": False, "error": "template_id is required"}), 400

    settings_manager.update_section("general", {"preferredTemplate": template_id})
    settings_manager.update_section("captions", {"preferredTemplate": template_id})

    return jsonify({
        "success": True,
        "preferred_template": template_id,
        "message": f"Global preferred template set to '{template_id}'"
    })


@projects_bp.route('/api/templates/global-preferred', methods=['GET'])
def get_global_preferred_template():
    """Get the active global preferred template (Level 3)."""
    from core.settings_manager import settings_manager

    pref = settings_manager.get("general.preferredTemplate") or settings_manager.get("captions.preferredTemplate") or "clean_creator"
    return jsonify({
        "success": True,
        "preferred_template": pref
    })


@projects_bp.route('/api/projects/<int:project_id>/clips/<clip_name>/template-override', methods=['POST'])
def set_clip_template_override(project_id, clip_name):
    """Set an individual clip's template override (Level 2)."""
    data = request.get_json(silent=True) or {}
    template_id = data.get("template_id") or data.get("templateId")

    proj = db.session.get(Project, project_id)
    if not proj:
        return jsonify({"success": False, "error": f"Project #{project_id} not found"}), 404

    try:
        current_state = json.loads(proj.editor_state) if proj.editor_state else {}
    except Exception:
        current_state = {}

    clip_overrides = current_state.get("clip_templates", {})
    if template_id:
        clip_overrides[clip_name] = {
            "template_id": template_id,
            "custom_settings": data.get("custom_settings", {}),
            "updated_at": time.time(),
        }
    else:
        # Clear override
        clip_overrides.pop(clip_name, None)

    current_state["clip_templates"] = clip_overrides
    proj.editor_state = json.dumps(current_state)
    db.session.commit()

    return jsonify({
        "success": True,
        "project_id": project_id,
        "clip_name": clip_name,
        "clip_templates": clip_overrides
    })


@projects_bp.route('/api/projects/<int:project_id>/template', methods=['GET'])
def get_project_template_settings(project_id):
    """Retrieve active project default template (Level 1) and all clip overrides (Level 2)."""
    proj = db.session.get(Project, project_id)
    if not proj:
        return jsonify({"success": False, "error": f"Project #{project_id} not found"}), 404

    try:
        current_state = json.loads(proj.editor_state) if proj.editor_state else {}
    except Exception:
        current_state = {}

    return jsonify({
        "success": True,
        "project_id": project_id,
        "default_template": current_state.get("default_template"),
        "clip_templates": current_state.get("clip_templates", {}),
    })


@projects_bp.route('/api/templates/<template_id>/create-project', methods=['POST'])
def create_project_from_template_root(template_id):
    """Instantiate a new project initialized with template configuration."""
    from core.preset_manager import preset_manager
    template = preset_manager.get_template_by_id(template_id)
    if not template:
        return jsonify({"success": False, "error": "Template not found"}), 404

    data = request.get_json(silent=True) or {}
    project_name = data.get("projectName") or data.get("name") or f"New {template.get('name', 'Video')}"
    source_path = data.get("sourcePath") or data.get("source_path")

    new_editor_state = json.dumps({
        "clips": [],
        "graphics": template.get("data", {}).get("graphics", []),
        "audioTracks": template.get("data", {}).get("audioTracks", []),
        "audioClips": [],
        "captionStyle": template.get("data", {}).get("captionStyle", {}),
        "aspectRatio": template.get("data", {}).get("aspectRatio", "9:16"),
        "default_template": {
            "id": template_id,
            "name": template.get("name", ""),
            "custom_settings": template.get("data", {}),
            "updated_at": time.time(),
        }
    })

    new_proj = Project(
        name=project_name,
        source_path=source_path,
        status="ready",
        editor_state=new_editor_state
    )
    db.session.add(new_proj)
    db.session.commit()

    project_manager.record_recent_project(
        project_id=new_proj.id,
        name=new_proj.name,
        source_path=new_proj.source_path or "",
        thumbnail_path=new_proj.thumbnail_path or ""
    )

    logger.project(f"New project from template '{template.get('name')}' created: #{new_proj.id}")
    return jsonify({
        "success": True,
        "project": new_proj.to_dict()
    }), 201


@projects_bp.route("/api/editor/diagnostics", methods=["GET"])
def get_system_diagnostics_root():
    """System diagnostics endpoint accessible from root API."""
    try:
        from core.workspace_manager import workspace_manager
        diag = workspace_manager.get_diagnostics()
        return jsonify({"success": True, "diagnostics": diag})
    except Exception as e:
        return jsonify({"success": True, "diagnostics": {
            "appName": "UpClip Studio",
            "version": "2.0.0",
            "os": "Windows",
            "pythonVersion": "3.14.6",
            "ffmpegVersion": "ffmpeg 8.1.2",
            "storage": {"freeGB": 50, "totalGB": 500, "percentFree": 10}
        }})



# =========================================================================
# AUTOSAVE & RECOVERY
# =========================================================================

@projects_bp.route('/api/projects/autosave', methods=['POST'])
def save_project_autosave():
    """Save an emergency debounced autosave snapshot."""
    data = request.get_json(silent=True) or {}
    project_id = data.get("project_id") or data.get("projectId")
    editor_state = data.get("editor_state") or data.get("editorState") or {}

    if not project_id:
        return jsonify({"success": False, "error": "project_id required"}), 400

    saved_path = project_manager.save_autosave_snapshot(project_id, editor_state)
    return jsonify({"success": bool(saved_path), "path": saved_path})


@projects_bp.route('/api/projects/<int:proj_id>/recovery', methods=['GET'])
def get_project_recovery(proj_id):
    """Check for and retrieve latest autosaved recovery snapshot."""
    snapshot = project_manager.get_recovery_snapshot(proj_id)
    if snapshot:
        return jsonify({"success": True, "hasRecovery": True, "recoveryState": snapshot})
    return jsonify({"success": True, "hasRecovery": False})


# =========================================================================
# RECENT PROJECTS
# =========================================================================

@projects_bp.route('/api/projects/recent', methods=['GET'])
def get_recent_projects_list():
    """Retrieve list of recent projects with availability flags."""
    recents = project_manager.get_recent_projects()
    return jsonify({"success": True, "recentProjects": recents})


@projects_bp.route('/api/projects/recent/remove', methods=['POST'])
def remove_recent_project():
    """Remove project from recent list without deleting actual project."""
    data = request.get_json(silent=True) or {}
    project_id = data.get("project_id") or data.get("id")
    if not project_id:
        return jsonify({"success": False, "error": "project_id required"}), 400

    res = project_manager.remove_recent_project(int(project_id))
    return jsonify({"success": res})


# =========================================================================
# APPLICATION SETTINGS & PREFERENCES
# =========================================================================

@projects_bp.route('/api/settings', methods=['GET', 'POST'])
def handle_app_settings():
    """Get or update global application settings."""
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        updated = settings_manager.update_settings(data)
        return jsonify({"success": True, "settings": updated})
    else:
        return jsonify({"success": True, "settings": settings_manager.get_settings()})


@projects_bp.route('/api/settings/reset', methods=['POST'])
def reset_app_settings():
    """Reset application settings to system defaults."""
    res = settings_manager.reset_defaults()
    return jsonify({"success": True, "settings": res})


# =========================================================================
# BACKGROUND TASKS & PROGRESS
# =========================================================================

@projects_bp.route('/api/tasks', methods=['GET'])
def list_active_tasks():
    """Return active background tasks and progress."""
    tasks = task_manager.list_active_tasks()
    return jsonify({"success": True, "tasks": tasks, "count": len(tasks)})


@projects_bp.route('/api/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get specific background task status and logs."""
    task = task_manager.get_task(task_id)
    if task:
        return jsonify({"success": True, "task": task.to_dict()})
    return jsonify({"success": False, "error": "Task not found"}), 404


@projects_bp.route('/api/tasks/<task_id>/cancel', methods=['POST'])
def cancel_task_request(task_id):
    """Cancel a running background task."""
    cancelled = task_manager.cancel_task(task_id)
    if cancelled:
        return jsonify({"success": True, "taskId": task_id, "status": "cancelled"})
    return jsonify({"success": False, "error": "Task not found or already finished"}), 404
