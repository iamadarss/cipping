"""
Emotion & Sentiment Tone Detector for UpClip Studio.
Identifies high-impact emotional moments (Excitement, Surprise, Curiosity, Urgency)
from transcript linguistics, punctuation dynamics, and acoustic signals.
"""

import re
from pathlib import Path
import config


class EmotionDetector:
    def __init__(self):
        # Lexicon with emotion category and weight
        self.emotion_lexicon = {
            "excited": {
                "keywords": ["amazing", "insane", "unbelievable", "awesome", "huge", "crazy", "wow", "omg",
                             "mindblowing", "epic", "fire", "boom", "love", "fantastic", "legendary", "super"],
                "label": "Excitement",
                "emoji": "🔥",
                "score_bonus": 15
            },
            "surprise": {
                "keywords": ["shocking", "unexpected", "what", "really", "never", "cannot believe", "impossible",
                             "no way", "secret", "exposed", "hidden", "mystery"],
                "label": "Surprise / Hook",
                "emoji": "😲",
                "score_bonus": 14
            },
            "curious": {
                "keywords": ["why", "how to", "how", "did you know", "question", "reason", "because",
                             "truth", "explained", "mistake", "think", "wonder"],
                "label": "Curiosity / Insight",
                "emoji": "💡",
                "score_bonus": 12
            },
            "urgent": {
                "keywords": ["warning", "stop", "danger", "urgent", "don't", "dont", "avoid", "risk",
                             "critical", "important", "now", "immediately", "beware"],
                "label": "Urgency / Caution",
                "emoji": "⚠️",
                "score_bonus": 14
            },
            "humor": {
                "keywords": ["haha", "funny", "hilarious", "joke", "lol", "laugh", "weird", "silly", "ridiculous"],
                "label": "Humor / Fun",
                "emoji": "😂",
                "score_bonus": 12
            }
        }

    def detect_in_text(self, text, audio_energy=50.0):
        """
        Analyze a sentence or chunk of text for emotional sentiment.

        Returns:
            dict: {
                "emotion": str,
                "emoji": str,
                "intensity": float (0.0 to 1.0),
                "bonus": int,
                "matched_words": list of str
            }
        """
        text = text or ""
        lower = text.lower()
        cleaned_words = [w.strip(".,!?()[]{}\"'") for w in lower.split()]

        # Check punctuation emphasis
        exclamation_count = text.count("!")
        question_count = text.count("?")
        has_caps = any(w.isupper() and len(w) > 2 for w in text.split())

        best_category = "neutral"
        highest_match_count = 0
        matched_keywords = []

        for category, data in self.emotion_lexicon.items():
            matches = [kw for kw in data["keywords"] if kw in lower or kw in cleaned_words]
            if len(matches) > highest_match_count:
                highest_match_count = len(matches)
                best_category = category
                matched_keywords = matches

        # If questions dominate
        if highest_match_count == 0 and question_count > 0:
            best_category = "curious"
            matched_keywords = ["?"]

        # If exclamations dominate with high audio energy
        if highest_match_count == 0 and (exclamation_count > 0 or audio_energy > 75.0):
            best_category = "excited"
            matched_keywords = ["!"]

        if best_category in self.emotion_lexicon:
            cat_data = self.emotion_lexicon[best_category]
            intensity = min(1.0, 0.4 + (highest_match_count * 0.2) + (0.2 if has_caps else 0.0) + (audio_energy / 250.0))
            return {
                "emotion": cat_data["label"],
                "category": best_category,
                "emoji": cat_data["emoji"],
                "intensity": round(intensity, 2),
                "bonus": int(cat_data["score_bonus"] * intensity),
                "matched_words": matched_keywords
            }

        return {
            "emotion": "Neutral / Informative",
            "category": "neutral",
            "emoji": "💬",
            "intensity": 0.3,
            "bonus": 4,
            "matched_words": []
        }

    def analyze_transcript(self, transcript_segments, energy_analysis=None):
        """
        Classify emotions across all segments of a transcript.

        Returns:
            list of dicts with segment timings and emotion metadata
        """
        results = []
        for seg in transcript_segments:
            text = seg.get("text", "")
            start = float(seg.get("start", 0.0))
            end = float(seg.get("end", start + 2.0))

            # Sample audio energy if available
            audio_score = 50.0
            if energy_analysis and "energy_curve" in energy_analysis:
                pts = [
                    p["energy"] for p in energy_analysis["energy_curve"]
                    if not (p["end"] <= start or p["start"] >= end)
                ]
                if pts:
                    audio_score = sum(pts) / len(pts)

            emo = self.detect_in_text(text, audio_energy=audio_score)
            results.append({
                "start": start,
                "end": end,
                "text": text,
                **emo
            })
        return results
