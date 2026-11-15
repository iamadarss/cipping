# UpClip Studio — Phase 0 Baseline Audit & Health Check

**Date:** November 15, 2026  
**Interpreter:** Python 3.14.6 (`.venv`)  
**Scope:** Complete codebase (`UpClipStudio/`)

---

## 1. Python Compilation Baseline (`python -m compileall -q .`)
- **Status:** **PASSED (Exit Code: 0)**
- **Result:** All Python source files in the application compiled without syntax errors.

---

## 2. Pytest Suite Baseline (`python -m pytest`)
- **Total Test Files:** 17
- **Total Passing Tests:** 105
- **Total Failing Tests:** 0
- **Breakdown by Suite:**
  - `test_ai_suite.py`: 12 passed
  - `test_broll_cutaways.py`: 3 passed
  - `test_caption_studio.py`: 15 passed
  - `test_caption_templates_and_emojis.py`: 7 passed
  - `test_cinematic_master_styles.py`: 1 passed
  - `test_clips.py`: 0 collected (standalone integration script without `def test_*`)
  - `test_custom_settings_and_upload.py`: 3 passed
  - `test_home.py`: 3 passed
  - `test_premium_presets.py`: 10 passed
  - `test_projects.py`: 2 passed
  - `test_settings_and_ui.py`: 11 passed
  - `test_social_feedback_loop.py`: 4 passed
  - `test_thumbnails.py`: 5 passed
  - `test_viral_features.py`: 7 passed
  - `test_workflows_engine.py`: 9 passed
  - `test_youtube.py`: 7 passed
  - `test_youtube_download.py`: 6 passed

---

## 3. Ruff Linter Baseline (`ruff check --select F821,F841,E722,BLE001,B904 .`)
- **Total Errors Detected:** 313
- **Rule Breakdown:**
  - **`BLE001` (Blind `except Exception: pass`):** **276 occurrences** across the application.
  - **`F841` (Unused local variables):** **34 occurrences** (e.g. in `ai_copilot.py`, `settings.py`, `video_utils.py`).
  - **`F821` (Undefined variable access):** **1 occurrence** (`video_to_load` in `routes/caption_studio.py:53` before assignment).
  - **`B904` (Exception re-raise without `from`):** **2 occurrences**.

---

## 4. Bandit Security Baseline (`bandit -r . -x ./caption_studio,./tests,./.venv -ll`)
- **SQL Injection Risk (B608):** Formatted SQL strings (`f"..."`) in `routes/youtube.py` (lines 1283, 1883, 2131, 2188, 2273, 2708, 2725).
- **Unverified URL Scheme Risk (B310):** Unchecked `urlopen()` protocols in `utils/hinglish_transliterator.py`, `ai/broll.py`, `routes/settings.py`, and `routes/download.py`.
- **Hard-coded Secret Key:** Default secret key `"ai-shorts-studio-secret-key-change-me"` in `config.py`.
- **Legacy XML Parsing:** Use of standard `xml.etree` without defusedxml in `routes/download.py`.
