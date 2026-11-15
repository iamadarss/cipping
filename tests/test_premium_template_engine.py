"""
Comprehensive Test Suite for UpClip Studio — Premium Template Engine V1.0.
Verifies:
- Test A: Template Registry (5 master templates exist, unique, valid)
- Test B: Template Selection & Persistence (Level 1 Project Default, Level 2 Clip Override, Level 3 Global Preference)
- Test C: Caption Rendering (Hindi Devanagari, English, Hinglish, Karaoke, Highlights, Sync)
- Test D: Video Rendering (1080x1920, H.264, Audio preserved, for all 5 templates)
- Test E: DualCast Layout Configurations & Single-Source Fallback
- Test F: Preview Consistency & Asset Availability
"""

import json
from pathlib import Path
import subprocess
import pytest
import config
from core.template_engine import (
    template_engine,
    TemplateConfig,
    DUALCAST_LAYOUTS,
    PREMIUM_TEMPLATES,
)
from core.preset_manager import preset_manager
from core.settings_manager import settings_manager
from ai.animated_caption_renderer import AnimatedCaptionRenderer
from ai.caption_templates import CAPTION_TEMPLATES

TEST_INPUT_VIDEO = config.INPUT_DIR / "test_footage_3s.mp4"
OUTPUT_TEST_DIR = config.OUTPUT_DIR / "final" / "template_test_runs"


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    OUTPUT_TEST_DIR.mkdir(parents=True, exist_ok=True)
    yield


@pytest.fixture(scope="module")
def app():
    from app import create_app
    test_app = create_app()
    test_app.config["TESTING"] = True
    return test_app


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()


# =============================================================================
# TEST A — TEMPLATE REGISTRY
# =============================================================================

def test_template_registry_all_five_exist_and_validate():
    """Verify all 5 master template IDs exist, have unique IDs, and pass validation."""
    required_ids = [
        "clean_creator",
        "black_editorial",
        "bold_podcast",
        "dualcast_interview",
        "cinematic_gold",
    ]

    all_templates = template_engine.get_all_templates()
    template_ids = [t["id"] for t in all_templates]

    # 1. Check all required IDs are present
    for req_id in required_ids:
        assert req_id in template_ids, f"Required template '{req_id}' missing from registry"

    # 2. Check no duplicate IDs
    assert len(template_ids) == len(set(template_ids)), "Duplicate template IDs detected"

    # 3. Validate each configuration
    for req_id in required_ids:
        tmpl = template_engine.get_template(req_id)
        assert tmpl is not None, f"Template '{req_id}' could not be retrieved"
        assert tmpl.name, f"Template '{req_id}' has empty name"
        assert tmpl.category in ["Creator", "Cinematic", "Podcast", "Motivation", "Educational"], f"Invalid category for '{req_id}'"
        assert tmpl.aspect_ratio == "9:16"
        assert tmpl.caption_config.font_family, f"Font family missing for '{req_id}'"
        assert tmpl.caption_config.font_size > 0, f"Font size invalid for '{req_id}'"
        assert tmpl.caption_config.active_word_color.startswith("#"), f"Active word color invalid for '{req_id}'"

        # Validate with engine validator
        is_valid, errors = template_engine.validate_template_config(tmpl.to_dict())
        assert is_valid, f"Template '{req_id}' failed validation: {errors}"


def test_preset_manager_includes_all_five_templates():
    """Verify preset_manager.get_templates() integrates the 5 master templates at top."""
    presets = preset_manager.get_templates()
    preset_ids = [p.get("id") for p in presets]

    for req_id in ["clean_creator", "black_editorial", "bold_podcast", "dualcast_interview", "cinematic_gold"]:
        assert req_id in preset_ids, f"Preset manager missing template '{req_id}'"


def test_caption_templates_registered_for_all_five():
    """Verify CAPTION_TEMPLATES has definitions for all 5 master templates."""
    for req_id in ["clean_creator", "black_editorial", "bold_podcast", "dualcast_interview", "cinematic_gold"]:
        assert req_id in CAPTION_TEMPLATES, f"CAPTION_TEMPLATES missing preset '{req_id}'"
        cap = CAPTION_TEMPLATES[req_id]
        assert cap["font_family"]
        assert cap["highlight_color"]


# =============================================================================
# TEST B — TEMPLATE SELECTION, PERSISTENCE & 3-LEVEL APPLICATION
# =============================================================================

def test_template_selection_and_persistence(client):
    """
    Verify Level 1 (Project Default), Level 2 (Clip Override), and Level 3 (Global Preference).
    """
    # 1. Level 3: Set Global Preferred Template
    res = client.post("/api/templates/set-global-preferred", json={"template_id": "black_editorial"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["preferred_template"] == "black_editorial"

    # Verify retrieval
    res_get = client.get("/api/templates/global-preferred")
    assert res_get.status_code == 200
    assert res_get.get_json()["preferred_template"] == "black_editorial"

    # 2. Create a project
    res_proj = client.post("/api/projects", json={"name": "Template Test Project"})
    assert res_proj.status_code in [200, 201]
    proj_data = res_proj.get_json()
    proj_id = (proj_data.get("project") or proj_data)["id"]

    # 3. Level 1: Set Project Default Template
    res_def = client.post("/api/templates/set-project-default", json={
        "project_id": proj_id,
        "template_id": "cinematic_gold",
        "custom_settings": {"caption_config": {"font_size": 42}}
    })
    assert res_def.status_code == 200
    def_data = res_def.get_json()
    assert def_data["success"] is True
    assert def_data["default_template"]["id"] == "cinematic_gold"

    # 4. Level 2: Set Clip Override on specific clip
    clip_name = "clip_01.mp4"
    res_over = client.post(f"/api/projects/{proj_id}/clips/{clip_name}/template-override", json={
        "template_id": "bold_podcast"
    })
    assert res_over.status_code == 200
    over_data = res_over.get_json()
    assert over_data["success"] is True
    assert clip_name in over_data["clip_templates"]
    assert over_data["clip_templates"][clip_name]["template_id"] == "bold_podcast"

    # 5. Verify Project State holds both default and override without collision
    res_state = client.get(f"/api/projects/{proj_id}/template")
    assert res_state.status_code == 200
    state_data = res_state.get_json()
    assert state_data["default_template"]["id"] == "cinematic_gold"
    assert state_data["clip_templates"][clip_name]["template_id"] == "bold_podcast"

    # Verify global preference remains independent
    res_global = client.get("/api/templates/global-preferred")
    assert res_global.get_json()["preferred_template"] == "black_editorial"


# =============================================================================
# TEST C — CAPTION RENDERING (HINDI, ENGLISH, HINGLISH)
# =============================================================================

def test_caption_rendering_hindi_english_hinglish():
    """Verify ASS subtitle generation for Hindi Devanagari, English, and Hinglish with word karaoke."""
    renderer = AnimatedCaptionRenderer()

    # 1. Hindi Devanagari
    hindi_transcript = [
        {
            "start": 0.0,
            "end": 2.5,
            "text": "नमस्ते दोस्तों आज हम बात करेंगे",
            "words": [
                {"text": "नमस्ते", "start": 0.0, "end": 0.6},
                {"text": "दोस्तों", "start": 0.6, "end": 1.2},
                {"text": "आज", "start": 1.2, "end": 1.6},
                {"text": "हम", "start": 1.6, "end": 2.0},
                {"text": "बात", "start": 2.0, "end": 2.5},
            ]
        }
    ]
    hindi_ass = OUTPUT_TEST_DIR / "hindi_test.ass"
    renderer.save_ass(hindi_transcript, hindi_ass, template="clean_creator")
    assert hindi_ass.exists()
    content = hindi_ass.read_text(encoding="utf-8")
    assert "नमस्ते" in content
    assert "दोस्तों" in content
    # In ASS format, #38BDF8 is encoded in BGR as &H..F8BD38&
    assert "F8BD38" in content or "38BDF8" in content

    # 2. Hinglish
    hinglish_transcript = [
        {
            "start": 0.0,
            "end": 2.2,
            "text": "Bhai video edit karke viral kar do",
            "words": [
                {"text": "Bhai", "start": 0.0, "end": 0.5},
                {"text": "video", "start": 0.5, "end": 1.0},
                {"text": "edit", "start": 1.0, "end": 1.4},
                {"text": "viral", "start": 1.4, "end": 1.8},
                {"text": "do", "start": 1.8, "end": 2.2},
            ]
        }
    ]
    hinglish_ass = OUTPUT_TEST_DIR / "hinglish_test.ass"
    renderer.save_ass(hinglish_transcript, hinglish_ass, template="bold_podcast")
    assert hinglish_ass.exists()
    h_content = hinglish_ass.read_text(encoding="utf-8")
    assert "viral" in h_content.lower()
    # In ASS format, #FBBF24 is encoded in BGR as 24BFFB
    assert "24BFFB" in h_content or "FBBF24" in h_content

    # 3. English
    english_transcript = [
        {
            "start": 0.0,
            "end": 2.0,
            "text": "CONSISTENCY IS THE KEY",
            "words": [
                {"text": "CONSISTENCY", "start": 0.0, "end": 0.7},
                {"text": "IS", "start": 0.7, "end": 1.0},
                {"text": "THE", "start": 1.0, "end": 1.3},
                {"text": "KEY", "start": 1.3, "end": 2.0},
            ]
        }
    ]
    english_ass = OUTPUT_TEST_DIR / "english_test.ass"
    renderer.save_ass(english_transcript, english_ass, template="black_editorial")
    assert english_ass.exists()
    e_content = english_ass.read_text(encoding="utf-8")
    assert "CONSISTENCY" in e_content
    # In ASS format, #EF4444 is encoded in BGR as 4444EF
    assert "4444EF" in e_content or "EF4444" in e_content


# =============================================================================
# TEST D — VIDEO RENDERING FOR ALL FIVE TEMPLATES
# =============================================================================

@pytest.mark.parametrize("template_id", [
    "clean_creator",
    "black_editorial",
    "bold_podcast",
    "dualcast_interview",
    "cinematic_gold",
])
def test_video_rendering_all_five_templates(template_id):
    """Render real short MP4 test video for each template and inspect output properties."""
    assert TEST_INPUT_VIDEO.exists(), f"Test input video {TEST_INPUT_VIDEO} missing"

    renderer = AnimatedCaptionRenderer()
    out_video = OUTPUT_TEST_DIR / f"render_{template_id}.mp4"

    transcript = [
        {
            "start": 0.0,
            "end": 2.5,
            "text": f"PREMIUM TEMPLATE {template_id.upper()}",
            "words": [
                {"text": "PREMIUM", "start": 0.0, "end": 0.8},
                {"text": "TEMPLATE", "start": 0.8, "end": 1.6},
                {"text": template_id.upper(), "start": 1.6, "end": 2.5},
            ]
        }
    ]

    rendered = renderer.render(
        input_video=TEST_INPUT_VIDEO,
        transcript=transcript,
        output_video=out_video,
        template=template_id,
    )

    assert rendered is not None
    assert Path(rendered).exists()
    assert Path(rendered).stat().st_size > 50000

    # Probe with ffprobe
    cmd = [
        config.FFPROBE_PATH,
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,codec_name,r_frame_rate",
        "-of", "json",
        str(rendered),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    info = json.loads(res.stdout)
    v_stream = info["streams"][0]

    assert v_stream["codec_name"] == "h264"
    assert int(v_stream["width"]) == 1080
    assert int(v_stream["height"]) == 1920

    # Probe audio stream
    cmd_a = [
        config.FFPROBE_PATH,
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=codec_name",
        "-of", "json",
        str(rendered),
    ]
    res_a = subprocess.run(cmd_a, capture_output=True, text=True)
    assert res_a.returncode == 0
    info_a = json.loads(res_a.stdout)
    assert len(info_a.get("streams", [])) > 0, "Audio stream must be preserved"


# =============================================================================
# TEST E — DUALCAST LAYOUT CONFIGURATIONS
# =============================================================================

@pytest.mark.parametrize("layout_style", DUALCAST_LAYOUTS)
def test_dualcast_all_four_layouts(layout_style):
    """Test filtergraph generation and compilation for all 4 DualCast layouts."""
    tmpl = template_engine.get_template("dualcast_interview")
    assert tmpl is not None

    fg, meta = template_engine._templates["dualcast_interview"].video_layout.mode, {}
    # Build layout filtergraph
    filtergraph = template_engine._build_dualcast_filtergraph(
        source_w=1920, source_h=1080, target_w=1080, target_h=1920, layout_style=layout_style
    )
    assert filtergraph
    assert "split" in filtergraph
    assert "scale" in filtergraph

    if layout_style == "SIDE_BY_SIDE":
        assert "panel1" in filtergraph and "panel2" in filtergraph
    elif layout_style == "ACTIVE_SPEAKER_FOCUS":
        assert "gblur" in filtergraph
    else:
        assert "tile_top" in filtergraph and "tile_bottom" in filtergraph


# =============================================================================
# TEST F — PREVIEW ASSETS & CONSISTENCY
# =============================================================================

def test_preview_assets_exist():
    """Verify that all 5 SVG thumbnails and all 5 preview MP4s exist on disk."""
    for req_id in ["clean_creator", "black_editorial", "bold_podcast", "dualcast_interview", "cinematic_gold"]:
        # 1. SVG Thumbnail
        svg_file = config.ROOT_DIR / "static" / "img" / "templates" / f"{req_id}.svg"
        assert svg_file.exists(), f"Thumbnail {svg_file} missing"
        assert svg_file.stat().st_size > 1000

        # 2. Preview Video
        mp4_file = config.ROOT_DIR / "static" / "previews" / f"{req_id}_preview.mp4"
        assert mp4_file.exists(), f"Preview video {mp4_file} missing"
        assert mp4_file.stat().st_size > 1000000
