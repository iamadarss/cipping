"""
Workflow, B-Roll, and Social Publishing API routes for UpClip Studio.
Exposes endpoints for:
  - 5-Mode AI Workflows (Highlights, Series, Topic, Recap, Trailer)
  - Windowed Analysis & 4-Pillar Virality Scoring
  - Pexels B-Roll search & local caching
  - Direct Social Publishing (YouTube, TikTok, Instagram) & Analytics Feedback Loop
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

from flask import Blueprint, jsonify, request

from ai.broll import (
    broll_configured,
    extract_filmable_moments,
    plan_broll_cutaways,
    search_pexels_videos,
)
from ai.workflows import (
    HOOK_TYPES,
    WORKFLOWS,
    WindowedAnalyzer,
    WorkflowOptions,
    WorkflowSpec,
    classify_hook_type,
)
from core.social_publisher import SocialPublisher

logger = logging.getLogger(__name__)

workflows_bp = Blueprint("workflows_api", __name__, url_prefix="/api")
social_publisher = SocialPublisher()


# ---------------------------------------------------------------------------
# 1. AI Workflows Endpoints
# ---------------------------------------------------------------------------


@workflows_bp.route("/workflows", methods=["GET"])
def get_workflows_catalog():
    """Return available workflow modes and descriptions."""
    catalog = [
        {
            "id": "highlights",
            "name": "Highlights",
            "badge": "★ Most Viral",
            "icon": "sparkles",
            "description": "Standalone viral clips with high-energy hook and maximum retention potential.",
            "fields": [],
        },
        {
            "id": "series",
            "name": "Series",
            "badge": "📖 Multi-Part",
            "icon": "layers",
            "description": "Sequential chronological multi-part numbered stories (Part 1, Part 2...) for episodic viewing.",
            "fields": [
                {"name": "part_count", "label": "Number of Parts", "type": "number", "default": 3, "min": 2, "max": 10}
            ],
        },
        {
            "id": "topic",
            "name": "Topic Focus",
            "badge": "🎯 Targeted",
            "icon": "crosshair",
            "description": "Clips tightly focused around your specific topic, question, or keyword.",
            "fields": [
                {"name": "topic", "label": "Target Topic / Keyword", "type": "text", "placeholder": "e.g. AI Tools, Bitcoin, Marketing"}
            ],
        },
        {
            "id": "recap",
            "name": "Recap & Key Points",
            "badge": "📋 Takeaways",
            "icon": "list-checks",
            "description": "Executive summary with on-screen point badges (Point 1, Point 2, Core Takeaway).",
            "fields": [],
        },
        {
            "id": "trailer",
            "name": "Hype Teaser",
            "badge": "🎬 High Energy",
            "icon": "zap",
            "description": "Fast-paced punchy teaser (15-35s) designed to drive viewers to watch the full episode.",
            "fields": [],
        },
    ]

    return jsonify({
        "success": True,
        "workflows": catalog,
        "hook_types": list(HOOK_TYPES),
    })


@workflows_bp.route("/workflows/analyze", methods=["POST"])
def analyze_workflow():
    """Run windowed workflow analysis on word-timed transcript."""
    body = request.get_json(silent=True) or {}
    wf_name = body.get("workflow", "highlights")
    clip_len = body.get("clip_length", "auto")
    words = body.get("words", [])
    topic = body.get("topic", "")
    part_count = body.get("part_count")

    if not words:
        return jsonify({"success": False, "error": "No words provided for analysis"}), 400

    options = WorkflowOptions(
        topic=topic,
        part_count=int(part_count) if part_count else None,
        instructions=body.get("instructions", ""),
    )
    spec = WorkflowSpec(workflow=wf_name, options=options, clip_length=clip_len)

    # Get audience feedback context to steer algorithm
    performance_context = social_publisher.get_steering_context()

    analyzer = WindowedAnalyzer(spec, performance_context=performance_context)
    result = analyzer.analyze(words, max_clips=int(body.get("max_clips", 10)))

    return jsonify({
        "success": True,
        "result": result.to_dict(),
        "performance_steered": bool(performance_context),
    })


# ---------------------------------------------------------------------------
# 2. B-Roll Endpoints
# ---------------------------------------------------------------------------


@workflows_bp.route("/broll/status", methods=["GET"])
def get_broll_status():
    """Check if Pexels B-Roll is configured and available."""
    configured = broll_configured()
    return jsonify({
        "configured": configured,
        "provider": "Pexels Video API",
        "orientation": "portrait (9:16)",
        "message": "Pexels API key active" if configured else "PEXELS_API_KEY environment variable not set",
    })


@workflows_bp.route("/broll/search", methods=["POST"])
def search_broll():
    """Direct search for portrait stock videos."""
    body = request.get_json(silent=True) or {}
    query = body.get("query", "")
    if not query:
        return jsonify({"success": False, "error": "Query required"}), 400

    videos = search_pexels_videos(query, orientation="portrait", per_page=int(body.get("limit", 6)))
    return jsonify({
        "success": True,
        "query": query,
        "videos": [
            {
                "id": v.get("id"),
                "duration": v.get("duration"),
                "image": v.get("image"),
                "url": v.get("url"),
            }
            for v in videos
        ],
    })


# ---------------------------------------------------------------------------
# 3. Social Publishing & Feedback Loop Endpoints
# ---------------------------------------------------------------------------


@workflows_bp.route("/social/publish", methods=["POST"])
def publish_or_schedule():
    """1-Click publish or schedule video to YouTube, TikTok, or Instagram."""
    body = request.get_json(silent=True) or {}
    platform = body.get("platform", "youtube")
    video_path = body.get("video_path", "")
    title = body.get("title", "Viral Clip")
    desc = body.get("description", "")
    hook_type = body.get("hook_type", "statement")
    duration = float(body.get("duration", 30.0))
    schedule_time = body.get("schedule_time")

    if not video_path:
        return jsonify({"success": False, "error": "video_path required"}), 400

    res = social_publisher.schedule_or_publish(
        platform=platform,
        video_path=video_path,
        title=title,
        description=desc,
        hook_type=hook_type,
        duration=duration,
        schedule_time=schedule_time,
    )
    return jsonify(res)


@workflows_bp.route("/social/performance", methods=["GET"])
def get_social_performance():
    """Retrieve creator audience history and current steering context."""
    posts = social_publisher.store.load_posts()
    by_hook = social_publisher.store.aggregate_performance_by_hook()
    by_dur = social_publisher.store.aggregate_performance_by_duration()
    context_str = social_publisher.get_steering_context()

    return jsonify({
        "success": True,
        "total_posts": len(posts),
        "posts": [p.to_dict() for p in posts],
        "by_hook_type": by_hook,
        "by_duration": by_dur,
        "steering_context": context_str,
    })


@workflows_bp.route("/social/sync-metrics", methods=["POST"])
def sync_social_metrics():
    """Record / sync metrics for a published video to update audience feedback loop."""
    body = request.get_json(silent=True) or {}
    post_id = body.get("post_id")
    if not post_id:
        return jsonify({"success": False, "error": "post_id required"}), 400

    res = social_publisher.sync_metrics_from_platform(post_id, body.get("metrics"))
    return jsonify(res)
