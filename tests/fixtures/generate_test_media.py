"""Lightweight synthetic media generator for automated test suites.

Generates small, valid MP4 video files and WAV audio files in memory or on disk
for fast, isolated testing without external asset dependencies.
"""

import math
import struct
import wave
from pathlib import Path
from typing import Tuple


def generate_synthetic_wav(
    output_path: Path,
    duration_sec: float = 2.0,
    sample_rate: int = 16000,
    frequency: float = 440.0,
) -> Path:
    """Generate a clean synthetic sine wave WAV file for Whisper/audio tests."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    num_samples = int(sample_rate * duration_sec)
    amplitude = 16000  # 16-bit signed integer amplitude

    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
        wav_file.setframerate(sample_rate)

        frames = bytearray()
        for i in range(num_samples):
            val = int(amplitude * math.sin(2.0 * math.pi * frequency * (i / sample_rate)))
            frames.extend(struct.pack("<h", max(-32768, min(32767, val))))

        wav_file.writeframes(frames)

    return output_path


def generate_synthetic_mp4(
    output_path: Path,
    duration_sec: float = 2.0,
    fps: int = 24,
    resolution: Tuple[int, int] = (320, 240),
) -> Path:
    """Generate a clean synthetic MP4 video file using OpenCV."""
    import cv2
    import numpy as np

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    width, height = resolution
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output_path), fourcc, float(fps), (width, height))

    total_frames = int(duration_sec * fps)
    for frame_idx in range(total_frames):
        # Generate color bars with frame counter
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # Shift colors across frames
        color_shift = int((frame_idx / max(1, total_frames)) * 255)
        frame[:, : width // 2] = [color_shift, 120, 200]
        frame[:, width // 2 :] = [200, color_shift, 120]

        # Draw frame number
        text = f"Frame {frame_idx}"
        cv2.putText(
            frame,
            text,
            (10, height // 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )
        writer.write(frame)

    writer.release()
    return output_path


if __name__ == "__main__":
    fixtures_dir = Path(__file__).resolve().parent
    wav_out = fixtures_dir / "sample_tone.wav"
    mp4_out = fixtures_dir / "sample_test_video.mp4"
    generate_synthetic_wav(wav_out)
    generate_synthetic_mp4(mp4_out)
    print(f"Generated test fixtures: {wav_out.name}, {mp4_out.name}")
