"""
Contextual Emoji & Power-Word Annotation Engine for UpClip Studio.
Lightweight, ultra-fast, and 100% deterministic (zero GPU or API overhead).

Sprinkles tasteful, rate-limited contextual emojis next to keywords
and highlights power words (superlatives, absolutes, hype words, numbers, percentages).
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Curated keyword -> emoji mapping (150+ keywords across 8 semantic pillars)
# ---------------------------------------------------------------------------
EMOJI_KEYWORD_MAP: Dict[str, str] = {
    # Money / Finance / Business
    "money": "💰", "cash": "💵", "dollar": "💵", "dollars": "💵", "rich": "🤑",
    "wealth": "💰", "wealthy": "💰", "millionaire": "🤑", "billionaire": "🤑",
    "million": "💰", "billion": "💰", "profit": "📈", "revenue": "📈",
    "income": "💵", "salary": "💸", "price": "🏷️", "cost": "💲", "free": "🆓",
    "invest": "📊", "investment": "📊", "investing": "📊", "stock": "📈",
    "stocks": "📈", "crypto": "🪙", "bitcoin": "₿", "business": "💼",
    "company": "🏢", "startup": "🚀", "deal": "🤝", "sale": "🛒", "buy": "🛒",
    "sell": "💸", "bank": "🏦", "tax": "🧾", "taxes": "🧾", "budget": "📒",
    "save": "🏦", "savings": "🏦", "debt": "💳", "fund": "💰",

    # Growth / Success / Winning
    "growth": "📈", "grow": "📈", "growing": "📈", "scale": "📊", "success": "🏆",
    "successful": "🏆", "win": "🏆", "winning": "🏆", "winner": "🥇", "won": "🏆",
    "goal": "🎯", "goals": "🎯", "target": "🎯", "achieve": "✅", "result": "✅",
    "results": "✅", "best": "🥇", "first": "🥇", "top": "⬆️", "champion": "🏆",
    "level": "🆙", "upgrade": "⬆️", "boost": "🚀", "rocket": "🚀",

    # Ideas / Mind / Intelligence
    "idea": "💡", "ideas": "💡", "think": "🤔", "thinking": "🤔", "thought": "💭",
    "smart": "🧠", "genius": "🧠", "brain": "🧠", "mind": "🧠", "learn": "📚",
    "learning": "📚", "study": "📚", "school": "🎓", "knowledge": "🧠",
    "lesson": "📖", "book": "📖", "books": "📚", "read": "📖", "question": "❓",
    "answer": "💡", "secret": "🤫", "truth": "💯", "fact": "📌", "facts": "💯",
    "remember": "🧠", "focus": "🎯", "discover": "🔍", "research": "🔬",

    # Emotion / Hype / Virality
    "love": "❤️", "loved": "❤️", "heart": "❤️", "amazing": "🤩", "incredible": "🤯",
    "insane": "🤯", "crazy": "🤯", "wow": "😮", "shocking": "😱", "scary": "😱",
    "fear": "😱", "happy": "😄", "happiness": "😄", "sad": "😢", "angry": "😡",
    "fire": "🔥", "hot": "🔥", "lit": "🔥", "cool": "😎", "perfect": "👌",
    "beautiful": "😍", "favorite": "⭐", "epic": "🤩", "magic": "✨",
    "powerful": "💪", "power": "⚡", "strong": "💪", "energy": "⚡",
    "stop": "✋", "warning": "⚠️", "danger": "⚠️", "boom": "💥", "explode": "💥",

    # Time / Speed
    "time": "⏰", "today": "📅", "tomorrow": "📅", "now": "⏰", "fast": "⚡",
    "quick": "⚡", "quickly": "⚡", "instantly": "⚡", "minute": "⏱️",
    "minutes": "⏱️", "hour": "⏰", "hours": "⏰", "day": "📅", "days": "📅",
    "year": "📆", "years": "📆", "future": "🔮", "forever": "♾️", "deadline": "⏳",

    # People / Social
    "people": "👥", "team": "🤝", "family": "👨‍👩‍👧", "friend": "🫂", "friends": "🫂",
    "everyone": "🙌", "everybody": "🙌", "you": "👉", "audience": "👀",
    "followers": "📲", "subscribe": "🔔", "viral": "📈", "famous": "🌟",
    "customer": "🛍️", "customers": "🛍️", "boss": "💼", "leader": "🫡",

    # Work / Hustle / Health
    "work": "💼", "working": "💼", "hustle": "💪", "grind": "💪", "effort": "💪",
    "hard": "💪", "build": "🛠️", "building": "🏗️", "create": "🎨",
    "creating": "🎨", "health": "🏥", "healthy": "🥗", "food": "🍽️", "eat": "🍴",
    "gym": "🏋️", "workout": "🏋️", "muscle": "💪", "sleep": "😴", "water": "💧",
    "run": "🏃", "running": "🏃",

    # Tech / Future
    "ai": "🤖", "robot": "🤖", "tech": "💻", "technology": "💻", "computer": "💻",
    "phone": "📱", "internet": "🌐", "online": "🌐", "data": "📊", "code": "👨‍💻",
    "world": "🌍", "earth": "🌍", "global": "🌍", "space": "🚀", "science": "🔬",
    "game": "🎮", "games": "🎮", "music": "🎵", "video": "🎬", "movie": "🎬",
    "car": "🚗", "house": "🏠", "home": "🏠", "travel": "✈️", "light": "💡",
    "key": "🔑",
}

# Words that should be visually highlighted (accent color + pop)
POWER_WORDS: Set[str] = {
    "never", "always", "everything", "nothing", "everyone", "nobody", "anyone",
    "best", "worst", "most", "biggest", "huge", "massive", "tiny", "every",
    "only", "first", "last", "free", "now", "today", "instantly", "forever",
    "guaranteed", "proven", "secret", "truth", "fact", "literally", "actually",
    "exactly", "must", "need", "stop", "warning", "danger", "critical", "key",
    "important", "remember", "mistake", "wrong", "right", "perfect", "ultimate",
    "powerful", "insane", "crazy", "incredible", "amazing", "shocking", "viral",
    "million", "billion", "thousand", "percent", "double", "triple", "ten",
}

_NORMALIZE_RE = re.compile(r"[^a-z0-9%]+")
_NUMBER_RE = re.compile(r"\d")


def normalize_token(text: str) -> str:
    """Lowercase a word and strip surrounding punctuation."""
    return _NORMALIZE_RE.sub("", (text or "").lower())


def _singularize(token: str) -> str:
    """Lightweight singular form rule for English plurals."""
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 4 and token.endswith("es") and not token.endswith("ses"):
        return token[:-2]
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def lookup_emoji(token: str, custom_map: Optional[Dict[str, str]] = None) -> Optional[str]:
    """Look up an emoji for a word token."""
    if not token:
        return None
    source = custom_map if custom_map is not None else EMOJI_KEYWORD_MAP
    if token in source:
        return source[token]
    singular = _singularize(token)
    if singular != token and singular in source:
        return source[singular]
    return None


def annotate_caption_words(
    words: List[Dict[str, Any]],
    ai_cues: Optional[List[Dict[str, Any]]] = None,
    *,
    enable_emoji: bool = True,
    enable_emphasis: bool = True,
    max_emojis: int = 8,
    min_word_gap: int = 3,
    repeat_gap: int = 8,
) -> Tuple[Dict[int, str], Set[int]]:
    """
    Annotate a short clip's word sequence with contextual emojis and power word highlights.

    Returns:
        (emoji_by_index, emphasis_indices)
        - emoji_by_index: {word_index: "🔥"}
        - emphasis_indices: set of word indices that should pop in accent color
    """
    emoji_by_index: Dict[int, str] = {}
    emphasis_indices: Set[int] = set()
    if not words:
        return emoji_by_index, emphasis_indices

    # Build active lookup
    lookup = dict(EMOJI_KEYWORD_MAP)
    if ai_cues:
        for cue in ai_cues:
            kw = normalize_token(str(cue.get("keyword", "")))
            em = str(cue.get("emoji", "")).strip()
            if kw and em:
                lookup[kw] = em

    last_emoji_word = -(min_word_gap + 1)
    recent_emoji: Dict[str, int] = {}
    emoji_count = 0

    for idx, word in enumerate(words):
        raw = str(word.get("text", ""))
        token = normalize_token(raw)
        if not token:
            continue

        is_number = bool(_NUMBER_RE.search(token))
        emoji = lookup_emoji(token, lookup) if enable_emoji else None

        # Emphasis: emoji words, power words, and numbers/percentages
        if enable_emphasis and (emoji or token in POWER_WORDS or is_number):
            emphasis_indices.add(idx)

        if not emoji or emoji_count >= max_emojis:
            continue
        if idx - last_emoji_word < min_word_gap:
            continue
        if idx - recent_emoji.get(emoji, -(repeat_gap + 1)) < repeat_gap:
            continue

        emoji_by_index[idx] = emoji
        emphasis_indices.add(idx)
        last_emoji_word = idx
        recent_emoji[emoji] = idx
        emoji_count += 1

    return emoji_by_index, emphasis_indices

