"""
Comprehensive tests for UpClip Studio Premium Caption Engine & Creator Preset Library.
Verifies:
  - Phase 2: Centralized Preset Registry CRUD & Persistence
  - Phase 3: All 20 Canonical Presets Across 5 Categories
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


EXPECTED_20_PRESET_IDS = [
    # Minimal & Luxury
    "pure_white",
    "soft_highlight",
    "luxury_editorial",
    "modern_creator",
    # Podcast
    "podcast_gold",
    "podcast_teal",
    "glass_caption",
    "speaker_focus",
    # Kinetic
    "karaoke_clean",
    "word_pill",
    "punch_orange",
    "creator_pink",
    # Cinematic
    "cinema_classic",
    "documentary",
    "editorial_gold",
    "top_clean",
    # Special
    "fresh_green",
    "lavender",
    "focus_red",
    "monochrome",
]


def test_20_canonical_presets_registered():
    """Verify all 20 specified premium presets are registered with exact IDs."""
    assert len(CANONICAL_PRESETS) == 20
    for preset_id in EXPECTED_20_PRESET_IDS:
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


def test_preset_categories_taxonomy():
    """Verify presets are correctly distributed across the 5 canonical categories."""
    categories = caption_registry.get_categories()
    assert "Minimal & Luxury" in categories
    assert "Podcast" in categories
    assert "Kinetic" in categories
    assert "Cinematic" in categories
    assert "Special" in categories

    minimal = list_presets("Minimal & Luxury")
    assert len(minimal) >= 4
    assert any(p.id == "pure_white" for p in minimal)
    assert any(p.id == "luxury_editorial" for p in minimal)

    podcast = list_presets("Podcast")
    assert len(podcast) >= 4
    assert any(p.id == "podcast_gold" for p in podcast)
    assert any(p.id == "glass_caption" for p in podcast)

    kinetic = list_presets("Kinetic")
    assert len(kinetic) >= 4
    assert any(p.id == "karaoke_clean" for p in kinetic)
    assert any(p.id == "word_pill" for p in kinetic)

    cinematic = list_presets("Cinematic")
    assert len(cinematic) >= 4
    assert any(p.id == "cinema_classic" for p in cinematic)
    assert any(p.id == "top_clean" for p in cinematic)

    special = list_presets("Special")
    assert len(special) >= 4
    assert any(p.id == "fresh_green" for p in special)
    assert any(p.id == "monochrome" for p in special)


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
    assert fallback.id == "pure_white"  # Defaults cleanly


def test_legacy_migrations():
    """Verify legacy preset names and aliases resolve seamlessly to canonical IDs."""
    assert resolve_canonical_id("hormozi") == "word_pill"
    assert resolve_canonical_id("hormozi_pop") == "word_pill"
    assert resolve_canonical_id("mrbeast") == "focus_red"
    assert resolve_canonical_id("beast_glow") == "focus_red"
    assert resolve_canonical_id("tiktok-pop") == "creator_pink"
    assert resolve_canonical_id("cap_clean") == "pure_white"
    assert resolve_canonical_id("cap_podcast") == "podcast_gold"

    # Test dictionary style migration
    legacy_style = {
        "preset_id": "hormozi_pop",
        "fontFamily": "Inter",
        "fontSize": 42,
        "textColor": "#FFFFFF",
        "activeWordColor": "#00FF66",
    }
    migrated = migrate_legacy_style(legacy_style)
    assert migrated["id"] == "word_pill"
    assert migrated["font_family"] == "Inter"
    assert migrated["font_size"] == 42
    assert migrated["text_color"] == "#FFFFFF"
    assert migrated["active_word_color"] == "#00FF66"


def test_10_animations_in_ass():
    """Verify each of the 10 canonical animations generates valid ASS override tags."""
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
        "color_karaoke",
        "smooth_fade",
        "soft_pop",
        "active_word_pill",
        "slide_up",
        "slide_down",
        "typewriter",
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
    """Verify REST endpoint /api/caption-studio/presets/canonical returns all 20 presets."""
    app = create_app()
    client = app.test_client()

    res = client.get("/api/caption-studio/presets/canonical")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["count"] >= 20
    assert len(data["categories"]) >= 5
    assert any(p["id"] == "pure_white" for p in data["presets"])
    assert any(p["id"] == "podcast_gold" for p in data["presets"])
    assert any(p["id"] == "word_pill" for p in data["presets"])
    assert any(p["id"] == "punch_orange" for p in data["presets"])
    assert any(p["id"] == "monochrome" for p in data["presets"])

    # Test category filter
    res_kinetic = client.get("/api/caption-studio/presets/canonical?category=Kinetic")
    assert res_kinetic.status_code == 200
    data_kinetic = res_kinetic.get_json()
    assert all(p["category"] == "Kinetic" for p in data_kinetic["presets"])

