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
    assert "translateCaptionsTopBtn" not in html

    # 2. Left Sidebar Navigation
    assert "appSidebar" in html
    assert "AI Clip Studio" in html
    assert "Caption Studio" in html
    assert "Studio Hub" in html
    assert "Downloader" in html
    assert "YouTube Desk" in html
    assert "Help & Guide" in html
    assert "sidebarToggle" in html

    # 3. 9:16 Mobile Reel Frame & Transport Controls
    assert "reelFrameSection" in html
    assert "mobilePhoneFrame" in html
    assert "previewCanvasBox" in html
    assert "captionVideo" in html
    assert "captionOverlayContainer" in html
    assert "captionDragBox" in html
    assert "videoBottomTransport" in html
    assert "btnPlayPause" in html
    assert "btnSeekLeft" in html
    assert "btnSeekRight" in html

    # 4. Two-Column Stage & Custom Preset Buttons
    assert "colPresets" in html
    assert "colSettings" in html
    assert "presetsGrid" in html
    assert "settingsAccordions" in html
    assert "savePresetBtn" in html
    assert "myPresetsBtn" in html

    # 5. Settings Accordions
    assert "accordionFont" in html
    assert "accordionPosition" in html
    assert "accordionText" in html
    assert "accordionStroke" in html
    assert "accordionShadow" in html
    assert "accordionBackground" in html
    assert "accordionAnimation" in html

    # 6. Modals & Flow Controls
    assert "generateCaptionsModal" in html
    assert "genApplyBtn" in html
    assert "genReadyPanel" in html
    assert "savePresetModal" in html
    assert "myPresetsModal" in html
    assert "exportVideoModal" in html





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


def test_caption_studio_translate_urdu_to_hinglish_and_hindi():
    app = create_app()
    client = app.test_client()

    urdu_captions = [
        {
            "id": 1,
            "text": "اب سوال کی دولر کماتا کیسے ہیں",
            "start": 0.0,
            "end": 2.5,
            "words": [
                {"text": "اب", "start": 0.0, "end": 0.5},
                {"text": "سوال", "start": 0.5, "end": 1.0},
                {"text": "کی", "start": 1.0, "end": 1.5},
                {"text": "دولر", "start": 1.5, "end": 2.0},
                {"text": "کماتا", "start": 2.0, "end": 2.5}
            ]
        }
    ]

    # Test translating to Hinglish (Roman English letters)
    res_hinglish = client.post(
        "/api/caption-studio/translate",
        json={"captions": urdu_captions, "target_language": "hinglish"}
    )
    assert res_hinglish.status_code == 200
    data_hinglish = res_hinglish.get_json()
    assert data_hinglish["success"] is True
    hinglish_text = data_hinglish["captions"][0]["text"]
    # Verify no Urdu/Arabic characters remain
    from utils.hinglish_transliterator import is_urdu_or_arabic
    assert not is_urdu_or_arabic(hinglish_text)
    assert "saval" in hinglish_text.lower() or "ab" in hinglish_text.lower()

    # Test translating to Hindi (Devanagari script)
    res_hindi = client.post(
        "/api/caption-studio/translate",
        json={"captions": urdu_captions, "target_language": "hi"}
    )
    assert res_hindi.status_code == 200
    data_hindi = res_hindi.get_json()
    assert data_hindi["success"] is True
    hindi_text = data_hindi["captions"][0]["text"]
    assert not is_urdu_or_arabic(hindi_text)
    assert any(0x0900 <= ord(c) <= 0x097F for c in hindi_text)


def test_caption_studio_custom_presets_crud():
    app = create_app()
    client = app.test_client()

    test_style = {
        "fontFamily": "Inter",
        "fontSize": 40,
        "textColor": "#FFFFFF",
        "activeWordColor": "#22C55E",
        "bgMode": "solid",
        "bgColor": "#000000"
    }

    # 1. Save custom preset
    res_save = client.post(
        "/api/caption-studio/presets/save",
        json={"name": "Test Viral Preset", "style": test_style}
    )
    assert res_save.status_code == 200
    save_data = res_save.get_json()
    assert save_data["success"] is True
    saved_preset = save_data["preset"]
    preset_id = saved_preset["id"]
    assert saved_preset["name"] == "Test Viral Preset"
    assert saved_preset["style"]["fontFamily"] == "Inter"

    # 2. List custom presets
    res_list = client.get("/api/caption-studio/presets/list")
    assert res_list.status_code == 200
    list_data = res_list.get_json()
    assert list_data["success"] is True
    assert any(p["id"] == preset_id for p in list_data["presets"])

    # 3. Delete custom preset
    res_del = client.post(
        "/api/caption-studio/presets/delete",
        json={"id": preset_id}
    )
    assert res_del.status_code == 200
    del_data = res_del.get_json()
    assert del_data["success"] is True
    assert not any(p["id"] == preset_id for p in del_data["presets"])


def test_auto_caption_input_validation_and_resilience(monkeypatch):
    app = create_app()
    client = app.test_client()

    # 1. Missing videoFileName -> 400
    res_empty = client.post("/api/caption-studio/auto-caption", json={})
    assert res_empty.status_code == 400
    assert "No video filename provided" in res_empty.get_json()["error"]

    # 2. Nonexistent video -> 404 (clean error, never 500)
    res_not_found = client.post("/api/caption-studio/auto-caption", json={"videoFileName": "nonexistent_abc_123.mp4"})
    assert res_not_found.status_code == 404
    assert res_not_found.get_json()["success"] is False

    # 3. Mocked Whisper pipeline verifying chunking, Hinglish conversion and timing
    from ai.whisper_engine import WhisperEngine

    fake_segments = [
        {"start": 0.0, "end": 2.5, "text": "नमस्ते दोस्तों यह एक परीक्षण वीडियो है"},
        {"start": 3.0, "end": 5.5, "text": "स्वागत है आपका अप क्लिप स्टूडियो में"}
    ]

    def mock_transcribe_cached(self, video_path, cache_file, language=None):
        return fake_segments

    monkeypatch.setattr(WhisperEngine, "transcribe_cached", mock_transcribe_cached)

    import config
    sample_video = config.INPUT_DIR / "sample.mp4"
    if not sample_video.exists():
        sample_video.write_bytes(b"\x00" * 2048)

    # Call with URL-encoded filename
    res_success = client.post(
        "/api/caption-studio/auto-caption",
        json={
            "videoFileName": "sample.mp4?t=12345",
            "language": "hinglish",
            "style": "viral"
        }
    )
    assert res_success.status_code == 200
    res_data = res_success.get_json()
    assert res_data["success"] is True
    captions = res_data["captions"]
    assert len(captions) > 0

    # Ensure words are parsed with start/end numbers
    for cap in captions:
        assert "start" in cap
        assert "end" in cap
        assert "words" in cap
        assert isinstance(cap["words"], list)
        for w in cap["words"]:
            assert "text" in w
            assert "start" in w
            assert "end" in w


def test_caption_studio_resolution_font_scaling():
    """Verify that caption font size, stroke, and shadow are proportionally scaled to video resolution."""
    from ai.animated_caption_renderer import AnimatedCaptionRenderer

    renderer = AnimatedCaptionRenderer()
    sample_transcript = [
        {"start": 0.0, "end": 2.0, "text": "Viral Shorts Caption", "words": [
            {"text": "Viral", "start": 0.0, "end": 0.6},
            {"text": "Shorts", "start": 0.6, "end": 1.2},
            {"text": "Caption", "start": 1.2, "end": 2.0}
        ]}
    ]

    # 1. Default preview font size 38 on 1080x1920 Full HD video -> scales by 4.5x to 171
    ass_1080p = renderer.build_ass(
        sample_transcript,
        opts={"fontSize": 38, "strokeWidth": 3.5, "shadowBlur": 8, "play_res_x": 1080, "play_res_y": 1920}
    )
    style_line = [l for l in ass_1080p.splitlines() if l.startswith("Style: Caption")][0]
    parts = style_line.split(",")
    # Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
    fontsize = int(parts[2])
    outline = int(parts[16])
    shadow = int(parts[17])
    assert fontsize == 171, f"Expected 171 for 1080p scaling of 38px, got {fontsize}"
    assert outline == 10, f"Expected 10 for 1080p outline, got {outline}"
    assert shadow == 24, f"Expected 24 for 1080p shadow, got {shadow}"

    # 2. Enlarged font size 50 on 1080x1920 Full HD video -> scales to 225
    ass_large = renderer.build_ass(
        sample_transcript,
        opts={"fontSize": 50, "play_res_x": 1080, "play_res_y": 1920}
    )
    style_large = [l for l in ass_large.splitlines() if l.startswith("Style: Caption")][0]
    assert int(style_large.split(",")[2]) == 225

    # 3. 720p video (720x1280) -> scales by 3.0x (38 * 3 = 114)
    ass_720p = renderer.build_ass(
        sample_transcript,
        opts={"fontSize": 38, "play_res_x": 720, "play_res_y": 1280}
    )
    style_720p = [l for l in ass_720p.splitlines() if l.startswith("Style: Caption")][0]
    assert int(style_720p.split(",")[2]) == 114


def test_viral_enhancer_features_and_routes():
    """Verify ViralEnhancer generation of Outro CTA cards, text watermarks, and upload routes."""
    import io
    from pathlib import Path
    from ai.viral_enhancer import ViralEnhancer
    import config
    from app import create_app

    enhancer = ViralEnhancer()

    # 1. Outro CTA Card generation
    out_dir = config.OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    card_path = out_dir / "test_outro_card.png"
    result_card = enhancer.generate_outro_cta_card(
        channel_name="UpClip Viral",
        handle="@upclipviral",
        output_path=card_path,
        card_width=860,
        card_height=240
    )
    assert result_card.exists()
    assert result_card.stat().st_size > 1000

    # 2. Text Watermark overlay generation
    wm_path = out_dir / "test_text_watermark.png"
    result_wm = enhancer.generate_text_watermark_image(
        text="@MyViralChannel",
        output_path=wm_path,
        font_size=42,
        opacity=0.85
    )
    assert result_wm.exists()
    assert result_wm.stat().st_size > 500

    # 3. Route tests: upload-logo, upload-broll, preview-outro-card
    app = create_app()
    client = app.test_client()

    # Test upload-logo
    logo_data = {
        "logo": (io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100), "channel_logo.png")
    }
    res_logo = client.post(
        "/api/caption-studio/upload-logo",
        data=logo_data,
        content_type="multipart/form-data"
    )
    assert res_logo.status_code == 200
    logo_json = res_logo.get_json()
    assert logo_json["success"] is True
    assert "file_path" in logo_json
    assert logo_json["url"].startswith("/static/uploads/logos/")

    # Test upload-broll
    broll_data = {
        "broll": (io.BytesIO(b"\x00\x00\x00 ftypisom" + b"\x00" * 100), "broll_clip.mp4")
    }
    res_broll = client.post(
        "/api/caption-studio/upload-broll",
        data=broll_data,
        content_type="multipart/form-data"
    )
    assert res_broll.status_code == 200
    broll_json = res_broll.get_json()
    assert broll_json["success"] is True
    assert "file_path" in broll_json
    assert broll_json["url"].startswith("/static/uploads/brolls/")

    # Test preview-outro-card
    res_outro = client.post(
        "/api/caption-studio/preview-outro-card",
        json={
            "channel_name": "Test Creator",
            "handle": "@testcreator"
        }
    )
    assert res_outro.status_code == 200
    outro_json = res_outro.get_json()
    assert outro_json["success"] is True
    assert "url" in outro_json
    assert outro_json["url"].startswith("/static/uploads/previews/")



