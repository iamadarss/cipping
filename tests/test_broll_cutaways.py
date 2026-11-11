"""
Automated unit tests for B-Roll Cutaway Engine (Pexels integration & timing guards).
"""

import pytest
from ai.broll import (
    extract_filmable_moments,
    plan_broll_cutaways,
    build_ffmpeg_broll_filter,
    EARLIEST_START_SECONDS,
    FILMABLE_KEYWORDS,
)


def test_filmable_keywords_catalog():
    """Verify filmable keywords catalog contains rich visual entities."""
    assert "money" in FILMABLE_KEYWORDS
    assert "laptop" in FILMABLE_KEYWORDS
    assert "crypto" in FILMABLE_KEYWORDS
    assert "sunset" in FILMABLE_KEYWORDS
    assert "workout" in FILMABLE_KEYWORDS


def test_extract_filmable_moments_guards():
    """Verify cutaways never trigger before EARLIEST_START_SECONDS (3.0s)."""
    words = [
        {"word": "money", "start": 1.0, "end": 1.5},  # Too early (under 3s)
        {"word": "car", "start": 4.5, "end": 5.0},    # Valid moment
        {"word": "laptop", "start": 8.0, "end": 8.5}, # Valid moment
        {"word": "crypto", "start": 29.5, "end": 30.0}, # Too late (within end guard of 30s clip)
    ]
    moments = extract_filmable_moments(words, clip_duration=30.0)
    assert len(moments) == 2
    # Both extracted moments must be >= EARLIEST_START_SECONDS
    for m_time, query in moments:
        assert m_time >= EARLIEST_START_SECONDS
        assert m_time <= 30.0 - 2.5


def test_build_ffmpeg_broll_filter():
    """Verify FFmpeg filter complex syntax for crossfading B-roll underneath captions."""
    cues = [
        {
            "query": "luxury car",
            "start": 4.0,
            "end": 6.5,
            "duration": 2.5,
            "video_path": "cache/pexels_1.mp4",
        }
    ]
    inputs, filter_str = build_ffmpeg_broll_filter("[v_base]", cues, width=1080, height=1920)
    assert "-i" in inputs
    assert "cache/pexels_1.mp4" in inputs
    assert "scale=1080:1920" in filter_str
    assert "overlay=0:0" in filter_str
    assert "between(t,4.0,6.5)" in filter_str

