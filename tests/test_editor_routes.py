# tests/test_editor_routes.py
"""
Integration test suite for all Editor API routes.
Verifies that all editor endpoints are reachable under the /editor prefix
and none return 404 (Not Found).
"""

import json
from unittest.mock import patch
import pytest
from app import create_app
from extensions import db
from models.project import Project
from core.render_queue import render_queue_manager
from core.content_intelligence import content_intelligence_engine

@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        # Ensure a test project exists for project-specific endpoints
        proj = Project.query.first()
        if not proj:
            proj = Project(name="Test Project", duration=10.0)
            db.session.add(proj)
            db.session.commit()
    return app

@pytest.fixture(scope="module")
def client(app):
    return app.test_client()

@pytest.fixture(scope="module")
def seeded_env(app):
    with app.app_context():
        proj = Project.query.first()
        pid = proj.id
        job = render_queue_manager.add_job(pid, "Test Job", {"clips": []})
        jid = job["id"]

        # Seed intelligence cache
        cache_file = content_intelligence_engine._get_cache_path(pid)
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps({"success": True, "topics": []}), encoding="utf-8")

        yield {"project_id": pid, "job_id": jid}

        # Cleanup
        try:
            if cache_file.exists():
                cache_file.unlink()
        except Exception:
            pass

def test_editor_view_exists(client):
    resp = client.get("/editor/")
    assert resp.status_code != 404

def test_editor_endpoints_reachability(client, seeded_env):
    pid = seeded_env["project_id"]
    jid = seeded_env["job_id"]

    endpoints = [
        # General Editor APIs
        ("GET", "/editor/api/editor/fonts", None),
        ("GET", "/editor/api/editor/templates", None),
        ("GET", "/editor/api/editor/templates/categories", None),
        ("GET", "/editor/api/editor/presets", None),
        ("POST", "/editor/api/editor/presets/save", {"preset": {"name": "Test"}}),
        ("GET", "/editor/api/editor/brand-kit", None),
        ("POST", "/editor/api/editor/brand-kit", {"brand": {}}),
        ("POST", "/editor/api/editor/ready-check", {}),
        ("GET", "/editor/api/editor/diagnostics", None),
        ("GET", "/editor/api/editor/cache", None),
        ("POST", "/editor/api/editor/cache", {"action": "clear"}),
        ("POST", "/editor/api/editor/project/package", {"project_id": pid}),
        # Render Queue
        ("POST", "/editor/api/editor/render-queue/add", {"project_id": pid}),
        ("GET", "/editor/api/editor/render-queue/status", None),
        ("POST", f"/editor/api/editor/render-queue/retry/{jid}", None),
        ("POST", f"/editor/api/editor/render-queue/cancel/{jid}", None),
        ("DELETE", f"/editor/api/editor/render-queue/job/{jid}", None),
        ("POST", "/editor/api/editor/render-queue/clear-history", None),
        # Graphics Studio
        ("GET", "/editor/api/editor/graphics/catalog", None),
        ("GET", "/editor/api/editor/graphics/templates", None),
        ("POST", "/editor/api/editor/graphics/templates", {"template": {}}),
        ("POST", "/editor/api/editor/graphics/align", {}),
        ("POST", "/editor/api/editor/graphics/group", {}),
        ("POST", "/editor/api/editor/graphics/ungroup", {}),
        ("POST", "/editor/api/editor/graphics/duplicate", {}),
        ("POST", "/editor/api/editor/graphics/keyframes", {"layerId": "test", "keyframes": []}),
        ("GET", "/editor/api/editor/graphics/test_graphic/keyframes", None),
        # Audio Studio
        ("GET", "/editor/api/editor/audio-library", None),
        ("GET", "/editor/api/editor/audio/waveform?file=test.mp3", None),
        ("POST", "/editor/api/editor/audio/diagnostics", {}),
        # Media & Relinking
        ("GET", "/editor/api/editor/media/library", None),
        ("GET", "/editor/api/editor/media/stats", None),
        ("POST", "/editor/api/editor/media/clear-cache", None),
        ("POST", "/editor/api/editor/media/relink", {"source": "old", "target": "new"}),
        ("GET", "/editor/api/media/list", None),
        # AI Studio & Copilot
        ("POST", "/editor/api/editor/ai/analyze", {}),
        ("POST", "/editor/api/editor/ai/detect-silence", {}),
        ("POST", "/editor/api/editor/ai/smart-reframe", {}),
        ("POST", "/editor/api/editor/copilot/query", {"query": "make a cut"}),
        ("POST", "/editor/api/editor/copilot/record", {"action": "split"}),
        ("GET", "/editor/api/editor/copilot/settings", None),
        ("POST", "/editor/api/editor/copilot/settings", {"settings": {}}),
        ("GET", "/editor/api/editor/copilot/history", None),
        # Project-specific endpoints under /editor/api/projects/
        ("POST", f"/editor/api/projects/{pid}/editor-state", {"editor_state": {}}),
        ("POST", f"/editor/api/projects/{pid}/export-timeline", {"clips": []}),
        # Project-specific endpoints under /editor/api/editor/projects/
        ("GET", f"/editor/api/editor/projects/{pid}/versions", None),
        ("POST", f"/editor/api/editor/projects/{pid}/versions/save", {"label": "v1"}),
        ("POST", f"/editor/api/editor/projects/{pid}/versions/restore", {"version_id": "v1"}),
        ("GET", f"/editor/api/editor/projects/{pid}/review", None),
        ("POST", f"/editor/api/editor/projects/{pid}/review/comment", {"text": "nice cut"}),
        ("POST", f"/editor/api/editor/projects/{pid}/review/comment/1/toggle", None),
        ("POST", f"/editor/api/editor/projects/{pid}/review/status", {"status": "approved"}),
        ("GET", f"/editor/api/editor/projects/{pid}/intelligence", None),
        ("POST", f"/editor/api/editor/projects/{pid}/intelligence/topics", {"topics": []}),
        ("GET", f"/editor/api/editor/projects/{pid}/intelligence/search?q=test", None),
        ("POST", f"/editor/api/editor/projects/{pid}/shorts/create", {"candidates": []}),
        ("POST", f"/editor/api/editor/projects/{pid}/shorts/bulk-export", {"short_ids": []}),
    ]

    with patch("core.content_intelligence.content_intelligence_engine.analyze_project", return_value={"success": True}):
        for method, path, payload in endpoints:
            if method == "GET":
                resp = client.get(path)
            elif method == "POST":
                resp = client.post(path, json=payload or {})
            elif method == "DELETE":
                resp = client.delete(path)
            else:
                pytest.fail(f"Unsupported method: {method}")

            assert resp.status_code != 404, f"Endpoint {method} {path} returned 404 Not Found"

        # Also test intelligence analyze endpoint
        resp = client.post(f"/editor/api/editor/projects/{pid}/intelligence/analyze", json={})
        assert resp.status_code != 404
