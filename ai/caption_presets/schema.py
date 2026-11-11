"""
Canonical Schema for UpClip Studio Caption Engine Presets.
Provides strictly validated, normalized dataclass and helper methods
for 1080x1920 ASS export and React live preview.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
import re


VALID_CATEGORIES = {
    "Minimal & Luxury",
    "Podcast",
    "Kinetic",
    "Cinematic",
    "Special",
    "Custom",
}

VALID_ANIMATIONS = {
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
    # Legacy aliases
    "pop",
    "fade",
    "bounce",
    "slide",
    "zoom",
    "glow",
    "none",
}

VALID_POSITIONS = {
    "bottom",
    "lower_third",
    "center",
    "upper_center",
    "top",
}


def sanitize_color(val: Optional[str], default: str = "#FFFFFF") -> str:
    """Normalize hex colors to #RRGGBB or #RRGGBBAA."""
    if not val:
        return default
    s = str(val).strip()
    if not s.startswith("#"):
        s = f"#{s}"
    # Remove invalid hex characters
    clean = "#" + re.sub(r"[^0-9a-fA-F]", "", s[1:])
    if len(clean) in (4, 7, 9):
        return clean.upper()
    return default


@dataclass
class CaptionPresetSchema:
    id: str
    name: str
    category: str = "Minimal & Luxury"
    description: str = ""

    # Typography
    font_family: str = "Inter"
    font_weight: int = 700
    font_size: int = 36
    letter_spacing: float = 0.0
    line_height: float = 1.25
    text_case: str = "normal"  # normal, uppercase, lowercase, capitalize
    uppercase: bool = False

    # Colors
    text_color: str = "#FFFFFF"
    active_word_color: str = "#FFE000"
    emphasis_color: Optional[str] = None

    # Word Box / Pill backing
    word_box: bool = False
    word_box_color: Optional[str] = None
    word_box_radius: int = 6

    # Outline / Stroke
    outline_enabled: bool = False
    outline_color: str = "#000000"
    outline_width: float = 0.0

    # Shadow
    shadow_enabled: bool = True
    shadow_color: str = "#000000"
    shadow_blur: float = 1.5
    shadow_offset_y: float = 1.5

    # Background Block
    background: bool = False
    background_color: Optional[str] = None
    background_opacity: float = 0.0
    bg_mode: str = "none"  # none, semi, solid, glass

    # Animation
    animation: str = "color_karaoke"
    animation_duration: float = 0.20
    word_pop: bool = False
    glow: bool = False
    emoji: bool = False

    # Layout & Alignment
    position: str = "bottom"
    position_y: float = 0.80
    alignment: int = 2  # ASS 2 = Bottom-Center
    text_align: str = "center"
    max_words_per_line: int = 4
    max_lines: int = 2
    safe_zone_padding: int = 60

    # System vs Custom
    is_system: bool = True
    is_custom: bool = False
    favorite: bool = False

    def validate_and_normalize(self) -> CaptionPresetSchema:
        """Sanitize values and ensure constraints match the master design system."""
        self.id = re.sub(r"[^a-zA-Z0-9_\-]", "_", self.id.lower().strip())
        self.name = self.name.strip() or self.id.replace("_", " ").title()

        if self.category not in VALID_CATEGORIES:
            self.category = "Minimal & Luxury"

        # Font weight clamping
        self.font_weight = max(100, min(900, int(self.font_weight)))
        self.font_size = max(18, min(84, int(self.font_size)))
        self.letter_spacing = max(-2.0, min(10.0, float(self.letter_spacing)))
        self.line_height = max(0.8, min(2.0, float(self.line_height)))

        # Colors
        self.text_color = sanitize_color(self.text_color, "#FFFFFF")
        self.active_word_color = sanitize_color(self.active_word_color, "#FFE000")
        if self.emphasis_color:
            self.emphasis_color = sanitize_color(self.emphasis_color, self.active_word_color)
        if self.word_box_color:
            self.word_box_color = sanitize_color(self.word_box_color, "#4F46E5")
        if self.background_color:
            self.background_color = sanitize_color(self.background_color, "#000000")
        self.outline_color = sanitize_color(self.outline_color, "#000000")
        self.shadow_color = sanitize_color(self.shadow_color, "#000000")

        # Uppercase sync
        if self.uppercase:
            self.text_case = "uppercase"
        elif self.text_case == "uppercase":
            self.uppercase = True

        # Stroke / Outline clamping
        self.outline_width = max(0.0, min(10.0, float(self.outline_width)))
        if self.outline_width > 0:
            self.outline_enabled = True

        # Shadow clamping
        self.shadow_blur = max(0.0, min(20.0, float(self.shadow_blur)))
        self.shadow_offset_y = max(0.0, min(20.0, float(self.shadow_offset_y)))

        # Background opacity
        self.background_opacity = max(0.0, min(1.0, float(self.background_opacity)))
        if self.background_opacity > 0.05:
            self.background = True

        # Word box
        if self.word_box and not self.word_box_color:
            self.word_box_color = self.active_word_color

        # Animation normalization
        anim = self.animation.lower().replace("-", "_").strip()
        if anim not in VALID_ANIMATIONS:
            anim = "color_karaoke"
        self.animation = anim
        self.animation_duration = max(0.05, min(1.0, float(self.animation_duration)))

        # Layout & Alignment
        if self.position not in VALID_POSITIONS:
            self.position = "bottom"
        self.position_y = max(0.05, min(0.95, float(self.position_y)))
        self.max_words_per_line = max(1, min(10, int(self.max_words_per_line)))
        self.max_lines = max(1, min(4, int(self.max_lines)))

        return self

    def to_dict(self) -> Dict[str, Any]:
        """Return dict representation with both snake_case and camelCase for React compatibility."""
        d = asdict(self)
        # React camelCase projections
        d["fontFamily"] = self.font_family
        d["fontWeight"] = self.font_weight
        d["fontSize"] = self.font_size
        d["letterSpacing"] = self.letter_spacing
        d["lineHeight"] = self.line_height
        d["textColor"] = self.text_color
        d["activeWordColor"] = self.active_word_color
        d["emphasisColor"] = self.emphasis_color
        d["wordBox"] = self.word_box
        d["wordBoxColor"] = self.word_box_color
        d["wordBoxRadius"] = self.word_box_radius
        d["outlineEnabled"] = self.outline_enabled
        d["outlineColor"] = self.outline_color
        d["outlineWidth"] = self.outline_width
        d["shadowEnabled"] = self.shadow_enabled
        d["shadowColor"] = self.shadow_color
        d["shadowBlur"] = self.shadow_blur
        d["shadowOffsetY"] = self.shadow_offset_y
        d["backgroundColor"] = self.background_color
        d["backgroundOpacity"] = self.background_opacity
        d["bgMode"] = self.bg_mode
        d["animationDuration"] = self.animation_duration
        d["wordPop"] = self.word_pop
        d["maxWordsPerLine"] = self.max_words_per_line
        d["maxLines"] = self.max_lines
        d["safeZonePadding"] = self.safe_zone_padding
        d["isSystem"] = self.is_system
        d["isCustom"] = self.is_custom
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CaptionPresetSchema:
        """Create instance from arbitrary dict supporting snake_case or camelCase keys."""
        data = data or {}
        instance = cls(
            id=str(data.get("id", "custom_style")),
            name=str(data.get("name", "Custom Style")),
            category=str(data.get("category", "Custom")),
            description=str(data.get("description", "")),
            font_family=str(data.get("font_family") or data.get("fontFamily") or data.get("font") or "Inter"),
            font_weight=int(data.get("font_weight") or data.get("fontWeight") or 700),
            font_size=int(data.get("font_size") or data.get("fontSize") or data.get("size") or 36),
            letter_spacing=float(data.get("letter_spacing") or data.get("letterSpacing") or 0.0),
            line_height=float(data.get("line_height") or data.get("lineHeight") or 1.25),
            text_case=str(data.get("text_case") or data.get("textCase") or ("uppercase" if data.get("uppercase") else "normal")),
            uppercase=bool(data.get("uppercase", False)),
            text_color=str(data.get("text_color") or data.get("textColor") or data.get("color") or "#FFFFFF"),
            active_word_color=str(data.get("active_word_color") or data.get("activeWordColor") or data.get("highlight_color") or "#FFE000"),
            emphasis_color=data.get("emphasis_color") or data.get("emphasisColor"),
            word_box=bool(data.get("word_box") or data.get("wordBox", False)),
            word_box_color=data.get("word_box_color") or data.get("wordBoxColor"),
            word_box_radius=int(data.get("word_box_radius") or data.get("wordBoxRadius") or 6),
            outline_enabled=bool(data.get("outline_enabled") or data.get("outlineEnabled") or (float(data.get("outline_width", 0) or data.get("outlineWidth", 0)) > 0)),
            outline_color=str(data.get("outline_color") or data.get("outlineColor") or data.get("stroke_color") or "#000000"),
            outline_width=float(data.get("outline_width") or data.get("outlineWidth") or data.get("stroke_width") or 0.0),
            shadow_enabled=bool(data.get("shadow_enabled") if "shadow_enabled" in data else data.get("shadowEnabled", True)),
            shadow_color=str(data.get("shadow_color") or data.get("shadowColor") or "#000000"),
            shadow_blur=float(data.get("shadow_blur") or data.get("shadowBlur") or 1.5),
            shadow_offset_y=float(data.get("shadow_offset_y") or data.get("shadowOffsetY") or 1.5),
            background=bool(data.get("background", False)),
            background_color=data.get("background_color") or data.get("backgroundColor"),
            background_opacity=float(data.get("background_opacity") or data.get("backgroundOpacity") or 0.0),
            bg_mode=str(data.get("bg_mode") or data.get("bgMode") or "none"),
            animation=str(data.get("animation", "color_karaoke")),
            animation_duration=float(data.get("animation_duration") or data.get("animationDuration") or data.get("animationSpeed", 0.20)),
            word_pop=bool(data.get("word_pop") or data.get("wordPop", False)),
            glow=bool(data.get("glow", False)),
            emoji=bool(data.get("emoji", False)),
            position=str(data.get("position", "bottom")),
            position_y=float(data.get("position_y") or data.get("positionY") or 0.80),
            alignment=int(data.get("alignment", 2)),
            text_align=str(data.get("text_align") or data.get("textAlign") or "center"),
            max_words_per_line=int(data.get("max_words_per_line") or data.get("maxWordsPerLine") or data.get("words_per_chunk") or 4),
            max_lines=int(data.get("max_lines") or data.get("maxLines") or 2),
            safe_zone_padding=int(data.get("safe_zone_padding") or data.get("safeZonePadding") or 60),
            is_system=bool(data.get("is_system", data.get("isSystem", False))),
            is_custom=bool(data.get("is_custom", data.get("isCustom", True))),
            favorite=bool(data.get("favorite", False)),
        )
        return instance.validate_and_normalize()
