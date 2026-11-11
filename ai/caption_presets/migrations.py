"""
Migration system for UpClip Studio Caption Presets.
Maps legacy IDs and names from previous versions to canonical preset IDs
without breaking saved projects or existing user configurations.
"""

from typing import Dict, Any, Optional


LEGACY_ID_MAP: Dict[str, str] = {
    # 7 Original Creator Presets
    "default": "boxed",
    "hormozi": "bold_pop",
    "mrbeast": "beast",
    "minimal": "subtitle",
    "tiktok": "bold_pop",
    "neon": "neon",
    "podcast": "karaoke",

    # Previous 20 Presets -> New 19 Creator Benchmarks
    "pure_white": "boxed",
    "soft_highlight": "highlighter",
    "luxury_editorial": "magazine",
    "modern_creator": "soft_glass",
    "podcast_gold": "karaoke",
    "podcast_teal": "neon",
    "glass_caption": "soft_glass",
    "speaker_focus": "highlight",
    "karaoke_clean": "karaoke",
    "word_pill": "highlight",
    "punch_orange": "comic",
    "creator_pink": "sticker",
    "cinema_classic": "subtitle",
    "documentary": "paper",
    "editorial_gold": "magazine",
    "top_clean": "label",
    "fresh_green": "terminal",
    "lavender": "highlight",
    "focus_red": "comic",
    "monochrome": "label",

    # Aliases from original caption_templates.py
    "hormozi_pop": "bold_pop",
    "beast_glow": "beast",
    "red_punch": "comic",
    "clean_gold": "karaoke",
    "neon_cyber": "neon",
    "karaoke_pill": "highlight",
    "tiktok_pop": "bold_pop",
    "tiktok-pop": "bold_pop",
    "clean": "boxed",
    "bold": "bold_pop",
    "creator": "soft_glass",

    # Aliases from preset_manager.py DEFAULT_PRESETS["captions"]
    "cap_clean": "boxed",
    "cap_bold": "bold_pop",
    "cap_minimal": "subtitle",
    "cap_creator": "soft_glass",
    "cap_podcast": "karaoke",
    "cap_news": "label",
    "cap_gaming": "comic",
    "cap_dynamic": "bold_pop",
    "cap_default": "boxed",
    "cap_hormozi": "bold_pop",
    "cap_mrbeast": "beast",
    "cap_tiktok": "bold_pop",
    "cap_neon": "neon",

    # Alternate naming
    "3d_pop": "pop_3d",
    "three_d_pop": "pop_3d",
    "softglass": "soft_glass",
}


def resolve_canonical_id(preset_id_or_name: Optional[str]) -> str:
    """
    Resolve any legacy identifier or name to a canonical preset ID.
    Defaults to 'boxed' if unresolvable.
    """
    if not preset_id_or_name:
        return "boxed"
    raw = str(preset_id_or_name).lower().strip().replace(" ", "_").replace("-", "_")
    return LEGACY_ID_MAP.get(raw, raw)


def migrate_legacy_style(style_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inspect a saved project style dict and update deprecated keys to canonical format.
    """
    if not isinstance(style_dict, dict):
        return {}

    migrated = dict(style_dict)
    raw_id = migrated.get("id") or migrated.get("preset_id") or migrated.get("template")
    if raw_id:
        migrated["id"] = resolve_canonical_id(raw_id)

    # Normalize font family aliases
    font = migrated.get("font") or migrated.get("fontFamily")
    if font and "font_family" not in migrated:
        migrated["font_family"] = font

    # Normalize size
    size = migrated.get("size") or migrated.get("fontSize")
    if size and "font_size" not in migrated:
        migrated["font_size"] = size

    # Normalize color
    color = migrated.get("color") or migrated.get("textColor") or migrated.get("font_color")
    if color and "text_color" not in migrated:
        migrated["text_color"] = color

    # Normalize active word color
    active_col = migrated.get("activeWordColor") or migrated.get("highlight_color") or migrated.get("highlightColor")
    if active_col and "active_word_color" not in migrated:
        migrated["active_word_color"] = active_col

    return migrated

