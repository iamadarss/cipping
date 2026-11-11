"""
Migration system for UpClip Studio Caption Presets.
Maps legacy IDs and names from previous versions to canonical preset IDs
without breaking saved projects or existing user configurations.
"""

from typing import Dict, Any, Optional


LEGACY_ID_MAP: Dict[str, str] = {
    # 7 Original Creator Presets
    "default": "soft_highlight",
    "hormozi": "word_pill",
    "mrbeast": "focus_red",
    "minimal": "pure_white",
    "tiktok": "creator_pink",
    "neon": "podcast_teal",
    "podcast": "podcast_gold",

    # Aliases from original caption_templates.py
    "hormozi_pop": "word_pill",
    "beast_glow": "focus_red",
    "red_punch": "focus_red",
    "clean_gold": "podcast_gold",
    "neon_cyber": "podcast_teal",
    "karaoke_pill": "word_pill",
    "tiktok_pop": "creator_pink",
    "tiktok-pop": "creator_pink",
    "clean": "pure_white",
    "bold": "punch_orange",
    "creator": "modern_creator",

    # Aliases from preset_manager.py DEFAULT_PRESETS["captions"]
    "cap_clean": "pure_white",
    "cap_bold": "punch_orange",
    "cap_minimal": "pure_white",
    "cap_creator": "modern_creator",
    "cap_podcast": "podcast_gold",
    "cap_news": "monochrome",
    "cap_gaming": "punch_orange",
    "cap_dynamic": "modern_creator",
    "cap_default": "soft_highlight",
    "cap_hormozi": "word_pill",
    "cap_mrbeast": "focus_red",
    "cap_tiktok": "creator_pink",
    "cap_neon": "podcast_teal",

    # Editor.tsx / editorStore.ts legacy IDs
    "karaoke": "karaoke_clean",
}


def resolve_canonical_id(preset_id_or_name: Optional[str]) -> str:
    """
    Resolve any legacy identifier or name to a canonical preset ID.
    Defaults to 'pure_white' if unresolvable.
    """
    if not preset_id_or_name:
        return "pure_white"
    raw = str(preset_id_or_name).lower().strip().replace(" ", "_")
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
