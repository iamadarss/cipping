"""Security tests for path traversal and input validation."""

import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_path_traversal_on_download_input(client):
    """Attempting path traversal via /input/ must not leak parent files."""
    # Attempting to fetch windows boot.ini or parent files
    resp = client.get("/input/../../boot.ini")
    assert resp.status_code in (400, 404)

    resp2 = client.get("/input/..%2F..%2Fconfig.py")
    assert resp2.status_code in (400, 404)


def test_path_traversal_on_thumbnail(client):
    """Attempting path traversal via /thumbnail/ must not leak parent files."""
    resp = client.get("/thumbnail/../../app.py")
    assert resp.status_code in (400, 404)


def test_path_traversal_on_media_thumbnail(client):
    """Attempting path traversal via /api/thumbnail/ must return 403 or 404."""
    resp = client.get("/api/thumbnail/../../../../windows/win.ini")
    assert resp.status_code in (403, 404)


def test_secret_key_is_not_default():
    """Verify SECRET_KEY is not the predictable default string."""
    import config
    assert config.SECRET_KEY != "ai-shorts-studio-secret-key-change-me"
    assert len(config.SECRET_KEY) >= 32
