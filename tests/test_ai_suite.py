"""
Automated unit tests for UpClip Studio AI Suite, Scene Detection, and Micro-Clip Prevention.
"""

import sys
from pathlib import Path
import pytest

# Ensure root directory is on Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config
from ai.audio_energy import AudioEnergyDetector
from ai.motion_detector import MotionDetector
from ai.face_detector import FaceDetector
from ai.emotion_detector import EmotionDetector
from ai.keyword_extractor import KeywordExtractor
from ai.viral_score import ViralScoreCalculator
from ai.clip_ranker import ClipRanker
from ai.highlight_ranker import HighlightRanker
from ai.transcript import TranscriptManager
from ai.scene_detector import SceneDetector
from utils.scene_merger import SceneMerger


class TestSceneMergerAndAntiMicroClip:
    def test_merger_prevents_micro_clips(self):
        merger = SceneMerger(min_duration=20.0, max_duration=60.0)
        # Input scenes with small fragments (e.g. 4s, 5s, 6s, 8s)
        scenes = [
            {"start": 0.0, "end": 6.0, "duration": 6.0},
            {"start": 6.0, "end": 12.0, "duration": 6.0},
            {"start": 12.0, "end": 22.0, "duration": 10.0},
            {"start": 22.0, "end": 25.0, "duration": 3.0}, # Tiny tail cut
        ]
        merged = merger.merge(scenes)
        assert len(merged) >= 1
        for clip in merged:
            assert clip["duration"] >= 15.0, f"Clip duration {clip['duration']}s is below minimum threshold!"

    def test_merger_absorbs_tiny_tail_scene(self):
        merger = SceneMerger(min_duration=20.0, max_duration=60.0)
        scenes = [
            {"start": 0.0, "end": 25.0, "duration": 25.0},
            {"start": 25.0, "end": 27.5, "duration": 2.5}, # 2.5s tiny leftover
        ]
        merged = merger.merge(scenes)
        # The 2.5s scene must be absorbed into the previous clip, not emitted as a separate 2.5s clip
        assert len(merged) == 1
        assert merged[0]["end"] == 27.5
        assert merged[0]["duration"] == 27.5


class TestAudioEnergy:
    def test_audio_energy_scoring(self):
        detector = AudioEnergyDetector()
        mock_analysis = {
            "energy_curve": [
                {"start": 0.0, "end": 1.0, "energy": 50.0},
                {"start": 1.0, "end": 2.0, "energy": 80.0},
                {"start": 2.0, "end": 3.0, "energy": 90.0},
                {"start": 3.0, "end": 4.0, "energy": 40.0},
            ]
        }
        score = detector.get_segment_energy_score(mock_analysis, 1.0, 3.0)
        assert 80.0 <= score <= 90.0


class TestMotionDetector:
    def test_segment_motion_score(self):
        detector = MotionDetector()
        mock_analysis = {
            "motion_curve": [
                {"time": 0.5, "motion": 30.0},
                {"time": 1.0, "motion": 70.0},
                {"time": 1.5, "motion": 80.0},
            ]
        }
        score = detector.get_segment_motion_score(mock_analysis, 0.8, 1.8)
        assert score == 75.0


class TestFaceDetector:
    def test_face_detector_initialization(self):
        detector = FaceDetector()
        # Should initialize gracefully without crashing even if cascade not immediately needed
        assert hasattr(detector, "detect_in_frame")
        assert hasattr(detector, "analyze_video")

    def test_segment_face_score(self):
        detector = FaceDetector()
        mock_analysis = {
            "face_keyframes": [
                {"time": 1.0, "face_count": 1},
                {"time": 2.0, "face_count": 1},
                {"time": 3.0, "face_count": 0},
            ]
        }
        score = detector.get_segment_face_score(mock_analysis, 0.5, 2.5)
        assert score == 100.0


class TestEmotionDetector:
    def test_detect_excited_emotion(self):
        detector = EmotionDetector()
        res = detector.detect_in_text("This is an absolutely insane and amazing secret!")
        assert res["category"] in ["excited", "surprise"]
        assert res["bonus"] > 5
        assert "🔥" in res["emoji"] or "😲" in res["emoji"]

    def test_detect_question_hook(self):
        detector = EmotionDetector()
        res = detector.detect_in_text("Why do 99% of creators make this fatal mistake?")
        assert res["category"] in ["curious", "urgent"]
        assert res["bonus"] >= 6


class TestKeywordExtractor:
    def test_keyword_extraction_and_hashtags(self):
        extractor = KeywordExtractor()
        text = "This secret AI tool creates viral youtube shorts in 10 seconds. Best AI video editor tutorial."
        keywords = extractor.extract_keywords(text, top_n=5)
        words = [kw["word"] for kw in keywords]
        assert "tool" in words or "secret" in words or "shorts" in words

        hashtags = extractor.generate_hashtags(text, max_tags=4)
        assert any("#" in tag for tag in hashtags)
        assert len(hashtags) <= 4


class TestViralScore:
    def test_viral_score_calculation(self):
        calculator = ViralScoreCalculator()
        res = calculator.calculate_score(
            duration=30.0,
            text="Here is the secret AI hack that made 100k views in 3 days. Watch step by step to avoid this mistake.",
            audio_energy=85.0,
            motion_score=80.0,
            face_score=90.0
        )
        assert 75 <= res["viral_score"] <= 100
        assert "breakdown" in res
        assert res["breakdown"]["duration_score"] == 15
        assert len(res["tips"]) > 0


class TestClipRanker:
    def test_clip_ranking_order(self):
        ranker = ClipRanker()
        clips = [
            {"id": "clip_low", "duration": 10.0, "text": "okay", "audio_energy": 30.0, "motion_score": 30.0},
            {"id": "clip_high", "duration": 30.0, "text": "This secret will change your life forever!", "audio_energy": 90.0, "motion_score": 85.0},
        ]
        ranked = ranker.rank_clips(clips)
        assert ranked[0]["id"] == "clip_high"
        assert ranked[0]["rank"] == 1
        assert ranked[0]["is_top_pick"] is True
        assert ranked[1]["id"] == "clip_low"


class TestTranscriptManager:
    def test_transcript_manager_slicing_and_search(self):
        segments = [
            {"start": 0.0, "end": 4.0, "text": "Welcome to UpClip Studio."},
            {"start": 4.0, "end": 10.0, "text": "Um, today we talk about artificial intelligence and shorts."},
            {"start": 10.0, "end": 20.0, "text": "The secret is to use high engagement hooks."}
        ]
        tm = TranscriptManager({"segments": segments, "language": "en"})

        # Test Search
        matches = tm.search("secret")
        assert len(matches) == 1
        assert matches[0]["start"] == 10.0

        # Test Slicing
        sliced = tm.slice(5.0, 15.0)
        assert len(sliced) >= 1
        assert "intelligence" in sliced[0]["text"] or "secret" in sliced[-1]["text"]

        # Test Filler Word Cleaning
        cleaned = tm.clean_filler_words()
        assert "Um" not in cleaned and "um" not in cleaned
