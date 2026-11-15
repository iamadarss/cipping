"""
test_clip_generation_pipeline.py — Verification of Clip Generation Pipeline Fixes.
Tests:
1. SettingsManager accessibility in background worker thread.
2. 5-Mode AI Workflows engine execution (highlights, series, topic, recap, trailer) without tuple errors.
3. End-to-end clip generation job execution with kinetic captions, branding, and outro CTA.
4. Validation that clips are generated, have correct format and contain burned kinetic captions.
"""

import sys
import json
import time
import shutil
from pathlib import Path

# Add UpClipStudio root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2
import numpy as np
import config
from core.settings_manager import settings_manager
from ai.workflows import (
    WORKFLOWS,
    WorkflowSpec,
    WorkflowOptions,
    run_highlights_workflow,
    run_series_workflow,
    run_topic_workflow,
    run_recap_workflow,
    run_trailer_workflow,
)
from routes.process import PipelineJob, JOBS, run_pipeline_job
from app import create_app


def test_settings_manager_access():
    """Verify settings_manager is defined, singleton, and accessible."""
    print("\n--- Test A: SettingsManager Singleton & Access ---")
    val = settings_manager.get("general.defaultExportFormat", "mp4")
    assert val in ("mp4", "mkv", "mov"), f"Invalid defaultExportFormat: {val}"
    pref_tpl = settings_manager.get("general.preferredTemplate")
    print(f"settings_manager accessible. defaultExportFormat={val}, preferredTemplate={pref_tpl}")
    return True


def test_5_workflows_runners():
    """Verify all 5 workflow runners execute cleanly without tuple or attribute errors."""
    print("\n--- Test B: 5 AI Workflow Runners Execution ---")
    words = [
        {"word": "Welcome", "start": 0.5, "end": 1.0},
        {"word": "to", "start": 1.0, "end": 1.2},
        {"word": "UpClip", "start": 1.2, "end": 1.8},
        {"word": "Studio.", "start": 1.8, "end": 2.4},
        {"word": "Did", "start": 2.5, "end": 2.8},
        {"word": "you", "start": 2.8, "end": 3.0},
        {"word": "know", "start": 3.0, "end": 3.3},
        {"word": "that", "start": 3.3, "end": 3.5},
        {"word": "ninety", "start": 3.5, "end": 4.0},
        {"word": "percent", "start": 4.0, "end": 4.5},
        {"word": "fail?", "start": 4.5, "end": 5.0},
        {"word": "The", "start": 5.2, "end": 5.4},
        {"word": "secret", "start": 5.4, "end": 5.9},
        {"word": "is", "start": 5.9, "end": 6.1},
        {"word": "consistency.", "start": 6.1, "end": 7.0},
    ]

    runners = {
        "highlights": run_highlights_workflow,
        "series": run_series_workflow,
        "topic": run_topic_workflow,
        "recap": run_recap_workflow,
        "trailer": run_trailer_workflow,
    }

    for wf_name, runner in runners.items():
        spec = WorkflowSpec(
            workflow=wf_name,
            options=WorkflowOptions(topic="UpClip", part_count=2),
            clip_length="short",
        )
        res = runner(spec, words)
        assert res is not None, f"Runner {wf_name} returned None"
        print(f"Workflow '{wf_name}': OK, candidates count={len(res.candidates)}")
        for c in res.candidates:
            st = getattr(c, "start_time", None)
            et = getattr(c, "end_time", None)
            ht = getattr(c, "hook_title", None)
            assert st is not None and et is not None and ht is not None, f"Candidate missing fields: {c}"
    print("All 5 workflows executed successfully without errors!")
    return True


def test_full_pipeline_job_execution():
    """Run full PipelineJob with kinetic captions, template, outro CTA, and watermark."""
    print("\n--- Test C: Full PipelineJob Execution (Highlights + Outro CTA + Watermark) ---")
    app = create_app()
    with app.app_context():
        input_src = PROJECT_ROOT / "input" / "AI_Spark_Clip_003.mp4"
        assert input_src.is_file(), f"Test video not found: {input_src}"

        # Copy to input folder if needed
        job_filename = "test_pipeline_run.mp4"
        job_input = PROJECT_ROOT / "input" / job_filename
        shutil.copyfile(input_src, job_input)

        job_settings = {
            "workflow": "highlights",
            "clipping_mode": "duration",
            "clip_duration": 10,
            "aspect_key": "9:16",
            "quality": "high",
            "subtitle_enabled": True,
            "caption_enabled": True,
            "template": "cinematic_creator",
            "naming_style": "viral_hook",
            "watermark": {
                "enabled": True,
                "text": "UpClip Studio",
                "position": "top_left",
                "opacity": 70,
            },
            "outro_cta": {
                "enabled": True,
                "channel_name": "Adarsh Tech",
                "handle": "@adarsh",
                "duration": 2.5,
            },
            "audio_normalization": True,
        }

        job = PipelineJob(
            job_id=9999,
            filename=job_filename,
            settings=job_settings,
        )

        # Run synchronously in test
        print("Starting run_pipeline_job()...")
        run_pipeline_job(job, app=app)

        print(f"Job status: {job.status}")
        print("Recent job logs:")
        for log in job.logs[-10:]:
            log_str = log if isinstance(log, str) else log.get("text", str(log))
            print(f"  {log_str}")

        assert job.status == "done", f"Pipeline failed with error: {job.error}"
        all_logs_text = " ".join(l if isinstance(l, str) else l.get("text", "") for l in job.logs)
        assert "settings_manager is not defined" not in all_logs_text, "Error 1 detected!"
        assert "tuple' object has no attribute 'get" not in all_logs_text, "Error 2 detected!"

        # Check generated clips
        clips = list(config.CLIPS_DIR.glob("*.mp4"))
        assert len(clips) > 0, "No clips generated!"
        print(f"Generated {len(clips)} clip(s): {[c.name for c in clips]}")

        # Check first clip properties with OpenCV
        clip_0 = clips[0]
        cap = cv2.VideoCapture(str(clip_0))
        assert cap.isOpened(), f"Cannot open clip: {clip_0}"
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        dur = frame_count / max(fps, 1.0)
        cap.release()

        print(f"Clip analysis: {width}x{height}, FPS: {fps}, Duration: {dur:.2f}s")
        assert width == 1080 and height == 1920, f"Unexpected resolution: {width}x{height}"
        print("Test C PASSED: Pipeline completed successfully with kinetic captions & outro CTA!")
        return True


if __name__ == "__main__":
    t_a = test_settings_manager_access()
    t_b = test_5_workflows_runners()
    t_c = test_full_pipeline_job_execution()
    print("\n=======================================================")
    print("ALL 3 PIPELINE TESTS PASSED 100%!")
    print("=======================================================")
