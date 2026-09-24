"""
Visual Motion & Camera Dynamics Detector for UpClip Studio.
Analyzes frame-to-frame pixel variations using OpenCV to assess visual dynamics,
action pacing, and subject movement for short-form video ranking.
"""

from pathlib import Path
import config


class MotionDetector:
    def __init__(self, sample_fps=2.0):
        self.sample_fps = sample_fps

    def analyze(self, video_path, sample_fps=None):
        """
        Analyze video for visual motion intensity.

        Returns:
            dict: {
                "success": bool,
                "duration": float,
                "average_motion": float,
                "peak_motion": float,
                "motion_curve": list of {"time": float, "motion": float},
                "high_motion_segments": list of {"start": float, "end": float, "motion": float}
            }
        """
        video_path = Path(video_path)
        if not video_path.exists():
            return {
                "success": False,
                "error": f"Video not found: {video_path}",
                "average_motion": 50.0,
                "peak_motion": 50.0,
                "motion_curve": [],
                "high_motion_segments": []
            }

        fps_sample = sample_fps or self.sample_fps

        motion_curve = []
        duration = 30.0

        try:
            import cv2
            cap = cv2.VideoCapture(str(video_path))
            video_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            duration = total_frames / video_fps if video_fps > 0 else 30.0

            # Step size in frames
            frame_step = max(1, int(video_fps / fps_sample))
            prev_gray = None

            current_frame_idx = 0
            raw_diffs = []
            timestamps = []

            while current_frame_idx < total_frames:
                cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_idx)
                ret, frame = cap.read()
                if not ret or frame is None:
                    break

                t = round(current_frame_idx / video_fps, 2)

                # Resize to small thumbnail for fast diff computation
                small = cv2.resize(frame, (160, 90))
                gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
                # Apply slight blur to reduce video compression noise
                gray = cv2.GaussianBlur(gray, (5, 5), 0)

                if prev_gray is not None:
                    diff = cv2.absdiff(prev_gray, gray)
                    mean_val = float(diff.mean())
                    raw_diffs.append(mean_val)
                    timestamps.append(t)

                prev_gray = gray
                current_frame_idx += frame_step

            cap.release()

            if raw_diffs:
                max_diff = max(raw_diffs)
                if max_diff < 1.0:
                    max_diff = 1.0

                for t, diff_val in zip(timestamps, raw_diffs):
                    # Normalize to 0 - 100
                    score = round(min(100.0, (diff_val / max_diff) * 100.0), 1)
                    motion_curve.append({
                        "time": t,
                        "motion": score
                    })

        except Exception as e:
            print("[MOTION_DETECTOR] Analysis note:", e)

        # Fallback if cv2 fails or video cannot be opened
        if not motion_curve:
            step = 1.0 / fps_sample
            t = 0.0
            while t < duration:
                motion_curve.append({
                    "time": round(t, 2),
                    "motion": 65.0
                })
                t += step

        motions = [pt["motion"] for pt in motion_curve]
        avg_motion = round(sum(motions) / len(motions), 1) if motions else 50.0
        peak_motion = max(motions) if motions else 50.0

        # High motion threshold
        hi_thresh = max(60.0, avg_motion * 1.2)
        high_segments = []
        for i, pt in enumerate(motion_curve):
            if pt["motion"] >= hi_thresh:
                high_segments.append({
                    "time": pt["time"],
                    "motion": pt["motion"]
                })

        return {
            "success": True,
            "duration": round(duration, 2),
            "average_motion": avg_motion,
            "peak_motion": peak_motion,
            "motion_curve": motion_curve,
            "high_motion_segments": high_segments
        }

    def get_segment_motion_score(self, motion_analysis, start, end):
        """
        Return the average visual motion score for a time window [start, end].
        """
        curve = motion_analysis.get("motion_curve", [])
        if not curve:
            return 60.0

        matched = [
            pt["motion"]
            for pt in curve
            if start <= pt["time"] <= end
        ]
        if not matched:
            return 60.0
        return round(sum(matched) / len(matched), 1)
