"""
Centralized Caption Preset Registry for UpClip Studio.
Acts as the single source of truth for all built-in and user-custom caption styles.
"""

from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

import config
from ai.caption_presets.schema import CaptionPresetSchema, VALID_CATEGORIES
from ai.caption_presets.defaults import CANONICAL_PRESETS
from ai.caption_presets.migrations import resolve_canonical_id, migrate_legacy_style


class CaptionPresetRegistry:
    """Singleton registry managing canonical system presets and user custom presets."""

    def __init__(self, storage_file: Optional[Path] = None):
        self.storage_file = storage_file or (config.DATA_DIR / "custom_caption_presets.json")
        self._system_presets: Dict[str, CaptionPresetSchema] = dict(CANONICAL_PRESETS)
        self._custom_presets: Dict[str, CaptionPresetSchema] = {}
        self._load_custom_presets()

    def _load_custom_presets(self) -> None:
        """Load user-defined custom presets from JSON disk storage."""
        if not self.storage_file.exists():
            return
        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                raw_list = json.load(f)
            if isinstance(raw_list, list):
                for item in raw_list:
                    if isinstance(item, dict):
                        # Some legacy entries might have nested "style"
                        if "style" in item and isinstance(item["style"], dict):
                            merged = dict(item["style"])
                            merged["id"] = item.get("id", merged.get("id"))
                            merged["name"] = item.get("name", merged.get("name"))
                            merged["category"] = "Custom"
                        else:
                            merged = dict(item)
                        preset = CaptionPresetSchema.from_dict(merged)
                        preset.is_system = False
                        preset.is_custom = True
                        preset.category = "Custom"
                        self._custom_presets[preset.id] = preset
        except Exception:
            pass

    def _persist_custom_presets(self) -> None:
        """Save custom presets to JSON disk storage."""
        try:
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)
            serializable = [preset.to_dict() for preset in self._custom_presets.values()]
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(serializable, f, indent=2)
        except Exception:
            pass

    def get_preset(self, preset_id: Optional[str]) -> CaptionPresetSchema:
        """
        Retrieve preset by ID or legacy alias.
        Falls back to 'boxed' if not found.
        """
        if not preset_id:
            return self._system_presets.get("boxed") or list(self._system_presets.values())[0]

        canonical_id = resolve_canonical_id(preset_id)

        # Check custom presets first
        if canonical_id in self._custom_presets:
            return self._custom_presets[canonical_id]
        if preset_id in self._custom_presets:
            return self._custom_presets[preset_id]

        # Check system presets
        if canonical_id in self._system_presets:
            return self._system_presets[canonical_id]
        if preset_id in self._system_presets:
            return self._system_presets[preset_id]

        # Fallback default
        return self._system_presets.get("boxed") or list(self._system_presets.values())[0]

    def list_presets(self, category: Optional[str] = None) -> List[CaptionPresetSchema]:
        """Return all system and custom presets, optionally filtered by category."""
        all_presets = list(self._system_presets.values()) + list(self._custom_presets.values())
        if not category or category.lower() in ("all", "any"):
            return all_presets
        cat_lower = category.lower().strip()
        return [p for p in all_presets if p.category.lower() == cat_lower]

    def list_presets_dict(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return dict representations with camelCase & snake_case for frontend consumption."""
        return [p.to_dict() for p in self.list_presets(category)]

    def get_categories(self) -> List[str]:
        """Return list of distinct categories in display order."""
        return [
            "Cinematic Master",
            "Card & Aesthetic",
            "Loud Captions",
            "Custom",
        ]

    def save_custom_preset(self, data: Dict[str, Any]) -> CaptionPresetSchema:
        """
        Validate and save a user-created or edited preset.
        Persists to custom_caption_presets.json.
        """
        style_data = dict(data)
        if "style" in data and isinstance(data["style"], dict):
            style_data = dict(data["style"])
            if "name" in data and not style_data.get("name"):
                style_data["name"] = data["name"]
            if "id" in data and not style_data.get("id"):
                style_data["id"] = data["id"]

        clean_id = style_data.get("id") or f"custom_{int(time.time() * 1000)}"
        style_data["id"] = clean_id
        style_data["is_system"] = False
        style_data["is_custom"] = True
        style_data["category"] = "Custom"

        preset = CaptionPresetSchema.from_dict(style_data)
        self._custom_presets[preset.id] = preset
        self._persist_custom_presets()
        return preset

    def delete_custom_preset(self, preset_id: str) -> bool:
        """Delete custom preset by ID. Cannot delete system presets."""
        canonical_id = resolve_canonical_id(preset_id)
        if canonical_id in self._custom_presets:
            del self._custom_presets[canonical_id]
            self._persist_custom_presets()
            return True
        if preset_id in self._custom_presets:
            del self._custom_presets[preset_id]
            self._persist_custom_presets()
            return True
        return False

    def reset_preset(self, preset_id: str) -> Optional[CaptionPresetSchema]:
        """
        If a custom preset overrode a system preset ID, delete it and return system default.
        """
        canonical_id = resolve_canonical_id(preset_id)
        if canonical_id in self._custom_presets:
            del self._custom_presets[canonical_id]
            self._persist_custom_presets()
        return self._system_presets.get(canonical_id)

    def duplicate_preset(self, preset_id: str, new_name: Optional[str] = None) -> CaptionPresetSchema:
        """Clone an existing preset as a new custom preset."""
        source = self.get_preset(preset_id)
        cloned_data = source.to_dict()
        cloned_data["id"] = f"custom_copy_{int(time.time() * 1000)}"
        cloned_data["name"] = new_name or f"{source.name} (Copy)"
        cloned_data["category"] = "Custom"
        cloned_data["is_system"] = False
        cloned_data["is_custom"] = True
        return self.save_custom_preset(cloned_data)


# Global singleton instance
caption_registry = CaptionPresetRegistry()


def get_preset(preset_id: Optional[str] = None) -> CaptionPresetSchema:
    """Convenience accessor for registry preset."""
    return caption_registry.get_preset(preset_id)


def list_presets(category: Optional[str] = None) -> List[CaptionPresetSchema]:
    """Convenience accessor for preset list."""
    return caption_registry.list_presets(category)

