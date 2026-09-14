import io
import uuid

import cv2
import numpy as np

from app import create_app


def test_home_page_exposes_youtube_downloader_route():
    app = create_app()
    client = app.test_client()

    home_response = client.get('/')
    assert home_response.status_code == 200
    home_html = home_response.get_data(as_text=True)
    assert 'Downloader' in home_html

    downloader_response = client.get('/yt-downloader')
    assert downloader_response.status_code == 200
    downloader_html = downloader_response.get_data(as_text=True)
    assert 'YouTube Video & Audio Downloader' in downloader_html


def test_core_routes_and_upload_work():
    app = create_app()
    client = app.test_client()

    # Test dashboard route
    dashboard_res = client.get('/dashboard')
    assert dashboard_res.status_code == 200

    # Test studio hub route
    studio_res = client.get('/studio')
    assert studio_res.status_code == 200

    # Test caption studio route
    caption_res = client.get('/caption-studio')
    assert caption_res.status_code == 200

    # Test video upload
    video_path = 'tests/data_test_upload.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(video_path, fourcc, 10.0, (64, 64))
    assert writer.isOpened()
    for _ in range(10):
        frame = np.zeros((64, 64, 3), dtype=np.uint8)
        cv2.putText(frame, 'X', (18, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        writer.write(frame)
    writer.release()

    with open(video_path, 'rb') as f:
        upload = client.post('/upload/video', data={'video': (io.BytesIO(f.read()), 'sample.mp4')}, content_type='multipart/form-data')

    assert upload.status_code == 200, upload.get_data(as_text=True)
    payload = upload.get_json()
    assert payload['success'] is True
    assert payload['metadata']['filename'] == 'sample.mp4'
