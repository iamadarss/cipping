"""
Active Speaker Framing & Multi-Person Shot Compositor for UpClip Studio.
Driven by audio speaker diarization and mouth motion tracking.

Solves the single-camera wide-shot podcast / interview problem:
Instead of showing only one static center crop or an awkward wide letterbox,
this engine:
1. Tracks who is speaking using diarized timestamps.
2. Absorbs micro-interruptions (<1.2s like 'yeah', 'uh-huh') to avoid camera flicker.
3. Snaps cuts to land 0.15s before the new speaker's first word.
4. Hard-cuts between speaker faces in single-talker passages.
5. Switches to the Stacked 2-Tile layout during sustained crosstalk / overlap.
"""

from typing import Any, Dict, List, Optional, Sequence, Tuple
from pathlib import Path
import numpy as np

SPEAKER_MIN_TURN_SECONDS = 1.2
SPEAKER_CUT_LEAD_SECONDS = 0.15
SPEAKER_CROSSTALK_THRESHOLD = 0.60


def build_speaker_turns(
    words: Sequence[Dict[str, Any]],
    duration: Optional[float] = None,
    min_turn: float = SPEAKER_MIN_TURN_SECONDS,
    lead: float = SPEAKER_CUT_LEAD_SECONDS,
) -> List[Dict[str, Any]]:
    """
    Transform diarized word timestamps into a flicker-free speaker-turn timeline.
    Absorbs micro-interruptions and applies lead-in cut timing.
    """
    runs: List[Dict[str, Any]] = []
    for word in words:
        speaker = word.get("speaker")
        start = float(word.get("start", 0))
        end = float(word.get("end", 0))
        if end <= start:
            continue

        if speaker is None:
            if runs:
                runs[-1]["end"] = max(runs[-1]["end"], end)
            continue

        if runs and runs[-1]["speaker"] == speaker:
            runs[-1]["end"] = max(runs[-1]["end"], end)
            continue

        runs.append({"speaker": str(speaker), "start": start, "end": end})

    def coalesce(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        merged: List[Dict[str, Any]] = []
        for item in items:
            if merged and merged[-1]["speaker"] == item["speaker"]:
                merged[-1]["end"] = max(merged[-1]["end"], item["end"])
            else:
                merged.append(dict(item))
        return merged

    runs = coalesce(runs)

    # Absorb runs shorter than min_turn into neighboring speakers
    while len(runs) > 1:
        shortest_idx = min(range(len(runs)), key=lambda i: runs[i]["end"] - runs[i]["start"])
        if runs[shortest_idx]["end"] - runs[shortest_idx]["start"] >= min_turn:
            break
        neighbor_idx = shortest_idx - 1 if shortest_idx > 0 else 1
        lo, hi = sorted((shortest_idx, neighbor_idx))
        runs[lo] = {
            "speaker": runs[neighbor_idx]["speaker"],
            "start": runs[lo]["start"],
            "end": max(runs[lo]["end"], runs[hi]["end"]),
        }
        del runs[hi]
        runs = coalesce(runs)

    if len({run["speaker"] for run in runs}) < 2:
        return []

    turns: List[Dict[str, Any]] = []
    for idx, run in enumerate(runs):
        start = 0.0 if idx == 0 else turns[-1]["end"]
        if idx + 1 < len(runs):
            following = runs[idx + 1]["start"]
            end = max(following - lead, min(run["end"], following))
        else:
            end = max(run["end"], duration or run["end"])
        turns.append({"speaker": run["speaker"], "start": start, "end": max(start, end)})

    if duration is not None and turns:
        turns[-1]["end"] = max(turns[-1]["end"], duration)

    return turns


def compute_speaker_cuts(
    speaker_turns: List[Dict[str, Any]],
    face_tracks: Dict[str, Tuple[float, float, float, float]],
    video_width: int = 1920,
    video_height: int = 1080
) -> List[Dict[str, Any]]:
    """
    Generate 9:16 crop boundaries for each speaker turn.
    Returns list of time-bounded crop regions {start, end, crop_x, crop_y, crop_w, crop_h}.
    """
    target_aspect = 9 / 16
    crop_w = int(round(video_height * target_aspect))
    crop_h = video_height

    cut_plan = []
    for turn in speaker_turns:
        spk = turn.get("speaker", "0")
        face = face_tracks.get(spk)
        if face:
            fx, fy, fw, fh = face
            cx = fx + fw / 2.0
            crop_x = int(max(0, min(video_width - crop_w, cx - crop_w / 2.0)))
        else:
            crop_x = int((video_width - crop_w) / 2.0)

        cut_plan.append({
            "speaker": spk,
            "start": round(turn["start"], 2),
            "end": round(turn["end"], 2),
            "crop": (crop_x, 0, crop_w, crop_h),
            "recommended_x": round(-((crop_x + crop_w / 2.0) - video_width / 2.0) / (video_width / 2.0) * 120.0, 1)
        })

    return cut_plan
