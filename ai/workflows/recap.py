"""
Recap Workflow Engine for UpClip Studio.
Extracts executive summary takeaway clips and attaches on-screen point labels/badges.
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


def generate_point_labels_for_clip(
    words: List[Dict[str, Any]], clip_start: float, clip_end: float
) -> List[Dict[str, Any]]:
    """
    Detect transition points and key takeaway sentences within the clip,
    generating timed on-screen point badges (e.g. 'Point 1: The Insight').
    """
    duration = clip_end - clip_start
    if duration < 12.0:
        return [{"text": "Key Takeaway", "start": 0.0, "duration": 3.5}]

    labels = []
    # Identify sentence starters or transition words
    transition_words = {"first", "second", "third", "finally", "next", "also", "most importantly", "remember", "the key"}

    clip_words = [w for w in words if clip_start <= float(w.get("start", 0.0)) <= clip_end]
    point_idx = 1

    # First point at start
    labels.append({"text": f"Point {point_idx}: The Setup", "start": 0.0, "duration": 3.0})
    point_idx += 1

    # Look for internal points
    for idx, w in enumerate(clip_words):
        word_token = re.sub(r"[^A-Za-z0-9]", "", str(w.get("word", "")).lower())
        rel_time = float(w.get("start", 0.0)) - clip_start
        if rel_time > 8.0 and rel_time < duration - 6.0:
            if word_token in transition_words:
                context_phrase = " ".join(
                    str(clip_words[i].get("word", ""))
                    for i in range(idx, min(len(clip_words), idx + 4))
                ).title()
                labels.append({
                    "text": f"Point {point_idx}: {context_phrase}",
                    "start": round(rel_time, 2),
                    "duration": 3.0,
                })
                point_idx += 1
                if point_idx > 3:
                    break

    # If only 1 label found and duration is long enough, add a takeaway label near midpoint
    if len(labels) == 1 and duration >= 25.0:
        labels.append({
            "text": "Core Takeaway",
            "start": round(duration * 0.45, 2),
            "duration": 3.5,
        })

    return labels


def run_recap_workflow(
    spec: WorkflowSpec,
    words: List[Dict[str, Any]],
    performance_context: Optional[str] = None,
    max_clips: int = 5,
) -> WorkflowResult:
    """Execute the Recap workflow: summary clips with on-screen point badges."""
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

        eval_res = engine.score_segment(text, dur)
        point_labels = generate_point_labels_for_clip(words, s_start, s_end)
        hook_title = f"Recap: {eval_res['hook_title']}"

        candidates.append(
            WorkflowCandidate(
                start_time=s_start,
                end_time=s_end,
                text=text,
                hook_title=hook_title,
                hook_type=eval_res["hook_type"],
                virality_score=eval_res["virality_score"],
                breakdown=eval_res["breakdown"],
                point_labels=point_labels,
                summary=f"Recap Summary: {text[:140]}...",
                tags=["recap", "summary", eval_res["hook_type"]],
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

    summary = f"Generated {len(final_clips)} recap clips with on-screen point badges."
    return WorkflowResult(
        workflow="recap",
        candidates=final_clips,
        summary=summary,
        key_topics=["Executive Summary", "Key Takeaways"],
        spec_fingerprint=spec.fingerprint(),
    )
