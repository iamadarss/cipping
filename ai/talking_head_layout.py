"""
Face-Aware 9:16 Video Layout Compositor for UpClip Studio.
Provides intelligent split-screen (Stacked 2-Tile), stage framing, and blur-padded gallery layouts.

Features:
- Stacked 2-Tile Call Layout:
  For 2 side-by-side speakers (Zoom/Meet/podcast), stacks Speaker 1 on top (800px)
  and Speaker 2 on bottom (800px), reserving the middle gap for kinetic captions!
- Stage / Blurred Padding:
  For low-seated webcam speakers, prevents pixelated 1.8x zooms by capping upscale to 1.32x
  and compositing the subject over a smooth Gaussian-blurred background.
- Gallery View:
  For 3+ people on screen, shows the wide shot downscaled over blur padding.
"""

from typing import Any, Dict, List, Optional, Sequence, Tuple
import cv2
import numpy as np

OUT_W = 1080
OUT_H = 1920
STAGE_MAX_UPSCALE = 1.32
STAGE_FACE_Y = 0.38
STACK_TOP = 168
STACK_TILE_H = 800
STACK_BOTTOM = 1120
STACK_CAPTION_Y = ((STACK_TOP + STACK_TILE_H) + STACK_BOTTOM) / 2 / OUT_H  # ~0.50 (Middle Gap)

Box = Tuple[float, float, float, float]
FaceFrame = Tuple[float, Sequence[Box]]


def round_to_even(value: float) -> int:
    """Ensure dimensions are even integers for FFmpeg codecs (h264/yuv420p)."""
    val = int(round(value))
    return val if val % 2 == 0 else val + 1


def clamp_even(value: int, min_val: int, max_val: int) -> int:
    """Clamp value inside [min_val, max_val] rounded to even."""
    clamped = max(min_val, min(value, max_val))
    return round_to_even(clamped)


def caption_y_below_subject(face_bottom: float, default: float = 0.80) -> float:
    """Calculate vertical caption position clear of the speaker's face."""
    if face_bottom + 0.04 < default - 0.06:
        return default
    return min(0.84, max(default, face_bottom + 0.12))


def _median(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[len(ordered) // 2]


def _even_box(box: Box) -> Tuple[int, int, int, int]:
    x, y, w, h = box
    return (
        int(round(x)),
        int(round(y)),
        max(2, int(round(w))),
        max(2, int(round(h))),
    )


def _blur_base(splits: int, *labels: str) -> str:
    sources = "".join(labels)
    return (
        f"[0:v]split={splits}{sources};"
        "[bgsrc]scale=540:960:force_original_aspect_ratio=increase,crop=540:960,"
        "gblur=sigma=18:steps=2,scale=1080:1920:flags=bilinear,setsar=1[bg];"
    )


def _foreground(label: str, crop: Tuple[int, int, int, int], out_w: int, out_h: int) -> str:
    x, y, w, h = crop
    return (
        f"{label}crop={w}:{h}:{x}:{y},"
        f"scale={out_w}:{out_h}:flags=lanczos,unsharp=5:5:0.5:5:5:0.0,setsar=1"
    )


def _tile_crop(
    width: int, height: int, box: Box, tile_w: int, tile_h: int
) -> Tuple[int, int, int, int]:
    """Source window matching the tile, biased to the face's half of the frame."""
    x, y, w, h = box
    cx = x + w / 2
    cy = y + h / 2
    crop_w = round_to_even(min(width, max(tile_w // 2, width // 2)))
    crop_h = round_to_even(max(2, int(round(crop_w * tile_h / tile_w))))
    crop_h = min(crop_h, round_to_even(height))

    if cx < width / 2:
        crop_x = clamp_even(int(min(cx - crop_w / 2, width / 2 - crop_w)), 0, max(0, width - crop_w))
    else:
        crop_x = clamp_even(int(max(cx - crop_w / 2, width / 2)), 0, max(0, width - crop_w))

    face_in = tile_h * 0.40
    crop_face = face_in / tile_h * crop_h
    crop_y = clamp_even(int(cy - crop_face), 0, max(0, height - crop_h))

    headroom = max(6, int(h * 0.25))
    if crop_y > y - headroom:
        crop_y = clamp_even(int(y - headroom), 0, max(0, height - crop_h))
    return crop_x, crop_y, crop_w, crop_h


def build_stacked_call_plan(width: int, height: int, left_face: Box, right_face: Box) -> Dict[str, Any]:
    """
    Build Stacked 2-Tile Call Layout (Top 800px Speaker 1, Bottom 800px Speaker 2, Middle Gap Captions).
    """
    left_crop = _tile_crop(width, height, left_face, OUT_W, STACK_TILE_H)
    right_crop = _tile_crop(width, height, right_face, OUT_W, STACK_TILE_H)
    video_filter = (
        f"{_blur_base(3, '[bgsrc]', '[lsrc]', '[rsrc]')}"
        f"{_foreground('[lsrc]', left_crop, OUT_W, STACK_TILE_H)}[lv];"
        f"{_foreground('[rsrc]', right_crop, OUT_W, STACK_TILE_H)}[rv];"
        f"[bg][lv]overlay=0:{STACK_TOP}[mid];"
        f"[mid][rv]overlay=0:{STACK_BOTTOM}[vout]"
    )
    return {
        "kind": "stack",
        "video_filter": video_filter,
        "caption_y": round(STACK_CAPTION_Y, 4),
        "left_crop": left_crop,
        "right_crop": right_crop,
        "video_bottom": (STACK_BOTTOM + STACK_TILE_H) / OUT_H,
    }


def build_stage_plan(width: int, height: int, box: Box) -> Dict[str, Any]:
    """
    Build Stage Layout: Place face in upper third over blurred background frame.
    Avoids pixelated 1.8x upscales for low-positioned webcam talking heads.
    """
    x, y, w, h = box
    cx = x + w / 2
    cy = y + h / 2
    min_crop_w = max(2, round_to_even(int(OUT_W / STAGE_MAX_UPSCALE)))
    preferred = round_to_even(int(width * 0.52))
    subject_limit = round_to_even(int(w / 0.16)) if w > 0 else width
    crop_w = min(width, max(min_crop_w, min(preferred, max(min_crop_w, subject_limit))))
    crop_w = max(2, round_to_even(crop_w))
    if crop_w > width:
        crop_w = round_to_even(width)
    crop_x = clamp_even(int(cx - crop_w / 2), 0, max(0, width - crop_w))

    scale = OUT_W / crop_w
    scaled_h = min(OUT_H, round_to_even(int(round(height * scale))))
    scaled_h = max(2, scaled_h)
    face_in = (cy / max(height, 1)) * scaled_h
    overlay = int(STAGE_FACE_Y * OUT_H - face_in)
    overlay = max(0, min(overlay, OUT_H - scaled_h))
    overlay = round_to_even(overlay)

    video_filter = (
        f"{_blur_base(2, '[bgsrc]', '[fgsrc]')}"
        f"{_foreground('[fgsrc]', (crop_x, 0, crop_w, height), OUT_W, scaled_h)}[fg];"
        f"[bg][fg]overlay=0:{overlay}[vout]"
    )
    video_bottom = (overlay + scaled_h) / OUT_H
    caption_y = min(0.84, video_bottom + (1 - video_bottom) * 0.45) if video_bottom < 0.82 else 0.80

    return {
        "kind": "stage",
        "video_filter": video_filter,
        "caption_y": round(caption_y, 4),
        "crop": (crop_x, 0, crop_w, height),
        "overlay_y": overlay,
    }


def build_gallery_plan(width: int, height: int) -> Dict[str, Any]:
    """
    Build Gallery Layout: 3+ faces shown wide on blurred background padding.
    """
    scaled_h = round_to_even(int(round(OUT_W * height / width)))
    overlay_y = round_to_even(int((OUT_H - scaled_h) / 2))
    video_filter = (
        f"{_blur_base(2, '[bgsrc]', '[fgsrc]')}"
        f"[fgsrc]scale={OUT_W}:{scaled_h}:flags=lanczos,setsar=1[fg];"
        f"[bg][fg]overlay=0:{overlay_y}[vout]"
    )
    return {
        "kind": "gallery",
        "video_filter": video_filter,
        "caption_y": 0.82,
        "overlay_y": overlay_y,
    }


def analyze_layout_for_faces(
    width: int,
    height: int,
    face_samples: Sequence[FaceFrame]
) -> Optional[Dict[str, Any]]:
    """
    Analyze sequence of face samples and select optimal layout:
    - Stacked 2-Tile if 2 side-by-side separated speakers
    - Gallery if 3+ faces consistently on screen
    - Stage if single face sitting low in the frame (<0.38)
    - None if standard dynamic tracked crop is best
    """
    if not face_samples:
        return None

    # Check for gallery (3+ faces)
    face_counts = [len(faces) for _, faces in face_samples if faces]
    if len(face_counts) >= 4 and sum(1 for c in face_counts if c >= 3) >= len(face_counts) * 0.5:
        return build_gallery_plan(width, height)

    # Check for 2 side-by-side call pairs
    pairs: List[Tuple[Box, Box]] = []
    for _, faces in face_samples:
        if len(faces) == 2:
            sorted_faces = sorted(faces, key=lambda f: f[0])
            left, right = sorted_faces[0], sorted_faces[1]
            left_cx = left[0] + left[2] / 2
            right_cx = right[0] + right[2] / 2
            # Must be horizontally separated by at least 25% of frame width
            if (right_cx - left_cx) > width * 0.25:
                pairs.append((left, right))

    if len(pairs) >= max(3, int(len(face_samples) * 0.4)):
        left_box = (
            _median([p[0][0] for p in pairs]),
            _median([p[0][1] for p in pairs]),
            _median([p[0][2] for p in pairs]),
            _median([p[0][3] for p in pairs]),
        )
        right_box = (
            _median([p[1][0] for p in pairs]),
            _median([p[1][1] for p in pairs]),
            _median([p[1][2] for p in pairs]),
            _median([p[1][3] for p in pairs]),
        )
        return build_stacked_call_plan(width, height, left_box, right_box)

    # Check for single low webcam face
    single_faces = [faces[0] for _, faces in face_samples if len(faces) == 1]
    if len(single_faces) >= max(3, int(len(face_samples) * 0.5)):
        med_y = _median([f[1] + f[3] / 2 for f in single_faces])
        # If face center is in the lower 55% of the 16:9 frame, use stage layout
        if med_y > height * 0.45:
            med_box = (
                _median([f[0] for f in single_faces]),
                _median([f[1] for f in single_faces]),
                _median([f[2] for f in single_faces]),
                _median([f[3] for f in single_faces]),
            )
            return build_stage_plan(width, height, med_box)

    return None
