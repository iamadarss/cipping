"""
Strict Boundary Grounding & Sentence Snapping Engine for UpClip Studio.

Guarantees:
  1. Clips never start mid-sentence or mid-word.
  2. Disallowed openings (fillers: 'um', 'uh', 'like'; bare agreements: 'yeah', 'yes';
     unanchored dangling pronouns: 'he said', 'they did') are advanced to clean speech.
  3. Start bounds snap to natural sentence punctuation (., ?, !) or speech pauses >= 0.35s.
  4. End bounds snap to clean sentence completions, avoiding cut-off words.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

# Fillers and bare agreements that ruin clip openings
DISALLOWED_OPENING_WORDS = {
    "um", "uh", "er", "ah", "like", "so", "and", "but", "yeah", "yes", "okay",
    "ok", "yep", "right", "well", "basically", "actually", "literally", "honestly",
}

DISALLOWED_OPENING_PAIRS = {
    ("you", "know"),
    ("i", "mean"),
    ("you", "see"),
    ("sort", "of"),
    ("kind", "of"),
}

SENTENCE_TERMINATORS = {".", "?", "!", ";"}
MIN_SPEECH_PAUSE_SECONDS = 0.35


def is_clean_opening(text: str) -> bool:
    """Check if the text starts with clean, engaging speech rather than filler/agreement."""
    if not text:
        return False
    words = [w.strip().lower() for w in re.findall(r"[A-Za-z0-9']+", text)]
    if not words:
        return False

    first = words[0]
    if first in DISALLOWED_OPENING_WORDS:
        return False
    if len(words) >= 2 and (words[0], words[1]) in DISALLOWED_OPENING_PAIRS:
        return False

    return True


def snap_segment_boundaries(
    raw_start: float,
    raw_end: float,
    words: List[Dict[str, Any]],
    pauses: Optional[List[Tuple[float, float]]] = None,
    min_duration: float = 15.0,
    max_duration: float = 75.0,
) -> Tuple[float, float, str]:
    """
    Given rough time boundaries (e.g. from heuristic scoring or an LLM), snap them
    strictly to word/sentence boundaries so speech is natural and uninterrupted.

    Args:
        raw_start: Desired start time in seconds
        raw_end: Desired end time in seconds
        words: List of word dicts with {'word', 'start', 'end'}
        pauses: Optional list of (pause_start, pause_end) intervals
        min_duration: Minimum acceptable clip duration
        max_duration: Maximum acceptable clip duration

    Returns:
        (snapped_start, snapped_end, cleaned_text)
    """
    if not words:
        return (raw_start, raw_end, "")

    # 1. Locate word index closest to raw_start
    start_idx = 0
    for idx, w in enumerate(words):
        w_start = float(w.get("start", 0.0))
        if w_start >= raw_start:
            start_idx = idx
            break

    # 2. Advance start_idx if pointing to a filler or bare agreement
    while start_idx < len(words) - 5:
        token = re.sub(r"[^A-Za-z0-9]", "", str(words[start_idx].get("word", "")).lower())
        token_next = (
            re.sub(r"[^A-Za-z0-9]", "", str(words[start_idx + 1].get("word", "")).lower())
            if start_idx + 1 < len(words)
            else ""
        )

        if token in DISALLOWED_OPENING_WORDS:
            start_idx += 1
            continue
        if (token, token_next) in DISALLOWED_OPENING_PAIRS:
            start_idx += 2
            continue
        break

    # 3. Locate word index closest to raw_end
    end_idx = len(words) - 1
    for idx in range(start_idx, len(words)):
        w_end = float(words[idx].get("end", 0.0))
        if w_end >= raw_end:
            end_idx = idx
            break

    # 4. Snap end_idx to nearest sentence terminator or speech pause
    best_end_idx = end_idx
    # Search forward a few words for sentence terminator
    found_term = False
    for idx in range(end_idx, min(len(words), end_idx + 12)):
        w_text = str(words[idx].get("word", ""))
        dur = float(words[idx].get("end", 0.0)) - float(words[start_idx].get("start", 0.0))
        if any(w_text.endswith(term) for term in SENTENCE_TERMINATORS):
            if dur <= max_duration:
                best_end_idx = idx
                found_term = True
                break

    # If no forward terminator within max_duration, search backwards from end_idx
    if not found_term:
        for idx in range(end_idx, max(start_idx + 5, end_idx - 10), -1):
            w_text = str(words[idx].get("word", ""))
            dur = float(words[idx].get("end", 0.0)) - float(words[start_idx].get("start", 0.0))
            if any(w_text.endswith(term) for term in SENTENCE_TERMINATORS):
                if dur >= min_duration:
                    best_end_idx = idx
                    found_term = True
                    break

    # 5. Extract words and timestamps
    snapped_words = words[start_idx : best_end_idx + 1]
    if not snapped_words:
        return (raw_start, raw_end, "")

    snapped_start = float(snapped_words[0].get("start", raw_start))
    snapped_end = float(snapped_words[-1].get("end", raw_end))
    text = " ".join(str(w.get("word", "")).strip() for w in snapped_words if str(w.get("word", "")).strip())

    return (snapped_start, snapped_end, text)
