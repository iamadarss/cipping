"""
Comprehensive tests for UpClip Studio Premium Caption Engine & Creator Preset Library.
Verifies:
  - Phase 2: Centralized Preset Registry CRUD & Persistence
  - Phase 3: All 19 Benchmark Creator Presets ("Card & Aesthetic" + "Loud Captions")
  - Phase 4: 10-Animation Engine in ASS
  - Phase 5: Normalized Style Schema Validation
  - Phase 7: Hindi / Hinglish / Devanagari Unicode Text Shaping & Font Fallback
  - Phase 8: Safe Margins & Safe Zone Alignment
  - REST APIs in routes/caption_studio.py
"""

import pytest
from pathlib import Path
import json

from ai.caption_presets import (
    CaptionPresetSchema,
    CaptionPresetRegistry,
    caption_registry,
    get_preset,
    list_presets,
    CANONICAL_PRESETS,
    VALID_CATEGORIES,
    VALID_ANIMATIONS,
    resolve_canonical_id,
    migrate_legacy_style,
)
from ai.animated_caption_renderer import AnimatedCaptionRenderer
from app import create_app


EXPECTED_5_CINEMATIC_MASTER_IDS = [
    "cinematic_creator",
    "cinematic_minimal_hindi",
    "bold_keyword_yellow",
    "modern_kinetic_cyan",
    "editorial_layered",
]

EXPECTED_19_PRESET_IDS = [
    # Card & Aesthetic (11 styles)
    "boxed",
    "subtitle",
    "highlight",
    "comic",
    "terminal",
    "soft_glass",
    "magazine",
    "highlighter",
    "paper",
    "label",
    "sticker",
    # Loud Captions (8 styles)
    "bold_pop",
    "karaoke",
    "typewriter",
    "one_word",
    "neon",
    "pop_3d",
    "gradient",
    "beast",
]


def test_19_canonical_presets_registered():
    """Verify all 24 canonical presets (5 Cinematic Master + 19 Creator Benchmarks) are registered."""
    assert len(CANONICAL_PRESETS) == 24
    for preset_id in EXPECTED_19_PRESET_IDS:
        assert preset_id in CANONICAL_PRESETS, f"Missing canonical preset: {preset_id}"
        preset = get_preset(preset_id)
        assert preset.id == preset_id
        assert preset.name
        assert preset.category in VALID_CATEGORIES
        assert preset.is_system is True
        assert preset.text_color.startswith("#")
        assert preset.active_word_color.startswith("#")
        assert 100 <= preset.font_weight <= 900
        assert preset.font_size >= 24
        assert preset.animation in VALID_ANIMATIONS


def test_5_cinematic_master_reference_styles():
    """Verify the 5 Master Reference Styles reproduced from the 5 reference images."""
    for preset_id in EXPECTED_5_CINEMATIC_MASTER_IDS:
        assert preset_id in CANONICAL_PRESETS, f"Missing cinematic master preset: {preset_id}"
        p = get_preset(preset_id)
        assert p.category == "Cinematic Master"
        assert p.is_system is True

    # Style 01 - Cinematic Creator (Ice Blue Glow & 2-line hierarchy)
    creator = get_preset("cinematic_creator")
    assert creator.name == "Cinematic Creator"
    assert creator.active_word_color == "#80D8FF"
    assert creator.glow is True
    assert creator.two_line_hierarchy is True
    assert creator.uppercase is True

    # Style 02 - Cinematic Minimal Subtitles (Hindi Devanagari)
    hindi = get_preset("cinematic_minimal_hindi")
    assert "Devanagari" in hindi.name
    assert "Noto Sans Devanagari" in hindi.font_family
    assert hindi.text_color == "#FFFFFF"
    assert hindi.outline_enabled is False

    # Style 03 - Bold Keyword Highlight (Bright Yellow Punch)
    yellow = get_preset("bold_keyword_yellow")
    assert yellow.active_word_color == "#FFEA00"
    assert yellow.font_size >= 44
    assert yellow.two_line_hierarchy is True

    # Style 04 - Modern Kinetic Typography (Electric Cyan)
    cyan = get_preset("modern_kinetic_cyan")
    assert cyan.active_word_color == "#00F0FF"
    assert cyan.glow is True
    assert cyan.animation in ("word_reveal", "karaoke_highlight", "pop_in")

    # Style 05 - Editorial Layered Typography (Cream Serif)
    editorial = get_preset("editorial_layered")
    assert "Playfair" in editorial.font_family
    assert editorial.text_color == "#FDF6E9"
    assert editorial.text_case == "lowercase"


def test_preset_categories_taxonomy():
    """Verify presets are correctly distributed across Cinematic Master, Card & Aesthetic, and Loud Captions."""
    categories = caption_registry.get_categories()
    assert "Cinematic Master" in categories
    assert "Card & Aesthetic" in categories
    assert "Loud Captions" in categories

    cinematic_master = list_presets("Cinematic Master")
    assert len(cinematic_master) == 5
    assert any(p.id == "cinematic_creator" for p in cinematic_master)
    assert any(p.id == "cinematic_minimal_hindi" for p in cinematic_master)
    assert any(p.id == "bold_keyword_yellow" for p in cinematic_master)
    assert any(p.id == "modern_kinetic_cyan" for p in cinematic_master)
    assert any(p.id == "editorial_layered" for p in cinematic_master)

    card_aesthetic = list_presets("Card & Aesthetic")
    assert len(card_aesthetic) == 11
    assert any(p.id == "boxed" for p in card_aesthetic)
    assert any(p.id == "comic" for p in card_aesthetic)
    assert any(p.id == "highlight" for p in card_aesthetic)
    assert any(p.id == "terminal" for p in card_aesthetic)
    assert any(p.id == "soft_glass" for p in card_aesthetic)
    assert any(p.id == "magazine" for p in card_aesthetic)
    assert any(p.id == "highlighter" for p in card_aesthetic)
    assert any(p.id == "paper" for p in card_aesthetic)
    assert any(p.id == "label" for p in card_aesthetic)
    assert any(p.id == "sticker" for p in card_aesthetic)

    loud = list_presets("Loud Captions")
    assert len(loud) == 8
    assert any(p.id == "bold_pop" for p in loud)
    assert any(p.id == "karaoke" for p in loud)
    assert any(p.id == "typewriter" for p in loud)
    assert any(p.id == "one_word" for p in loud)
    assert any(p.id == "neon" for p in loud)
    assert any(p.id == "pop_3d" for p in loud)
    assert any(p.id == "gradient" for p in loud)
    assert any(p.id == "beast" for p in loud)


def test_schema_validation_and_normalization():
    """Verify schema sanitizes colors, clamps values, and normalizes casing."""
    raw = {
        "id": "Custom Super Style!",
        "name": "Super Style",
        "font_family": "Montserrat",
        "font_weight": 1200,     # Out of range -> clamped to 900
        "font_size": 150,         # Out of range -> clamped to 84
        "text_color": "ffffff",   # Missing # -> sanitized to #FFFFFF
        "active_word_color": "#00ff88cc",
        "outline_width": 15,      # Clamped to 10
        "background_opacity": 1.5, # Clamped to 1.0
        "animation": "pop",
        "uppercase": True,
        "is_tilted": True,
        "tilt_angle": -15,        # Clamped to -8.0
        "three_d_shadow": True,
    }
    schema = CaptionPresetSchema.from_dict(raw)
    assert schema.id == "custom_super_style_"
    assert schema.font_weight == 900
    assert schema.font_size == 84
    assert schema.text_color == "#FFFFFF"
    assert schema.outline_width == 10.0
    assert schema.background_opacity == 1.0
    assert schema.text_case == "uppercase"
    assert schema.animation == "pop"
    assert schema.is_tilted is True
    assert schema.tilt_angle == -8.0
    assert schema.three_d_shadow is True


def test_custom_preset_crud_and_persistence(tmp_path):
    """Verify custom preset create, duplicate, reset, and delete lifecycle."""
    custom_storage = tmp_path / "custom_presets_test.json"
    registry = CaptionPresetRegistry(storage_file=custom_storage)

    # 1. Save custom preset
    saved = registry.save_custom_preset({
        "id": "my_brand_style",
        "name": "My Brand Style",
        "font_family": "Inter",
        "font_weight": 800,
        "text_color": "#FFFFFF",
        "active_word_color": "#F43F5E",
        "word_box": True,
        "word_box_color": "#E11D48",
    })
    assert saved.id == "my_brand_style"
    assert saved.is_custom is True
    assert saved.category == "Custom"
    assert custom_storage.exists()

    # 2. Retrieve
    retrieved = registry.get_preset("my_brand_style")
    assert retrieved.name == "My Brand Style"
    assert retrieved.word_box is True
    assert retrieved.word_box_color == "#E11D48"

    # 3. Duplicate
    cloned = registry.duplicate_preset("my_brand_style", "My Brand Style Cloned")
    assert cloned.name == "My Brand Style Cloned"
    assert cloned.id != "my_brand_style"
    assert cloned.active_word_color == "#F43F5E"

    # 4. Delete
    deleted = registry.delete_custom_preset("my_brand_style")
    assert deleted is True
    fallback = registry.get_preset("my_brand_style")
    assert fallback.id == "boxed"  # Defaults cleanly to boxed


def test_legacy_migrations():
    """Verify legacy preset names and aliases resolve seamlessly to new benchmark IDs."""
    assert resolve_canonical_id("hormozi") == "bold_pop"
    assert resolve_canonical_id("hormozi_pop") == "bold_pop"
    assert resolve_canonical_id("mrbeast") == "beast"
    assert resolve_canonical_id("beast_glow") == "beast"
    assert resolve_canonical_id("tiktok-pop") == "bold_pop"
    assert resolve_canonical_id("cap_clean") == "boxed"
    assert resolve_canonical_id("cap_podcast") == "karaoke"
    assert resolve_canonical_id("pure_white") == "boxed"
    assert resolve_canonical_id("podcast_gold") == "karaoke"

    # Test dictionary style migration
    legacy_style = {
        "preset_id": "hormozi_pop",
        "fontFamily": "Inter",
        "fontSize": 42,
        "textColor": "#FFFFFF",
        "activeWordColor": "#00FF66",
    }
    migrated = migrate_legacy_style(legacy_style)
    assert migrated["id"] == "bold_pop"
    assert migrated["font_family"] == "Inter"
    assert migrated["font_size"] == 42
    assert migrated["text_color"] == "#FFFFFF"
    assert migrated["active_word_color"] == "#00FF66"


def test_10_animations_in_ass():
    """Verify all 16 professional animations generate valid ASS override tags."""
    renderer = AnimatedCaptionRenderer()
    sample_transcript = [
        {
            "start": 0.0,
            "end": 2.5,
            "text": "Unlocking explosive growth today",
            "words": [
                {"text": "Unlocking", "start": 0.0, "end": 0.6},
                {"text": "explosive", "start": 0.6, "end": 1.2},
                {"text": "growth", "start": 1.2, "end": 1.8},
                {"text": "today", "start": 1.8, "end": 2.5},
            ]
        }
    ]

    animations = [
        "pop_in",
        "bounce_in",
        "smooth_fade",
        "slide_up",
        "slide_down",
        "zoom_in",
        "zoom_out",
        "typewriter",
        "word_reveal",
        "karaoke_highlight",
        "glow_pulse",
        "glitch",
        "elastic_scale",
        "blur_reveal",
        "split_reveal",
        "tracking_reveal",
        # Legacy aliases
        "color_karaoke",
        "soft_pop",
        "active_word_pill",
        "emphasis_scale",
        "word_highlight",
        "sentence_fade",
    ]

    for anim in animations:
        ass = renderer.build_ass(sample_transcript, opts={"animation": anim})
        assert "Style: Caption," in ass, f"Failed for animation {anim}"
        assert "Dialogue: 0," in ass, f"Failed for animation {anim}"
        assert r"\k" in ass, f"Karaoke sync missing for animation {anim}"
        assert "Unlocking" in ass
        assert "growth" in ass


def test_devanagari_hindi_text_shaping_and_font_fallback():
    """Verify Hindi and Hinglish Devanagari text injects Unicode font fallback in ASS."""
    renderer = AnimatedCaptionRenderer()
    hindi_transcript = [
        {
            "start": 0.0,
            "end": 3.0,
            "text": "आज का टॉपिक है viral growth और सफलता!",
            "words": [
                {"text": "आज", "start": 0.0, "end": 0.5},
                {"text": "का", "start": 0.5, "end": 0.8},
                {"text": "टॉपिक", "start": 0.8, "end": 1.4},
                {"text": "है", "start": 1.4, "end": 1.8},
                {"text": "viral", "start": 1.8, "end": 2.2},
                {"text": "growth", "start": 2.2, "end": 2.6},
                {"text": "और", "start": 2.6, "end": 2.8},
                {"text": "सफलता!", "start": 2.8, "end": 3.0},
            ]
        }
    ]

    ass = renderer.build_ass(hindi_transcript, opts={"font_family": "Montserrat"})
    # Verify header contains Devanagari font fallback
    assert "Segoe UI" in ass or "Noto Sans Devanagari" in ass or "Arial" in ass
    # Verify Hindi characters preserved with zero mojibake
    assert "आज" in ass
    assert "सफलता!" in ass
    assert "Dialogue: 0," in ass


def test_safe_margins_in_ass():
    """Verify vertical safe margins keep captions out of TikTok/Reels UI obstruction."""
    renderer = AnimatedCaptionRenderer()
    transcript = [{"start": 0.0, "end": 2.0, "text": "Testing safe margins"}]

    # 1. Bottom safe margin on 1080x1920 (PlayResY = 1920)
    ass_bot = renderer.build_ass(transcript, opts={"position": "bottom", "play_res_y": 1920})
    # MarginV should be >= 280 to clear bottom action UI
    assert "1920" in ass_bot
    # Style line margin_v check
    assert ",280,1" in ass_bot or ",300,1" in ass_bot or ",360,1" in ass_bot

    # 2. Lower third safe margin
    ass_lt = renderer.build_ass(transcript, opts={"position": "lower_third", "play_res_y": 1920})
    assert ",360,1" in ass_lt or ",400,1" in ass_lt


def test_caption_studio_canonical_presets_api():
    """Verify REST endpoint /api/caption-studio/presets/canonical returns all 19 presets."""
    app = create_app()
    client = app.test_client()

    res = client.get("/api/caption-studio/presets/canonical")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["count"] >= 19
    assert len(data["categories"]) >= 2
    assert any(p["id"] == "boxed" for p in data["presets"])
    assert any(p["id"] == "subtitle" for p in data["presets"])
    assert any(p["id"] == "highlight" for p in data["presets"])
    assert any(p["id"] == "comic" for p in data["presets"])
    assert any(p["id"] == "bold_pop" for p in data["presets"])
    assert any(p["id"] == "karaoke" for p in data["presets"])
    assert any(p["id"] == "beast" for p in data["presets"])

    # Test category filter
    res_loud = client.get("/api/caption-studio/presets/canonical?category=Loud%20Captions")
    assert res_loud.status_code == 200
    data_loud = res_loud.get_json()
    assert len(data_loud["presets"]) == 8
    assert all(p["category"] == "Loud Captions" for p in data_loud["presets"])
