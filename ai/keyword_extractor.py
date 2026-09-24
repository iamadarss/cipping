"""
High-Impact Keyword & Hashtag Extractor for UpClip Studio.
Extracts viral topics, prominent multi-word phrases, and suggested hashtags
from video speech transcripts for SEO metadata, YouTube Desk, and ranking.
"""

import re
from collections import Counter
from pathlib import Path


# Comprehensive common stop words to filter out
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does",
    "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had",
    "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd",
    "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself",
    "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off",
    "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through",
    "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're",
    "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you",
    "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
    # Common conversational fillers
    "like", "just", "know", "yeah", "okay", "actually", "right", "basically", "gonna", "wanna",
    "um", "uh", "well", "see", "think", "really", "thing", "things", "going"
}

VIRAL_BOOST_WORDS = {
    "secret", "best", "worst", "top", "free", "money", "hack", "trick", "ai", "chatgpt", "millionaire",
    "mistake", "never", "always", "watch", "guide", "tutorial", "explained", "proof", "easy", "fast"
}


class KeywordExtractor:
    def __init__(self):
        pass

    def extract_keywords(self, text, top_n=10):
        """
        Extract the most significant keywords from text with importance scores.

        Returns:
            list of dicts: [{"word": str, "count": int, "score": float}]
        """
        if not text:
            return []

        # Tokenize words of 3+ letters
        tokens = re.findall(r"[A-Za-z]{3,}", text.lower())
        filtered = [t for t in tokens if t not in STOP_WORDS]

        if not filtered:
            return []

        counts = Counter(filtered)
        results = []

        for word, count in counts.most_common(top_n * 2):
            base_score = count * 10
            if word in VIRAL_BOOST_WORDS:
                base_score += 25
            results.append({
                "word": word,
                "count": count,
                "score": round(base_score, 1)
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_n]

    def extract_phrases(self, text, top_n=5):
        """
        Extract meaningful 2-word or 3-word recurring phrases.
        """
        if not text:
            return []

        tokens = re.findall(r"[A-Za-z]{2,}", text.lower())
        bigrams = []
        for i in range(len(tokens) - 1):
            w1, w2 = tokens[i], tokens[i + 1]
            if w1 not in STOP_WORDS and w2 not in STOP_WORDS:
                bigrams.append(f"{w1} {w2}")

        counts = Counter(bigrams)
        return [phrase for phrase, _ in counts.most_common(top_n)]

    def generate_hashtags(self, text, max_tags=6, fallback_tags=None):
        """
        Generate relevant social media hashtags (#Shorts, #Topic) for export/upload.
        """
        tags = ["#shorts", "#viral"]
        kw = self.extract_keywords(text, top_n=8)

        for item in kw:
            tag = f"#{item['word'].capitalize()}"
            if tag.lower() not in [t.lower() for t in tags]:
                tags.append(tag)
            if len(tags) >= max_tags:
                break

        if fallback_tags:
            for ft in fallback_tags:
                formatted = ft if ft.startswith("#") else f"#{ft}"
                if formatted.lower() not in [t.lower() for t in tags] and len(tags) < max_tags:
                    tags.append(formatted)

        return tags[:max_tags]

    def summarize_topics(self, transcript_segments, top_n=4):
        """
        Extract overarching topic clusters from transcript segment sequence.
        """
        if not transcript_segments:
            return ["General Content"]

        full_text = " ".join([seg.get("text", "") for seg in transcript_segments])
        keywords = self.extract_keywords(full_text, top_n=top_n)
        if keywords:
            return [kw["word"].title() for kw in keywords]
        return ["Highlights", "Core Insights"]
