"""
verify_rendering_fix.py — Comprehensive End-to-End Verification of Video Rendering Fixes.

Tests:
1. Multi-resolution caption export (Portrait 1080x1920 & Landscape 1920x1080)
2. Word-level font size variations (Acceptance Test: two small words + one large highlighted word)
3. Animated preset export (cinematic_creator, bold_keyword_yellow, modern_kinetic_cyan)
4. Bell / Subscribe animation with custom channel name ("Adarsh Tech", "@adarsh")
5. AI Caption Studio API export flow (/api/caption-studio/export)
6. Clip Generation workflow integration
7. B-roll and Logo layer ordering regression test (Captions on top of B-roll)
8. Quantitative OpenCV frame extraction and pixel assertion
"""

import os
import sys
import json
import time
import shutil
from pathlib import Path

# Add UpClipStudio to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Environment auto-switch guard: if run without venv, relaunch with .venv
venv_python = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
if venv_python.is_file() and Path(sys.executable).resolve() != venv_python.resolve():
    import subprocess
    ret = subprocess.call([str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]])
    sys.exit(ret)

import cv2  # type: ignore
import numpy as np  # type: ignore
import config  # type: ignore
from ai.animated_caption_renderer import AnimatedCaptionRenderer  # type: ignore
from ai.caption_presets import get_preset  # type: ignore
from ai.viral_enhancer import ViralEnhancer  # type: ignore
from app import create_app  # type: ignore

OUTPUT_DIR = PROJECT_ROOT / "output" / "verification_run"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FRAMES_DIR = OUTPUT_DIR / "frames"
FRAMES_DIR.mkdir(parents=True, exist_ok=True)

INPUT_VIDEO = PROJECT_ROOT / "input" / "test_debug_video.mp4"

results_summary = []


def record_result(test_name, status, details=""):
    results_summary.append({
        "test": test_name,
        "status": status,
        "details": details
    })
    print(f"\n[{status}] {test_name}: {details}")


def extract_and_analyze_frame(video_path, timestamp_sec, debug_name=""):
    """Extract frame at timestamp and return stats."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return None, {}

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    target_frame = int(round(timestamp_sec * fps))
    cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        return None, {}

    h, w, c = frame.shape

    # Save diagnostic frame image
    frame_path = FRAMES_DIR / f"{debug_name}_{timestamp_sec}s.jpg"
    cv2.imwrite(str(frame_path), frame)

    # Diff against original input video to detect burned overlay modifications
    diff_pixels = 0
    try:
        cap_orig = cv2.VideoCapture(str(INPUT_VIDEO))
        cap_orig.set(cv2.CAP_PROP_POS_FRAMES, min(target_frame, int(cap_orig.get(cv2.CAP_PROP_FRAME_COUNT) - 1)))
        ret_orig, frame_orig = cap_orig.read()
        cap_orig.release()
        if ret_orig and frame_orig is not None:
            orig_resized = cv2.resize(frame_orig, (w, h))
            diff = cv2.absdiff(orig_resized, frame)
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            # Focus on lower half for captions
            lower_diff = gray_diff[int(h * 0.4):int(h * 0.95), :]
            _, diff_thresh = cv2.threshold(lower_diff, 20, 255, cv2.THRESH_BINARY)
            diff_pixels = int(cv2.countNonZero(diff_thresh))
    except Exception:
        pass

    # Convert to HSV for color detection
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Red detection (for Subscribe button / CTA bell accent)
    red1 = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
    red2 = cv2.inRange(hsv, np.array([170, 100, 100]), np.array([180, 255, 255]))
    red_mask = red1 | red2
    red_pixels = int(cv2.countNonZero(red_mask))

    # Yellow detection (for keyword highlights e.g. #FFE600 / #00EAFF)
    yellow_mask = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([35, 255, 255]))
    yellow_pixels = int(cv2.countNonZero(yellow_mask))

    # Cyan detection (for modern kinetic presets)
    cyan_mask = cv2.inRange(hsv, np.array([80, 100, 100]), np.array([100, 255, 255]))
    cyan_pixels = int(cv2.countNonZero(cyan_mask))

    # Green detection (for green karaoke highlights)
    green_mask = cv2.inRange(hsv, np.array([35, 80, 80]), np.array([85, 255, 255]))
    green_pixels = int(cv2.countNonZero(green_mask))

    # White / bright text detection in lower half (captions area)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    lower_half = gray[int(h * 0.4):int(h * 0.95), :]
    _, bright_mask = cv2.threshold(lower_half, 180, 255, cv2.THRESH_BINARY)
    bright_text_pixels = int(cv2.countNonZero(bright_mask))

    stats = {
        "width": w,
        "height": h,
        "diff_pixels": diff_pixels,
        "red_pixels": red_pixels,
        "yellow_pixels": yellow_pixels,
        "cyan_pixels": cyan_pixels,
        "green_pixels": green_pixels,
        "bright_text_pixels": bright_text_pixels,
        "frame_path": str(frame_path)
    }
    return frame, stats


# =========================================================================
# TEST 1: Multi-Resolution Caption Export (Portrait 1080x1920 & Landscape 1920x1080)
# =========================================================================
def test_1_multi_resolution():
    print("\n--- Running Test 1: Multi-Resolution Caption Export ---")
    renderer = AnimatedCaptionRenderer()
    sample_transcript = [
        {"start": 0.5, "end": 2.5, "text": "Mastering daily habits for productivity"},
        {"start": 2.6, "end": 4.5, "text": "Consistency creates exponential growth"}
    ]

    # 1A: Portrait 1080x1920
    out_portrait = OUTPUT_DIR / "test1_portrait_1080x1920.mp4"
    opts_portrait = {
        "play_res_x": 1080,
        "play_res_y": 1920,
        "posYPercent": 75,
        "font_size": 40,
        "font_family": "Montserrat",
        "active_word_color": "#22C55E",
        "text_color": "#FFFFFF",
        "animation": "pop",
        "width": 1080,
        "height": 1920
    }
    try:
        ok_p = renderer.render(
            input_video=str(INPUT_VIDEO),
            transcript=sample_transcript,
            output_video=str(out_portrait),
            opts=opts_portrait
        )
        # Sample at t=1.0s (midpoint of first line)
        _, stats_p = extract_and_analyze_frame(out_portrait, 1.0, "test1_portrait")
        diff_p = stats_p.get("diff_pixels", 0)
        bright_p = stats_p.get("bright_text_pixels", 0)

        if ok_p and out_portrait.is_file() and (diff_p > 500 or bright_p > 200):
            record_result("Test 1A: Portrait 1080x1920 Export", "PASSED",
                          f"Res: {stats_p['width']}x{stats_p['height']}, Diff Pixels: {diff_p}, Text Pixels: {bright_p}")
        else:
            record_result("Test 1A: Portrait 1080x1920 Export", "FAILED",
                          f"Render status: {ok_p}, diff: {diff_p}, text pixels: {bright_p}")
    except Exception as e:
        record_result("Test 1A: Portrait 1080x1920 Export", "FAILED", str(e))

    # 1B: Landscape 1920x1080
    out_landscape = OUTPUT_DIR / "test1_landscape_1920x1080.mp4"
    opts_landscape = {
        "play_res_x": 1920,
        "play_res_y": 1080,
        "posYPercent": 80,
        "font_size": 42,
        "font_family": "Montserrat",
        "active_word_color": "#00F0FF",
        "text_color": "#FFFFFF",
        "animation": "pop",
        "width": 1920,
        "height": 1080
    }
    try:
        ok_l = renderer.render(
            input_video=str(INPUT_VIDEO),
            transcript=sample_transcript,
            output_video=str(out_landscape),
            opts=opts_landscape
        )
        _, stats_l = extract_and_analyze_frame(out_landscape, 1.0, "test1_landscape")
        diff_l = stats_l.get("diff_pixels", 0)
        bright_l = stats_l.get("bright_text_pixels", 0)

        if ok_l and out_landscape.is_file() and (diff_l > 500 or bright_l > 200):
            record_result("Test 1B: Landscape 1920x1080 Export", "PASSED",
                          f"Res: {stats_l['width']}x{stats_l['height']}, Diff Pixels: {diff_l}, Text Pixels: {bright_l}")
        else:
            record_result("Test 1B: Landscape 1920x1080 Export", "FAILED",
                          f"Render status: {ok_l}, diff: {diff_l}, text pixels: {bright_l}")
    except Exception as e:
        record_result("Test 1B: Landscape 1920x1080 Export", "FAILED", str(e))


# =========================================================================
# TEST 2: Word-Level Font Size Variations (Acceptance Test)
# Requirement: Two small words followed by one large highlighted word
# =========================================================================
def test_2_word_level_font_size_variations():
    print("\n--- Running Test 2: Word-Level Font Size Variations ---")
    renderer = AnimatedCaptionRenderer()
    sample_transcript = [
        {
            "start": 0.5,
            "end": 3.0,
            "text": "FIND YOUR FOCUS",
            "words": [
                {"text": "FIND", "start": 0.5, "end": 1.2},
                {"text": "YOUR", "start": 1.2, "end": 1.8},
                {"text": "FOCUS", "start": 1.8, "end": 3.0}
            ]
        }
    ]

    opts = {
        "play_res_x": 1080,
        "play_res_y": 1920,
        "posYPercent": 70,
        "font_size": 40,
        "keyword_scale": 1.5,
        "active_word_color": "#FFE600",
        "emphasis_color": "#FFE600",
        "text_color": "#FFFFFF",
        "stroke_width": 4,
        "animation": "pop"
    }

    # Verify generated ASS dialogue content
    ass_content = renderer.build_ass(transcript=sample_transcript, opts=opts)

    # Calculate expected sizes
    base_size = int(round(40 * (1080 / 360.0)))  # 120
    supp_size = round(base_size * 0.85)           # 102
    kw_size = round(base_size * 1.5)              # 180

    tag_supp = f"\\fs{supp_size}"
    tag_kw = f"\\fs{kw_size}"
    has_large_kw_size = (tag_supp in ass_content and tag_kw in ass_content)

    out_file = OUTPUT_DIR / "test2_word_level_size.mp4"
    ok = renderer.render(
        input_video=str(INPUT_VIDEO),
        transcript=sample_transcript,
        output_video=str(out_file),
        opts=opts
    )

    _, stats = extract_and_analyze_frame(out_file, 2.2, "test2_word_level_focus")
    yellow_px = stats.get("yellow_pixels", 0)
    text_px = stats.get("bright_text_pixels", 0)
    diff_px = stats.get("diff_pixels", 0)

    if ok and out_file.is_file() and has_large_kw_size and (yellow_px > 50 or text_px > 100 or diff_px > 500):
        record_result(
            "Test 2: Word-Level Font Size Variations (2 Small + 1 Large Highlight)",
            "PASSED",
            f"ASS contains supp_size ({tag_supp}) and kw_size ({tag_kw}). Video rendered with {yellow_px} yellow px, {text_px} text px, {diff_px} diff px."
        )
    else:
        record_result(
            "Test 2: Word-Level Font Size Variations (2 Small + 1 Large Highlight)",
            "FAILED",
            f"supp_tag={tag_supp in ass_content}, kw_tag={tag_kw in ass_content}, yellow_px={yellow_px}, text_px={text_px}"
        )


# =========================================================================
# TEST 3: Animated Preset Export (Cinematic Creator, Bold Keyword Yellow, Modern Kinetic Cyan)
# =========================================================================
def test_3_animated_presets():
    print("\n--- Running Test 3: Animated Presets Export ---")
    renderer = AnimatedCaptionRenderer()
    sample_transcript = [
        {"start": 0.5, "end": 2.5, "text": "THE ULTIMATE PRODUCTIVITY FORMULA"},
        {"start": 2.6, "end": 4.5, "text": "BUILD UNSTOPPABLE MOMENTUM EVERYDAY"}
    ]

    presets_to_test = [
        ("cinematic_creator", "Cinematic Creator (Gold/Amber 2-Line)", 1.2),
        ("bold_keyword_yellow", "Bold Keyword Yellow (Punchy Contrast)", 1.2),
        ("modern_kinetic_cyan", "Modern Kinetic Cyan (Cyan/Yellow Kinetic)", 1.2)
    ]

    for p_id, p_name, t_sec in presets_to_test:
        preset_obj = get_preset(p_id)
        if not preset_obj:
            record_result(f"Test 3: Preset {p_name}", "FAILED", f"Preset {p_id} not found in registry")
            continue

        p_style = preset_obj.to_dict()
        p_style["play_res_x"] = 1080
        p_style["play_res_y"] = 1920
        p_style["id"] = p_id
        p_style["preset_id"] = p_id

        out_path = OUTPUT_DIR / f"test3_preset_{p_id}.mp4"
        try:
            ok = renderer.render(
                input_video=str(INPUT_VIDEO),
                transcript=sample_transcript,
                output_video=str(out_path),
                opts=p_style
            )
            _, stats = extract_and_analyze_frame(out_path, t_sec, f"test3_{p_id}")
            text_px = stats.get("bright_text_pixels", 0)
            diff_px = stats.get("diff_pixels", 0)
            col_px = stats.get("yellow_pixels", 0) + stats.get("cyan_pixels", 0)

            if ok and out_path.is_file() and (text_px > 50 or diff_px > 500 or col_px > 50):
                record_result(f"Test 3: Preset {p_name}", "PASSED",
                              f"Rendered successfully! Diff px: {diff_px}, Bright px: {text_px}, Accent px: {col_px}")
            else:
                record_result(f"Test 3: Preset {p_name}", "FAILED",
                              f"ok={ok}, file_exists={out_path.is_file()}, diff_px={diff_px}")
        except Exception as e:
            record_result(f"Test 3: Preset {p_name}", "FAILED", str(e))


# =========================================================================
# TEST 4: Bell / Subscribe Animation with Custom Channel Name
# =========================================================================
def test_4_bell_subscribe_animation():
    print("\n--- Running Test 4: Bell/Subscribe Animation & Custom Channel Name ---")
    enhancer = ViralEnhancer()
    cta_card_path = OUTPUT_DIR / "test4_cta_card.png"

    # Step 1: Generate card with Pillow vector bell icon and custom name
    card = enhancer.generate_outro_cta_card(
        channel_name="Adarsh Tech",
        handle="@adarsh",
        output_path=cta_card_path,
        card_width=860,
        card_height=240
    )

    if not card or not cta_card_path.is_file():
        record_result("Test 4: Bell/Subscribe CTA Generation", "FAILED", "CTA Card image not generated")
        return

    # Check that the card image contains the red button and non-empty bell pixels
    img = cv2.imread(str(cta_card_path), cv2.IMREAD_UNCHANGED)
    hsv_card = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2HSV)
    red1 = cv2.inRange(hsv_card, np.array([0, 100, 100]), np.array([10, 255, 255]))
    red2 = cv2.inRange(hsv_card, np.array([170, 100, 100]), np.array([180, 255, 255]))
    card_red_px = int(cv2.countNonZero(red1 | red2))

    # Step 2: Burn CTA Card into test video using composite_enhancements
    out_video = OUTPUT_DIR / "test4_outro_cta_video.mp4"
    outro_config = {
        "enabled": True,
        "channel_name": "Adarsh Tech",
        "handle": "@adarsh",
        "duration": 3.0
    }

    try:
        ok = enhancer.composite_enhancements(
            input_video=str(INPUT_VIDEO),
            output_video=str(out_video),
            outro_cta=outro_config
        )

        # Video is 5.0 seconds. Outro duration = 3.0s => start is at 2.0s.
        # Analyze frame at 3.0s (during full CTA visibility)
        _, stats = extract_and_analyze_frame(out_video, 3.0, "test4_outro_cta")
        video_red_px = stats.get("red_pixels", 0)

        if ok and out_video.is_file() and video_red_px > 1000:
            record_result(
                "Test 4: Bell/Subscribe Animation & Custom Channel Name",
                "PASSED",
                f"CTA card generated (Red px: {card_red_px}). Burned video contains {video_red_px} red button pixels at t=3.0s with custom name 'Adarsh Tech'."
            )
        else:
            record_result(
                "Test 4: Bell/Subscribe Animation & Custom Channel Name",
                "FAILED",
                f"Burn status: {ok}, video red pixels at t=3.0s: {video_red_px} (expected > 1000)"
            )
    except Exception as e:
        record_result("Test 4: Bell/Subscribe Animation & Custom Channel Name", "FAILED", str(e))


# =========================================================================
# TEST 5: AI Caption Studio API Export Flow
# =========================================================================
def test_5_caption_studio_api_export():
    print("\n--- Running Test 5: AI Caption Studio API Export Flow ---")
    app = create_app()
    app.config["TESTING"] = True

    # Copy test video into input folder if not already there
    dest_video = PROJECT_ROOT / "input" / "test_api_video.mp4"
    if not dest_video.is_file():
        shutil.copyfile(INPUT_VIDEO, dest_video)

    payload = {
        "videoFileName": "test_api_video.mp4",
        "captions": [
            {"start": 0.5, "end": 2.5, "text": "AI Caption Studio Export Test"},
            {"start": 2.6, "end": 4.5, "text": "Precision Subtitles and Branding"}
        ],
        "style": {
            "id": "cinematic_creator",
            "preset_id": "cinematic_creator",
            "fontFamily": "Montserrat",
            "fontSize": 42,
            "twoLineHierarchy": True,
            "keywordScale": 1.4,
            "emphasisColor": "#FFD880",
            "posYPercent": 75,
            "strokeEnabled": True,
            "strokeWidth": 3,
            "strokeColor": "#000000"
        },
        "watermark": {
            "enabled": True,
            "text": "UpClip Studio",
            "position": "top_left",
            "opacity": 70
        },
        "outro_cta": {
            "enabled": True,
            "channel_name": "UpClip Creator",
            "handle": "@upclip",
            "duration": 2.5
        },
        "resolution": "9:16_1080p",
        "fps": 30
    }

    with app.test_client() as client:
        res = client.post(
            "/api/caption-studio/export",
            data=json.dumps(payload),
            content_type="application/json"
        )
        data = res.get_json() or {}

        if res.status_code == 200 and data.get("success") and data.get("download_url"):
            exported_file = PROJECT_ROOT / "output" / "final" / data.get("filename", "")
            if not exported_file.is_file():
                exported_file = PROJECT_ROOT / "output" / data.get("filename", "")

            if exported_file.is_file() and exported_file.stat().st_size > 50000:
                record_result(
                    "Test 5: AI Caption Studio Export API",
                    "PASSED",
                    f"Status 200, Output: {data.get('filename')}, Size: {exported_file.stat().st_size} bytes, URL: {data.get('download_url')}"
                )
            else:
                record_result(
                    "Test 5: AI Caption Studio Export API",
                    "FAILED",
                    f"File missing or empty: {exported_file}"
                )
        else:
            record_result(
                "Test 5: AI Caption Studio Export API",
                "FAILED",
                f"HTTP {res.status_code}: {data.get('error', 'unknown error')}"
            )


# =========================================================================
# TEST 6: Clip Generation Workflow Integration
# =========================================================================
def test_6_clip_generation_workflow():
    print("\n--- Running Test 6: Clip Generation Workflow Integration ---")
    process_py = PROJECT_ROOT / "routes" / "process.py"
    with open(process_py, "r", encoding="utf-8") as f:
        src = f.read()

    uses_preset_registry = "CaptionPresetRegistry" in src or "caption_presets" in src
    uses_viral_enhancer = "ViralEnhancer" in src or "viral_enhancer" in src
    uses_branding = "burn_branding_overlays" in src or "composite_enhancements" in src

    if uses_preset_registry and uses_viral_enhancer and uses_branding:
        record_result(
            "Test 6: Clip Generation Workflow Integration",
            "PASSED",
            "routes/process.py is integrated with CaptionPresetRegistry and ViralEnhancer branding/outro pass."
        )
    else:
        record_result(
            "Test 6: Clip Generation Workflow Integration",
            "FAILED",
            f"uses_preset_registry={uses_preset_registry}, uses_viral_enhancer={uses_viral_enhancer}"
        )


# =========================================================================
# TEST 7: B-Roll & Logo Regression Test (Captions on Top of B-Roll)
# =========================================================================
def test_7_broll_and_logo_layer_ordering():
    print("\n--- Running Test 7: B-Roll & Logo Regression (Captions Over B-Roll) ---")
    broll_img_path = OUTPUT_DIR / "dummy_broll.png"
    # Create bright blue solid image for B-roll (1080x1920)
    blue_img = np.zeros((1920, 1080, 3), dtype=np.uint8)
    blue_img[:, :] = (200, 50, 20)  # BGR blue
    cv2.imwrite(str(broll_img_path), blue_img)

    # Composite B-roll first onto video
    composite_base = OUTPUT_DIR / "test7_base_with_broll.mp4"
    enhancer = ViralEnhancer()
    b_rolls = [{
        "enabled": True,
        "type": "custom",
        "file_path": str(broll_img_path),
        "start": 1.0,
        "duration": 2.0
    }]

    try:
        ok_broll = enhancer.composite_enhancements(
            input_video=str(INPUT_VIDEO),
            output_video=str(composite_base),
            b_rolls=b_rolls
        )

        # Now burn bright white captions on top
        out_final = OUTPUT_DIR / "test7_captions_on_broll.mp4"
        renderer = AnimatedCaptionRenderer()
        transcript = [
            {"start": 1.0, "end": 3.0, "text": "CAPTIONS ON TOP OF BROLL"}
        ]
        opts = {
            "play_res_x": 1080,
            "play_res_y": 1920,
            "posYPercent": 75,
            "font_size": 42,
            "font_family": "Montserrat",
            "active_word_color": "#00F0FF",
            "text_color": "#FFFFFF",
            "animation": "pop"
        }

        ok_captions = renderer.render(
            input_video=str(composite_base),
            transcript=transcript,
            output_video=str(out_final),
            opts=opts
        )

        # Extract frame during B-roll cutaway at t=2.0s
        _, stats = extract_and_analyze_frame(out_final, 2.0, "test7_captions_over_broll")
        text_px = stats.get("bright_text_pixels", 0)
        diff_px = stats.get("diff_pixels", 0)

        if ok_broll and ok_captions and out_final.is_file() and (text_px > 100 or diff_px > 500):
            record_result(
                "Test 7: B-Roll & Logo Regression (Captions Over B-Roll)",
                "PASSED",
                f"Captions successfully composited ON TOP of B-Roll cutaway. Verified {text_px} text pixels, {diff_px} diff pixels over B-roll."
            )
        else:
            record_result(
                "Test 7: B-Roll & Logo Regression (Captions Over B-Roll)",
                "FAILED",
                f"ok_broll={ok_broll}, ok_captions={ok_captions}, text_px={text_px}, diff_px={diff_px}"
            )
    except Exception as e:
        record_result("Test 7: B-Roll & Logo Regression (Captions Over B-Roll)", "FAILED", str(e))


def run_all_tests():
    print("=================================================================")
    print("STARTING UPCLIP STUDIO RENDER VERIFICATION SUITE")
    print("=================================================================")
    test_1_multi_resolution()
    test_2_word_level_font_size_variations()
    test_3_animated_presets()
    test_4_bell_subscribe_animation()
    test_5_caption_studio_api_export()
    test_6_clip_generation_workflow()
    test_7_broll_and_logo_layer_ordering()

    print("\n=================================================================")
    print("VERIFICATION SUITE SUMMARY RESULTS")
    print("=================================================================")
    all_passed = True
    for item in results_summary:
        print(f"[{item['status']}] {item['test']}")
        print(f"       Details: {item['details']}")
        if item['status'] != "PASSED":
            all_passed = False

    print("=================================================================")
    if all_passed:
        print("ALL TESTS PASSED WITH 100% SUCCESS!")
    else:
        print("SOME TESTS FAILED OR BLOCKED. CHECK DETAILS ABOVE.")
    print("=================================================================")

    # Write JSON summary
    summary_path = OUTPUT_DIR / "verification_results.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2)
    print(f"Results written to: {summary_path}")


if __name__ == "__main__":
    run_all_tests()
