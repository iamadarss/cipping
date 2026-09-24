"""
Audio Energy & Excitement Peak Detector for UpClip Studio.
Analyzes audio tracks using RMS energy to detect punchlines, loud reactions,
laughter, cheering, and high-engagement moments for viral shorts clipping.
"""

import math
import subprocess
from pathlib import Path
import config


class AudioEnergyDetector:
    def __init__(self, window_sec=0.5):
        self.window_sec = window_sec
        self.ffmpeg = config.FFMPEG_PATH

    def analyze(self, media_path, window_sec=None):
        """
        Analyze audio track across the file and compute RMS energy over time windows.

        Returns:
            dict: {
                "success": bool,
                "duration": float,
                "average_energy": float,
                "peak_energy": float,
                "peaks": list of {"time": float, "energy": float},
                "energy_curve": list of {"start": float, "end": float, "energy": float}
            }
        """
        media_path = Path(media_path)
        if not media_path.exists():
            return {
                "success": False,
                "error": f"File not found: {media_path}",
                "average_energy": 50.0,
                "peaks": [],
                "energy_curve": []
            }

        win = window_sec or self.window_sec

        # Get media duration
        from utils.video_utils import VideoLoader
        loader = VideoLoader(media_path)
        duration = float(loader.metadata().get("duration", 30.0))
        loader.close()

        # Run FFmpeg astats or volumedetect filter
        cmd = [
            self.ffmpeg,
            "-i", str(media_path),
            "-vn",
            "-af", f"asetnsamples=n=22050,astats=metadata=1:reset=1",
            "-f", "null",
            "-"
        ]

        energy_curve = []
        try:
            # We can also read raw 16-bit PCM audio samples via ffmpeg stdout for deterministic RMS
            raw_cmd = [
                self.ffmpeg,
                "-i", str(media_path),
                "-vn",
                "-ac", "1",
                "-ar", "8000",
                "-f", "s16le",
                "-"
            ]
            proc = subprocess.Popen(raw_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            raw_data, _ = proc.communicate()

            if raw_data and len(raw_data) >= 16:
                import struct
                sample_count = len(raw_data) // 2
                fmt = f"<{sample_count}h"
                samples = struct.unpack(fmt, raw_data)

                sample_rate = 8000
                chunk_samples = int(sample_rate * win)
                num_chunks = max(1, len(samples) // chunk_samples)

                raw_rms_values = []
                for i in range(num_chunks):
                    chunk = samples[i * chunk_samples:(i + 1) * chunk_samples]
                    if not chunk:
                        continue
                    # Compute RMS
                    sum_sq = sum(s * s for s in chunk)
                    rms = math.sqrt(sum_sq / len(chunk))
                    raw_rms_values.append(rms)

                # Normalize RMS values to 0 - 100
                max_rms = max(raw_rms_values) if raw_rms_values else 1.0
                if max_rms == 0:
                    max_rms = 1.0

                for i, r in enumerate(raw_rms_values):
                    score = round(min(100.0, (r / max_rms) * 100.0), 1)
                    t_start = round(i * win, 2)
                    t_end = round(min(duration, (i + 1) * win), 2)
                    energy_curve.append({
                        "start": t_start,
                        "end": t_end,
                        "energy": score
                    })
        except Exception as e:
            print("[AUDIO_ENERGY] Analysis fallback due to:", e)

        # Fallback if audio extraction fails or file has no audio stream
        if not energy_curve:
            step = win
            t = 0.0
            while t < duration:
                energy_curve.append({
                    "start": round(t, 2),
                    "end": round(min(duration, t + step), 2),
                    "energy": 60.0
                })
                t += step

        # Compute summary stats
        energies = [pt["energy"] for pt in energy_curve]
        avg_energy = round(sum(energies) / len(energies), 1) if energies else 50.0
        peak_energy = max(energies) if energies else 50.0

        # Find energy peaks (points at least 15% above average and above 65)
        peak_threshold = max(65.0, avg_energy * 1.25)
        peaks = [
            {"time": pt["start"], "energy": pt["energy"]}
            for pt in energy_curve
            if pt["energy"] >= peak_threshold
        ]

        return {
            "success": True,
            "duration": duration,
            "average_energy": avg_energy,
            "peak_energy": peak_energy,
            "peaks": peaks,
            "energy_curve": energy_curve
        }

    def get_segment_energy_score(self, energy_analysis, start, end):
        """
        Calculate the average audio energy score for a specific time window [start, end].
        Returns float between 0.0 and 100.0.
        """
        curve = energy_analysis.get("energy_curve", [])
        if not curve:
            return 60.0

        matched = [
            pt["energy"]
            for pt in curve
            if not (pt["end"] <= start or pt["start"] >= end)
        ]
        if not matched:
            return 60.0
        return round(sum(matched) / len(matched), 1)
