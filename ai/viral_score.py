"""
Viral Potential & Social Media Retention Scorer for UpClip Studio.
Calculates a multi-factor viral prediction score (0-100) based on Hook Strength,
Speech Pacing, Audio Energy, Visual Dynamics, and Duration Optimization.
"""

from pathlib import Path


class ViralScoreCalculator:
    def __init__(self):
        pass

    def calculate_score(
        self,
        duration,
        text="",
        opening_text="",
        audio_energy=60.0,
        motion_score=60.0,
        face_score=70.0,
        keywords_matched=None
    ):
        """
        Compute an explainable viral score (0-100) for a short-form video clip.

        Returns:
            dict: {
                "viral_score": int (0-100),
                "rating": str,
                "badge": str,
                "breakdown": dict,
                "tips": list of str
            }
        """
        duration = max(1.0, float(duration))
        text = text or ""
        opening_text = opening_text or text[:120]
        keywords_matched = keywords_matched or []

        # 1. Hook Strength (0 - 25 pts)
        hook_score = 12
        opening_lower = opening_text.lower()
        # Question hooks
        if "?" in opening_text or any(w in opening_lower for w in ["why", "how", "what", "did you", "wait"]):
            hook_score += 6
        # Curiosity/High-stake words
        if any(w in opening_lower for w in ["secret", "never", "mistake", "stop", "best", "warning", "truth", "money"]):
            hook_score += 7
        hook_score = min(25, max(5, hook_score))

        # 2. Pacing & Speech Density (0 - 20 pts)
        word_count = len(text.split())
        words_per_sec = word_count / duration
        pacing_score = 10
        if 1.8 <= words_per_sec <= 3.6:
            pacing_score = 20  # Ideal rapid-fire shorts retention
        elif 1.2 <= words_per_sec < 1.8 or 3.6 < words_per_sec <= 4.2:
            pacing_score = 16
        elif words_per_sec >= 0.5:
            pacing_score = 12
        else:
            pacing_score = 7

        # 3. Audio Energy & Dynamics (0 - 20 pts)
        # Normalizes audio_energy (0-100) to 0-20
        audio_score = int(round((max(0.0, min(100.0, audio_energy)) / 100.0) * 20))

        # 4. Visual Dynamics & Motion (0 - 20 pts)
        # Blend motion (60%) and face presence (40%)
        combined_visual = (motion_score * 0.6) + (face_score * 0.4)
        visual_score = int(round((max(0.0, min(100.0, combined_visual)) / 100.0) * 20))

        # 5. Duration Sweet Spot (0 - 15 pts)
        # YouTube Shorts sweet spot is 20s - 45s
        duration_score = 8
        if 20.0 <= duration <= 45.0:
            duration_score = 15
        elif 15.0 <= duration < 20.0 or 45.0 < duration <= 60.0:
            duration_score = 12
        elif duration < 15.0:
            duration_score = 4  # Micro clips suffer in algorithm retention
        else:
            duration_score = 7

        total_score = min(99, hook_score + pacing_score + audio_score + visual_score + duration_score)

        # Rating & Badge
        if total_score >= 88:
            rating = "Explosive Viral Potential"
            badge = "🔥 Viral Rocket"
        elif total_score >= 76:
            rating = "High Engagement"
            badge = "⚡ High Performer"
        elif total_score >= 62:
            rating = "Good Momentum"
            badge = "📈 Solid Reach"
        else:
            rating = "Standard Retention"
            badge = "💬 Steady"

        # Actionable tips
        tips = []
        if hook_score < 18:
            tips.append("Add a punchy animated caption hook in the first 3 seconds.")
        if pacing_score < 14:
            tips.append("Tighten dead pauses using Silence Detector to increase speech density.")
        if visual_score < 14:
            tips.append("Use 9:16 Smart Reframe with face tracking to keep speaker centered.")
        if duration < 15.0:
            tips.append("Clip duration is too short for shorts monetization; merge with adjacent scene.")
        if not tips:
            tips.append("High-quality clip parameters ready for YouTube Shorts and Instagram Reels.")

        return {
            "viral_score": total_score,
            "rating": rating,
            "badge": badge,
            "words_per_sec": round(words_per_sec, 2),
            "breakdown": {
                "hook_score": hook_score,
                "pacing_score": pacing_score,
                "audio_score": audio_score,
                "visual_score": visual_score,
                "duration_score": duration_score
            },
            "tips": tips
        }
