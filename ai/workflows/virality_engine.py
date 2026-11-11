"""
4-Pillar Virality Scoring & Classification Engine for UpClip Studio.

Virality Score (0 - 100) = Hook (0 - 25) + Engagement (0 - 25) + Value (0 - 25) + Shareability (0 - 25)
Includes Hook Type classification and steering via creator audience performance data.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from ai.emoji_captions import normalize_token, POWER_WORDS
from ai.workflows.contracts import HookType


# ---------------------------------------------------------------------------
# Hook Type Detection Patterns
# ---------------------------------------------------------------------------

QUESTION_PATTERNS = [
    r"^(why|how|what|when|where|who|which|did you|have you|can you|is it|are you|do you|would you)\b",
    r"\?$",
]

STATISTIC_PATTERNS = [
    r"\b\d+([.,]\d+)?\s*(%|percent|million|billion|thousand|k|x|dollars?|\$)\b",
    r"\$\d+",
    r"\b(one|two|three|five|ten|100)\s+(reasons|ways|mistakes|rules|steps|tips)\b",
]

CONTRAST_PATTERNS = [
    r"\b(stop|never|don't|instead of|most people think|everyone believes|the truth is|nobody talks about)\b",
    r"\b(but actually|in reality|the difference between)\b",
]

STORY_PATTERNS = [
    r"\b(when i was|years ago|i remember|one day|this happened|my first|i used to|last year)\b",
    r"\b(he told me|she said to me|i realized)\b",
]

VALUE_WORDS = {
    "secret", "mistake", "step", "rule", "framework", "strategy", "tip", "hack",
    "lesson", "method", "system", "formula", "blueprint", "guide", "tactic",
    "advice", "solve", "improve", "grow", "scale", "money", "profit", "wealth",
}


def classify_hook_type(text: str) -> Tuple[HookType, str]:
    """
    Classify the opening hook type and generate a short punchy hook title.
    Returns: (hook_type, suggested_hook_title)
    """
    clean = text.strip()
    words = clean.split()
    first_chunk = " ".join(words[:15]).lower()

    # 1. Question hook
    if any(re.search(p, first_chunk) for p in QUESTION_PATTERNS) or "?" in " ".join(words[:12]):
        title = " ".join(words[:7]).rstrip(",.!? ") + "?"
        return ("question", title)

    # 2. Statistic / Number hook
    if any(re.search(p, first_chunk) for p in STATISTIC_PATTERNS):
        title = " ".join(words[:6]).rstrip(",.!? ")
        return ("statistic", title)

    # 3. Contrast / Contrarian hook
    if any(re.search(p, first_chunk) for p in CONTRAST_PATTERNS):
        title = " ".join(words[:7]).rstrip(",.!? ")
        return ("contrast", title)

    # 4. Story hook
    if any(re.search(p, first_chunk) for p in STORY_PATTERNS):
        title = " ".join(words[:6]).rstrip(",.!? ")
        return ("story", title)

    # 5. Bold Statement
    if len(words) >= 3:
        title = " ".join(words[:6]).rstrip(",.!? ")
        return ("statement", title)

    return ("none", " ".join(words[:5]))


class ViralityEngine:
    """Calculates 4-Pillar Virality Score (0-100) with hook classification and audience steering."""

    def __init__(self, performance_context: Optional[str] = None):
        self.performance_context = performance_context or ""
        self._bias_weights = self._parse_performance_bias(self.performance_context)

    def _parse_performance_bias(self, context_str: str) -> Dict[str, float]:
        """Extract creator preferences from social performance history context."""
        biases = {"question": 1.0, "statistic": 1.0, "contrast": 1.0, "story": 1.0, "statement": 1.0}
        if not context_str:
            return biases

        lower = context_str.lower()
        if "question" in lower and ("highest" in lower or "top" in lower or "best" in lower):
            biases["question"] = 1.20
        if "statistic" in lower and ("highest" in lower or "top" in lower or "best" in lower):
            biases["statistic"] = 1.20
        if "contrast" in lower and ("highest" in lower or "top" in lower or "best" in lower):
            biases["contrast"] = 1.20

        return biases

    def score_segment(
        self,
        text: str,
        duration: float,
        audio_energy: float = 60.0,
        motion_score: float = 60.0,
    ) -> Dict[str, Any]:
        """
        Evaluate candidate segment across the 4 pillars.
        Returns:
            {
                "virality_score": int (0-100),
                "hook_type": HookType,
                "hook_title": str,
                "breakdown": {
                    "hook": int (0-25),
                    "engagement": int (0-25),
                    "value": int (0-25),
                    "shareability": int (0-25)
                }
            }
        """
        words = text.split()
        word_count = len(words)
        duration = max(1.0, float(duration))
        hook_type, suggested_title = classify_hook_type(text)

        # 1. Hook Pillar (0 - 25)
        hook_base = {
            "question": 23,
            "statistic": 22,
            "contrast": 21,
            "story": 19,
            "statement": 16,
            "none": 8,
        }.get(hook_type, 14)

        # Bias multiplier from creator's audience history
        multiplier = self._bias_weights.get(hook_type, 1.0)
        hook_score = int(min(25, round(hook_base * multiplier)))

        # 2. Engagement Pillar (0 - 25)
        # Optimal speech rate for vertical video: 2.2 to 3.8 words/sec
        wps = word_count / duration
        if 2.2 <= wps <= 3.8:
            pacing_pts = 14
        elif 1.8 <= wps < 2.2 or 3.8 < wps <= 4.4:
            pacing_pts = 10
        else:
            pacing_pts = 6

        # Audio & visual dynamics (0 to 11 pts)
        dyn_pts = int(round((audio_energy * 0.5 + motion_score * 0.5) / 100.0 * 11))
        engagement_score = min(25, max(4, pacing_pts + dyn_pts))

        # 3. Value Pillar (0 - 25)
        # Count value words and power words
        val_count = sum(1 for w in words if normalize_token(w) in VALUE_WORDS or normalize_token(w) in POWER_WORDS)
        if val_count >= 5:
            value_score = 24
        elif val_count >= 3:
            value_score = 20
        elif val_count >= 1:
            value_score = 15
        else:
            value_score = 10

        # 4. Shareability Pillar (0 - 25)
        # Sweet-spot length (25 - 55s), strong resolution, question/callout
        share_pts = 12
        if 22.0 <= duration <= 50.0:
            share_pts += 7
        elif 15.0 <= duration < 22.0 or 50.0 < duration <= 65.0:
            share_pts += 4

        if hook_type in ("question", "contrast", "statistic"):
            share_pts += 4
        if "?" in text or "!" in text:
            share_pts += 2

        shareability_score = min(25, max(5, share_pts))

        total_score = min(99, max(20, hook_score + engagement_score + value_score + shareability_score))

        return {
            "virality_score": total_score,
            "hook_type": hook_type,
            "hook_title": suggested_title,
            "breakdown": {
                "hook": hook_score,
                "engagement": engagement_score,
                "value": value_score,
                "shareability": shareability_score,
            },
        }

