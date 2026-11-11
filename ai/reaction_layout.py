"""
Reaction Video Layout Compositor for UpClip Studio.
Separates persistent corner streamer webcams from main content/gameplay footage.

Composites into a vertical 1080x1920 layout:
- Top 640px: Reactor / Streamer facecam (face-centered).
- Bottom 1280px: Source reaction content / gameplay video.
- Safe Seam: Subtitles sit in the natural seam between the reactor and source.
"""

from typing import Any, Dict, List, Optional, Sequence, Tuple
from pathlib import Path
import cv2
import numpy as np

Box = Tuple[float, float, float, float]
FaceFrame = Tuple[float, Sequence[Box]]

REACTOR_HEIGHT = 640
SOURCE_HEIGHT = 1280
OUT_W = 1080
OUT_H = 1920


def round_to_even(value: float) -> int:
    val = int(round(value))
    return val if val % 2 == 0 else val + 1


def clamp_even(value: int, min_val: int, max_val: int) -> int:
    clamped = max(min_val, min(value, max_val))
    return round_to_even(clamped)


def find_reactor_face(width: int, height: int, samples: Sequence[FaceFrame]) -> Optional[Box]:
    """
    Find a small, stationary upper-corner face that persists across the video.
    Typically represents a streamer/reactor webcam overlay.
    """
    if len(samples) < 6:
        return None

    # Check Top-Right and Top-Left corners
    for right in (True, False):
        found = []
        for _, faces in samples:
            corner_faces = [
                f for f in faces
                if (f[0] + f[2] / 2 > width * 0.70 if right else f[0] + f[2] / 2 < width * 0.30)
                and (f[1] + f[3] / 2 < height * 0.35)
                and (0.001 < (f[2] * f[3]) / (width * height) < 0.04)  # Small inset face
            ]
            if len(corner_faces) == 1:
                found.append(corner_faces[0])

        if len(found) >= len(samples) * 0.60:
            boxes = np.asarray(found)
            centres = boxes[:, :2] + boxes[:, 2:] / 2
            # Verify facecam is stationary (low standard deviation in coordinates)
            if np.std(centres[:, 0]) < width * 0.03 and np.std(centres[:, 1]) < height * 0.03:
                return (
                    float(np.median(boxes[:, 0])),
                    float(np.median(boxes[:, 1])),
                    float(np.median(boxes[:, 2])),
                    float(np.median(boxes[:, 3])),
                )
    return None


def build_reaction_layout_plan(
    width: int,
    height: int,
    reactor_face: Box
) -> Dict[str, Any]:
    """
    Build FFmpeg filter graph for Reaction layout:
    - Top 640px: Reactor Facecam (scaled 9:16 slice)
    - Bottom 1280px: Main content (centered 9:16 crop)
    """
    fx, fy, fw, fh = reactor_face
    cx = fx + fw / 2
    cy = fy + fh / 2

    # Reactor crop (top 640px of vertical frame, ratio 1080:640 = 27:16)
    reactor_crop_w = round_to_even(min(width * 0.4, max(fw * 2.2, 320)))
    reactor_crop_h = round_to_even(int(reactor_crop_w * REACTOR_HEIGHT / OUT_W))
    reactor_crop_x = clamp_even(int(cx - reactor_crop_w / 2), 0, max(0, width - reactor_crop_w))
    reactor_crop_y = clamp_even(int(cy - reactor_crop_h / 2), 0, max(0, height - reactor_crop_h))

    # Source crop (bottom 1280px of vertical frame, ratio 1080:1280 = 27:32)
    source_crop_w = round_to_even(min(width, int(height * OUT_W / SOURCE_HEIGHT)))
    source_crop_h = height
    source_crop_x = clamp_even(int((width - source_crop_w) / 2), 0, max(0, width - source_crop_w))
    source_crop_y = 0

    video_filter = (
        f"[0:v]split=2[rx][sx];"
        f"[rx]crop={reactor_crop_w}:{reactor_crop_h}:{reactor_crop_x}:{reactor_crop_y},"
        f"scale={OUT_W}:{REACTOR_HEIGHT}:flags=lanczos,unsharp=5:5:0.5:5:5:0.0[rtop];"
        f"[sx]crop={source_crop_w}:{source_crop_h}:{source_crop_x}:{source_crop_y},"
        f"scale={OUT_W}:{SOURCE_HEIGHT}:flags=lanczos[sbot];"
        f"color=c=black:s={OUT_W}x{OUT_H}:d=1[bg];"
        f"[bg][rtop]overlay=0:0[topm];"
        f"[topm][sbot]overlay=0:{REACTOR_HEIGHT}[vout]"
    )

    # Caption center sits right in the bottom third of the source video or just above it
    caption_y = round((REACTOR_HEIGHT + 240) / OUT_H, 4)

    return {
        "kind": "reaction",
        "video_filter": video_filter,
        "caption_y": caption_y,
        "reactor_crop": (reactor_crop_x, reactor_crop_y, reactor_crop_w, reactor_crop_h),
        "source_crop": (source_crop_x, source_crop_y, source_crop_w, source_crop_h),
    }

