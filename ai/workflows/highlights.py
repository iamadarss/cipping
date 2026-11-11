"""
Highlights Workflow Engine for UpClip Studio.
Extracts top standalone viral moments sorted by virality score.
Applies 4-pillar virality evaluation and strict boundary grounding.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from ai.workflows.boundary_snapping import snap_segment_boundaries
from ai.workflows.contracts import (
    WorkflowCandidate,
    WorkflowResult,
    WorkflowSpec,
    clip_duration_bounds,
)
from ai.workflows.virality_engine import ViralityEngine

logger = logging.getLogger(__name__)


def extract_candidate_chunks(
    words: List[Dict[str, Any]],
    target_min_dur: float = 20.0,
    target_max_dur: float = 60.0,
    step_words: int = 40,
) -> List[Tuple[float, float]]:
    """Scan word list and identify candidate time windows."""
    if not words:
        return []

    total_span = float(words[-1].get("end", 0.0)) - float(words[0].get("start", 0.0))
    eff_min_dur = min(target_min_dur, max(5.0, total_span * 0.6))

    candidates: List[Tuple[float, float]] = []
    total_words = len(words)
    idx = 0

    while idx < total_words:
        start_t = float(words[idx].get("start", 0.0))
        end_idx = idx
        while end_idx < total_words:
            curr_dur = float(words[end_idx].get("end", 0.0)) - start_t
            if curr_dur >= eff_min_dur:
                candidates.append((start_t, float(words[end_idx].get("end", 0.0))))
                break
            end_idx += 1
        idx += max(10, step_words)

    if not candidates and words:
        candidates.append((float(words[0].get("start", 0.0)), float(words[-1].get("end", 0.0))))

    return candidates


def run_highlights_workflow(
    spec: WorkflowSpec,
    words: List[Dict[str, Any]],
    audio_energy_map: Optional[Dict[str, float]] = None,
    performance_context: Optional[str] = None,
    max_clips: int = 10,
) -> WorkflowResult:
    """Execute the Highlights workflow: select the best standalone viral clips."""
    min_dur, max_dur = clip_duration_bounds(spec.clip_length)
    if words:
        total_span = float(words[-1].get("end", 0.0)) - float(words[0].get("start", 0.0))
        if total_span < min_dur:
            min_dur = max(5.0, total_span * 0.6)

    engine = ViralityEngine(performance_context=performance_context)
    raw_chunks = extract_candidate_chunks(words, target_min_dur=min_dur, target_max_dur=max_dur)
    scored_candidates: List[WorkflowCandidate] = []

    for raw_start, raw_end in raw_chunks:
        s_start, s_end, text = snap_segment_boundaries(
            raw_start, raw_end, words, min_duration=min_dur, max_duration=max_dur
        )
        dur = s_end - s_start
        if dur < min_dur or not text.strip():
            continue

        eval_res = engine.score_segment(text, dur)
        scored_candidates.append(
            WorkflowCandidate(
                start_time=s_start,
                end_time=s_end,
                text=text,
                hook_title=eval_res["hook_title"],
                hook_type=eval_res["hook_type"],
                virality_score=eval_res["virality_score"],
                breakdown=eval_res["breakdown"],
                summary=text[:160] + "...",
                tags=["highlight", eval_res["hook_type"]],
            )
        )

    # Sort descending by virality score
    scored_candidates.sort(key=lambda c: c.virality_score, reverse=True)

    # Deduplicate overlapping candidates (IoU / overlap > 40%)
    final_clips: List[WorkflowCandidate] = []
    for cand in scored_candidates:
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

    summary = f"Selected {len(final_clips)} top standalone viral highlight clips."
    topics = list({c.hook_type for c in final_clips})

    return WorkflowResult(
        workflow="highlights",
        candidates=final_clips,
        summary=summary,
        key_topics=topics,
        spec_fingerprint=spec.fingerprint(),
    )
