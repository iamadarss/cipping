"""
Highlight Candidate Ranker for UpClip Studio.
Ranks candidate narrative highlights, prioritizing complete thoughts,
high speech density, and strong opening hooks.
"""

from ai.viral_score import ViralScoreCalculator


class HighlightRanker:
    def __init__(self):
        self.calculator = ViralScoreCalculator()

    def rank_highlights(self, highlights, min_score=60):
        """
        Rank raw highlights by engagement retention score.

        Returns:
            list of dicts sorted by score descending.
        """
        if not highlights:
            return []

        ranked = []
        for hl in highlights:
            item = dict(hl)
            text = item.get("text") or item.get("reason", "")
            duration = float(item.get("duration", 20.0))
            score = item.get("score")

            if score is None:
                calc_res = self.calculator.calculate_score(duration=duration, text=text)
                score = calc_res["viral_score"]
                item["score"] = score
                item["badge"] = calc_res["badge"]

            if score >= min_score:
                ranked.append(item)

        ranked.sort(key=lambda x: x["score"], reverse=True)

        for i, h in enumerate(ranked, 1):
            h["priority"] = i
            h["is_recommended"] = (i <= 3)

        return ranked
