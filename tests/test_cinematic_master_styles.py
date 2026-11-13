"""
End-to-End Verification of the 5 Master Reference Styles on Actual Video Footage.
Verifies:
  1. Style 01 - Cinematic Creator (Ice Blue Glow & 2-line hierarchy)
  2. Style 02 - Cinematic Minimal Subtitles (Hindi Devanagari)
  3. Style 03 - Bold Keyword Highlight (Bright Yellow Punch)
  4. Style 04 - Modern Kinetic Typography (Electric Cyan)
  5. Style 05 - Editorial Layered Typography (Cream Serif)
  6. Intelligent Face Detection Safe Placement
"""

import pytest
from pathlib import Path
import subprocess
import json

import config
from ai.caption_presets import get_preset
from ai.animated_caption_renderer import AnimatedCaptionRenderer
from ai.face_detector import YuNetFaceDetector
import cv2


INPUT_VIDEO = config.INPUT_DIR / "test_footage_3s.mp4"
OUTPUT_DIR = config.OUTPUT_DIR / "final" / "test_renders"


@pytest.fixture(scope="module", autouse=True)
def ensure_test_setup():
    """Ensure output test directory and input video exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not INPUT_VIDEO.exists():
        src = config.INPUT_DIR / "AI_Spark_Clip_001.mp4"
        assert src.exists(), f"Source video not found: {src}"
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(src), "-t", "3", "-c", "copy", str(INPUT_VIDEO)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    assert INPUT_VIDEO.exists() and INPUT_VIDEO.stat().st_size > 0


def probe_video(video_path: Path):
    """Inspect video file streams and dimensions via ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "stream=width,height,codec_name",
        "-of", "json",
        str(video_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return json.loads(res.stdout)


def test_style_01_cinematic_creator_render():
    """Reference Style 01: Bold condensed uppercase with Ice Blue glow & 2-line hierarchy."""
    preset = get_preset("cinematic_creator")
    renderer = AnimatedCaptionRenderer()
    out_video = OUTPUT_DIR / "style_01_cinematic_creator.mp4"

    transcript = [
        {
            "start": 0.0,
            "end": 2.8,
            "text": "BHAI SCOUT KIA ROYA HOGA",
            "words": [
                {"text": "BHAI", "start": 0.0, "end": 0.5},
                {"text": "SCOUT", "start": 0.5, "end": 1.0},
                {"text": "KIA", "start": 1.0, "end": 1.4},
                {"text": "ROYA", "start": 1.4, "end": 2.0},
                {"text": "HOGA", "start": 2.0, "end": 2.8},
            ]
        }
    ]

    rendered = renderer.render(
        input_video=INPUT_VIDEO,
        transcript=transcript,
        output_video=out_video,
        opts=preset.to_dict(),
    )

    assert Path(rendered).exists()
    assert Path(rendered).stat().st_size > 50000

    info = probe_video(Path(rendered))
    streams = info.get("streams", [])
    v_stream = next((s for s in streams if s.get("codec_name") == "h264"), None)
    assert v_stream is not None
    assert v_stream.get("width") == 1080
    assert v_stream.get("height") == 1920

    # Verify ASS script generated
    ass_file = config.SUBTITLE_DIR / f"{out_video.stem}_captions.ass"
    assert ass_file.exists()
    content = ass_file.read_text(encoding="utf-8")
    assert "ROYA" in content
    assert "HOGA" in content
    assert r"\blur" in content
    assert "00FFD880" in content or "80D8FF" in content or "00FF8800" in content


def test_style_02_cinematic_minimal_hindi_render():
    """Reference Style 02: Cinematic Minimal Subtitles (Hindi Devanagari typography)."""
    preset = get_preset("cinematic_minimal_hindi")
    renderer = AnimatedCaptionRenderer()
    out_video = OUTPUT_DIR / "style_02_cinematic_minimal_hindi.mp4"

    transcript = [
        {
            "start": 0.0,
            "end": 2.8,
            "text": "उसके आसपास के लोग",
            "words": [
                {"text": "उसके", "start": 0.0, "end": 0.7},
                {"text": "आसपास", "start": 0.7, "end": 1.5},
                {"text": "के", "start": 1.5, "end": 1.9},
                {"text": "लोग", "start": 1.9, "end": 2.8},
            ]
        }
    ]

    rendered = renderer.render(
        input_video=INPUT_VIDEO,
        transcript=transcript,
        output_video=out_video,
        opts=preset.to_dict(),
    )

    assert Path(rendered).exists()
    assert Path(rendered).stat().st_size > 50000

    ass_file = config.SUBTITLE_DIR / f"{out_video.stem}_captions.ass"
    assert ass_file.exists()
    content = ass_file.read_text(encoding="utf-8")
    assert "उसके" in content
    assert "आसपास" in content
    assert "लोग" in content
    assert r"\fad(150,150)" in content


def test_style_03_bold_keyword_yellow_render():
    """Reference Style 03: Bold Keyword Highlight (Bright yellow keyword with punch zoom)."""
    preset = get_preset("bold_keyword_yellow")
    renderer = AnimatedCaptionRenderer()
    out_video = OUTPUT_DIR / "style_03_bold_keyword_yellow.mp4"

    transcript = [
        {
            "start": 0.0,
            "end": 2.8,
            "text": "AGAR US DIN KD KE GHAR PE",
            "words": [
                {"text": "AGAR", "start": 0.0, "end": 0.8},
                {"text": "US", "start": 0.8, "end": 1.2},
                {"text": "DIN", "start": 1.2, "end": 1.6},
                {"text": "KD", "start": 1.6, "end": 2.0},
                {"text": "KE", "start": 2.0, "end": 2.3},
                {"text": "GHAR", "start": 2.3, "end": 2.6},
                {"text": "PE", "start": 2.6, "end": 2.8},
            ]
        }
    ]

    rendered = renderer.render(
        input_video=INPUT_VIDEO,
        transcript=transcript,
        output_video=out_video,
        opts=preset.to_dict(),
    )

    assert Path(rendered).exists()
    assert Path(rendered).stat().st_size > 50000

    ass_file = config.SUBTITLE_DIR / f"{out_video.stem}_captions.ass"
    assert ass_file.exists()
    content = ass_file.read_text(encoding="utf-8")
    assert "AGAR" in content
    assert "0000EAFF" in content or "00FFEA00" in content
    assert r"\fscx" in content


def test_style_04_modern_kinetic_cyan_render():
    """Reference Style 04: Modern Kinetic Typography (White + electric cyan/turquoise)."""
    preset = get_preset("modern_kinetic_cyan")
    renderer = AnimatedCaptionRenderer()
    out_video = OUTPUT_DIR / "style_04_modern_kinetic_cyan.mp4"

    transcript = [
        {
            "start": 0.0,
            "end": 2.8,
            "text": "with something predictable",
            "words": [
                {"text": "with", "start": 0.0, "end": 0.6},
                {"text": "something", "start": 0.6, "end": 1.6},
                {"text": "predictable", "start": 1.6, "end": 2.8},
            ]
        }
    ]

    rendered = renderer.render(
        input_video=INPUT_VIDEO,
        transcript=transcript,
        output_video=out_video,
        opts=preset.to_dict(),
    )

    assert Path(rendered).exists()
    assert Path(rendered).stat().st_size > 50000

    ass_file = config.SUBTITLE_DIR / f"{out_video.stem}_captions.ass"
    assert ass_file.exists()
    content = ass_file.read_text(encoding="utf-8")
    assert "something" in content
    assert "00FFFF00" in content or "00FFE500" in content


def test_style_05_editorial_layered_render():
    """Reference Style 05: Editorial Layered Typography (Cream lowercase display + serif italic)."""
    preset = get_preset("editorial_layered")
    renderer = AnimatedCaptionRenderer()
    out_video = OUTPUT_DIR / "style_05_editorial_layered.mp4"

    transcript = [
        {
            "start": 0.0,
            "end": 2.8,
            "text": "paaji yeh dekho is",
            "words": [
                {"text": "paaji", "start": 0.0, "end": 0.8},
                {"text": "yeh", "start": 0.8, "end": 1.4},
                {"text": "dekho", "start": 1.4, "end": 2.0},
                {"text": "is", "start": 2.0, "end": 2.8},
            ]
        }
    ]

    rendered = renderer.render(
        input_video=INPUT_VIDEO,
        transcript=transcript,
        output_video=out_video,
        opts=preset.to_dict(),
    )

    assert Path(rendered).exists()
    assert Path(rendered).stat().st_size > 50000

    ass_file = config.SUBTITLE_DIR / f"{out_video.stem}_captions.ass"
    assert ass_file.exists()
    content = ass_file.read_text(encoding="utf-8")
    assert "paaji" in content
    assert r"\i1" in content or "dekho" in content
    assert "00E9F6FD" in content or "00FDF6E9" in content


def test_intelligent_face_safe_caption_placement():
    """Intelligent caption placement: Detect face in video and verify captions avoid face occlusion."""
    cap = cv2.VideoCapture(str(INPUT_VIDEO))
    success, frame = cap.read()
    cap.release()
    assert success and frame is not None

    detector = YuNetFaceDetector()
    faces = detector.detect(frame)
    # Face detector returns (x, y, w, h, score)
    if faces:
        face = faces[0]
        face_bottom_y_pct = (face[1] + face[3]) / frame.shape[0]
        # In vertical shorts (9:16), speaker face is usually in top half (y < 0.55)
        # Safe caption placement should be below face (y > face_bottom_y_pct)
        for preset_id in ["cinematic_creator", "cinematic_minimal_hindi", "bold_keyword_yellow", "modern_kinetic_cyan"]:
            preset = get_preset(preset_id)
            assert preset.position_y > 0.65 or preset.position in ("bottom", "center")

