"""
Smart Reframe & Subject-Aware Framing Engine for UpClip Studio.
Converts 16:9 landscape footage into vertical 9:16 framing with YuNet face tracking,
multi-person active speaker cutting, stacked call layouts, and reaction streamer layouts.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np

import config
from ai.face_detector import FaceDetector
from ai.talking_head_layout import analyze_layout_for_faces, Box
from ai.reaction_layout import find_reactor_face, build_reaction_layout_plan


class SmartReframer:
    def __init__(self):
        self.detector = FaceDetector(use_yunet=True)

    def compute_reframe(
        self,
        video_path,
        mode: str = "smart",
        target_aspect: str = "9:16",
        words: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Compute optimal horizontal framing offset X, keyframes, and layout recommendation
        (Single Crop, Stacked 2-Tile, Reaction Box, or Stage Blur-Pad).

        Returns:
            dict: {
                "mode": str,
                "targetAspect": "9:16",
                "recommendedX": float,
                "scale": float,
                "keyframes": list of {"time": float, "x": float},
                "layout": dict or None
            }
        """
        video_path = Path(video_path)
        default_scale = 177.78  # 16/9 * 100 for vertical fill

        if not video_path.exists():
            return {
                "mode": mode,
                "targetAspect": target_aspect,
                "recommendedX": 0.0,
                "scale": default_scale,
                "keyframes": [],
                "layout": None
            }

        if mode == "center":
            return {
                "mode": "center",
                "targetAspect": target_aspect,
                "recommendedX": 0.0,
                "scale": default_scale,
                "keyframes": [],
                "layout": None
            }

        recommended_x = 0.0
        keyframes = []
        detected_x_positions = []
        face_samples = []
        layout_plan = None

        try:
            cap = cv2.VideoCapture(str(video_path))
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1920)
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1080)

            # Sample 10 frames across the video for robust layout decision
            sample_ratios = [0.08, 0.18, 0.28, 0.38, 0.48, 0.58, 0.68, 0.78, 0.88, 0.95]
            sample_indices = [int(total_frames * r) for r in sample_ratios if int(total_frames * r) < total_frames]

            for idx in sample_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if not ret or frame is None:
                    continue

                t_sec = round(idx / fps, 2)
                faces = self.detector.detect_in_frame(frame)
                if faces:
                    raw_boxes = [(float(f["x"]), float(f["y"]), float(f["w"]), float(f["h"])) for f in faces]
                    face_samples.append((t_sec, raw_boxes))

                    largest = faces[0]
                    face_center_x = largest["center_x"]
                    shift_ratio = (face_center_x - (width / 2.0)) / (width / 2.0)
                    target_canvas_x = round(-shift_ratio * 120.0, 1)
                    detected_x_positions.append(target_canvas_x)
                    keyframes.append({"time": t_sec, "x": target_canvas_x})
                else:
                    face_samples.append((t_sec, []))

            cap.release()

            if detected_x_positions:
                recommended_x = round(sum(detected_x_positions) / len(detected_x_positions), 1)

            # Check for Reaction Streamer corner face layout
            reactor_face = find_reactor_face(width, height, face_samples)
            if reactor_face:
                layout_plan = build_reaction_layout_plan(width, height, reactor_face)
            else:
                # Check for Stacked 2-Tile (video call) or Stage blur padding
                layout_plan = analyze_layout_for_faces(width, height, face_samples)

        except Exception as e:
            print("[REFRAME] Smart reframing analysis note (fallback to safe center):", e)
            recommended_x = 0.0

        return {
            "mode": mode,
            "targetAspect": target_aspect,
            "recommendedX": recommended_x,
            "scale": default_scale,
            "keyframes": keyframes,
            "layout": layout_plan
        }
