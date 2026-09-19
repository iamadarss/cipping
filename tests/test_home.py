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

    try:
        with open(video_path, 'rb') as f:
            upload = client.post('/upload/video', data={'video': (io.BytesIO(f.read()), 'sample.mp4')}, content_type='multipart/form-data')

        assert upload.status_code == 200, upload.get_data(as_text=True)
        payload = upload.get_json()
        assert payload['success'] is True
        assert payload['metadata']['filename'] == 'sample.mp4'
    finally:
        import os
        if os.path.exists(video_path):
            try:
                os.remove(video_path)
            except Exception:
                pass


def test_step1_and_step2_dashboard_layout():
    """Verify that Step 1 is dedicated to video import & metadata,
    and Step 2 is 100% dedicated to settings studio with crisp icons and zero video player."""
    app = create_app()
    client = app.test_client()

    res = client.get('/dashboard')
    assert res.status_code == 200
    html = res.get_data(as_text=True)

    # Step 1 Verification
    assert 'data-panel="1"' in html
    assert 'id="uploadZone"' in html
    assert 'id="videoMetaCard"' in html
    assert 'id="btnProceedToSettings"' in html
    assert 'id="btnChangeVideo"' in html
    assert 'id="metaDisplayResolution"' in html
    assert 'id="metaDisplayDuration"' in html
    assert 'id="metaDisplayFPS"' in html
    assert 'id="metaDisplaySize"' in html
    assert 'id="metaThumbImg"' in html

    # Step 2 Verification (Dedicated Full-Width Settings Studio, Zero Video Player)
    assert 'data-panel="2"' in html
    assert 'class="step2-full-settings"' in html
    assert 'class="settings-studio-grid"' in html
    assert 'id="btnToggleAllSettings"' in html

    # Extract Step 2 HTML slice
    step2_start = html.find('data-panel="2"')
    step3_start = html.find('data-panel="3"')
    assert step2_start != -1 and step3_start != -1
    step2_html = html[step2_start:step3_start]

    # Zero video player in Step 2
    assert 'id="sourceVideoPlayer"' not in step2_html
    assert '<video' not in step2_html

    # Step 2 All 7 Accordions with inline SVGs present
    assert 'Target Aspect Ratio' in step2_html
    assert 'Clipping Strategy' in step2_html
    assert 'Language & Translation' in step2_html
    assert 'Subtitles' in step2_html
    assert 'Animated Captions' in step2_html
    assert 'Clip Naming' in step2_html
    assert 'Advanced Engine Settings' in step2_html

    # Aspect ratio cards with SVG icons
    assert 'value="9:16"' in step2_html
    assert 'value="16:9"' in step2_html
    assert 'value="1:1"' in step2_html
    assert 'value="4:5"' in step2_html

    # Slider threshold
    assert 'id="sceneThresholdRange"' in step2_html
    assert 'id="sceneThresholdDisplay"' in step2_html

