"""
Series Workflow Engine for UpClip Studio.
Extracts sequential chronological multi-part numbered episodes (Part 1, Part 2...).
Preserves narrative progression and tags each candidate with part badges.
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
from ai.workflows.virality_engine import ViralityEngine

logger = logging.getLogger(__name__)


def run_series_workflow(
    spec: WorkflowSpec,
    words: List[Dict[str, Any]],
    performance_context: Optional[str] = None,
) -> WorkflowResult:
    """Execute the Series workflow: chronological multi-part storytelling clips."""
    min_dur, max_dur = clip_duration_bounds(spec.clip_length)
    target_parts = spec.options.part_count or 3
    target_parts = max(2, min(target_parts, 10))

    if not words:
        return WorkflowResult(workflow="series", candidates=[], spec_fingerprint=spec.fingerprint())

    total_start = float(words[0].get("start", 0.0))
    total_end = float(words[-1].get("end", 0.0))
    total_duration = max(1.0, total_end - total_start)

    # Divide total duration into evenly spaced narrative regions
    chunk_span = total_duration / target_parts
    engine = ViralityEngine(performance_context=performance_context)
    series_candidates: List[WorkflowCandidate] = []

    for part_idx in range(target_parts):
        region_start = total_start + (part_idx * chunk_span)
        region_end = min(total_end, region_start + max_dur * 1.5)

        s_start, s_end, text = snap_segment_boundaries(
            region_start, region_start + ((min_dur + max_dur) / 2), words, min_duration=min_dur, max_duration=max_dur
        )
        dur = s_end - s_start
        if dur < min_dur:
            s_start, s_end, text = snap_segment_boundaries(
                region_start, min(total_end, region_start + min_dur), words, min_duration=10.0, max_duration=max_dur
            )
            dur = s_end - s_start

        eval_res = engine.score_segment(text, dur)
        part_num = part_idx + 1
        hook_title = f"Part {part_num}: {eval_res['hook_title']}"

        series_candidates.append(
            WorkflowCandidate(
                start_time=s_start,
                end_time=s_end,
                text=text,
                hook_title=hook_title,
                hook_type=eval_res["hook_type"],
                virality_score=eval_res["virality_score"],
                breakdown=eval_res["breakdown"],
                part_number=part_num,
                part_count=target_parts,
                summary=f"Episode {part_num} of {target_parts}: {text[:140]}...",
                tags=["series", f"part-{part_num}", eval_res["hook_type"]],
            )
        )

    summary = f"Generated {len(series_candidates)}-part chronological series."
    return WorkflowResult(
        workflow="series",
        candidates=series_candidates,
        summary=summary,
        key_topics=[f"Part {i+1}" for i in range(len(series_candidates))],
        spec_fingerprint=spec.fingerprint(),
    )

