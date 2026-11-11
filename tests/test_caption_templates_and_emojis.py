"""
Tests for Caption Templates, Contextual Emojis, and Hook Title Banner Generation.
Verifies SupoClip-compatible creator presets and ASS rendering.
"""

import pytest
from ai.caption_templates import (
    get_template,
    get_all_templates,
    get_template_names,
    get_template_info,
    create_custom_template,
    build_hook_title_ass,
    CAPTION_TEMPLATES,
)
from ai.emoji_captions import (
    lookup_emoji,
    annotate_caption_words,
    normalize_token,
    POWER_WORDS,
)
from ai.animated_caption_renderer import AnimatedCaptionRenderer


def test_caption_templates_catalog():
    templates = get_all_templates()
    expected_keys = {"default", "hormozi", "mrbeast", "minimal", "tiktok", "neon", "podcast"}
    for key in expected_keys:
        assert key in templates
        preset = templates[key]
        assert "name" in preset
        assert "font_family" in preset
        assert "font_size" in preset
        assert "highlight_color" in preset

    # Hormozi specific checks
    hormozi = get_template("hormozi")
    assert hormozi["word_box"] is True
    assert hormozi["word_box_color"] == "#00BF49"
    assert hormozi["uppercase"] is True

    # Neon specific checks
    neon = get_template("neon")
    assert neon["glow"] is True
    assert neon["highlight_color"] == "#FF00FF"

    # Minimal specific checks
    minimal = get_template("minimal")
    assert minimal["background"] is True
    assert minimal["animation"] == "fade"


def test_get_template_aliases():
    assert get_template("hormozi_pop")["id"] == "hormozi"
    assert get_template("beast_glow")["id"] == "mrbeast"
    assert get_template("tiktok_pop")["id"] == "tiktok"
    assert get_template("neon_cyber")["id"] == "neon"
    assert get_template("clean")["id"] == "minimal"
    # Unknown fallback to default
    assert get_template("unknown_preset_xyz")["id"] == "default"


def test_create_custom_template():
    custom = create_custom_template(
        "My Cyber Style",
        base_template="neon",
        highlight_color="#FFFF00",
        font_size=42,
    )
    assert custom["name"] == "My Cyber Style"
    assert custom["highlight_color"] == "#FFFF00"
    assert custom["font_size"] == 42
    assert custom["glow"] is True  # Inherited from neon


def test_emoji_lookup_and_singularization():
    assert lookup_emoji("money") == "💰"
    assert lookup_emoji("dollars") == "💵"  # Plural handling
    assert lookup_emoji("rich") == "🤑"
    assert lookup_emoji("win") == "🏆"
    assert lookup_emoji("rocket") == "🚀"
    assert lookup_emoji("smart") == "🧠"
    assert lookup_emoji("fire") == "🔥"
    assert lookup_emoji("ai") == "🤖"
    assert lookup_emoji("unknown_word_123") is None


def test_emoji_rate_limiting_and_power_words():
    # Sequence with multiple rapid emoji words
    sample_words = [
        {"text": "This", "start": 0.0, "end": 0.4},
        {"text": "money", "start": 0.4, "end": 0.8},       # Should get 💰
        {"text": "cash", "start": 0.8, "end": 1.1},        # Too close (<3 words gap)
        {"text": "is", "start": 1.1, "end": 1.3},
        {"text": "literally", "start": 1.3, "end": 1.6},   # Power word -> emphasis
        {"text": "insane", "start": 1.6, "end": 2.0},      # Power word + emoji
        {"text": "100%", "start": 2.0, "end": 2.4},        # Number/percent -> emphasis
    ]

    emojis, emphasis = annotate_caption_words(
        sample_words, enable_emoji=True, enable_emphasis=True, min_word_gap=3
    )

    # Word 1 ('money') should have emoji
    assert 1 in emojis
    assert emojis[1] == "💰"

    # Word 2 ('cash') should NOT have emoji due to min_word_gap
    assert 2 not in emojis

    # Power words ('literally', 'insane', '100%') should be in emphasis
    assert 4 in emphasis  # literally
    assert 5 in emphasis  # insane
    assert 6 in emphasis  # 100%


def test_build_hook_title_ass():
    template = get_template("hormozi")
    style_line, dialogue_events = build_hook_title_ass(
        hook_title="The $40k Secret to Going Viral",
        template=template,
        video_width=1080,
        video_height=1920,
        output_duration=30.0,
    )

    assert "Style: Hook" in style_line
    assert len(dialogue_events) == 1
    event = dialogue_events[0]
    assert "Dialogue: 1," in event
    assert r"\fad(160,240)" in event
    assert r"\fscx92\fscy92" in event
    # Check that power words / numbers are highlighted
    assert r"\c" in event


def test_animated_caption_renderer_with_new_templates():
    renderer = AnimatedCaptionRenderer()
    transcript = [
        {
            "start": 0.5,
            "end": 3.0,
            "text": "Make big money with AI today",
            "words": [
                {"text": "Make", "start": 0.5, "end": 0.9},
                {"text": "big", "start": 0.9, "end": 1.3},
                {"text": "money", "start": 1.3, "end": 1.8},
                {"text": "with", "start": 1.8, "end": 2.1},
                {"text": "AI", "start": 2.1, "end": 2.5},
                {"text": "today", "start": 2.5, "end": 3.0},
            ]
        }
    ]

    # 1. Hormozi Preset (Uppercase + Emojis)
    ass_hormozi = renderer.build_ass(transcript, template="hormozi")
    assert "Style: Caption," in ass_hormozi
    assert "Dialogue: 0," in ass_hormozi
    assert "MONEY" in ass_hormozi or "money" in ass_hormozi
    # Check emoji injection (money -> 💰)
    assert "💰" in ass_hormozi

    # 2. Neon Preset (Glow)
    ass_neon = renderer.build_ass(transcript, template="neon")
    assert r"\blur4" in ass_neon

    # 3. Hook Title Integration
    ass_with_hook = renderer.build_ass(
        transcript,
        opts={"hook_title": "How to win big in 2026", "emoji": True},
        template="default"
    )
    assert "Style: Hook," in ass_with_hook
    assert "Dialogue: 1," in ass_with_hook
    assert "2026" in ass_with_hook

