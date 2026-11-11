"""
Topic Workflow Engine for UpClip Studio.
Extracts clips tightly focused around a user-specified topic or keyword.
Ranks candidates by combining topic relevance density with virality potential.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from ai.workflows.boundary_snapping import snap_segment_boundaries
from ai.workflows.contracts import (
    WorkflowCandidate,
    WorkflowResult,
    WorkflowSpec,
    clip_duration_bounds,
)
from ai.workflows.highlights import extract_candidate_chunks
from ai.workflows.virality_engine import ViralityEngine

logger = logging.getLogger(__name__)


def compute_topic_relevance(text: str, topic: str) -> float:
    """Compute lexical and semantic keyword matching score (0.0 to 1.0)."""
    if not topic or not text:
        return 0.5
    clean_topic = topic.strip().lower()
    topic_terms = [t for t in re.split(r"[\s,]+", clean_topic) if t]
    if not topic_terms:
        return 0.5

    clean_text = text.lower()
    matches = 0
    for term in topic_terms:
        matches += len(re.findall(r"\b" + re.escape(term) + r"\b", clean_text))

    # Density score
    words = clean_text.split()
    density = matches / max(1, len(words))
    # Normalized score between 0.0 and 1.0
    score = min(1.0, (matches * 0.25) + (density * 5.0))
    return score


def run_topic_workflow(
    spec: WorkflowSpec,
    words: List[Dict[str, Any]],
    performance_context: Optional[str] = None,
    max_clips: int = 8,
) -> WorkflowResult:
    """Execute the Topic workflow: find the best clips focusing on spec.options.topic."""
    topic = spec.options.topic or "Key Discussion"
    min_dur, max_dur = clip_duration_bounds(spec.clip_length)
    if words:
        total_span = float(words[-1].get("end", 0.0)) - float(words[0].get("start", 0.0))
        if total_span < min_dur:
            min_dur = max(5.0, total_span * 0.6)

    engine = ViralityEngine(performance_context=performance_context)

    raw_chunks = extract_candidate_chunks(words, target_min_dur=min_dur, target_max_dur=max_dur)
    candidates: List[WorkflowCandidate] = []

    for raw_start, raw_end in raw_chunks:
        s_start, s_end, text = snap_segment_boundaries(
            raw_start, raw_end, words, min_duration=min_dur, max_duration=max_dur
        )
        dur = s_end - s_start
        if dur < min_dur or not text.strip():
            continue

        relevance = compute_topic_relevance(text, topic)
        if relevance < 0.15:
            # Skip chunks with negligible topic mention
            continue

        eval_res = engine.score_segment(text, dur)
        # Combined weighted score
        combined_score = int(round(eval_res["virality_score"] * 0.60 + (relevance * 100.0) * 0.40))
        combined_score = min(99, max(25, combined_score))

        hook_title = f"{topic.title()}: {eval_res['hook_title']}"
        candidates.append(
            WorkflowCandidate(
                start_time=s_start,
                end_time=s_end,
                text=text,
                hook_title=hook_title,
                hook_type=eval_res["hook_type"],
                virality_score=combined_score,
                breakdown=eval_res["breakdown"],
                summary=f"Topic [{topic}]: {text[:140]}...",
                tags=["topic", topic.lower(), eval_res["hook_type"]],
            )
        )

    # Sort by score
    candidates.sort(key=lambda c: c.virality_score, reverse=True)

    # Deduplicate overlapping candidates
    final_clips: List[WorkflowCandidate] = []
    for cand in candidates:
        overlap = False
        for chosen in final_clips:
            inter = max(0.0, min(cand.end_time, chosen.end_time) - max(cand.start_time, chosen.start_time))
            if inter > 5.0 and inter / min(cand.duration, chosen.duration) > 0.40:
                overlap = True
                break
        if not overlap:
            final_clips.append(cand)
        if len(final_clips) >= max_clips:
            break

    summary = f"Selected {len(final_clips)} clips matching topic: '{topic}'."
    return WorkflowResult(
        workflow="topic",
        candidates=final_clips,
        summary=summary,
        key_topics=[topic],
        spec_fingerprint=spec.fingerprint(),
    )
