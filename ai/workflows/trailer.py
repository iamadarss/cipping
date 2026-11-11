"""
Trailer Workflow Engine for UpClip Studio.
Extracts fast-paced high-energy hype teaser moments designed to drive viewers
to watch the full long-form video or episode.
"""

from __future__ import annotations

import logging
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


def run_trailer_workflow(
    spec: WorkflowSpec,
    words: List[Dict[str, Any]],
    performance_context: Optional[str] = None,
    max_clips: int = 4,
) -> WorkflowResult:
    """Execute the Trailer workflow: high-energy teaser hype clips."""
    min_dur, max_dur = clip_duration_bounds(spec.clip_length)
    min_dur = min(min_dur, 15.0)
    max_dur = min(max_dur, 35.0)

    if words:
        total_span = float(words[-1].get("end", 0.0)) - float(words[0].get("start", 0.0))
        min_dur = min(min_dur, max(5.0, total_span * 0.6))

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

        eval_res = engine.score_segment(text, dur)
        # Trailers reward high curiosity questions, statistics and contrasts
        bonus = 5 if eval_res["hook_type"] in ("question", "contrast", "statistic") else 0
        trailer_score = min(99, eval_res["virality_score"] + bonus)

        hook_title = f"Teaser: {eval_res['hook_title']}"
        candidates.append(
            WorkflowCandidate(
                start_time=s_start,
                end_time=s_end,
                text=text,
                hook_title=hook_title,
                hook_type=eval_res["hook_type"],
                virality_score=trailer_score,
                breakdown=eval_res["breakdown"],
                summary=f"Hype Teaser: {text[:130]}...",
                tags=["trailer", "teaser", "hype", eval_res["hook_type"]],
            )
        )

    candidates.sort(key=lambda c: c.virality_score, reverse=True)

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

    summary = f"Generated {len(final_clips)} fast-paced trailer teaser clips."
    return WorkflowResult(
        workflow="trailer",
        candidates=final_clips,
        summary=summary,
        key_topics=["Hype Teaser", "Full Video Preview"],
        spec_fingerprint=spec.fingerprint(),
    )
