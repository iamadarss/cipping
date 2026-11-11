"""
Caption Presets Package for UpClip Studio.
Exports canonical registry, schema, and defaults.
"""

from ai.caption_presets.schema import (
    CaptionPresetSchema,
    VALID_CATEGORIES,
    VALID_ANIMATIONS,
    VALID_POSITIONS,
    sanitize_color,
)
from ai.caption_presets.defaults import CANONICAL_PRESETS
from ai.caption_presets.migrations import (
    LEGACY_ID_MAP,
    resolve_canonical_id,
    migrate_legacy_style,
)
from ai.caption_presets.registry import (
    CaptionPresetRegistry,
    caption_registry,
    get_preset,
    list_presets,
)

__all__ = [
    "CaptionPresetSchema",
    "CaptionPresetRegistry",
    "caption_registry",
    "get_preset",
    "list_presets",
    "CANONICAL_PRESETS",
    "VALID_CATEGORIES",
    "VALID_ANIMATIONS",
    "VALID_POSITIONS",
    "sanitize_color",
    "LEGACY_ID_MAP",
    "resolve_canonical_id",
    "migrate_legacy_style",
]
