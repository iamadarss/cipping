"""
UpClip Studio — Premium Template Engine V1.0
Centralized configuration, validation, layout compositing, and rendering engine
for production-quality video templates.

Supports the 5 Initial Master Templates:
1. Clean Creator (clean_creator)
2. Black Editorial (black_editorial)
3. Bold Podcast (bold_podcast)
4. DualCast Host + Guest (dualcast_interview)
5. Cinematic Podcast Gold (cinematic_gold)
"""

from __future__ import annotations

import copy
import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import config

logger = logging.getLogger(__name__)

# Constants
ASPECT_9_16 = "9:16"
ASPECT_16_9 = "16:9"
ASPECT_1_1 = "1:1"

DUALCAST_LAYOUTS = [
    "HOST_TOP_GUEST_BOTTOM",
    "GUEST_TOP_HOST_BOTTOM",
    "SIDE_BY_SIDE",
    "ACTIVE_SPEAKER_FOCUS",
]

ANIMATION_TYPES = [
    "karaoke_highlight",
    "pop",
    "bounce",
    "fade",
    "slide_up",
    "slide_down",
    "typewriter",
    "line_by_line",
]

CATEGORIES = [
    "All",
    "Podcast",
    "Creator",
    "Motivation",
    "Educational",
    "Cinematic",
]


@dataclass
class VideoLayoutConfig:
    mode: str = "centered_framed"  # centered_framed | full_crop | dual_split | framed_black | cinematic_crop
    aspect_ratio: str = ASPECT_9_16
    frame_radius: int = 16
    border_width: int = 0
    border_color: str = "#FFFFFF"
    background_color: str = "#0F172A"
    blur_background: bool = True
    blur_sigma: int = 20
    crop_x: Optional[int] = None
    crop_y: Optional[int] = None
    scale: float = 1.0
    safe_inset_percent: int = 4

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CaptionStyleConfig:
    enabled: bool = True
    font_family: str = "Inter"
    font_size: int = 34
    font_weight: int = 800
    text_color: str = "#FFFFFF"
    active_word_color: str = "#FBBF24"
    stroke_color: str = "#000000"
    stroke_width: int = 3
    shadow_color: str = "#000000"
    shadow_blur: int = 4
    shadow_offset_y: int = 2
    background: bool = False
    background_color: str = "#000000"
    background_opacity: float = 0.0
    background_radius: int = 8
    position_y: float = 0.78  # 0.0 to 1.0 (vertical alignment ratio)
    alignment: int = 2  # ASS alignment: 2 = Bottom-Center, 5 = Center-Center
    max_words_per_line: int = 3
    line_spacing: int = 6
    uppercase: bool = False
    animation: str = "karaoke_highlight"  # pop, bounce, fade, slide_up, typewriter, line_by_line, karaoke_highlight
    glow: bool = False
    glow_color: str = "#38BDF8"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VisualEffectsConfig:
    color_grading: str = "none"  # none | warm_gold | cinematic_contrast | dark_editorial | clean_vivid
    brightness: float = 0.0  # -0.5 to 0.5
    contrast: float = 1.0  # 0.5 to 1.5
    saturation: float = 1.0  # 0.5 to 1.5
    warmth: float = 0.0  # -0.3 to 0.3
    film_grain: bool = False
    film_grain_intensity: float = 0.08
    subtle_zoom: bool = False
    subtle_zoom_rate: float = 0.04

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BrandingConfig:
    creator_name: str = ""
    watermark_enabled: bool = False
    watermark_text: str = ""
    watermark_position: str = "top_right"  # top_right | top_left | bottom_right | bottom_left
    logo_path: str = ""
    speaker_labels: Dict[str, str] = field(default_factory=lambda: {"host": "Host", "guest": "Guest"})
    accent_line_enabled: bool = False
    accent_line_color: str = "#EF4444"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TemplateConfig:
    id: str
    name: str
    version: str = "1.0"
    category: str = "Creator"  # Podcast | Creator | Motivation | Educational | Cinematic
    description: str = ""
    thumbnail_url: str = ""
    preview_video_url: str = ""
    aspect_ratio: str = ASPECT_9_16
    video_layout: VideoLayoutConfig = field(default_factory=VideoLayoutConfig)
    dualcast_layout: str = "HOST_TOP_GUEST_BOTTOM"
    caption_config: CaptionStyleConfig = field(default_factory=CaptionStyleConfig)
    caption_animation: str = "karaoke_highlight"
    visual_effects: VisualEffectsConfig = field(default_factory=VisualEffectsConfig)
    branding: BrandingConfig = field(default_factory=BrandingConfig)
    export_defaults: Dict[str, Any] = field(
        default_factory=lambda: {
            "width": 1080,
            "height": 1920,
            "fps": 30,
            "codec": "libx264",
            "crf": 21,
            "preset": "veryfast",
            "audio_codec": "aac",
            "audio_bitrate": "192k",
        }
    )
    is_system: bool = True
    favorite: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "category": self.category,
            "description": self.description,
            "thumbnail_url": self.thumbnail_url,
            "preview_video_url": self.preview_video_url,
            "aspect_ratio": self.aspect_ratio,
            "aspectRatio": self.aspect_ratio,
            "dualcast_layout": self.dualcast_layout,
            "caption_animation": self.caption_animation,
            "is_system": self.is_system,
            "isSystem": self.is_system,
            "favorite": self.favorite,
            "video_layout": self.video_layout.to_dict() if hasattr(self.video_layout, "to_dict") else self.video_layout,
            "caption_config": self.caption_config.to_dict() if hasattr(self.caption_config, "to_dict") else self.caption_config,
            "visual_effects": self.visual_effects.to_dict() if hasattr(self.visual_effects, "to_dict") else self.visual_effects,
            "branding": self.branding.to_dict() if hasattr(self.branding, "to_dict") else self.branding,
            "export_defaults": self.export_defaults,
            # Backward-compatibility alias for editor preset manager
            "data": {
                "aspectRatio": self.aspect_ratio,
                "captionStyle": {
                    "fontFamily": self.caption_config.font_family,
                    "fontSize": self.caption_config.font_size,
                    "fontWeight": self.caption_config.font_weight,
                    "textColor": self.caption_config.text_color,
                    "activeWordColor": self.caption_config.active_word_color,
                    "backgroundColor": self.caption_config.background_color,
                    "backgroundOpacity": self.caption_config.background_opacity,
                    "outlineColor": self.caption_config.stroke_color,
                    "outlineWidth": self.caption_config.stroke_width,
                    "shadowColor": self.caption_config.shadow_color,
                    "shadowBlur": self.caption_config.shadow_blur,
                    "position": "bottom" if self.caption_config.position_y > 0.6 else "middle",
                    "animation": self.caption_animation,
                    "uppercase": self.caption_config.uppercase,
                },
                "branding": self.branding.to_dict() if hasattr(self.branding, "to_dict") else self.branding,
                "graphics": [],
                "audioTracks": [
                    {"id": "track_video_audio", "type": "video_audio", "name": "Video Audio", "volume": 100, "muted": False, "solo": False},
                    {"id": "track_music", "type": "music", "name": "Music", "volume": 60, "muted": False, "solo": False, "ducking": {"enabled": True, "amount": 60}},
                ],
            },
        }
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TemplateConfig:
        data = copy.deepcopy(data)
        v_layout_data = data.get("video_layout", {})
        if isinstance(v_layout_data, dict):
            v_layout = VideoLayoutConfig(**{k: v for k, v in v_layout_data.items() if k in VideoLayoutConfig.__annotations__})
        else:
            v_layout = VideoLayoutConfig()

        cap_data = data.get("caption_config", {})
        if isinstance(cap_data, dict):
            cap_config = CaptionStyleConfig(**{k: v for k, v in cap_data.items() if k in CaptionStyleConfig.__annotations__})
        else:
            cap_config = CaptionStyleConfig()

        vfx_data = data.get("visual_effects", {})
        if isinstance(vfx_data, dict):
            vfx = VisualEffectsConfig(**{k: v for k, v in vfx_data.items() if k in VisualEffectsConfig.__annotations__})
        else:
            vfx = VisualEffectsConfig()

        branding_data = data.get("branding", {})
        if isinstance(branding_data, dict):
            branding = BrandingConfig(**{k: v for k, v in branding_data.items() if k in BrandingConfig.__annotations__})
        else:
            branding = BrandingConfig()

        return cls(
            id=data["id"],
            name=data["name"],
            version=data.get("version", "1.0"),
            category=data.get("category", "Creator"),
            description=data.get("description", ""),
            thumbnail_url=data.get("thumbnail_url", ""),
            preview_video_url=data.get("preview_video_url", ""),
            aspect_ratio=data.get("aspect_ratio") or data.get("aspectRatio", ASPECT_9_16),
            video_layout=v_layout,
            dualcast_layout=data.get("dualcast_layout", "HOST_TOP_GUEST_BOTTOM"),
            caption_config=cap_config,
            caption_animation=data.get("caption_animation", "karaoke_highlight"),
            visual_effects=vfx,
            branding=branding,
            export_defaults=data.get("export_defaults", {
                "width": 1080, "height": 1920, "fps": 30, "codec": "libx264", "crf": 21, "preset": "veryfast"
            }),
            is_system=data.get("is_system", True),
            favorite=data.get("favorite", False),
        )


# =============================================================================
# INITIAL 5 PRODUCTION MASTER TEMPLATES
# =============================================================================

TEMPLATE_CLEAN_CREATOR = TemplateConfig(
    id="clean_creator",
    name="Clean Creator",
    version="1.0",
    category="Creator",
    description="Minimalist creator aesthetic with centered rounded frame, clean contrast, rounded black subtitle background & ice blue word-by-word karaoke.",
    thumbnail_url="/static/img/templates/clean_creator.svg",
    preview_video_url="/static/previews/clean_creator_preview.mp4",
    aspect_ratio=ASPECT_9_16,
    video_layout=VideoLayoutConfig(
        mode="centered_framed",
        aspect_ratio=ASPECT_9_16,
        frame_radius=20,
        border_width=2,
        border_color="#FFFFFF",
        background_color="#0F172A",
        blur_background=True,
        blur_sigma=24,
        scale=0.92,
        safe_inset_percent=4,
    ),
    caption_config=CaptionStyleConfig(
        enabled=True,
        font_family="Inter",
        font_size=36,
        font_weight=800,
        text_color="#FFFFFF",
        active_word_color="#38BDF8",  # Ice Blue accent
        stroke_color="#000000",
        stroke_width=2,
        shadow_color="#000000",
        shadow_blur=4,
        background=True,
        background_color="#000000",
        background_opacity=0.75,
        background_radius=8,
        position_y=0.78,
        max_words_per_line=3,
        uppercase=False,
        animation="karaoke_highlight",
        glow=False,
    ),
    caption_animation="karaoke_highlight",
    visual_effects=VisualEffectsConfig(
        color_grading="clean_vivid",
        brightness=0.02,
        contrast=1.05,
        saturation=1.08,
        warmth=0.0,
        film_grain=False,
        subtle_zoom=False,
    ),
    branding=BrandingConfig(
        creator_name="Creator Studio",
        watermark_enabled=True,
        watermark_text="@creator",
        watermark_position="top_right",
        accent_line_enabled=False,
    ),
    favorite=True,
)

TEMPLATE_BLACK_EDITORIAL = TemplateConfig(
    id="black_editorial",
    name="Black Editorial",
    version="1.0",
    category="Cinematic",
    description="Pitch-black luxury editorial canvas with serif typography, centered framed video window, subtle red accent line, and elegant line-by-line fade.",
    thumbnail_url="/static/img/templates/black_editorial.svg",
    preview_video_url="/static/previews/black_editorial_preview.mp4",
    aspect_ratio=ASPECT_9_16,
    video_layout=VideoLayoutConfig(
        mode="framed_black",
        aspect_ratio=ASPECT_9_16,
        frame_radius=12,
        border_width=1,
        border_color="#27272A",
        background_color="#050505",  # Deep pitch black canvas
        blur_background=False,
        scale=0.88,
        safe_inset_percent=6,
    ),
    caption_config=CaptionStyleConfig(
        enabled=True,
        font_family="Georgia",
        font_size=32,
        font_weight=700,
        text_color="#F8FAFC",
        active_word_color="#EF4444",  # Editorial Red keyword highlight
        stroke_color="#000000",
        stroke_width=1,
        shadow_color="#000000",
        shadow_blur=3,
        background=False,
        background_color="#000000",
        background_opacity=0.0,
        position_y=0.80,
        max_words_per_line=4,
        uppercase=False,
        animation="fade",  # Smooth line-by-line fade and slide
    ),
    caption_animation="fade",
    visual_effects=VisualEffectsConfig(
        color_grading="dark_editorial",
        brightness=-0.02,
        contrast=1.12,
        saturation=0.94,
        warmth=-0.05,
        film_grain=True,
        film_grain_intensity=0.05,
        subtle_zoom=False,
    ),
    branding=BrandingConfig(
        creator_name="Editorial Review",
        watermark_enabled=True,
        watermark_text="EDITORIAL",
        watermark_position="top_left",
        accent_line_enabled=True,
        accent_line_color="#EF4444",
    ),
    favorite=True,
)

TEMPLATE_BOLD_PODCAST = TemplateConfig(
    id="bold_podcast",
    name="Bold Podcast",
    version="1.0",
    category="Podcast",
    description="High-energy speaker-focused viral shorts with bold typography, electric yellow pop karaoke, heavy outline, and speaker-centered framing.",
    thumbnail_url="/static/img/templates/bold_podcast.svg",
    preview_video_url="/static/previews/bold_podcast_preview.mp4",
    aspect_ratio=ASPECT_9_16,
    video_layout=VideoLayoutConfig(
        mode="speaker_crop",
        aspect_ratio=ASPECT_9_16,
        frame_radius=0,
        border_width=0,
        blur_background=False,
        scale=1.0,
    ),
    caption_config=CaptionStyleConfig(
        enabled=True,
        font_family="Montserrat",
        font_size=40,
        font_weight=900,
        text_color="#FFFFFF",
        active_word_color="#FBBF24",  # High-energy electric yellow
        stroke_color="#000000",
        stroke_width=5,
        shadow_color="#000000",
        shadow_blur=6,
        background=False,
        background_color="#000000",
        background_opacity=0.0,
        position_y=0.74,
        max_words_per_line=3,
        uppercase=True,
        animation="pop",
    ),
    caption_animation="pop",
    visual_effects=VisualEffectsConfig(
        color_grading="cinematic_contrast",
        brightness=0.0,
        contrast=1.15,
        saturation=1.12,
        warmth=0.02,
        film_grain=False,
        subtle_zoom=True,
        subtle_zoom_rate=0.03,
    ),
    branding=BrandingConfig(
        creator_name="Podcast Clips",
        watermark_enabled=False,
        watermark_text="@podcast",
        watermark_position="top_right",
        accent_line_enabled=False,
    ),
    favorite=True,
)

TEMPLATE_DUALCAST_INTERVIEW = TemplateConfig(
    id="dualcast_interview",
    name="DualCast Host + Guest",
    version="1.0",
    category="Podcast",
    description="Balanced vertical 9:16 split-screen layout for 2-person interviews with host & guest panels, middle-seam subtitles, and 4 layout configurations.",
    thumbnail_url="/static/img/templates/dualcast_interview.svg",
    preview_video_url="/static/previews/dualcast_interview_preview.mp4",
    aspect_ratio=ASPECT_9_16,
    video_layout=VideoLayoutConfig(
        mode="dualcast_split",
        aspect_ratio=ASPECT_9_16,
        frame_radius=8,
        border_width=2,
        border_color="#334155",
        background_color="#090D16",
        blur_background=True,
        scale=1.0,
    ),
    dualcast_layout="HOST_TOP_GUEST_BOTTOM",
    caption_config=CaptionStyleConfig(
        enabled=True,
        font_family="Inter",
        font_size=32,
        font_weight=800,
        text_color="#FFFFFF",
        active_word_color="#38BDF8",  # Cyan for host, yellow for guest
        stroke_color="#000000",
        stroke_width=3,
        shadow_color="#000000",
        shadow_blur=4,
        background=True,
        background_color="#0F172A",
        background_opacity=0.85,
        background_radius=6,
        position_y=0.50,  # Perfectly centered in the natural seam between panels!
        max_words_per_line=4,
        uppercase=False,
        animation="karaoke_highlight",
    ),
    caption_animation="karaoke_highlight",
    visual_effects=VisualEffectsConfig(
        color_grading="clean_vivid",
        brightness=0.0,
        contrast=1.06,
        saturation=1.05,
        warmth=0.0,
        film_grain=False,
        subtle_zoom=False,
    ),
    branding=BrandingConfig(
        creator_name="The Conversation",
        watermark_enabled=True,
        watermark_text="DUALCAST",
        watermark_position="top_right",
        speaker_labels={"host": "HOST", "guest": "GUEST"},
        accent_line_enabled=True,
        accent_line_color="#38BDF8",
    ),
    favorite=True,
)

TEMPLATE_CINEMATIC_GOLD = TemplateConfig(
    id="cinematic_gold",
    name="Cinematic Podcast Gold",
    version="1.0",
    category="Cinematic",
    description="Warm cinematic golden tones, subtle film grain, full-frame speaker composition, and luxurious gold karaoke subtitles.",
    thumbnail_url="/static/img/templates/cinematic_gold.svg",
    preview_video_url="/static/previews/cinematic_gold_preview.mp4",
    aspect_ratio=ASPECT_9_16,
    video_layout=VideoLayoutConfig(
        mode="cinematic_crop",
        aspect_ratio=ASPECT_9_16,
        frame_radius=0,
        border_width=0,
        blur_background=False,
        scale=1.0,
    ),
    caption_config=CaptionStyleConfig(
        enabled=True,
        font_family="Montserrat",
        font_size=38,
        font_weight=800,
        text_color="#FFFFFF",
        active_word_color="#F59E0B",  # Warm Amber Gold
        stroke_color="#18181B",
        stroke_width=4,
        shadow_color="#000000",
        shadow_blur=6,
        background=False,
        background_color="#000000",
        background_opacity=0.0,
        position_y=0.82,
        max_words_per_line=3,
        uppercase=True,
        animation="pop",
        glow=True,
        glow_color="#F59E0B",
    ),
    caption_animation="pop",
    visual_effects=VisualEffectsConfig(
        color_grading="warm_gold",
        brightness=0.02,
        contrast=1.08,
        saturation=1.12,
        warmth=0.15,
        film_grain=True,
        film_grain_intensity=0.06,
        subtle_zoom=True,
        subtle_zoom_rate=0.02,
    ),
    branding=BrandingConfig(
        creator_name="Masterclass",
        watermark_enabled=True,
        watermark_text="GOLD EDITION",
        watermark_position="top_right",
        accent_line_enabled=False,
    ),
    favorite=True,
)

PREMIUM_TEMPLATES: Dict[str, TemplateConfig] = {
    TEMPLATE_CLEAN_CREATOR.id: TEMPLATE_CLEAN_CREATOR,
    TEMPLATE_BLACK_EDITORIAL.id: TEMPLATE_BLACK_EDITORIAL,
    TEMPLATE_BOLD_PODCAST.id: TEMPLATE_BOLD_PODCAST,
    TEMPLATE_DUALCAST_INTERVIEW.id: TEMPLATE_DUALCAST_INTERVIEW,
    TEMPLATE_CINEMATIC_GOLD.id: TEMPLATE_CINEMATIC_GOLD,
}


class TemplateEngine:
    """Central registry and rendering planner for UpClip Studio Premium Templates."""

    def __init__(self):
        self._templates: Dict[str, TemplateConfig] = copy.deepcopy(PREMIUM_TEMPLATES)
        self._init_custom_templates()

    def _init_custom_templates(self):
        """Load any user-saved custom template configs from disk."""
        custom_file = config.ROOT_DIR / "data" / "premium_custom_templates.json"
        if custom_file.exists():
            try:
                with open(custom_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        if isinstance(item, dict) and "id" in item:
                            self._templates[item["id"]] = TemplateConfig.from_dict(item)
            except Exception as e:
                logger.warning(f"Could not load custom premium templates: {e}")

    def get_all_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return serialized list of all templates, optionally filtered by category."""
        templates = list(self._templates.values())
        if category and category.lower() != "all":
            templates = [t for t in templates if t.category.lower() == category.lower()]
        return [t.to_dict() for t in templates]

    def get_template(self, template_id: str) -> Optional[TemplateConfig]:
        """Look up a template by ID with safe fallback."""
        if not template_id:
            return self._templates.get("clean_creator")
        clean_id = template_id.strip()
        return self._templates.get(clean_id)

    def validate_template_config(self, cfg_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate template configuration object."""
        errors: List[str] = []
        if not isinstance(cfg_data, dict):
            return False, ["Configuration must be a JSON object"]

        if not cfg_data.get("id"):
            errors.append("Template 'id' is required")
        if not cfg_data.get("name"):
            errors.append("Template 'name' is required")

        aspect = cfg_data.get("aspect_ratio") or cfg_data.get("aspectRatio", "9:16")
        if aspect not in [ASPECT_9_16, ASPECT_16_9, ASPECT_1_1]:
            errors.append(f"Invalid aspect ratio '{aspect}'. Must be 9:16, 16:9, or 1:1.")

        dual_layout = cfg_data.get("dualcast_layout")
        if dual_layout and dual_layout not in DUALCAST_LAYOUTS:
            errors.append(f"Invalid dualcast_layout '{dual_layout}'. Must be one of {DUALCAST_LAYOUTS}")

        anim = cfg_data.get("caption_animation")
        if anim and anim not in ANIMATION_TYPES:
            # Not fatal, but warn
            pass

        return len(errors) == 0, errors

    def save_custom_template(self, template_data: Dict[str, Any]) -> Tuple[bool, Optional[TemplateConfig], List[str]]:
        """Validate and persist a custom template."""
        valid, errors = self.validate_template_config(template_data)
        if not valid:
            return False, None, errors

        t = TemplateConfig.from_dict(template_data)
        t.is_system = False
        self._templates[t.id] = t

        custom_file = config.ROOT_DIR / "data" / "premium_custom_templates.json"
        custom_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            custom_list = [tmpl.to_dict() for tmpl in self._templates.values() if not tmpl.is_system]
            with open(custom_file, "w", encoding="utf-8") as f:
                json.dump(custom_list, f, indent=2)
            return True, t, []
        except Exception as e:
            return False, None, [f"Failed to persist custom template: {e}"]

    # =========================================================================
    # FFMPEG FILTERGRAPH GENERATION
    # =========================================================================

    def build_video_filtergraph(
        self,
        template: TemplateConfig,
        source_w: int,
        source_h: int,
        target_w: int = 1080,
        target_h: int = 1920,
        is_dual_source: bool = False,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate the exact FFmpeg video filtergraph chain to realize the template's
        framing, aspect ratio, blur padding, color grading, and branding overlay.
        """
        mode = template.video_layout.mode
        vfx = template.visual_effects
        brand = template.branding

        filters: List[str] = []

        # 1. Base Video Framing & Layout
        if mode == "dualcast_split":
            # Template 04: DualCast Host + Guest
            layout_style = template.dualcast_layout
            fg = self._build_dualcast_filtergraph(
                source_w, source_h, target_w, target_h, layout_style, is_dual_source
            )
            return fg, {"target_w": target_w, "target_h": target_h}

        elif mode == "centered_framed":
            # Template 01: Clean Creator (Centered rounded frame over blurred or solid canvas)
            scale_factor = template.video_layout.scale or 0.92
            fg_w = int(round((target_w * scale_factor) / 2) * 2)
            fg_h = int(round((target_h * scale_factor) / 2) * 2)
            pad_x = (target_w - fg_w) // 2
            pad_y = (target_h - fg_h) // 2

            filter_str = (
                f"[0:v]split=2[bgsrc][fgsrc];"
                f"[bgsrc]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,"
                f"crop={target_w}:{target_h},gblur=sigma=22:steps=2,setsar=1[bg];"
                f"[fgsrc]scale={fg_w}:{fg_h}:force_original_aspect_ratio=decrease,"
                f"pad={fg_w}:{fg_h}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1[fg];"
                f"[bg][fg]overlay={pad_x}:{pad_y}[vframed]"
            )
            last_tag = "[vframed]"

        elif mode == "framed_black":
            # Template 02: Black Editorial (Framed window over luxury pitch black canvas)
            scale_factor = template.video_layout.scale or 0.88
            fg_w = int(round((target_w * scale_factor) / 2) * 2)
            fg_h = int(round((target_h * scale_factor) / 2) * 2)
            pad_x = (target_w - fg_w) // 2
            pad_y = (target_h - fg_h) // 2

            filter_str = (
                f"[0:v]scale={fg_w}:{fg_h}:force_original_aspect_ratio=decrease,"
                f"pad={fg_w}:{fg_h}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1[fg];"
                f"color=c=0x050505:s={target_w}x{target_h}:d=1000[bg];"
                f"[bg][fg]overlay={pad_x}:{pad_y}[vframed]"
            )
            last_tag = "[vframed]"

        elif mode == "cinematic_crop" or mode == "speaker_crop":
            # Template 03 (Bold Podcast) & Template 05 (Cinematic Gold): Full-bleed 9:16 crop
            filter_str = (
                f"[0:v]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,"
                f"crop={target_w}:{target_h}:(in_w-out_w)/2:(in_h-out_h)/2,setsar=1[vframed]"
            )
            last_tag = "[vframed]"

        else:
            # Default portrait conform
            filter_str = (
                f"[0:v]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,"
                f"crop={target_w}:{target_h},setsar=1[vframed]"
            )
            last_tag = "[vframed]"

        # 2. Visual Effects & Color Grading
        vfx_filters: List[str] = []
        if vfx.color_grading == "warm_gold":
            # Warm golden cinematic tones: boost contrast, lift saturation, slight warm shift
            vfx_filters.append("eq=contrast=1.08:brightness=0.02:saturation=1.12")
            vfx_filters.append("colorbalance=rs=0.08:gs=0.03:bs=-0.06:rm=0.06:gm=0.02:bm=-0.05")
        elif vfx.color_grading == "cinematic_contrast":
            # High-retention bold punch
            vfx_filters.append("eq=contrast=1.15:brightness=0.0:saturation=1.12")
            vfx_filters.append("unsharp=5:5:0.6:5:5:0.0")
        elif vfx.color_grading == "dark_editorial":
            # Moody desaturated editorial
            vfx_filters.append("eq=contrast=1.12:brightness=-0.02:saturation=0.92")
            vfx_filters.append("colorbalance=rs=0.02:gs=-0.02:bs=-0.03")
        elif vfx.color_grading == "clean_vivid":
            # Crisp modern creator look
            vfx_filters.append("eq=contrast=1.05:brightness=0.02:saturation=1.08")
        elif vfx.contrast != 1.0 or vfx.brightness != 0.0 or vfx.saturation != 1.0:
            vfx_filters.append(f"eq=contrast={vfx.contrast}:brightness={vfx.brightness}:saturation={vfx.saturation}")

        # Optional subtle film grain
        if vfx.film_grain:
            vfx_filters.append("noise=alls=6:allf=t+u")

        # Chain VFX if present
        if vfx_filters:
            combined_vfx = ",".join(vfx_filters)
            filter_str += f";{last_tag}{combined_vfx}[v_vfx]"
            last_tag = "[v_vfx]"

        # 3. Branding & Accent Lines
        branding_filters: List[str] = []
        if brand.accent_line_enabled:
            # Subtle accent line (e.g. red line for Black Editorial or cyan line for DualCast)
            line_color = brand.accent_line_color.lstrip("#")
            branding_filters.append(
                f"drawbox=x=80:y={int(target_h * 0.16)}:w={target_w - 160}:h=3:color=0x{line_color}@0.9:t=fill"
            )

        if brand.watermark_enabled and brand.watermark_text:
            wm_text = brand.watermark_text.replace(":", "\\:").replace("'", "\\'")
            # Position coordinates
            if brand.watermark_position == "top_left":
                x_pos, y_pos = "48", "60"
            elif brand.watermark_position == "bottom_right":
                x_pos, y_pos = f"w-text_w-48", f"{target_h - 80}"
            else:  # top_right
                x_pos, y_pos = f"w-text_w-48", "60"

            branding_filters.append(
                f"drawtext=text='{wm_text}':font='Arial':fontsize=22:fontcolor=white@0.65:"
                f"x={x_pos}:y={y_pos}:shadowcolor=black@0.4:shadowx=2:shadowy=2"
            )

        if branding_filters:
            combined_brand = ",".join(branding_filters)
            filter_str += f";{last_tag}{combined_brand}[v_final]"
            last_tag = "[v_final]"

        return filter_str, {"output_tag": last_tag.strip("[]")}

    def _build_dualcast_filtergraph(
        self,
        source_w: int,
        source_h: int,
        target_w: int,
        target_h: int,
        layout_style: str,
        is_dual_source: bool = False,
    ) -> str:
        """
        Build DualCast split-screen filtergraph.
        Supports 4 layout configurations:
        1. HOST_TOP_GUEST_BOTTOM (default stacked 2-tile call layout)
        2. GUEST_TOP_HOST_BOTTOM
        3. SIDE_BY_SIDE (vertical side-by-side or pillar)
        4. ACTIVE_SPEAKER_FOCUS (single-source dynamic framing fallback)
        """
        tile_h = 800
        tile_w = target_w - 64  # 1016px with 32px safe gutters
        gap_h = target_h - (tile_h * 2)  # 320px middle seam reserved for kinetic subtitles!
        top_y = 60
        bottom_y = top_y + tile_h + gap_h

        # Determine top vs bottom speaker allocation
        if layout_style == "GUEST_TOP_HOST_BOTTOM":
            top_label = "GUEST"
            bottom_label = "HOST"
            top_color = "0xFBBF24"  # Amber
            bottom_color = "0x38BDF8"  # Cyan
        else:
            top_label = "HOST"
            bottom_label = "GUEST"
            top_color = "0x38BDF8"
            bottom_color = "0xFBBF24"

        if layout_style == "SIDE_BY_SIDE":
            # Side-by-side vertical panels
            col_w = (target_w - 60) // 2
            panel_h = 1200
            panel_y = (target_h - panel_h) // 2

            return (
                f"[0:v]split=3[bgsrc][s1][s2];"
                f"[bgsrc]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,"
                f"crop={target_w}:{target_h},gblur=sigma=20:steps=2,setsar=1[bg];"
                f"[s1]crop=iw/2:ih:0:0,scale={col_w}:{panel_h}:force_original_aspect_ratio=increase,"
                f"crop={col_w}:{panel_h},setsar=1[panel1];"
                f"[s2]crop=iw/2:ih:iw/2:0,scale={col_w}:{panel_h}:force_original_aspect_ratio=increase,"
                f"crop={col_w}:{panel_h},setsar=1[panel2];"
                f"[bg][panel1]overlay=20:{panel_y}[b1];"
                f"[b1][panel2]overlay={col_w + 40}:{panel_y}[b2];"
                f"[b2]drawbox=x={col_w + 28}:y={panel_y}:w=4:h={panel_h}:color=0x334155@0.8:t=fill[vframed]"
            )

        elif layout_style == "ACTIVE_SPEAKER_FOCUS":
            # Single-speaker fallback: dynamic centered portrait crop with blur background
            return (
                f"[0:v]split=2[bgsrc][fgsrc];"
                f"[bgsrc]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,"
                f"crop={target_w}:{target_h},gblur=sigma=24:steps=2,setsar=1[bg];"
                f"[fgsrc]scale={target_w}:ih*({target_w}/iw):flags=lanczos,unsharp=5:5:0.5:5:5:0.0,"
                f"crop={target_w}:{tile_h * 2 + 100}:0:(in_h-out_h)/2,setsar=1[fg];"
                f"[bg][fg]overlay=0:(H-h)/2[vframed]"
            )

        else:
            # Default Stacked 2-Tile Call Layout (HOST_TOP_GUEST_BOTTOM or GUEST_TOP_HOST_BOTTOM)
            # From single landscape source, crop left speaker for top, right speaker for bottom!
            return (
                f"[0:v]split=3[bgsrc][left_cam][right_cam];"
                f"[bgsrc]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,"
                f"crop={target_w}:{target_h},gblur=sigma=24:steps=2,setsar=1[bg];"
                f"[left_cam]crop=iw/2:ih:0:0,scale={tile_w}:{tile_h}:force_original_aspect_ratio=increase,"
                f"crop={tile_w}:{tile_h},setsar=1[tile_top];"
                f"[right_cam]crop=iw/2:ih:iw/2:0,scale={tile_w}:{tile_h}:force_original_aspect_ratio=increase,"
                f"crop={tile_w}:{tile_h},setsar=1[tile_bottom];"
                f"[bg][tile_top]overlay=32:{top_y}[bg1];"
                f"[bg1][tile_bottom]overlay=32:{bottom_y}[bg2];"
                f"[bg2]drawbox=x=32:y={top_y + tile_h + (gap_h // 2)}:w={tile_w}:h=2:color=0x334155@0.7:t=fill,"
                f"drawtext=text='{top_label}':font='Arial':fontsize=20:fontcolor={top_color}@0.95:"
                f"x=52:y={top_y + 20}:box=1:boxcolor=0x000000@0.6:boxborderw=6,"
                f"drawtext=text='{bottom_label}':font='Arial':fontsize=20:fontcolor={bottom_color}@0.95:"
                f"x=52:y={bottom_y + 20}:box=1:boxcolor=0x000000@0.6:boxborderw=6[vframed]"
            )


# Global singleton instance
template_engine = TemplateEngine()


def get_template_engine() -> TemplateEngine:
    return template_engine

