"""
Automated B-Roll Cutaway Engine for UpClip Studio (via Pexels Stock Video API).

Features:
  1. Identifies filmable nouns and concepts from word-level transcripts.
  2. Queries Pexels for vertical portrait HD stock footage.
  3. Safe placement guards:
     - EARLIEST_START = 3.0s (never covers hook title or speaker face at clip opening)
     - END_GUARD = 1.0s
     - MIN_CUE = 1.5s, MAX_CUE = 3.5s
     - MIN_GAP = 3.0s between consecutive cutaways
  4. Local caching in output/broll_cache/ to minimize network and API usage.
  5. Crossfade composite generator for FFmpeg rendering.
"""

from __future__ import annotations

import json
import logging
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import config

logger = logging.getLogger(__name__)

PEXELS_SEARCH_URL = "https://api.pexels.com/videos/search"

# Cutaway Placement Parameters
EARLIEST_START_SECONDS = 3.0
END_GUARD_SECONDS = 1.0
MIN_CUE_SECONDS = 1.5
MAX_CUE_SECONDS = 3.5
MIN_GAP_SECONDS = 3.0
MAX_CUES_PER_CLIP = 3

# In-memory query cache: {query: (timestamp, [video_dicts])}
_SEARCH_CACHE: Dict[str, List[Dict[str, Any]]] = {}

# Filmable visual keyword dictionary
FILMABLE_KEYWORDS = {
    "money": "money cash dollars wealth",
    "dollar": "money dollars cash",
    "cash": "counting money cash",
    "wealth": "luxury lifestyle wealth",
    "rich": "luxury rich lifestyle",
    "crypto": "bitcoin cryptocurrency trading",
    "bitcoin": "bitcoin blockchain trading",
    "stock": "stock market trading chart",
    "market": "stock market trading",
    "invest": "financial investment growth",
    "car": "luxury sports car driving",
    "lamborghini": "supercar luxury driving",
    "laptop": "typing on laptop computer",
    "computer": "working on computer technology",
    "code": "software code programming screen",
    "coding": "programming developer screen",
    "phone": "smartphone scrolling mobile",
    "ai": "artificial intelligence robot tech",
    "robot": "robot technology future",
    "office": "modern office corporate workplace",
    "business": "business team meeting discussion",
    "meeting": "corporate team meeting conference",
    "travel": "airplane travel scenic flight",
    "airplane": "airplane flying clouds",
    "beach": "tropical beach ocean waves",
    "sunset": "golden hour sunset sky",
    "city": "modern city skyline aerial",
    "nature": "forest mountain nature scenic",
    "gym": "workout gym fitness training",
    "workout": "athlete workout fitness training",
    "coffee": "espresso coffee cup morning cafe",
    "crowd": "concert crowd festival audience",
    "success": "celebration victory success winning",
    "rocket": "space rocket launch smoke",
    "study": "studying books library reading",
}


def broll_configured() -> bool:
    """Return True if Pexels API key is present in environment or config."""
    key = getattr(config, "PEXELS_API_KEY", "") or os.environ.get("PEXELS_API_KEY", "")
    return bool(key and key.strip())


def get_pexels_api_key() -> str:
    return getattr(config, "PEXELS_API_KEY", "") or os.environ.get("PEXELS_API_KEY", "")


def extract_filmable_moments(
    words: List[Dict[str, Any]], clip_duration: float
) -> List[Tuple[float, str]]:
    """
    Find timestamps in transcript where a filmable concept is spoken.
    Returns: list of (word_start_time, pexels_query)
    """
    moments: List[Tuple[float, str]] = []
    if not words:
        return moments

    for w in words:
        w_start = float(w.get("start", 0.0))
        # Must be past initial hook title safe region
        if w_start < EARLIEST_START_SECONDS or w_start > clip_duration - END_GUARD_SECONDS - MIN_CUE_SECONDS:
            continue

        raw_token = re.sub(r"[^A-Za-z]", "", str(w.get("word", "")).lower())
        if raw_token in FILMABLE_KEYWORDS:
            query = FILMABLE_KEYWORDS[raw_token]
            moments.append((w_start, query))

    return moments


def search_pexels_videos(
    query: str, orientation: str = "portrait", per_page: int = 5
) -> List[Dict[str, Any]]:
    """Search Pexels API for vertical stock videos."""
    api_key = get_pexels_api_key()
    if not api_key:
        return []

    clean_query = " ".join(query.strip().split())[:60]
    cache_key = f"{clean_query}:{orientation}"
    if cache_key in _SEARCH_CACHE:
        return _SEARCH_CACHE[cache_key]

    params = urllib.parse.urlencode({
        "query": clean_query,
        "orientation": orientation,
        "per_page": per_page,
    })
    url = f"{PEXELS_SEARCH_URL}?{params}"

    req = urllib.request.Request(url, headers={"Authorization": api_key, "User-Agent": "UpClipStudio/2.0"})
    try:
        with urllib.request.urlopen(req, timeout=8.0) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                videos = data.get("videos", [])
                _SEARCH_CACHE[cache_key] = videos
                return videos
    except Exception as exc:
        logger.warning("Pexels search failed for '%s': %s", clean_query, exc)

    return []


def pick_best_video_file(video_entry: Dict[str, Any]) -> Optional[str]:
    """Extract best MP4 download link covering 1080x1920 (portrait)."""
    files = video_entry.get("video_files") or []
    portrait_files = []

    for f in files:
        if f.get("file_type") not in (None, "video/mp4"):
            continue
        link = f.get("link")
        if not link:
            continue
        w = int(f.get("width") or 0)
        h = int(f.get("height") or 0)
        if h >= w:  # portrait or square
            portrait_files.append((w * h, link))

    if portrait_files:
        # Choose highest resolution portrait
        portrait_files.sort(key=lambda x: x[0], reverse=True)
        return portrait_files[0][1]

    # Fallback to any mp4
    for f in files:
        if f.get("link"):
            return f.get("link")

    return None


def download_broll_cached(video_url: str, video_id: int) -> Optional[Path]:
    """Download stock video to local cache if not already present."""
    cache_dir = Path(getattr(config, "BROLL_CACHE_DIR", config.OUTPUT_DIR / "broll_cache"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    target = cache_dir / f"pexels_{video_id}.mp4"

    if target.exists() and target.stat().st_size > 10000:
        return target

    try:
        req = urllib.request.Request(video_url, headers={"User-Agent": "UpClipStudio/2.0"})
        with urllib.request.urlopen(req, timeout=20.0) as resp, open(target, "wb") as out_f:
            out_f.write(resp.read())
        return target
    except Exception as exc:
        logger.warning("Failed to download B-roll video %s: %s", video_id, exc)
        if target.exists():
            target.unlink(missing_ok=True)

    return None


def plan_broll_cutaways(
    words: List[Dict[str, Any]], clip_duration: float, max_cues: int = MAX_CUES_PER_CLIP
) -> List[Dict[str, Any]]:
    """
    Plan cutaway timings and download matching B-roll footage.
    Returns:
        List of cues:
        [
            {
                "query": "money cash",
                "start": 4.5,
                "end": 7.0,
                "duration": 2.5,
                "video_path": "path/to/pexels_123.mp4"
            }
        ]
    """
    if not broll_configured():
        return []

    moments = extract_filmable_moments(words, clip_duration)
    if not moments:
        return []

    cues: List[Dict[str, Any]] = []
    last_end = 0.0

    for m_time, query in moments:
        if len(cues) >= max_cues:
            break

        start = max(m_time, last_end + MIN_GAP_SECONDS)
        if start + MIN_CUE_SECONDS > clip_duration - END_GUARD_SECONDS:
            break

        # Calculate cue duration
        cue_dur = min(MAX_CUE_SECONDS, clip_duration - END_GUARD_SECONDS - start)
        if cue_dur < MIN_CUE_SECONDS:
            continue
        end = start + cue_dur

        # Search Pexels
        videos = search_pexels_videos(query)
        if not videos:
            continue

        selected_video = videos[0]
        vid_id = selected_video.get("id", 0)
        file_link = pick_best_video_file(selected_video)
        if not file_link:
            continue

        local_path = download_broll_cached(file_link, vid_id)
        if not local_path or not local_path.exists():
            continue

        cues.append({
            "query": query,
            "start": round(start, 2),
            "end": round(end, 2),
            "duration": round(cue_dur, 2),
            "video_path": str(local_path),
            "video_id": vid_id,
        })
        last_end = end

    return cues


def build_ffmpeg_broll_filter(
    base_stream: str, cues: List[Dict[str, Any]], width: int = 1080, height: int = 1920
) -> Tuple[List[str], str]:
    """
    Construct FFmpeg filter complex snippets to overlay cutaways with fade transitions.
    Returns: (input_args, filter_str)
    """
    if not cues:
        return [], base_stream

    inputs = []
    current_stream = base_stream
    filter_parts = []

    for idx, cue in enumerate(cues):
        input_idx = idx + 1
        inputs.extend(["-i", cue["video_path"]])

        # Scale and loop/trim cutaway video
        scaled_stream = f"[broll_{idx}]"
        start = cue["start"]
        dur = cue["duration"]
        filter_parts.append(
            f"[{input_idx}:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},setsar=1,fade=t=in:st=0:d=0.25:alpha=1,"
            f"fade=t=out:st={dur-0.25}:d=0.25:alpha=1{scaled_stream}"
        )

        next_stream = f"[v_broll_{idx}]"
        filter_parts.append(
            f"{current_stream}{scaled_stream}overlay=0:0:enable='between(t,{start},{start+dur})':eof_action=pass{next_stream}"
        )
        current_stream = next_stream

    return inputs, ";".join(filter_parts)

