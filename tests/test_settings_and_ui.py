"""
Comprehensive Unit & Integration Test Suite for Master Prompt V2:
- Settings & Resource Manager Endpoints (/settings, /api/settings/*)
- AI Model Manager Catalog & Operations
- Dependency & Library Detection
- Storage & Cache Management
- Import & Export Folders
- Performance & Hardware Detection
- System Diagnostics
- Favicon & Brand Asset Integrity
- All Workspace Templates & Route Accessibility
"""

import os
import sys
import json
from pathlib import Path
import pytest

# Ensure UpClipStudio root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from app import create_app
from routes.settings import WHISPER_CATALOG, WHISPER_CACHE_DIR, download_mgr


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_favicon_assets_exist():
    """Verify all 8 brand icon variants required by Phase 2 are present on disk."""
    static_dir = config.STATIC_DIR
    expected_assets = [
        "favicon.svg",
        "favicon.ico",
        "favicon-16x16.png",
        "favicon-32x32.png",
        "apple-touch-icon.png",
        "android-chrome-192x192.png",
        "android-chrome-512x512.png",
        "site.webmanifest"
    ]
    for asset in expected_assets:
        asset_path = static_dir / asset
        assert asset_path.exists(), f"Asset {asset} missing from static directory"
        assert asset_path.stat().st_size > 0, f"Asset {asset} is empty"


def test_settings_page_renders(client):
    """Verify /settings renders HTML successfully with all 10 tab anchors."""
    response = client.get("/settings")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Settings & Resource Manager" in html
    assert 'data-tab="general"' in html
    assert 'data-tab="models"' in html
    assert 'data-tab="dependencies"' in html
    assert 'data-tab="downloads"' in html
    assert 'data-tab="storage"' in html
    assert 'data-tab="folders"' in html
    assert 'data-tab="performance"' in html
    assert 'data-tab="privacy"' in html
    assert 'data-tab="diagnostics"' in html
    assert 'data-tab="about"' in html


def test_all_workspace_routes_render_with_settings_in_sidebar(client):
    """Verify all primary application pages render 200 and include Settings in sidebar."""
    routes = [
        "/",
        "/dashboard",
        "/caption-studio",
        "/studio",
        "/settings",
        "/yt-downloader",
        "/youtube-desk",
        "/guide"
    ]
    for r in routes:
        resp = client.get(r)
        assert resp.status_code == 200, f"Route {r} returned status {resp.status_code}"
        html = resp.get_data(as_text=True)
        assert "/settings" in html, f"Settings link missing from navigation in {r}"
        assert "favicon.svg" in html, f"Favicon svg missing in {r}"


def test_api_settings_all(client):
    """Verify /api/settings/all returns complete preferences."""
    resp = client.get("/api/settings/all")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "settings" in data
    settings = data["settings"]
    assert "general" in settings
    assert "models" in settings
    assert "folders" in settings


def test_api_settings_save(client):
    """Verify /api/settings/save updates preferences."""
    payload = {
        "general": {
            "defaultLanguage": "en",
            "defaultAspectRatio": "9:16",
            "defaultResolution": "1080p",
            "defaultFps": 30
        }
    }
    resp = client.post("/api/settings/save", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True


def test_api_settings_models(client):
    """Verify /api/settings/models returns Whisper catalog with genuine metadata."""
    resp = client.get("/api/settings/models")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    models = data["models"]
    assert len(models) >= 10
    model_ids = [m["id"] for m in models]
    for expected in ["tiny", "base", "small", "medium", "large-v3", "turbo"]:
        assert expected in model_ids


def test_api_settings_dependencies(client):
    """Verify /api/settings/dependencies detects actual libraries."""
    resp = client.get("/api/settings/dependencies")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    deps = {d["name"]: d for d in data["dependencies"]}
    assert any("FFmpeg" in k for k in deps)
    assert any("PyTorch" in k for k in deps)
    assert any("Whisper" in k for k in deps)
    assert any("OpenCV" in k for k in deps)
    assert any("Pillow" in k for k in deps)


def test_api_settings_storage(client):
    """Verify /api/settings/storage reports real disk stats."""
    resp = client.get("/api/settings/storage")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "disk" in data
    assert data["disk"]["total_gb"] > 0
    assert "breakdown" in data


def test_api_settings_performance(client):
    """Verify /api/settings/performance reports real CPU and RAM."""
    resp = client.get("/api/settings/performance")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "cpu" in data
    assert data["cpu"]["cores"] >= 1
    assert "ram" in data
    assert data["ram"]["total_gb"] > 0


def test_api_settings_diagnostics(client):
    """Verify /api/settings/diagnostics executes real checks."""
    resp = client.get("/api/settings/diagnostics")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "diagnostics" in data
    assert len(data["diagnostics"]) >= 4


def test_api_folders_reset(client):
    """Verify /api/settings/folders/reset restores default project folders."""
    resp = client.post("/api/settings/folders/reset")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "folders" in data
    folders = data["folders"]
    assert str(config.INPUT_DIR) in folders["mediaImportFolder"]
    assert str(config.FINAL_DIR) in folders["exportFolder"]
