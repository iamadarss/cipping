"""
Face Detection and Subject Presence Engine for UpClip Studio.
Detects human faces, tracks speaker positions, and evaluates face prominence
for vertical smart reframing (9:16) and clip engagement scoring.
"""

from pathlib import Path
import config


class FaceDetector:
    def __init__(self):
        self._cascade = None
        self._initialized = False

    def _get_cascade(self):
        if not self._initialized:
            self._initialized = True
            try:
                import cv2
                cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                if Path(cascade_path).exists():
                    self._cascade = cv2.CascadeClassifier(cascade_path)
            except Exception as e:
                print("[FACE_DETECTOR] Cascade initialization note:", e)
        return self._cascade

    def detect_in_frame(self, frame):
        """
        Detect faces in a single BGR OpenCV frame.

        Returns:
            list of dicts: [
                {"x": int, "y": int, "w": int, "h": int, "center_x": float, "center_y": float, "area": int}
            ]
        """
        if frame is None:
            return []

        cascade = self._get_cascade()
        if not cascade:
            return []

        try:
            import cv2
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Detect multi-scale
            faces = cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=4, minSize=(30, 30))
            results = []
            for (x, y, w, h) in faces:
                results.append({
                    "x": int(x),
                    "y": int(y),
                    "w": int(w),
                    "h": int(h),
                    "center_x": round(float(x + w / 2.0), 1),
                    "center_y": round(float(y + h / 2.0), 1),
                    "area": int(w * h)
                })
            # Sort by area descending (largest face first)
            results.sort(key=lambda f: f["area"], reverse=True)
            return results
        except Exception as e:
            return []

    def analyze_video(self, video_path, sample_interval=1.0):
        """
        Sample video at regular intervals and map face presence across time.

        Returns:
            dict: {
                "success": bool,
                "duration": float,
                "face_presence_percent": float,
                "face_keyframes": list of {"time": float, "face_count": int, "primary_face": dict},
                "average_face_count": float
            }
        """
        video_path = Path(video_path)
        if not video_path.exists():
            return {
                "success": False,
                "error": f"Video not found: {video_path}",
                "face_presence_percent": 0.0,
                "face_keyframes": []
            }

        keyframes = []
        duration = 30.0

        try:
            import cv2
            cap = cv2.VideoCapture(str(video_path))
            video_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            duration = total_frames / video_fps if video_fps > 0 else 30.0

            frame_step = max(1, int(video_fps * sample_interval))
            current_frame_idx = 0

            detected_frames = 0
            total_sampled = 0

            while current_frame_idx < total_frames:
                cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_idx)
                ret, frame = cap.read()
                if not ret or frame is None:
                    break

                t = round(current_frame_idx / video_fps, 2)
                faces = self.detect_in_frame(frame)
                total_sampled += 1

                if faces:
                    detected_frames += 1
                    keyframes.append({
                        "time": t,
                        "face_count": len(faces),
                        "primary_face": faces[0]
                    })
                else:
                    keyframes.append({
                        "time": t,
                        "face_count": 0,
                        "primary_face": None
                    })

                current_frame_idx += frame_step

            cap.release()

            presence_pct = round((detected_frames / max(1, total_sampled)) * 100.0, 1)
            avg_count = round(sum(k["face_count"] for k in keyframes) / max(1, len(keyframes)), 2)

            return {
                "success": True,
                "duration": round(duration, 2),
                "face_presence_percent": presence_pct,
                "average_face_count": avg_count,
                "face_keyframes": keyframes
            }

        except Exception as e:
            print("[FACE_DETECTOR] Analysis error:", e)
            return {
                "success": False,
                "duration": 30.0,
                "face_presence_percent": 75.0,
                "average_face_count": 1.0,
                "face_keyframes": []
            }

    def get_segment_face_score(self, face_analysis, start, end):
        """
        Compute face prominence score (0 to 100) for a given time window.
        """
        keyframes = face_analysis.get("face_keyframes", [])
        if not keyframes:
            return 70.0

        matched = [k for k in keyframes if start <= k["time"] <= end]
        if not matched:
            return 70.0

        with_faces = sum(1 for k in matched if k.get("face_count", 0) > 0)
        presence = (with_faces / len(matched)) * 100.0
        return round(min(100.0, presence), 1)
