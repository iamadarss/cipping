"""Tests for Flip Studio Caption Studio workspace and APIs."""

import json
import io
from pathlib import Path
from app import create_app


def test_caption_studio_page_renders_with_full_workspace():
    app = create_app()
    client = app.test_client()

    response = client.get("/caption-studio")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # 1. Branding & Topbar
    assert "Up Clip Studio" in html
    assert "Caption Studio" in html
    assert "importVideoTopBtn" in html
    assert "importCaptionsTopBtn" in html
    assert "generateCaptionsTopBtn" in html
    assert "exportVideoTopBtn" in html
    assert "undoBtn" in html
    assert "redoBtn" in html

    # 2. Left Sidebar Navigation
    assert "appSidebar" in html
    assert "AI Clip Studio" in html
    assert "Caption Studio" in html
    assert "Studio Hub" in html
    assert "Downloader" in html
    assert "YouTube Desk" in html
    assert "Help & Guide" in html
    assert "sidebarToggle" in html

    # 3. Center Video Canvas & Controls
    assert "captionCanvasArea" in html
    assert "previewCanvasBox" in html
    assert "captionVideo" in html
    assert "captionDragBox" in html
    assert "canvasAspectSelect" in html
    assert "canvasSafeGuides" in html
    assert "captionEmptyState" in html
    assert "modeCaptionBtn" in html
    assert "modeVideoBtn" in html
    assert "videoZoomSelect" in html

    # 4. Bottom Caption Timeline
    assert "captionBottomTimeline" in html
    assert "timelineRulerCanvas" in html
    assert "captionTrackLane" in html
    assert "timelinePlayheadLine" in html
    assert "addCaptionBtn" in html
    assert "splitCaptionBtn" in html
    assert "mergeCaptionBtn" in html
    assert "duplicateCaptionBtn" in html
    assert "deleteCaptionBtn" in html
    assert "autoSplitCaptionsBtn" in html

    # 5. Right Inspector Three-Column Panels & Accordions
    assert "captionInspectorContainer" in html
    assert "colPresets" in html
    assert "colSettings" in html
    assert "colInspector" in html
    assert "accordionPresetsSetting" in html
    assert "accordionText" in html
    assert "accordionFont" in html
    assert "accordionStroke" in html
    assert "accordionShadow" in html
    assert "accordionGlow" in html
    assert "accordionBackground" in html
    assert "accordionPosition" in html
    assert "accordionAnimation" in html
    assert "accordionKaraoke" in html
    assert "accordionSettingsType" in html
    assert "accordionTools" in html
    assert "expandAllAccordionsBtn" in html
    assert "collapseAllAccordionsBtn" in html
    assert "generateCaptionsModal" in html





def test_caption_studio_subtitle_import_srt_vtt_json():
    app = create_app()
    client = app.test_client()

    # 1. Import SRT
    srt_content = (
        "1\n"
        "00:00:01,000 --> 00:00:03,500\n"
        "Welcome to Flip Studio\n\n"
        "2\n"
        "00:00:03,500 --> 00:00:07,000\n"
        "Create high-impact video captions\n"
    )
    res_srt = client.post(
        "/api/caption-studio/import",
        data={"file": (io.BytesIO(srt_content.encode("utf-8")), "demo.srt")},
        content_type="multipart/form-data"
    )
    assert res_srt.status_code == 200
    data_srt = res_srt.get_json()
    assert data_srt["success"] is True
    assert len(data_srt["captions"]) == 2
    assert data_srt["captions"][0]["text"] == "Welcome to Flip Studio"
    assert data_srt["captions"][0]["start"] == 1.0
    assert data_srt["captions"][0]["end"] == 3.5
    assert len(data_srt["captions"][0]["words"]) == 4

    # 2. Import VTT
    vtt_content = (
        "WEBVTT\n\n"
        "00:00:00.500 --> 00:00:02.800 line:80%\n"
        "Modern Video Editing\n\n"
        "00:00:02.800 --> 00:00:05.500\n"
        "Powered by Flip Studio\n"
    )
    res_vtt = client.post(
        "/api/caption-studio/import",
        data={"file": (io.BytesIO(vtt_content.encode("utf-8")), "demo.vtt")},
        content_type="multipart/form-data"
    )
    assert res_vtt.status_code == 200
    data_vtt = res_vtt.get_json()
    assert data_vtt["success"] is True
    assert len(data_vtt["captions"]) == 2
    assert data_vtt["captions"][0]["text"] == "Modern Video Editing"
    assert data_vtt["captions"][0]["start"] == 0.5
    assert data_vtt["captions"][0]["end"] == 2.8

    # 3. Import JSON
    json_payload = {
        "filename": "captions.json",
        "captions": [
            {"id": "c1", "start": 0.0, "end": 2.0, "text": "First caption segment"},
            {"id": "c2", "start": 2.0, "end": 4.5, "text": "Second caption segment"}
        ]
    }
    res_json = client.post(
        "/api/caption-studio/import",
        json=json_payload
    )
    assert res_json.status_code == 200
    data_json = res_json.get_json()
    assert data_json["success"] is True
    assert len(data_json["captions"]) == 2
    assert data_json["captions"][0]["text"] == "First caption segment"


def test_caption_studio_export_captions_srt_vtt_json():
    app = create_app()
    client = app.test_client()

    captions = [
        {"id": "1", "start": 0.0, "end": 2.5, "text": "Welcome to Flip Studio"},
        {"id": "2", "start": 2.5, "end": 5.0, "text": "Professional Caption Engine"}
    ]

    res = client.post(
        "/api/caption-studio/export-captions",
        json={"captions": captions, "format": "all"}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "srt" in data["files"]
    assert "vtt" in data["files"]
    assert "json" in data["files"]


def test_caption_studio_auto_split_algorithm():
    app = create_app()
    client = app.test_client()

    long_caption = [
        {
            "id": "long_1",
            "start": 0.0,
            "end": 8.0,
            "text": "Welcome to Flip Studio today we are creating awesome video captions for YouTube shorts and reels",
            "words": [
                {"text": "Welcome", "start": 0.0, "end": 0.5},
                {"text": "to", "start": 0.5, "end": 0.9},
                {"text": "Flip", "start": 0.9, "end": 1.4},
                {"text": "Studio", "start": 1.4, "end": 2.0},
                {"text": "today", "start": 2.0, "end": 2.6},
                {"text": "we", "start": 2.6, "end": 3.0},
                {"text": "are", "start": 3.0, "end": 3.4},
                {"text": "creating", "start": 3.4, "end": 4.2},
                {"text": "awesome", "start": 4.2, "end": 5.0},
                {"text": "video", "start": 5.0, "end": 5.6},
                {"text": "captions", "start": 5.6, "end": 6.3},
                {"text": "for", "start": 6.3, "end": 6.8},
                {"text": "YouTube", "start": 6.8, "end": 7.3},
                {"text": "shorts", "start": 7.3, "end": 7.7},
                {"text": "and", "start": 7.7, "end": 7.9},
                {"text": "reels", "start": 7.9, "end": 8.0},
            ]
        }
    ]

    res = client.post(
        "/api/caption-studio/auto-split",
        json={"captions": long_caption, "max_words": 5}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    # Should be split into multiple shorter segments
    assert len(data["captions"]) >= 3
    for chunk in data["captions"]:
        assert len(chunk["text"].split()) <= 6


def test_caption_studio_search_and_replace():
    app = create_app()
    client = app.test_client()

    captions = [
        {"id": "1", "start": 0.0, "end": 2.0, "text": "Hello world from Flip"},
        {"id": "2", "start": 2.0, "end": 4.0, "text": "Flip is amazing"}
    ]

    res = client.post(
        "/api/caption-studio/search-replace",
        json={
            "captions": captions,
            "search": "Flip",
            "replace": "Flip Studio",
            "case_sensitive": True
        }
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["replaceCount"] == 2
    assert data["captions"][0]["text"] == "Hello world from Flip Studio"
    assert data["captions"][1]["text"] == "Flip Studio is amazing"


def test_caption_studio_style_apply_all():
    app = create_app()
    client = app.test_client()

    captions = [
        {"id": "c1", "start": 0.0, "end": 2.0, "text": "Line 1", "style": {}},
        {"id": "c2", "start": 2.0, "end": 4.0, "text": "Line 2", "style": {}}
    ]
    new_style = {
        "font_family": "Poppins",
        "font_size": 48,
        "text_color": "#FACC15"
    }

    res = client.post(
        "/api/caption-studio/style/apply",
        json={"captions": captions, "style": new_style, "scope": "all"}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["captions"][0]["style"]["font_family"] == "Poppins"
    assert data["captions"][1]["style"]["font_size"] == 48


def test_caption_studio_segments_split_and_merge():
    app = create_app()
    client = app.test_client()

    captions = [
        {
            "id": "c1",
            "start": 0.0,
            "end": 4.0,
            "text": "First caption before split",
            "words": [
                {"text": "First", "start": 0.0, "end": 1.0},
                {"text": "caption", "start": 1.0, "end": 2.0},
                {"text": "before", "start": 2.0, "end": 3.0},
                {"text": "split", "start": 3.0, "end": 4.0}
            ]
        }
    ]

    # Split at 2.0 seconds
    res_split = client.post(
        "/api/caption-studio/segments/split",
        json={"captions": captions, "caption_id": "c1", "split_time": 2.0}
    )
    assert res_split.status_code == 200
    data_split = res_split.get_json()
    assert data_split["success"] is True
    assert len(data_split["captions"]) == 2
    assert data_split["captions"][0]["end"] == 2.0
    assert data_split["captions"][1]["start"] == 2.0

    # Merge back
    first_id = data_split["captions"][0]["id"]
    res_merge = client.post(
        "/api/caption-studio/segments/merge",
        json={"captions": data_split["captions"], "caption_id": first_id}
    )
    assert res_merge.status_code == 200
    data_merge = res_merge.get_json()
    assert data_merge["success"] is True
    assert len(data_merge["captions"]) == 1
    assert data_merge["captions"][0]["start"] == 0.0
    assert data_merge["captions"][0]["end"] == 4.0


def test_hinglish_transliteration_utility():
    from utils.hinglish_transliterator import transliterate_devanagari_to_hinglish

    # 1. Standard sentence
    result = transliterate_devanagari_to_hinglish("मुझे वीडियो बनाना है")
    assert result.strip().lower() == "mujhe video banana hai"

    # 2. Words with conjuncts and matras
    res_namaste = transliterate_devanagari_to_hinglish("नमस्ते भारत")
    assert "namaste" in res_namaste.lower()
    assert "bharat" in res_namaste.lower()

    # 3. Mixed English and Hindi
    res_mixed = transliterate_devanagari_to_hinglish("Hello दोस्त")
    assert "Hello" in res_mixed
    assert "dost" in res_mixed.lower()


def test_caption_studio_auto_caption_validation():
    app = create_app()
    client = app.test_client()

    # When no video file is specified
    res = client.post(
        "/api/caption-studio/auto-caption",
        json={"videoFileName": "", "language": "hinglish"}
    )
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False
    assert "No video filename provided" in data["error"]


def test_caption_studio_navigation_routes_resolve():
    app = create_app()
    client = app.test_client()

    routes_to_test = [
        "/caption-studio",
        "/open-caption-studio?video=test.mp4&project_id=1",
        "/",
        "/dashboard",
        "/studio",
        "/yt-downloader",
        "/youtube-desk",
        "/guide",
    ]
    for r in routes_to_test:
        res = client.get(r)
        assert res.status_code in (200, 302), f"Route {r} returned {res.status_code}"


def test_caption_studio_export_validation_missing_video():
    app = create_app()
    client = app.test_client()

    res = client.post(
        "/api/caption-studio/export",
        json={"videoFileName": "", "captions": []}
    )
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False




