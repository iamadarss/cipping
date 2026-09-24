"""
Clip Ranking & Selection Engine for UpClip Studio.
Evaluates and ranks generated clips or candidate segments using composite multi-modal
signals (viral score, speech density, audio energy, motion, and topic clarity).
"""

from ai.viral_score import ViralScoreCalculator


class ClipRanker:
    def __init__(self):
        self.scorer = ViralScoreCalculator()

    def rank_clips(self, clips):
        """
        Rank a list of clip dictionaries and append ranking badges and composite scores.

        Each clip item can contain:
            { "id", "title", "start", "end", "duration", "text", "audio_energy", "motion_score", "face_score" }

        Returns:
            list of clips sorted descending by composite rank score.
        """
        if not clips:
            return []

        ranked_list = []

        for clip in clips:
            c = dict(clip)
            dur = float(c.get("duration", 0.0))
            if dur <= 0:
                s = float(c.get("start", 0.0))
                e = float(c.get("end", s + 20.0))
                dur = round(e - s, 2)
                c["duration"] = dur

            text = c.get("text", "")
            audio_energy = float(c.get("audio_energy", 65.0))
            motion_score = float(c.get("motion_score", 65.0))
            face_score = float(c.get("face_score", 75.0))

            # Compute viral metrics
            viral_res = self.scorer.calculate_score(
                duration=dur,
                text=text,
                audio_energy=audio_energy,
                motion_score=motion_score,
                face_score=face_score
            )

            composite_score = viral_res["viral_score"]
            c["score"] = composite_score
            c["viral_rating"] = viral_res["rating"]
            c["viral_badge"] = viral_res["badge"]
            c["tips"] = viral_res["tips"]
            c["breakdown"] = viral_res["breakdown"]

            ranked_list.append(c)

        # Sort descending by score
        ranked_list.sort(key=lambda x: x["score"], reverse=True)

        # Assign ordinal ranks and top-tier badges
        for idx, item in enumerate(ranked_list, start=1):
            item["rank"] = idx
            if idx == 1:
                item["grade"] = "A+"
                item["is_top_pick"] = True
                item["rank_badge"] = "🏆 Best Overall Clip"
            elif idx <= 3:
                item["grade"] = "A"
                item["is_top_pick"] = True
                item["rank_badge"] = f"⭐ Top Short #{idx}"
            elif item["score"] >= 70:
                item["grade"] = "B+"
                item["is_top_pick"] = False
                item["rank_badge"] = f"Recommended #{idx}"
            else:
                item["grade"] = "B"
                item["is_top_pick"] = False
                item["rank_badge"] = f"Clip #{idx}"

        return ranked_list
