from unittest.mock import patch, MagicMock
from app import create_app
import config


def test_youtube_download_requires_valid_url():
    app = create_app()
    client = app.test_client()

    response = client.post('/download/youtube', json={'url': 'not-a-url'})

    assert response.status_code == 400
    payload = response.get_json()
    assert 'valid YouTube URL' in payload['error']


def test_subtitles_only_requires_valid_url():
    app = create_app()
    client = app.test_client()

    response = client.post('/download/subtitles-only', json={'url': 'invalid'})
    assert response.status_code == 400
    payload = response.get_json()
    assert 'valid YouTube URL' in payload['error']


def test_analyze_youtube_subtitles_detection():
    app = create_app()
    client = app.test_client()

    mock_info = {
        'id': 'test12345',
        'title': 'Test Video with Captions',
        'uploader': 'Test Creator',
        'duration': 120,
        'view_count': 5000,
        'thumbnail': 'https://example.com/thumb.jpg',
        'subtitles': {
            'en': [{'ext': 'vtt'}],
            'hi': [{'ext': 'vtt'}],
        },
        'automatic_captions': {
            'en': [{'ext': 'vtt'}],
            'es': [{'ext': 'vtt'}],
        },
    }

    with patch('yt_dlp.YoutubeDL') as mock_ydl_cls:
        instance = MagicMock()
        instance.extract_info.return_value = mock_info
        mock_ydl_cls.return_value.__enter__.return_value = instance

        res = client.post('/download/analyze', json={'url': 'https://www.youtube.com/watch?v=test12345'})
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['has_subtitles'] is True
        assert len(data['subtitles']) >= 2
        # Check that English and Hindi are detected
        langs = [s['lang'] for s in data['subtitles']]
        assert 'en' in langs
        assert 'hi' in langs
        assert data['default_subtitle_lang'] == 'en'


def test_download_youtube_with_subtitles_queued():
    app = create_app()
    client = app.test_client()

    with patch('threading.Thread') as mock_thread:
        mock_thread.return_value.start.return_value = None

        res = client.post('/download/youtube', json={
            'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'format': 'video',
            'quality': '1080p',
            'download_subtitles': True,
            'subtitle_lang': 'en',
            'subtitle_format': 'srt',
            'async': True,
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['download_subtitles'] is True
        assert 'task_id' in data


def test_list_downloaded_detects_matching_subtitles(tmp_path):
    app = create_app()
    client = app.test_client()

    # Create dummy video and dummy subtitle file in input dir
    test_video = config.INPUT_DIR / "sample_test_vid.mp4"
    test_srt = config.INPUT_DIR / "sample_test_vid.srt"
    try:
        test_video.write_bytes(b"dummy video data")
        test_srt.write_text("1\n00:00:01,000 --> 00:00:03,000\nHello World\n", encoding="utf-8")

        res = client.get('/download/downloaded')
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        matching = [f for f in data['files'] if f['name'] == 'sample_test_vid.mp4']
        assert len(matching) == 1
        assert matching[0]['has_caption'] is True
        assert matching[0]['caption_file'] == 'sample_test_vid.srt'
    finally:
        if test_video.exists():
            test_video.unlink()
        if test_srt.exists():
            test_srt.unlink()


def test_subtitles_only_direct_download(tmp_path):
    app = create_app()
    client = app.test_client()

    mock_info = {
        'title': 'Test Subtitle Video',
        'subtitles': {},
        'automatic_captions': {
            'hi': [{'ext': 'json3', 'url': 'https://www.youtube.com/api/timedtext?v=test&lang=hi'}],
        },
    }

    clean_sub = config.INPUT_DIR / "Test_Subtitle_Video.srt"
    clean_sub_out = config.SUBTITLE_DIR / "Test_Subtitle_Video.srt"

    try:
        with patch('yt_dlp.YoutubeDL') as mock_ydl_cls, \
             patch('routes.download._fetch_youtube_captions_direct') as mock_fetch:

            instance = MagicMock()
            instance.extract_info.return_value = mock_info
            mock_ydl_cls.return_value.__enter__.return_value = instance

            def fake_fetch(info, target_lang, output_format, output_path):
                output_path.write_text("1\n00:00:01,000 --> 00:00:03,000\nNamaste\n", encoding="utf-8")
                return output_path

            mock_fetch.side_effect = fake_fetch

            res = client.post('/download/subtitles-only', json={
                'url': 'https://www.youtube.com/watch?v=12345678901',
                'subtitle_lang': 'hi',
                'subtitle_format': 'srt',
                'title': 'Test Subtitle Video',
            })

            assert res.status_code == 200
            data = res.get_json()
            assert data['success'] is True
            assert 'Test_Subtitle_Video.srt' in data['filename']
            assert clean_sub.exists()
            assert clean_sub_out.exists()
    finally:
        if clean_sub.exists():
            clean_sub.unlink()
        if clean_sub_out.exists():
            clean_sub_out.unlink()

