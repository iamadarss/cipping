"""Tests for custom subtitle/transcript uploads and modular AI engine toggle settings."""

import io
import json
import os
import pytest
from app import create_app
from extensions import db


SAMPLE_SRT = """1
00:00:01,000 --> 00:00:04,500
Welcome to UpClip Studio AI Clipper.

2
00:00:05,000 --> 00:00:08,200
In this video we demonstrate automated highlight detection.

3
00:00:09,000 --> 00:00:13,000
Viral hooks and kinetic captions will make your shorts explode!
"""

SAMPLE_VTT = """WEBVTT

1
00:00:01.000 --> 00:00:04.500
Welcome to UpClip Studio with WebVTT subtitles.

2
00:00:05.000 --> 00:00:08.500
Everything can now be fully toggled ON and OFF.
"""

SAMPLE_JSON = json.dumps([
    {"start": 1.0, "end": 4.5, "text": "JSON transcript item one."},
    {"start": 5.0, "end": 8.0, "text": "JSON transcript item two with high energy."}
])


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_upload_subtitle_no_file(client):
    """Test /upload/subtitle with no file payload."""
    res = client.post("/upload/subtitle")
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False
    assert "No subtitle" in data["error"]


def test_upload_subtitle_invalid_extension(client):
    """Test /upload/subtitle with invalid file extension."""
    data = {
        "subtitle": (io.BytesIO(b"malicious executable"), "payload.exe")
    }
    res = client.post("/upload/subtitle", data=data, content_type="multipart/form-data")
    assert res.status_code == 400
    body = res.get_json()
    assert body["success"] is False
    assert "Unsupported subtitle" in body["error"]


def test_upload_subtitle_srt_success(client):
    """Test uploading a valid SRT file."""
    data = {
        "subtitle": (io.BytesIO(SAMPLE_SRT.encode("utf-8")), "sample_subs.srt")
    }
    res = client.post("/upload/subtitle", data=data, content_type="multipart/form-data")
    assert res.status_code == 200
    body = res.get_json()
    assert body["success"] is True
    assert body["segments_count"] == 3
    assert body["duration"] >= 12.0
    assert body["word_count"] > 10
    assert "UpClip Studio" in body["text_preview"]
    assert "filename" in body
    assert body["srt_url"].startswith("/download/subtitle")


def test_upload_subtitle_vtt_success(client):
    """Test uploading a valid WebVTT file."""
    data = {
        "subtitle": (io.BytesIO(SAMPLE_VTT.encode("utf-8")), "captions.vtt")
    }
    res = client.post("/upload/subtitle", data=data, content_type="multipart/form-data")
    assert res.status_code == 200
    body = res.get_json()
    assert body["success"] is True
    assert body["segments_count"] == 2
    assert "WebVTT" in body["text_preview"]


def test_upload_subtitle_json_success(client):
    """Test uploading a JSON transcript file via /upload/transcript."""
    data = {
        "transcript": (io.BytesIO(SAMPLE_JSON.encode("utf-8")), "transcript.json")
    }
    res = client.post("/upload/transcript", data=data, content_type="multipart/form-data")
    assert res.status_code == 200
    body = res.get_json()
    assert body["success"] is True
    assert body["segments_count"] == 2
    assert "JSON transcript" in body["text_preview"]


def test_process_start_with_modular_engine_settings(client):
    """Test /process/start endpoint accepting and recording all customized engine toggles."""
    from config import INPUT_DIR
    dummy_video = "test_custom_settings_video.mp4"
    dummy_path = os.path.join(INPUT_DIR, dummy_video)
    if not os.path.exists(dummy_path):
        with open(dummy_path, "wb") as f:
            f.write(b"dummy video data")

    # Custom settings with all toggles specified:
    settings_payload = {
        "filename": dummy_video,
        "settings": {
            # Whisper Engine Customization
            "whisper_enabled": False,  # Bypassed
            "whisper_model": "turbo",
            "gpu_accel": True,
            # Custom Subtitle Upload
            "use_uploaded_subtitles": True,
            "uploaded_subtitle_file": "sample_subs.srt",
            # Modular AI Engines
            "scene_detection_enabled": True,
            "scene_threshold": 32.5,
            "scene_merger_enabled": True,
            "min_clip_duration": 18,
            "target_clip_duration": 35,
            "max_clip_duration": 55,
            "silence_trimming_enabled": True,
            "silence_threshold_db": -28.0,
            "min_silence_duration": 0.4,
            "smart_reframe_enabled": True,
            "reframe_mode": "smart",
            "audio_energy_enabled": True,
            "motion_detection_enabled": False,
            "emotion_detection_enabled": True,
            "viral_ranking_enabled": True,
            "min_viral_score": 65.0,
            "hook_detection_enabled": True,
            "keyword_extraction_enabled": True,
            "subtitle_enabled": True,
            "caption_enabled": True,
            "audio_normalization_enabled": True,
        }
    }

    res = client.post("/process/start", data=json.dumps(settings_payload), content_type="application/json")
    assert res.status_code == 200
    body = res.get_json()
    assert body["success"] is True
    assert "job_id" in body

    # Verify status endpoint returns job state
    job_id = body["job_id"]
    status_res = client.get(f"/process/status/{job_id}")
    assert status_res.status_code == 200
    status_body = status_res.get_json()
    assert status_body["success"] is True
    assert "status" in status_body
