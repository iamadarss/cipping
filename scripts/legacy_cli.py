# UpClip Studio - Legacy CLI Pipeline
import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import config

from utils.video_utils import VideoLoader
from utils.ffmpeg_utils import check_ffmpeg
from utils.clip_generator import ClipGenerator
from utils.scene_detector import SceneDetector
from utils.scene_merger import SceneMerger

from ai.whisper_engine import WhisperEngine
from ai.subtitle_builder import SubtitleBuilder
from ai.subtitle_renderer import SubtitleRenderer
from ai.ass_builder import ASSBuilder

from flask import Flask, send_from_directory, request, jsonify, render_template
from extensions import db


# ===================================================
# Main AI Pipeline
# ===================================================

def main():

    print("=" * 60)
    print("YouTube AI Shorts Generator")
    print("=" * 60)
    print()

    # ---------------------------------
    # FFmpeg Check
    # ---------------------------------

    print("Checking FFmpeg...")

    status, version = check_ffmpeg()

    if not status:
        print("❌ FFmpeg Not Installed")
        print(version)
        return

    print("✅ FFmpeg Installed")
    print(version)
    print()

    # ---------------------------------
    # Load Video
    # ---------------------------------

    video = config.INPUT_DIR / "sample.mp4"

    if not video.exists():
        print(f"❌ Video not found : {video}")
        return

    loader = VideoLoader(video)

    info = loader.metadata()

    print("=" * 60)
    print("Video Metadata")
    print("=" * 60)

    for key, value in info.items():
        print(f"{key:15}: {value}")

    print()

    # ---------------------------------
    # Thumbnail
    # ---------------------------------

    print("=" * 60)
    print("Generating Thumbnail")
    print("=" * 60)

    thumb = config.THUMBNAIL_DIR / "thumbnail.jpg"

    loader.thumbnail(thumb)
    loader.close()

    print("✅ Thumbnail Saved")

    print()

    # ---------------------------------
    # Scene Detection
    # ---------------------------------

    print("=" * 60)
    print("Scene Detection")
    print("=" * 60)

    detector = SceneDetector(video)

    scenes = detector.detect_scenes(
        threshold=config.SCENE_THRESHOLD
    )

    print(f"Original Scenes : {len(scenes)}")

    print()

    # ---------------------------------
    # Merge Scenes
    # ---------------------------------

    print("=" * 60)
    print("Scene Merge")
    print("=" * 60)

    merger = SceneMerger()

    merged_scenes = merger.merge(scenes)

    print(f"Merged Clips : {len(merged_scenes)}")

    print()

    # ---------------------------------
    # Clip Generation
    # ---------------------------------

    print("=" * 60)
    print("Generating Clips")
    print("=" * 60)

    generator = ClipGenerator(video)

    clips = generator.split_by_scenes(
        merged_scenes
    )

    print(f"Total Clips Generated : {len(clips)}")

    print()

    # ---------------------------------
    # Whisper AI
    # ---------------------------------

    print("=" * 60)
    print("Speech Detection (Whisper)")
    print("=" * 60)

    whisper = WhisperEngine(config.WHISPER_MODEL)

    transcript = whisper.transcribe(video)

    transcript_file = (
        config.TRANSCRIPT_DIR /
        "sample.json"
    )

    whisper.save_json(
        transcript,
        transcript_file
    )

    print(f"✅ Transcript Saved : {transcript_file}")

    print()

    # ---------------------------------
    # Subtitle Generation
    # ---------------------------------

    print("=" * 60)
    print("Subtitle Generation")
    print("=" * 60)

    subtitle = SubtitleBuilder()

    srt_file = config.SUBTITLE_DIR / "sample.srt"
    vtt_file = config.SUBTITLE_DIR / "sample.vtt"

    subtitle.save_all(
        transcript,
        srt_file,
        vtt_file
    )

    print("✅ Subtitle Files Created")

    print()


    

    # ---------------------------------
    # Subtitle Rendering
    # ---------------------------------

    print("=" * 60)
    print("Rendering Subtitle")
    print("=" * 60)

    renderer = SubtitleRenderer()

    output_video = (
        config.FINAL_DIR /
        "sample_subtitle.mp4"
    )

    renderer.burn_subtitle(
        input_video=video,
        subtitle_file=srt_file,
        output_video=output_video
    )

    print()

    # ---------------------------------
    # Completed
    # ---------------------------------

    print("=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print()

    print(f"Video       : {video}")
    print(f"Transcript  : {transcript_file}")
    print(f"SRT         : {srt_file}")
    print(f"VTT         : {vtt_file}")
    print(f"Final Video : {output_video}")

    print()


# ===================================================

if __name__ == '__main__':
    main()
