"""
Windowed Sliding Analysis Engine for UpClip Studio.
Enables fast, scalable analysis of long-form videos (1 - 3+ hour podcasts & streams).

Mechanics:
  1. Partitions long transcripts into 12-minute sliding windows with 2-minute overlaps.
  2. Processes windows concurrently using a worker pool.
  3. Deduplicates overlapping candidates using temporal IoU (> 0.35).
  4. Global reranking pass integrates creator performance history context.
"""

from __future__ import annotations

import concurrent.futures
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

from ai.workflows.contracts import (
    WorkflowCandidate,
    WorkflowResult,
    WorkflowSpec,
)
from ai.workflows.highlights import run_highlights_workflow
from ai.workflows.recap import run_recap_workflow
from ai.workflows.series import run_series_workflow
from ai.workflows.topic import run_topic_workflow
from ai.workflows.trailer import run_trailer_workflow

logger = logging.getLogger(__name__)

WINDOW_SIZE_SECONDS = 720.0  # 12 minutes
WINDOW_OVERLAP_SECONDS = 120.0  # 2 minutes overlap
MAX_PARALLEL_WORKERS = 4


def partition_windows(
    words: List[Dict[str, Any]],
    window_size: float = WINDOW_SIZE_SECONDS,
    overlap: float = WINDOW_OVERLAP_SECONDS,
) -> List[Tuple[float, float, List[Dict[str, Any]]]]:
    """Partition word sequence into overlapping time windows."""
    if not words:
        return []

    total_start = float(words[0].get("start", 0.0))
    total_end = float(words[-1].get("end", 0.0))
    total_span = total_end - total_start

    # If shorter than 15 minutes, single window suffices
    if total_span <= window_size + 180.0:
        return [(total_start, total_end, words)]

    windows: List[Tuple[float, float, List[Dict[str, Any]]]] = []
    step = window_size - overlap
    curr_start = total_start

    while curr_start < total_end:
        curr_end = min(total_end, curr_start + window_size)
        win_words = [
            w for w in words
            if curr_start <= float(w.get("start", 0.0)) < curr_end
        ]
        if win_words:
            windows.append((curr_start, curr_end, win_words))
        if curr_end >= total_end:
            break
        curr_start += step

    return windows


def deduplicate_candidates(
    candidates: List[WorkflowCandidate], iou_threshold: float = 0.35
) -> List[WorkflowCandidate]:
    """
    Remove overlapping candidate segments from adjacent windows.
    Keeps the higher-scoring candidate.
    """
    # Sort descending by virality score
    sorted_cands = sorted(candidates, key=lambda c: c.virality_score, reverse=True)
    kept: List[WorkflowCandidate] = []

    for cand in sorted_cands:
        collision = False
        for existing in kept:
            # Overlap interval
            inter = max(
                0.0,
                min(cand.end_time, existing.end_time) - max(cand.start_time, existing.start_time),
            )
            if inter > 3.0:
                union = max(cand.end_time, existing.end_time) - min(cand.start_time, existing.start_time)
                iou = inter / max(0.1, union)
                if iou >= iou_threshold:
                    collision = True
                    break
        if not collision:
            kept.append(cand)

    return kept


class WindowedAnalyzer:
    """Executes windowed parallel processing of long audio/video transcripts."""

    def __init__(self, spec: WorkflowSpec, performance_context: Optional[str] = None):
        self.spec = spec
        self.performance_context = performance_context

    def _execute_window(
        self, window_data: Tuple[float, float, List[Dict[str, Any]]]
    ) -> List[WorkflowCandidate]:
        w_start, w_end, win_words = window_data
        wf = self.spec.workflow

        if wf == "series":
            res = run_series_workflow(self.spec, win_words, self.performance_context)
        elif wf == "topic":
            res = run_topic_workflow(self.spec, win_words, self.performance_context)
        elif wf == "recap":
            res = run_recap_workflow(self.spec, win_words, self.performance_context)
        elif wf == "trailer":
            res = run_trailer_workflow(self.spec, win_words, self.performance_context)
        else:
            res = run_highlights_workflow(self.spec, win_words, performance_context=self.performance_context)

        return res.candidates

    def analyze(
        self,
        words: List[Dict[str, Any]],
        max_clips: int = 12,
        progress_cb: Optional[Callable[[int, str], None]] = None,
    ) -> WorkflowResult:
        """Run windowed parallel analysis across the entire video transcript."""
        windows = partition_windows(words)
        total_windows = len(windows)

        if progress_cb:
            progress_cb(10, f"Partitioned into {total_windows} analysis window(s)...")

        all_candidates: List[WorkflowCandidate] = []

        if total_windows <= 1:
            all_candidates = self._execute_window(windows[0]) if windows else []
        else:
            # Parallel execution
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(MAX_PARALLEL_WORKERS, total_windows)) as pool:
                futures = {pool.submit(self._execute_window, win): idx for idx, win in enumerate(windows)}
                done_count = 0
                for fut in concurrent.futures.as_completed(futures):
                    try:
                        cands = fut.result()
                        all_candidates.extend(cands)
                    except Exception as err:
                        logger.warning("Error analyzing window: %s", err)
                    done_count += 1
                    if progress_cb:
                        pct = int(15 + (done_count / total_windows) * 60)
                        progress_cb(pct, f"Analyzed window {done_count}/{total_windows}...")

        if progress_cb:
            progress_cb(80, "Deduplicating and reranking viral candidate clips...")

        # Global deduplication
        deduped = deduplicate_candidates(all_candidates)

        # Global top-N selection
        if self.spec.workflow == "series":
            # Keep series in chronological order
            final_cands = sorted(deduped[:max_clips], key=lambda c: c.start_time)
            # Re-index parts
            for idx, c in enumerate(final_cands):
                c.part_number = idx + 1
                c.part_count = len(final_cands)
                c.hook_title = f"Part {idx+1}: {c.hook_title.split(':', 1)[-1].strip()}"
        else:
            final_cands = sorted(deduped, key=lambda c: c.virality_score, reverse=True)[:max_clips]

        if progress_cb:
            progress_cb(100, f"Complete: {len(final_cands)} viral candidate clips selected.")

        summary = (
            f"Analyzed {total_windows} window(s). Selected {len(final_cands)} top viral clips "
            f"using '{self.spec.workflow}' workflow."
        )

        return WorkflowResult(
            workflow=self.spec.workflow,
            candidates=final_cands,
            summary=summary,
            key_topics=[c.hook_type for c in final_cands],
            spec_fingerprint=self.spec.fingerprint(),
        )

