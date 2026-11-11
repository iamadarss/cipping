"""
Caption Template & Preset System for UpClip Studio.
Complete library of creator presets (Hormozi, MrBeast, TikTok, Neon, Minimal, Podcast, Default)
and dynamic ASS animation builders.

Supports:
  - word_box:           Draw a filled rounded "pill" backing box behind the active spoken word
  - word_box_color:     Color of that pill (e.g. #00BF49)
  - word_pop:           Scale entrance on line appearance without causing word jitter
  - emoji:              Deterministic contextual emoji injection (via emoji_captions.py)
  - emphasis_color:     Accent color for power/keyword words and numbers
  - uppercase:          Force caption text to uppercase
  - glow:               Soft neon glow on text outline (\\blur4)
  - stroke_width / stroke_color: Heavy contrast outline
  - max_words_per_line: Words displayed per kinetic line chunk
  - position_y:         Vertical position ratio (0.0 to 1.0)
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import re

from ai.emoji_captions import normalize_token, POWER_WORDS
from ai.caption_presets.defaults import CANONICAL_PRESETS

# ---------------------------------------------------------------------------
# The 7 Production Creator Presets + 20 Canonical Premium Presets
# ---------------------------------------------------------------------------
CAPTION_TEMPLATES: Dict[str, Dict[str, Any]] = {
    # Legacy Creator Presets (Preserved 100% for Backward-Compatibility)
    "default": {
        "id": "default",
        "name": "Default",
        "category": "Kinetic",
        "description": "Punchy word-by-word captions with yellow pop highlight and emojis",
        "font_family": "Montserrat",
        "font_size": 36,
        "font_color": "#FFFFFF",
        "highlight_color": "#FFE000",   # Electric Yellow
        "emphasis_color": "#FFE000",
        "stroke_color": "#000000",
        "stroke_width": 3,
        "background": False,
        "background_color": None,
        "word_box": False,
        "word_box_color": None,
        "animation": "pop",
        "word_pop": True,
        "emoji": True,
        "uppercase": False,
        "shadow": True,
        "glow": False,
        "max_words_per_line": 4,
        "position_y": 0.80,
    },
    "hormozi": {
        "id": "hormozi",
        "name": "Hormozi",
        "category": "Kinetic",
        "description": "Alex Hormozi Viral Style — Green highlight with rounded pill backing box",
        "font_family": "Arial Black",
        "font_size": 38,
        "font_color": "#FFFFFF",
        "highlight_color": "#00FF66",   # Electric Neon Green
        "emphasis_color": "#FFE000",    # Yellow emphasis for numbers
        "stroke_color": "#000000",
        "stroke_width": 4,
        "background": False,
        "background_color": None,
        "word_box": True,
        "word_box_color": "#00BF49",    # Solid Green Pill
        "animation": "pop",
        "word_pop": True,
        "emoji": True,
        "uppercase": True,
        "shadow": True,
        "glow": False,
        "max_words_per_line": 3,
        "position_y": 0.74,
    },
    "mrbeast": {
        "id": "mrbeast",
        "name": "MrBeast",
        "category": "Kinetic",
        "description": "MrBeast Style — Large yellow text with red pop highlights & heavy stroke",
        "font_family": "Arial Black",
        "font_size": 40,
        "font_color": "#FFFF00",        # Vivid Yellow
        "highlight_color": "#FF2D2D",   # Punchy Red
        "emphasis_color": "#FFFFFF",
        "stroke_color": "#000000",
        "stroke_width": 5,
        "background": False,
        "background_color": None,
        "word_box": False,
        "word_box_color": None,
        "animation": "bounce",
        "word_pop": True,
        "emoji": True,
        "uppercase": True,
        "shadow": True,
        "glow": False,
        "max_words_per_line": 3,
        "position_y": 0.70,
    },
    "minimal": {
        "id": "minimal",
        "name": "Minimal",
        "category": "Minimal & Luxury",
        "description": "Clean, subtle captions with soft semi-transparent background",
        "font_family": "Inter",
        "font_size": 28,
        "font_color": "#FFFFFF",
        "highlight_color": "#FFFFFF",
        "emphasis_color": None,
        "stroke_color": None,
        "stroke_width": 0,
        "background": True,
        "background_color": "#00000080", # 50% dark overlay
        "word_box": False,
        "word_box_color": None,
        "animation": "fade",
        "word_pop": False,
        "emoji": False,
        "uppercase": False,
        "shadow": False,
        "glow": False,
        "max_words_per_line": 6,
        "position_y": 0.82,
    },
    "tiktok": {
        "id": "tiktok",
        "name": "TikTok",
        "category": "Kinetic",
        "description": "Official TikTok-style captions with crimson pink pop highlights",
        "font_family": "Montserrat",
        "font_size": 34,
        "font_color": "#FFFFFF",
        "highlight_color": "#FE2C55",   # TikTok Crimson Pink
        "emphasis_color": "#FE2C55",
        "stroke_color": "#000000",
        "stroke_width": 3,
        "background": False,
        "background_color": None,
        "word_box": False,
        "word_box_color": None,
        "animation": "pop",
        "word_pop": True,
        "emoji": True,
        "uppercase": False,
        "shadow": True,
        "glow": False,
        "max_words_per_line": 4,
        "position_y": 0.78,
    },
    "neon": {
        "id": "neon",
        "name": "Neon",
        "category": "Special",
        "description": "Glowing cyberpunk neon text with magenta highlights & blur glow",
        "font_family": "Montserrat",
        "font_size": 34,
        "font_color": "#00FFFF",        # Electric Cyan
        "highlight_color": "#FF00FF",   # Vibrant Magenta
        "emphasis_color": "#FF00FF",
        "stroke_color": "#002A6B",      # Dark Blue Outline
        "stroke_width": 2,
        "background": False,
        "background_color": None,
        "word_box": False,
        "word_box_color": None,
        "animation": "pop",
        "word_pop": True,
        "emoji": False,
        "uppercase": False,
        "shadow": False,
        "glow": True,                   # Neon blur glow
        "max_words_per_line": 4,
        "position_y": 0.76,
    },
    "podcast": {
        "id": "podcast",
        "name": "Podcast",
        "category": "Podcast",
        "description": "Professional podcast captions with warm gold highlight on dark backdrop",
        "font_family": "Inter",
        "font_size": 30,
        "font_color": "#FFFFFF",
        "highlight_color": "#FFB800",   # Warm Amber Gold
        "emphasis_color": "#FFB800",
        "stroke_color": "#1A1A1A",
        "stroke_width": 2,
        "background": True,
        "background_color": "#1A1A1ACC", # 80% opacity dark box
        "word_box": False,
        "word_box_color": None,
        "animation": "fade",
        "word_pop": False,
        "emoji": False,
        "uppercase": False,
        "shadow": False,
        "glow": False,
        "max_words_per_line": 5,
        "position_y": 0.80,
    },
}

# Ingest all 20 Canonical Presets into CAPTION_TEMPLATES
for _cid, _preset in CANONICAL_PRESETS.items():
    if _cid not in CAPTION_TEMPLATES:
        CAPTION_TEMPLATES[_cid] = {
            "id": _preset.id,
            "name": _preset.name,
            "category": _preset.category,
            "description": _preset.description,
            "font_family": _preset.font_family,
            "font_size": _preset.font_size,
            "font_weight": _preset.font_weight,
            "letter_spacing": _preset.letter_spacing,
            "line_height": _preset.line_height,
            "font_color": _preset.text_color,
            "highlight_color": _preset.active_word_color,
            "emphasis_color": _preset.emphasis_color,
            "stroke_color": _preset.outline_color if _preset.outline_enabled else None,
            "stroke_width": _preset.outline_width if _preset.outline_enabled else 0,
            "background": _preset.background,
            "background_color": _preset.background_color,
            "background_opacity": _preset.background_opacity,
            "word_box": _preset.word_box,
            "word_box_color": _preset.word_box_color,
            "word_box_radius": _preset.word_box_radius,
            "animation": _preset.animation,
            "word_pop": _preset.word_pop,
            "emoji": _preset.emoji,
            "uppercase": _preset.uppercase,
            "shadow": _preset.shadow_enabled,
            "shadow_blur": _preset.shadow_blur,
            "shadow_offset_y": _preset.shadow_offset_y,
            "glow": _preset.glow,
            "max_words_per_line": _preset.max_words_per_line,
            "max_lines": _preset.max_lines,
            "position": _preset.position,
            "position_y": _preset.position_y,
            "alignment": _preset.alignment,
        }

# Backward-compatibility aliases for existing UpClipStudio preset names
ALIASES: Dict[str, str] = {
    "hormozi_pop": "hormozi",
    "beast_glow": "mrbeast",
    "red_punch": "mrbeast",
    "clean_gold": "podcast",
    "neon_cyber": "neon",
    "karaoke_pill": "hormozi",
    "tiktok_pop": "tiktok",
    "tiktok-pop": "tiktok",
    "clean": "minimal",
    "bold": "hormozi",
    "creator": "default",
    "karaoke": "karaoke_clean",
    "cap_clean": "pure_white",
    "cap_bold": "punch_orange",
    "cap_minimal": "pure_white",
    "cap_creator": "modern_creator",
    "cap_podcast": "podcast_gold",
    "cap_news": "monochrome",
    "cap_gaming": "punch_orange",
    "cap_dynamic": "modern_creator",
    "cap_default": "default",
    "cap_hormozi": "hormozi",
    "cap_mrbeast": "mrbeast",
    "cap_tiktok": "tiktok",
    "cap_neon": "neon",
}

TEMPLATE_DEFAULTS: Dict[str, Any] = {
    "font_family": "Montserrat",
    "font_size": 34,
    "font_color": "#FFFFFF",
    "highlight_color": "#FFE000",
    "emphasis_color": None,
    "stroke_color": "#000000",
    "stroke_width": 3,
    "background": False,
    "background_color": None,
    "word_box": False,
    "word_box_color": None,
    "animation": "pop",
    "word_pop": True,
    "emoji": True,
    "uppercase": False,
    "shadow": True,
    "glow": False,
    "max_words_per_line": 4,
    "position_y": 0.80,
}


def get_template(template_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a caption template by name or alias.
    Defaults to 'default' if not found.
    """
    key = (template_name or "default").lower().strip()
    resolved_key = ALIASES.get(key, key)
    template = CAPTION_TEMPLATES.get(resolved_key, CAPTION_TEMPLATES["default"])

    merged = dict(TEMPLATE_DEFAULTS)
    merged.update(template)
    # Ensure aliases for legacy test compatibility
    if "font" not in merged and "font_family" in merged:
        merged["font"] = merged["font_family"]
    if "color" not in merged and "font_color" in merged:
        merged["color"] = merged["font_color"]
    if "size" not in merged and "font_size" in merged:
        merged["size"] = merged["font_size"]
    return merged


def get_all_templates() -> Dict[str, Dict[str, Any]]:
    """Get all 7 official production caption presets."""
    return CAPTION_TEMPLATES


def get_template_names() -> List[str]:
    """Get list of all primary template names."""
    return list(CAPTION_TEMPLATES.keys())


def get_template_info() -> List[Dict[str, Any]]:
    """Return template metadata for UI and REST APIs."""
    result = []
    for name, t in CAPTION_TEMPLATES.items():
        result.append({
            "id": name,
            "name": t.get("name", name.title()),
            "category": t.get("category", "Minimal & Luxury"),
            "description": t.get("description", ""),
            "animation": t.get("animation", "pop"),
            "font_family": t.get("font_family", "Montserrat"),
            "font_weight": t.get("font_weight", 700),
            "font_size": t.get("font_size", 34),
            "font_color": t.get("font_color", "#FFFFFF"),
            "highlight_color": t.get("highlight_color", "#FFE000"),
            "active_word_color": t.get("highlight_color", "#FFE000"),
            "emphasis_color": t.get("emphasis_color"),
            "word_box": t.get("word_box", False),
            "word_box_color": t.get("word_box_color"),
            "glow": t.get("glow", False),
            "emoji": t.get("emoji", True),
            "uppercase": t.get("uppercase", False),
            "position": t.get("position", "bottom"),
            "position_y": t.get("position_y", 0.80),
        })
    return result


def create_custom_template(
    name: str,
    base_template: str = "default",
    **custom_overrides
) -> Dict[str, Any]:
    """
    Create a new customized template based on an existing preset.
    """
    base = get_template(base_template)
    new_template = dict(base)
    new_template["id"] = f"custom_{re.sub(r'[^a-z0-9_]+', '', name.lower().replace(' ', '_'))}"
    new_template["name"] = name
    new_template.update(custom_overrides)
    return new_template


# ---------------------------------------------------------------------------
# ASS Color & Timestamp Helpers
# ---------------------------------------------------------------------------

def hex_to_ass_color(
    value: Optional[str], fallback: str = "#FFFFFF", include_alpha: bool = True
) -> str:
    """Convert hex (#RRGGBB or #RRGGBBAA) to ASS &HAABBGGRR& color string."""
    value = (value or fallback).strip().lstrip("#")
    alpha = 0
    if len(value) == 8:
        css_alpha = int(value[6:8], 16)
        alpha = 255 - css_alpha
        value = value[:6]
    if len(value) != 6:
        value = fallback.lstrip("#")[:6]
    red, green, blue = value[0:2], value[2:4], value[4:6]
    alpha_part = f"{alpha:02X}" if include_alpha else "00"
    return f"&H{alpha_part}{blue}{green}{red}&"


def ass_timestamp(seconds: float) -> str:
    """Format seconds into ASS dialogue timestamp (H:MM:SS.cc)."""
    seconds = max(0.0, float(seconds))
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds - (hours * 3600) - (minutes * 60)
    return f"{hours}:{minutes:02d}:{secs:05.2f}"


def escape_ass_text(value: str) -> str:
    """Escape ASS special syntax brackets and linebreaks."""
    return (
        str(value or "")
        .replace("\\", "\\\\")
        .replace("{", "\\{")
        .replace("}", "\\}")
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
    )


# ---------------------------------------------------------------------------
# Hook Title Banner Builder
# ---------------------------------------------------------------------------

def build_hook_title_ass(
    hook_title: str,
    template: Dict[str, Any],
    video_width: int = 1080,
    video_height: int = 1920,
    output_duration: float = 30.0,
    caption_font_px: int = 40,
) -> Tuple[str, List[str]]:
    """
    Build the ASS style line and dialogue event for a burned-in Hook Title.
    The headline sits in the top safe area (Alignment 8 / Top-Center),
    styled with the template's accent color for power words & numbers,
    and a subtle fade-in + scale entrance pop.
    """
    if not hook_title or not hook_title.strip():
        return "", []

    title_text = hook_title.strip()
    if template.get("uppercase"):
        title_text = title_text.upper()

    font_name = template.get("font_family") or "Montserrat"
    primary = hex_to_ass_color(template.get("font_color"), "#FFFFFF")
    highlight = hex_to_ass_color(
        template.get("emphasis_color") or template.get("highlight_color"), "#FFE000"
    )
    outline = hex_to_ass_color(template.get("stroke_color") or "#000000", "#000000")
    back_color = hex_to_ass_color(template.get("background_color"), "#00000080")

    # Headline is ~1.35x caption font size
    hook_px = min(84, max(36, int(round(caption_font_px * 1.35))))
    stroke_width = max(2, int(round(hook_px * 0.08)))
    margin_v = max(48, int(video_height * 0.08))  # 8% top margin

    style_line = (
        f"Style: Hook,{font_name},{hook_px},{primary},&H000000FF,{outline},{back_color},"
        f"1,0,0,0,100,100,0,0,1,{stroke_width},2,8,60,60,{margin_v},1"
    )

    # Highlight numbers and power words
    words = title_text.split()
    styled_words = []
    for word in words:
        norm = normalize_token(word)
        accented = norm in POWER_WORDS or any(c.isdigit() for c in norm)
        col = highlight if accented else primary
        styled_words.append(f"{{\\c{col}}}{escape_ass_text(word)}")

    headline_body = " ".join(styled_words)

    # Hook plays during first 3.5 to 4.5 seconds
    start_time = 0.10
    end_time = min(4.0, max(2.5, output_duration - 0.2))

    # Entrance animation: smooth fade in (160ms) and pop scale (92% -> 100%)
    entrance = r"{\fad(160,240)\fscx92\fscy92\t(0,160,\fscx100\fscy100)}"
    dialogue_line = (
        f"Dialogue: 1,{ass_timestamp(start_time)},{ass_timestamp(end_time)},Hook,,0,0,0,,"
        f"{entrance}{headline_body}"
    )

    return style_line, [dialogue_line]


# ---------------------------------------------------------------------------
# Point Label ASS Builder (for Recap / Series Workflow on-screen points)
# ---------------------------------------------------------------------------

POINT_LABEL_SECONDS = 3.0
POINT_LABEL_MIN_SECONDS = 1.0


def build_point_label_ass(
    labels: List[Dict[str, Any]],
    template: Dict[str, Any],
    video_width: int = 1080,
    video_height: int = 1920,
    output_duration: float = 30.0,
    caption_font_px: int = 40,
    position_y: Optional[float] = None,
    hook_end: float = 0.0,
) -> Tuple[str, List[str]]:
    """
    Build on-screen point label badges (e.g. 'POINT 1: THE HOOK', 'KEY TAKEAWAY')
    for Recap and Series workflows, sitting in the top safe zone on a dark pill backing.
    """
    if not labels:
        return "", []

    font_name = template.get("font_family") or "Montserrat"
    primary = hex_to_ass_color(template.get("font_color"), "#FFFFFF")
    highlight = hex_to_ass_color(
        template.get("emphasis_color") or template.get("highlight_color"), "#FFE000"
    )
    outline = hex_to_ass_color(template.get("stroke_color") or "#000000", "#000000")
    back_color = hex_to_ass_color(template.get("background_color"), "#00000080")

    base_px = min(60, max(28, int(round(caption_font_px * 0.85))))
    stroke_width = max(2, int(round(base_px * 0.08)))
    margin_v = max(40, int(video_height * 0.09))

    style_line = (
        f"Style: Point,{font_name},{base_px},{primary},&H000000FF,{outline},{back_color},"
        f"1,0,0,0,100,100,0,0,1,{stroke_width},2,8,50,50,{margin_v},1"
    )

    events: List[str] = []
    starts = [max(0.0, float(label.get("start", 0.0))) for label in labels]

    for position, label in enumerate(labels):
        raw = " ".join(str(label.get("text") or "").split())
        if not raw:
            continue
        text_val = raw.upper() if template.get("uppercase") else raw

        start = max(starts[position], hook_end)
        next_start = starts[position + 1] if position + 1 < len(starts) else output_duration
        duration_allocated = float(label.get("duration", POINT_LABEL_SECONDS))
        end = min(start + duration_allocated, output_duration, max(start + POINT_LABEL_MIN_SECONDS, next_start - 0.1))

        if end - start < POINT_LABEL_MIN_SECONDS:
            continue

        words = text_val.split()
        styled_words = []
        for word in words:
            norm = normalize_token(word)
            accented = norm in POWER_WORDS or any(c.isdigit() for c in norm)
            col = highlight if accented else primary
            styled_words.append(f"{{\\c{col}}}{escape_ass_text(word)}")

        body = " ".join(styled_words)
        entrance = r"{\fad(120,180)\fscx95\fscy95\t(0,120,\fscx100\fscy100)}"
        placement = f"\\pos({video_width // 2},{round(video_height * position_y)})" if position_y is not None else ""
        events.append(
            f"Dialogue: 1,{ass_timestamp(start)},{ass_timestamp(end)},Point,,0,0,0,,"
            f"{entrance}{placement}{body}"
        )

    return style_line, events

