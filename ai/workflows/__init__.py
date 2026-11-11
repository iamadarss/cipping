"""
UpClip Studio AI Workflows Engine.
Exposes:
  - WORKFLOWS: ('highlights', 'series', 'topic', 'recap', 'trailer')
  - WorkflowOptions, WorkflowSpec, WorkflowCandidate, WorkflowResult
  - ViralityEngine, WindowedAnalyzer
  - run_highlights_workflow, run_series_workflow, run_topic_workflow, run_recap_workflow, run_trailer_workflow
"""

from ai.workflows.contracts import (
    WORKFLOWS,
    HOOK_TYPES,
    CLIP_LENGTHS,
    Workflow,
    HookType,
    WorkflowOptions,
    WorkflowSpec,
    WorkflowCandidate,
    WorkflowResult,
    clip_duration_bounds,
    normalize_clip_length,
)
from ai.workflows.boundary_snapping import is_clean_opening, snap_segment_boundaries
from ai.workflows.virality_engine import ViralityEngine, classify_hook_type
from ai.workflows.highlights import run_highlights_workflow
from ai.workflows.series import run_series_workflow
from ai.workflows.topic import run_topic_workflow
from ai.workflows.recap import run_recap_workflow
from ai.workflows.trailer import run_trailer_workflow
from ai.workflows.windowed_analyzer import WindowedAnalyzer, partition_windows, deduplicate_candidates

__all__ = [
    "WORKFLOWS",
    "HOOK_TYPES",
    "CLIP_LENGTHS",
    "Workflow",
    "HookType",
    "WorkflowOptions",
    "WorkflowSpec",
    "WorkflowCandidate",
    "WorkflowResult",
    "clip_duration_bounds",
    "normalize_clip_length",
    "is_clean_opening",
    "snap_segment_boundaries",
    "ViralityEngine",
    "classify_hook_type",
    "run_highlights_workflow",
    "run_series_workflow",
    "run_topic_workflow",
    "run_recap_workflow",
    "run_trailer_workflow",
    "WindowedAnalyzer",
    "partition_windows",
    "deduplicate_candidates",
]

