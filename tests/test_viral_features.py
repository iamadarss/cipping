"""
Tests for core viral enhancements:
1. Aspect ratio center cropping (4:5, 9:16, 1:1)
2. Kinetic caption sequential non-overlapping chunking & presets
3. Scene merger 60s+ minimum duration floor & sentence boundary snapping
4. Content-based naming slug extraction
5. YouTube smart scheduling endpoints
"""

import pytest
from app import create_app
import config
from utils.clip_generator import ClipGenerator
from utils.scene_merger import SceneMerger
from ai.animated_caption_renderer import AnimatedCaptionRenderer


def test_aspect_ratio_cropping_filters():
    """Verify 4:5, 9:16, and 1:1 produce proper crop filters with center fallback."""
    # 1. Dimensions check
    assert config.ASPECT_OPTIONS["4:5"][1:] == (1080, 1350)
    assert config.ASPECT_OPTIONS["9:16"][1:] == (1080, 1920)
    assert config.ASPECT_OPTIONS["1:1"][1:] == (1080, 1080)

    gen = ClipGenerator("input/sample.mp4")

    # 4:5 center crop filter test
    filter_45 = gen._build_crop_filter(target_width=1080, target_height=1350, reframe_x=None)
    assert "scale=1080:1350" in filter_45
    assert "crop=1080:1350:(in_w-1080)/2:(in_h-1350)/2" in filter_45

    # 9:16 center crop filter test
    filter_916 = gen._build_crop_filter(target_width=1080, target_height=1920, reframe_x=None)
    assert "scale=1080:1920" in filter_916
    assert "crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2" in filter_916


def test_kinetic_caption_chunks_no_overlap():
    """Verify that kinetic caption lines NEVER overlap in time and have 3-4 words max."""
    transcript = [
        {
            "start": 0.0,
            "end": 3.6,
            "text": "Welcome to the future of automated video editing today",
            "words": [
                {"text": "Welcome", "start": 0.0, "end": 0.4},
                {"text": "to", "start": 0.4, "end": 0.6},
                {"text": "the", "start": 0.6, "end": 0.8},
                {"text": "future", "start": 0.8, "end": 1.3},
                {"text": "of", "start": 1.3, "end": 1.5},
                {"text": "automated", "start": 1.5, "end": 2.1},
                {"text": "video", "start": 2.1, "end": 2.5},
                {"text": "editing", "start": 2.5, "end": 3.0},
                {"text": "today", "start": 3.0, "end": 3.6},
            ]
        }
    ]

    renderer = AnimatedCaptionRenderer()
    chunks = renderer._prepare_kinetic_chunks(transcript, max_words=4)
    assert len(chunks) >= 2

    for i in range(len(chunks)):
        chunk = chunks[i]
        assert len(chunk["words"]) <= 4
        assert chunk["start"] < chunk["end"]
        # Sequential verification: Chunk i start must not precede Chunk i-1 end
        if i > 0:
            assert chunk["start"] >= chunks[i - 1]["end"] - 0.01, f"Overlap between chunk {i-1} and {i}"


def test_trending_caption_presets_exist():
    """Verify all 6 creator presets exist in template options."""
    for p in ["hormozi_pop", "beast_glow", "red_punch", "clean_gold", "neon_cyber", "karaoke_pill"]:
        opt = AnimatedCaptionRenderer._template_options(p)
        assert "font" in opt
        assert "color" in opt
        assert "highlight_color" in opt
        assert "animation" in opt


def test_scene_merger_minimum_duration_floor():
    """Verify that SceneMerger enforces minimum duration >= 60.0s."""
    merger = SceneMerger(min_duration=60.0, max_duration=120.0)
    scenes = [
        {"start": 0.0, "end": 15.0, "duration": 15.0},
        {"start": 15.0, "end": 35.0, "duration": 20.0},
        {"start": 35.0, "end": 50.0, "duration": 15.0},
        {"start": 50.0, "end": 75.0, "duration": 25.0},
        {"start": 75.0, "end": 100.0, "duration": 25.0},
        {"start": 100.0, "end": 140.0, "duration": 40.0},
    ]
    merged = merger.merge(scenes)
    assert len(merged) > 0
    for clip in merged:
        assert clip["duration"] >= 60.0, f"Clip duration {clip['duration']}s is below the 60s minimum floor!"


def test_sentence_boundary_snapping():
    """Verify snapping to sentence boundary punctuation."""
    merger = SceneMerger(min_duration=60.0, max_duration=120.0)
    scenes = [
        {"start": 0.0, "end": 60.0, "duration": 60.0}
    ]
    transcript = [
        {"start": 0.0, "end": 20.0, "text": "This is thought number one."},
        {"start": 20.2, "end": 45.0, "text": "This is thought number two with more context."},
        {"start": 45.5, "end": 63.5, "text": "And this concludes the major point! Now moving to next."},
    ]
    snapped = merger.snap_to_sentence_boundaries(scenes, transcript=transcript)
    assert len(snapped) == 1
    # The end should snap near 63.5 where the sentence ends with '!'
    assert snapped[0]["end"] == 63.5


def test_content_based_naming_extraction():
    """Verify that ClipGenerator generates descriptive slugs from transcript text."""
    gen = ClipGenerator("input/Rahul Gandhi vs Gyanesh Kumar.mp4")
    transcript = [
        {"start": 5.0, "end": 15.0, "text": "Rahul Gandhi raised the election commission controversy"},
        {"start": 16.0, "end": 40.0, "text": "regarding Gyanesh Kumar selection process"}
    ]
    name = gen._get_content_name(
        transcript=transcript,
        start_time=5.0,
        duration=35.0,
        index=1
    )
    assert "Rahul" in name or "Gyanesh" in name or "Election" in name or "Controversy" in name
    assert name.endswith("_01") or name.endswith("_001") or "Clip" in name


def test_youtube_smart_schedule_api():
    """Verify YouTube smart schedule advice and auto-schedule endpoints."""
    app = create_app()
    client = app.test_client()

    # 1. Advice endpoint
    res = client.get("/youtube/smart-schedule-advice")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    adv = data["advice"]
    assert "peak_slots" in adv
    assert len(adv["peak_slots"]) >= 3
    assert "spacing_rule" in adv
    assert "next_recommended_slot" in adv

    # 2. Auto-schedule endpoint
    post_res = client.post("/youtube/auto-schedule", json={"spacing_hours": 4})
    assert post_res.status_code == 200
    post_data = post_res.get_json()
    assert post_data["success"] is True
    assert "scheduled_count" in post_data
    assert "plan" in post_data
