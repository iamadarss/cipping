"""
Shared workflow contracts and data classes for UpClip Studio.
Defines specifications, candidate structures, and options for:
  - Highlights: Standalone viral clips
  - Series: Chronological multi-part stories (Part 1, Part 2...)
  - Topic: Segments strictly focused on user-specified topics
  - Recap: Executive summary with on-screen point badges
  - Trailer: High-energy fast-cut hype teaser
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple

WORKFLOWS: Tuple[str, ...] = ("highlights", "series", "topic", "recap", "trailer")
Workflow = Literal["highlights", "series", "topic", "recap", "trailer"]

HOOK_TYPES: Tuple[str, ...] = (
    "question",
    "statement",
    "statistic",
    "story",
    "contrast",
    "none",
)
HookType = Literal["question", "statement", "statistic", "story", "contrast", "none"]

CLIP_LENGTHS: Tuple[str, ...] = ("auto", "short", "medium", "long")


def normalize_clip_length(val: Optional[str]) -> str:
    if not val:
        return "auto"
    val = str(val).strip().lower()
    return val if val in CLIP_LENGTHS else "auto"


def clip_duration_bounds(length_pref: str) -> Tuple[float, float]:
    """Target min and max duration in seconds for given clip length preference."""
    pref = normalize_clip_length(length_pref)
    if pref == "short":
        return (15.0, 35.0)
    elif pref == "medium":
        return (30.0, 60.0)
    elif pref == "long":
        return (60.0, 95.0)
    return (20.0, 60.0)  # auto sweet spot for Shorts / Reels


@dataclass(frozen=True)
class WorkflowOptions:
    topic: str = ""
    part_count: Optional[int] = None
    instructions: str = ""
    advanced: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        if self.topic:
            out["topic"] = self.topic
        if self.part_count is not None:
            out["part_count"] = self.part_count
        if self.instructions:
            out["instructions"] = self.instructions
        if self.advanced:
            out["advanced"] = dict(sorted(self.advanced.items()))
        return out

    @classmethod
    def from_json(cls, raw: Any) -> "WorkflowOptions":
        if isinstance(raw, (str, bytes)):
            try:
                raw = json.loads(raw)
            except Exception:
                return cls()
        if not isinstance(raw, dict):
            return cls()
        part_count = raw.get("part_count")
        if isinstance(part_count, (int, float)):
            part_count = int(part_count)
            if not (2 <= part_count <= 20):
                part_count = None
        else:
            part_count = None

        return cls(
            topic=str(raw.get("topic") or "").strip(),
            part_count=part_count,
            instructions=str(raw.get("instructions") or "").strip(),
            advanced=raw.get("advanced") if isinstance(raw.get("advanced"), dict) else {},
        )

    def for_workflow(self, workflow: str) -> "WorkflowOptions":
        return WorkflowOptions(
            topic=self.topic if workflow == "topic" else "",
            part_count=self.part_count if workflow == "series" else None,
            instructions=self.instructions,
            advanced=self.advanced,
        )


@dataclass(frozen=True)
class WorkflowSpec:
    workflow: str = "highlights"
    options: WorkflowOptions = field(default_factory=WorkflowOptions)
    clip_length: str = "auto"

    def __post_init__(self):
        wf = self.workflow if self.workflow in WORKFLOWS else "highlights"
        cl = normalize_clip_length(self.clip_length)
        object.__setattr__(self, "workflow", wf)
        object.__setattr__(self, "clip_length", cl)

    @property
    def is_series(self) -> bool:
        return self.workflow == "series"

    @property
    def is_topic(self) -> bool:
        return self.workflow == "topic"

    @property
    def is_recap(self) -> bool:
        return self.workflow == "recap"

    @property
    def is_trailer(self) -> bool:
        return self.workflow == "trailer"

    def fingerprint(self) -> str:
        payload = {
            "workflow": self.workflow,
            "clip_length": self.clip_length,
            "topic": self.options.topic.lower(),
            "part_count": self.options.part_count,
            "instructions": hashlib.sha256(self.options.instructions.encode("utf-8")).hexdigest()[:16]
            if self.options.instructions
            else "",
            "advanced": self.options.advanced,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass
class WorkflowCandidate:
    start_time: float
    end_time: float
    text: str
    hook_title: str
    hook_type: HookType = "statement"
    virality_score: int = 70
    breakdown: Dict[str, int] = field(default_factory=dict)
    point_labels: Optional[List[Dict[str, Any]]] = None
    part_number: Optional[int] = None
    part_count: Optional[int] = None
    summary: str = ""
    tags: List[str] = field(default_factory=list)

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_time": round(self.start_time, 2),
            "end_time": round(self.end_time, 2),
            "duration": round(self.duration, 2),
            "text": self.text,
            "hook_title": self.hook_title,
            "hook_type": self.hook_type,
            "virality_score": int(self.virality_score),
            "breakdown": self.breakdown,
            "point_labels": self.point_labels,
            "part_number": self.part_number,
            "part_count": self.part_count,
            "summary": self.summary,
            "tags": self.tags,
        }


@dataclass
class WorkflowResult:
    workflow: str
    candidates: List[WorkflowCandidate]
    summary: str = ""
    key_topics: List[str] = field(default_factory=list)
    spec_fingerprint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow": self.workflow,
            "candidates": [c.to_dict() for c in self.candidates],
            "candidate_count": len(self.candidates),
            "summary": self.summary,
            "key_topics": self.key_topics,
            "spec_fingerprint": self.spec_fingerprint,
        }

