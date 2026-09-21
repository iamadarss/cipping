"""Tests for Project API endpoints and database integration."""

import json
from app import create_app
from extensions import db
from models.project import Project


def test_api_projects_endpoints():
    app = create_app()
    client = app.test_client()

    # 1. GET /
    res = client.get('/')
    assert res.status_code == 200

    # 2. GET /guide
    res = client.get('/guide')
    assert res.status_code == 200

    # 3. GET /api/templates
    res = client.get('/api/templates')
    assert res.status_code == 200
    templates_data = res.get_json()
    assert templates_data.get('success') is True
    assert isinstance(templates_data.get('templates'), list)

    # 4. GET /api/projects
    res = client.get('/api/projects')
    assert res.status_code == 200
    projects_list = res.get_json()
    assert isinstance(projects_list, list)

    # 5. POST /api/projects (Create)
    create_payload = {
        "name": "Integration Test Project",
        "source_path": "sample.mp4",
        "aspect_ratio": "9:16",
        "fps": 30
    }
    res = client.post('/api/projects', data=json.dumps(create_payload), content_type='application/json')
    assert res.status_code == 201
    created_data = res.get_json()
    assert created_data["name"] == "Integration Test Project"
    proj_id = created_data["id"]
    assert proj_id is not None

    # 6. GET /api/projects/<id>
    res = client.get(f'/api/projects/{proj_id}')
    assert res.status_code == 200
    detail = res.get_json()
    assert detail["id"] == proj_id
    assert detail["name"] == "Integration Test Project"

    # 7. PUT /api/projects/<id> (Update)
    update_payload = {"name": "Updated Test Project"}
    res = client.put(f'/api/projects/{proj_id}', data=json.dumps(update_payload), content_type='application/json')
    assert res.status_code == 200
    updated_data = res.get_json()
    assert updated_data["name"] == "Updated Test Project"

    # 8. POST /api/projects/<id>/save-as
    res = client.post(f'/api/projects/{proj_id}/save-as', data=json.dumps({"name": "Save As Project"}), content_type='application/json')
    assert res.status_code == 201
    save_as_data = res.get_json()
    assert save_as_data.get("success") is True
    save_as_id = save_as_data["project"]["id"]

    # 9. POST /api/projects/<id>/duplicate
    res = client.post(f'/api/projects/{proj_id}/duplicate')
    assert res.status_code == 201
    dup_data = res.get_json()
    assert dup_data.get("success") is True
    dup_id = dup_data["project"]["id"]

    # 10. POST /api/projects/<id>/save-as-template
    res = client.post(f'/api/projects/{proj_id}/save-as-template', data=json.dumps({"name": "Test Template"}), content_type='application/json')
    assert res.status_code == 201
    tpl_data = res.get_json()
    assert tpl_data.get("success") is True

    # 11. Cleanup created test records
    res = client.delete(f'/api/projects/{proj_id}')
    assert res.status_code == 200

    res = client.delete(f'/api/projects/{save_as_id}')
    assert res.status_code == 200

    res = client.delete(f'/api/projects/{dup_id}')
    assert res.status_code == 200

    from core.preset_manager import preset_manager
    if tpl_data and "template" in tpl_data and "id" in tpl_data["template"]:
        preset_manager.delete_user_template(tpl_data["template"]["id"])


def test_project_thumbnail_and_recent_sync():
    app = create_app()
    client = app.test_client()

    # 1. Verify /api/projects returns projects with thumbnail_path
    res = client.get('/api/projects')
    assert res.status_code == 200
    projects = res.get_json()
    assert len(projects) > 0

    for p in projects:
        thumb = p.get("thumbnail_path")
        assert thumb is not None
        assert thumb.startswith("/download/thumbnail/") or thumb.startswith("/static/img/")
        # Ensure thumbnail endpoint returns 200
        thumb_res = client.get(thumb)
        assert thumb_res.status_code == 200, f"Thumbnail failed for {p['name']}: {thumb}"
