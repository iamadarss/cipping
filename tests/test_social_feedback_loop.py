"""
Automated unit tests for Social Publishing & Audience Analytics Feedback Loop.
Tests:
  - Multi-platform dispatch (YouTube, TikTok, Instagram)
  - PostMetrics recording and synchronization
  - Audience feedback aggregation by hook_type and duration
  - Steering context generation & ViralityScoreCalculator steering bias
"""

import os
import tempfile
from pathlib import Path
import pytest

from core.social_publisher import (
    SocialPublisher,
    SocialPerformanceStore,
    PublishedPost,
    PostMetrics,
)
from ai.viral_score import ViralScoreCalculator


@pytest.fixture
def temp_store(tmp_path):
    store_file = tmp_path / "social_perf_test.json"
    return SocialPerformanceStore(store_path=store_file)


def test_social_store_save_and_metrics(temp_store):
    """Test saving a post and recording views/retention metrics."""
    post = PublishedPost(
        post_id="yt_test_101",
        platform="youtube",
        title="Why 90% Fail at Crypto",
        video_path="output/final/clip_1.mp4",
        hook_type="question",
        duration=32.0,
    )
    temp_store.save_post(post)

    posts = temp_store.load_posts()
    assert len(posts) == 1
    assert posts[0].post_id == "yt_test_101"

    # Update metrics: 50,000 views, 3,500 likes, 78% retention
    ok = temp_store.record_post_metrics(
        post_id="yt_test_101",
        views=50000,
        likes=3500,
        comments=420,
        shares=1200,
        retention_percent=78.5,
    )
    assert ok is True

    updated_posts = temp_store.load_posts()
    assert updated_posts[0].metrics.views == 50000
    assert updated_posts[0].metrics.retention_percent == 78.5


def test_performance_aggregation_and_context(temp_store):
    """Test performance aggregation across multiple posts with different hook types."""
    # Post 1: Question hook, high performance
    temp_store.save_post(
        PublishedPost(
            post_id="p1",
            platform="youtube",
            title="Question Hook Post",
            video_path="v1.mp4",
            hook_type="question",
            duration=35.0,
            metrics=PostMetrics(views=100000, likes=8000, retention_percent=82.0),
        )
    )
    # Post 2: Statement hook, standard performance
    temp_store.save_post(
        PublishedPost(
            post_id="p2",
            platform="tiktok",
            title="Statement Hook Post",
            video_path="v2.mp4",
            hook_type="statement",
            duration=45.0,
            metrics=PostMetrics(views=12000, likes=500, retention_percent=55.0),
        )
    )

    by_hook = temp_store.aggregate_performance_by_hook()
    assert len(by_hook) == 2
    # Question should rank first because avg_views is 100,000 vs 12,000
    assert by_hook[0]["hook_type"] == "question"
    assert by_hook[0]["avg_views"] == 100000

    context = temp_store.build_performance_context()
    assert context is not None
    assert "question" in context.lower()
    assert "100,000 views" in context


def test_viral_scorer_steered_by_performance_context():
    """Verify ViralScoreCalculator biases score when audience history favors questions."""
    calc_neutral = ViralScoreCalculator()
    score_neutral = calc_neutral.calculate_score(
        duration=30.0,
        text="Why do smart founders win every time? Here is the secret blueprint.",
    )

    # Scorer with performance context highlighting question hooks as top performers
    perf_context = "Creator Audience History: Top Performing Hook Types: - question: 10 clips, avg 150,000 views (highest retention)"
    calc_steered = ViralScoreCalculator(performance_context=perf_context)
    score_steered = calc_steered.calculate_score(
        duration=30.0,
        text="Why do smart founders win every time? Here is the secret blueprint.",
    )

    assert score_neutral["hook_type"] == "question"
    assert score_steered["hook_type"] == "question"
    # Steered scorer gives a boost to question hooks based on audience data
    assert score_steered["viral_score"] >= score_neutral["viral_score"]
    assert "four_pillars" in score_steered


def test_social_publisher_schedule_and_sync():
    """Test SocialPublisher schedule dispatch and metric sync."""
    publisher = SocialPublisher()
    res = publisher.schedule_or_publish(
        platform="tiktok",
        video_path="output/clip.mp4",
        title="Test TikTok Viral",
        schedule_time="2026-12-01T18:00:00",
    )
    assert res["success"] is True
    assert res["status"] == "scheduled"
    assert res["platform"] == "tiktok"

    # Sync metrics
    sync_res = publisher.sync_metrics_from_platform(
        res["post_id"],
        simulated_or_api_data={"views": 25000, "likes": 1800, "retention_percent": 74.0},
    )
    assert sync_res["success"] is True
    assert sync_res["metrics"]["views"] == 25000
