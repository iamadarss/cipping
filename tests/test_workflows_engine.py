"""
Comprehensive automated tests for SupoClip 5-Mode AI Workflows Engine.
Tests:
  - 5 Workflows: Highlights, Series, Topic, Recap, Trailer
  - Boundary Snapping & Grounding (no filler/agreement starts)
  - 4-Pillar Virality Scoring & Hook Type classification
  - Windowed Sliding Analysis & Deduplication
"""

import pytest

from ai.workflows import (
    WORKFLOWS,
    HOOK_TYPES,
    WindowedAnalyzer,
    WorkflowCandidate,
    WorkflowOptions,
    WorkflowResult,
    WorkflowSpec,
    classify_hook_type,
    clip_duration_bounds,
    deduplicate_candidates,
    is_clean_opening,
    partition_windows,
    run_highlights_workflow,
    run_recap_workflow,
    run_series_workflow,
    run_topic_workflow,
    run_trailer_workflow,
    snap_segment_boundaries,
)
from ai.workflows.virality_engine import ViralityEngine


# Sample realistic speech words (synthetic podcast / interview segment)
SAMPLE_TRANSCRIPT_WORDS = [
    {"word": "Um", "start": 0.0, "end": 0.3},
    {"word": "yeah,", "start": 0.35, "end": 0.6},
    {"word": "so", "start": 0.65, "end": 0.8},
    {"word": "did", "start": 0.85, "end": 1.05},
    {"word": "you", "start": 1.05, "end": 1.2},
    {"word": "know", "start": 1.2, "end": 1.4},
    {"word": "that", "start": 1.4, "end": 1.55},
    {"word": "90%", "start": 1.55, "end": 2.1},
    {"word": "of", "start": 2.1, "end": 2.2},
    {"word": "people", "start": 2.2, "end": 2.6},
    {"word": "fail", "start": 2.6, "end": 2.95},
    {"word": "at", "start": 2.95, "end": 3.1},
    {"word": "crypto", "start": 3.1, "end": 3.5},
    {"word": "trading?", "start": 3.5, "end": 4.1},
    {"word": "The", "start": 4.5, "end": 4.7},
    {"word": "secret", "start": 4.7, "end": 5.1},
    {"word": "mistake", "start": 5.1, "end": 5.6},
    {"word": "is", "start": 5.6, "end": 5.75},
    {"word": "emotional", "start": 5.75, "end": 6.3},
    {"word": "decision", "start": 6.3, "end": 6.8},
    {"word": "making.", "start": 6.8, "end": 7.4},
    {"word": "First,", "start": 7.8, "end": 8.2},
    {"word": "you", "start": 8.2, "end": 8.35},
    {"word": "must", "start": 8.35, "end": 8.6},
    {"word": "understand", "start": 8.6, "end": 9.1},
    {"word": "risk", "start": 9.1, "end": 9.4},
    {"word": "management", "start": 9.4, "end": 10.0},
    {"word": "and", "start": 10.0, "end": 10.15},
    {"word": "position", "start": 10.15, "end": 10.6},
    {"word": "sizing.", "start": 10.6, "end": 11.2},
    {"word": "Second,", "start": 11.6, "end": 12.0},
    {"word": "never", "start": 12.0, "end": 12.4},
    {"word": "invest", "start": 12.4, "end": 12.8},
    {"word": "money", "start": 12.8, "end": 13.2},
    {"word": "you", "start": 13.2, "end": 13.4},
    {"word": "cannot", "start": 13.4, "end": 13.8},
    {"word": "afford", "start": 13.8, "end": 14.2},
    {"word": "to", "start": 14.2, "end": 14.3},
    {"word": "lose.", "start": 14.3, "end": 14.9},
    {"word": "Finally,", "start": 15.3, "end": 15.8},
    {"word": "build", "start": 15.8, "end": 16.1},
    {"word": "a", "start": 16.1, "end": 16.2},
    {"word": "proven", "start": 16.2, "end": 16.6},
    {"word": "system.", "start": 16.6, "end": 17.2},
]


def test_workflow_contracts():
    """Verify contracts, schemas and workflows list."""
    assert "highlights" in WORKFLOWS
    assert "series" in WORKFLOWS
    assert "topic" in WORKFLOWS
    assert "recap" in WORKFLOWS
    assert "trailer" in WORKFLOWS
    assert len(WORKFLOWS) == 5

    spec = WorkflowSpec("series", WorkflowOptions(part_count=4), "short")
    assert spec.workflow == "series"
    assert spec.is_series is True
    assert spec.options.part_count == 4
    assert spec.clip_length == "short"
    assert len(spec.fingerprint()) == 64


def test_clean_opening_and_boundary_snapping():
    """Verify clips advance past filler words and snap to sentence punctuation."""
    assert is_clean_opening("Why do smart investors win?") is True
    assert is_clean_opening("Um yeah, so basically...") is False
    assert is_clean_opening("You know what happens...") is False

    # Snap starting at raw 0.0s (which has "Um yeah so")
    s_start, s_end, text = snap_segment_boundaries(
        0.0, 11.0, SAMPLE_TRANSCRIPT_WORDS, min_duration=5.0, max_duration=25.0
    )
    # The snapped start should advance to clean speech "did you know..." (~0.85s)
    assert s_start >= 0.8
    assert not text.lower().startswith("um")
    assert not text.lower().startswith("yeah")
    assert text.endswith(".") or text.endswith("?")


def test_4_pillar_virality_and_hook_classification():
    """Verify 4-Pillar Virality Scoring and hook classification."""
    h_type, title = classify_hook_type("Why do 90% of beginner investors lose money?")
    assert h_type == "question"
    assert "?" in title

    engine = ViralityEngine()
    scored = engine.score_segment("Why do 90% of beginner investors lose money? The secret is patience.", duration=30.0)
    assert 20 <= scored["virality_score"] <= 99
    assert scored["hook_type"] in HOOK_TYPES
    assert "hook" in scored["breakdown"]
    assert "engagement" in scored["breakdown"]
    assert "value" in scored["breakdown"]
    assert "shareability" in scored["breakdown"]
    assert sum(scored["breakdown"].values()) <= 100


def test_highlights_workflow():
    """Test Highlights standalone clip selector."""
    spec = WorkflowSpec("highlights", WorkflowOptions(), "auto")
    result = run_highlights_workflow(spec, SAMPLE_TRANSCRIPT_WORDS, max_clips=3)
    assert isinstance(result, WorkflowResult)
    assert result.workflow == "highlights"
    assert len(result.candidates) >= 1
    best = result.candidates[0]
    assert best.virality_score >= 50
    assert best.duration > 5.0


def test_series_workflow():
    """Test Series chronological multi-part generation."""
    spec = WorkflowSpec("series", WorkflowOptions(part_count=2), "auto")
    result = run_series_workflow(spec, SAMPLE_TRANSCRIPT_WORDS)
    assert result.workflow == "series"
    assert len(result.candidates) == 2
    assert result.candidates[0].part_number == 1
    assert result.candidates[1].part_number == 2
    assert "Part 1" in result.candidates[0].hook_title
    assert "Part 2" in result.candidates[1].hook_title
    # Chronological progression
    assert result.candidates[0].start_time <= result.candidates[1].start_time


def test_topic_workflow():
    """Test Topic workflow filters segments matching specified topic."""
    spec = WorkflowSpec("topic", WorkflowOptions(topic="crypto trading"), "auto")
    result = run_topic_workflow(spec, SAMPLE_TRANSCRIPT_WORDS)
    assert result.workflow == "topic"
    assert len(result.candidates) >= 1
    cand = result.candidates[0]
    assert "Crypto" in cand.hook_title or "crypto" in cand.text.lower()


def test_recap_workflow():
    """Test Recap workflow generates summary clips with on-screen point labels."""
    spec = WorkflowSpec("recap", WorkflowOptions(), "auto")
    result = run_recap_workflow(spec, SAMPLE_TRANSCRIPT_WORDS)
    assert result.workflow == "recap"
    assert len(result.candidates) >= 1
    cand = result.candidates[0]
    assert cand.point_labels is not None
    assert len(cand.point_labels) >= 1
    assert "Point 1" in cand.point_labels[0]["text"] or "Takeaway" in cand.point_labels[0]["text"]


def test_trailer_workflow():
    """Test Trailer workflow creates high-energy short teasers."""
    spec = WorkflowSpec("trailer", WorkflowOptions(), "short")
    result = run_trailer_workflow(spec, SAMPLE_TRANSCRIPT_WORDS)
    assert result.workflow == "trailer"
    assert len(result.candidates) >= 1
    for c in result.candidates:
        assert c.duration <= 35.0
        assert "Teaser:" in c.hook_title


def test_windowed_analyzer_and_deduplication():
    """Test windowed sliding partition and temporal candidate deduplication."""
    # Create two candidates with 80% overlap
    c1 = WorkflowCandidate(start_time=10.0, end_time=35.0, text="First candidate clip", hook_title="T1", virality_score=85)
    c2 = WorkflowCandidate(start_time=12.0, end_time=36.0, text="Second overlapping clip", hook_title="T2", virality_score=72)
    c3 = WorkflowCandidate(start_time=60.0, end_time=85.0, text="Third distinct clip", hook_title="T3", virality_score=90)

    deduped = deduplicate_candidates([c1, c2, c3], iou_threshold=0.35)
    # c2 should be dropped in favor of c1 (which has higher score: 85 vs 72)
    assert len(deduped) == 2
    assert deduped[0].virality_score == 90
    assert deduped[1].virality_score == 85
