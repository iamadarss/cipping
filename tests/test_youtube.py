"""Tests for YouTube Desk workspace, async upload queue, and automation endpoints."""

import json
from app import create_app


def test_youtube_desk_page_renders():
    app = create_app()
    client = app.test_client()

    response = client.get("/youtube-desk")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # 1. Page Title & Navigation
    assert "YouTube Desk" in html
    assert "wizard-progress-state" in html

    # 2. Upload Wizard & Action Controls
    assert "uploadProgressBarFill" in html
    assert "uploadStatusTitle" in html
    assert "uploadStatusMessage" in html

    # 3. Queue & History Views
    assert "queueItemsList" in html
    assert "historyTableBody" in html


def test_youtube_upload_queue_list():
    app = create_app()
    client = app.test_client()

    response = client.get("/youtube/upload-queue")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "items" in data
    assert isinstance(data["items"], list)


def test_youtube_status():
    app = create_app()
    client = app.test_client()

    response = client.get("/youtube/status")
    assert response.status_code == 200
    data = response.get_json()
    assert "connected" in data


def test_youtube_history():
    app = create_app()
    client = app.test_client()

    response = client.get("/youtube/history")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "history" in data
    assert isinstance(data["history"], list)


def test_youtube_status_expired_handling(monkeypatch):
    """Ensure /youtube/status accurately reports expired=True and connected=False when refresh fails."""
    app = create_app()
    client = app.test_client()

    from routes import youtube

    class MockExpiredCreds:
        token = "expired_token_mock"
        refresh_token = "mock_refresh"
        expired = True
        valid = False

        def refresh(self, req):
            from google.auth.exceptions import RefreshError
            raise RefreshError("invalid_grant: Token has been expired or revoked.")

    monkeypatch.setattr(youtube, "dict_to_credentials", lambda d: MockExpiredCreds())

    response = client.get("/youtube/status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["connected"] is False
    assert data["expired"] is True
    assert "reconnect" in data["error"].lower()

