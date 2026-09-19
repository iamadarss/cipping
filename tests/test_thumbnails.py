"""Comprehensive tests for video thumbnail generation and serving."""

import io
import os
import cv2
import numpy as np
import urllib.parse
from pathlib import Path
from app import create_app
import config


def _create_dummy_video_bytes(filename: str = "temp_test.mp4") -> bytes:
    """Generate a valid minimal MP4 video in memory/temp file and return its bytes."""
    temp_path = config.ROOT_DIR / "tests" / filename
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(temp_path), fourcc, 10.0, (64, 64))
    for _ in range(10):
        frame = np.zeros((64, 64, 3), dtype=np.uint8)
        cv2.putText(frame, 'T', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        writer.write(frame)
    writer.release()
    try:
        with open(temp_path, "rb") as f:
            data = f.read()
    finally:
        if temp_path.exists():
            temp_path.unlink()
    return data


def test_thumbnail_flow_normal_filename():
    app = create_app()
    client = app.test_client()

    video_bytes = _create_dummy_video_bytes("test_normal.mp4")
    upload_res = client.post(
        "/upload/video",
        data={"video": (io.BytesIO(video_bytes), "test_normal.mp4")},
        content_type="multipart/form-data"
    )
    assert upload_res.status_code == 200
    data = upload_res.get_json()
    assert data["success"] is True
    assert "thumbnail" in data
    thumb_url = data["thumbnail"]

    # Test thumbnail serving
    thumb_res = client.get(thumb_url)
    assert thumb_res.status_code == 200
    assert len(thumb_res.data) > 0

    # Verify physical file existence
    expected_thumb = config.THUMBNAIL_DIR / "test_normal_thumb.jpg"
    assert expected_thumb.exists()
    assert expected_thumb.stat().st_size > 0

    # Cleanup
    thumb_res.close()
    if expected_thumb.exists():
        expected_thumb.unlink()
    uploaded_video = config.INPUT_DIR / "test_normal.mp4"
    if uploaded_video.exists():
        uploaded_video.unlink()


def test_thumbnail_flow_spaces_in_filename():
    app = create_app()
    client = app.test_client()

    video_bytes = _create_dummy_video_bytes("my_spaces_test.mp4")
    upload_res = client.post(
        "/upload/video",
        data={"video": (io.BytesIO(video_bytes), "My Test Video With Spaces.mp4")},
        content_type="multipart/form-data"
    )
    assert upload_res.status_code == 200
    data = upload_res.get_json()
    assert data["success"] is True
    thumb_url = data["thumbnail"]

    # Test thumbnail serving (both raw and percent-encoded)
    thumb_res = client.get(thumb_url)
    assert thumb_res.status_code == 200
    assert len(thumb_res.data) > 0

    encoded_url = urllib.parse.quote(thumb_url, safe="/:")
    thumb_res2 = client.get(encoded_url)
    assert thumb_res2.status_code == 200

    # Cleanup
    thumb_res.close()
    thumb_res2.close()
    expected_thumb = config.THUMBNAIL_DIR / "My Test Video With Spaces_thumb.jpg"
    if expected_thumb.exists():
        expected_thumb.unlink()
    uploaded_video = config.INPUT_DIR / "My Test Video With Spaces.mp4"
    if uploaded_video.exists():
        uploaded_video.unlink()


def test_thumbnail_flow_unicode_filename():
    app = create_app()
    client = app.test_client()

    video_bytes = _create_dummy_video_bytes("my_unicode_test.mp4")
    unicode_name = "The Dollar Monopoly Is Breaking？ The End Of America’s Power？ Shubhankar Mishra.mp4"
    upload_res = client.post(
        "/upload/video",
        data={"video": (io.BytesIO(video_bytes), unicode_name)},
        content_type="multipart/form-data"
    )
    assert upload_res.status_code == 200
    data = upload_res.get_json()
    assert data["success"] is True
    thumb_url = data["thumbnail"]

    # Test thumbnail serving
    thumb_res = client.get(thumb_url)
    assert thumb_res.status_code == 200
    assert len(thumb_res.data) > 0

    # Also test with percent-encoded URL as sent by browsers
    encoded_url = "/download/thumbnail/" + urllib.parse.quote(f"{Path(unicode_name).stem}_thumb.jpg")
    thumb_res_enc = client.get(encoded_url)
    assert thumb_res_enc.status_code == 200
    assert len(thumb_res_enc.data) > 0

    # Cleanup
    thumb_res.close()
    thumb_res_enc.close()
    expected_thumb = config.THUMBNAIL_DIR / f"{Path(unicode_name).stem}_thumb.jpg"
    if expected_thumb.exists():
        expected_thumb.unlink()
    uploaded_video = config.INPUT_DIR / unicode_name
    if uploaded_video.exists():
        uploaded_video.unlink()


def test_thumbnail_flow_long_filename():
    app = create_app()
    client = app.test_client()

    long_name = "Very_Long_Video_Title_Testing_Deep_Character_Lengths_And_Unicode_Support_In_Flask_Upload_Flow_9876543210.mp4"
    video_bytes = _create_dummy_video_bytes("long_test.mp4")
    upload_res = client.post(
        "/upload/video",
        data={"video": (io.BytesIO(video_bytes), long_name)},
        content_type="multipart/form-data"
    )
    assert upload_res.status_code == 200
    data = upload_res.get_json()
    assert data["success"] is True
    thumb_url = data["thumbnail"]

    thumb_res = client.get(thumb_url)
    assert thumb_res.status_code == 200
    assert len(thumb_res.data) > 0

    # Cleanup
    thumb_res.close()
    expected_thumb = config.THUMBNAIL_DIR / f"{Path(long_name).stem}_thumb.jpg"
    if expected_thumb.exists():
        expected_thumb.unlink()
    uploaded_video = config.INPUT_DIR / long_name
    if uploaded_video.exists():
        uploaded_video.unlink()


def test_missing_thumbnail_returns_404():
    app = create_app()
    client = app.test_client()

    res = client.get("/download/thumbnail/nonexistent_file_123456.jpg")
    assert res.status_code == 404
    payload = res.get_json()
    assert payload["success"] is False
    assert "error" in payload
