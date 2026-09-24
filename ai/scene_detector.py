"""
Video Scene Boundary Detector for UpClip Studio.
Analyzes visual frame differences and camera angle cuts to detect meaningful,
production-grade scenes while preventing micro-clips (minimum 15s-20s).
"""

import re
import subprocess
from pathlib import Path

import config


class SceneDetector:
    def __init__(self, threshold=0.35, min_scene_duration=None):
        self.threshold = threshold
        self.ffmpeg = config.FFMPEG_PATH
        self.min_scene_duration = min_scene_duration or getattr(config, "MIN_DURATION", 15.0)

    def detect_scenes(self, video_path, threshold=None, min_duration=None):
        """
        Analyze video for visual scene changes and produce legitimate scene boundaries.

        Returns:
            list of dicts: [{ id, sceneNumber, start, end, duration, confidence }]
        """
        video_path = Path(video_path)
        if not video_path.exists():
            return []

        th = threshold if threshold is not None else self.threshold
        min_dur = min_duration if min_duration is not None else self.min_scene_duration

        # Get total duration
        from utils.video_utils import VideoLoader
        loader = VideoLoader(video_path)
        total_duration = float(loader.metadata().get("duration", 30.0))
        loader.close()

        # If video is shorter than minimum legitimate clip duration, return 1 whole scene
        if total_duration <= min_dur:
            return [{
                "id": "scene_1",
                "sceneNumber": 1,
                "start": 0.0,
                "end": round(total_duration, 2),
                "duration": round(total_duration, 2),
                "confidence": 1.0
            }]

        # Run FFmpeg scene change filter
        cmd = [
            self.ffmpeg,
            "-i", str(video_path),
            "-filter:v", f"select='gt(scene,{th:.2f})',showinfo",
            "-f", "null",
            "-"
        ]

        raw_cuts = []
        try:
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, check=False)
            stderr_output = res.stderr or ""
            matches = re.findall(r"pts_time:([\d\.]+)", stderr_output)
            for m in matches:
                t = float(m)
                if 0.5 < t < total_duration - 0.5:
                    raw_cuts.append(round(t, 2))
        except Exception as e:
            print("[SCENE] Detection failed, using fallback segmenting:", e)

        # Enforce minimum scene duration by filtering cuts that are too close together
        filtered_cuts = []
        last_t = 0.0
        for cut in raw_cuts:
            if cut - last_t >= min_dur and (total_duration - cut) >= (min_dur * 0.75):
                filtered_cuts.append(cut)
                last_t = cut

        # If no cuts survived filtering, use intelligent natural pacing (20s - 45s)
        if not filtered_cuts:
            step = min(35.0, max(min_dur, total_duration / 3.0))
            t = step
            while t < total_duration - (min_dur * 0.75):
                filtered_cuts.append(round(t, 2))
                t += step

        # Assemble scene list
        timestamps = [0.0] + filtered_cuts + [round(total_duration, 2)]
        scenes = []

        for i in range(len(timestamps) - 1):
            start = timestamps[i]
            end = timestamps[i + 1]
            dur = round(end - start, 2)
            if dur > 0:
                scenes.append({
                    "id": f"scene_{i + 1}",
                    "sceneNumber": i + 1,
                    "start": start,
                    "end": end,
                    "duration": dur,
                    "confidence": 0.88 if len(filtered_cuts) > 0 else 0.75
                })

        # Final safety check: if last scene is shorter than minimum, merge it with previous
        if len(scenes) > 1 and scenes[-1]["duration"] < min_dur:
            last = scenes.pop()
            scenes[-1]["end"] = last["end"]
            scenes[-1]["duration"] = round(scenes[-1]["end"] - scenes[-1]["start"], 2)

        return scenes
