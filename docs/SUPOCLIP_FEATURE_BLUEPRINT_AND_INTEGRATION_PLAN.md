# 🚀 SupoClip Complete Analysis & UpClip Studio Integration Blueprint

> **Reference Repository:** [FujiwaraChoki/supoclip](https://github.com/FujiwaraChoki/supoclip.git)  
> **Target Project:** UpClip Studio (`clipper 2.0`)  
> **Author & Architect:** Antigravity AI  
> **Date:** November 2026

---

## 📑 Table of Contents
1. [Executive Summary & Architectural Comparison](#1-executive-summary--architectural-comparison)
2. [SupoClip UI/UX Theme & Design System](#2-supoclip-uiux-theme--design-system)
3. [Full Feature Matrix & New Features Breakdown](#3-full-feature-matrix--new-features-breakdown)
4. [Exhaustive Caption Preset Catalog & ASS Rendering Mechanics](#4-exhaustive-caption-preset-catalog--ass-rendering-mechanics)
   - 4.1. The 7 Production Presets
   - 4.2. Contextual Emoji Injection (`emoji_captions.py`)
   - 4.3. Non-Vibrating Kinetic Word Pop & Pill Box
   - 4.4. Hook Title Burned Banner
5. [Clipping Methods & Advanced Video Layouts](#5-clipping-methods--advanced-video-layouts)
   - 5.1. YuNet ONNX Neural Face Detection
   - 5.2. Diarization-Driven Active-Speaker Auto-Framing
   - 5.3. Split-Screen / Stacked Call Layout
   - 5.4. Reaction Video Inset Separation & Layout
   - 5.5. Blur-Padded Frame for Galleries and Low Angles
6. [AI Viral Clip Selector, Prompts & Scoring Engine](#6-ai-viral-clip-selector-prompts--scoring-engine)
   - 6.1. 4-Pillar Virality Scoring Formula (0–100)
   - 6.2. Windowed Sliding Analysis for 1–3 Hour VODs
   - 6.3. Global Candidate Deduplication & Reranker
   - 6.4. The 5 Specialized Workflows
7. [Gap Analysis: UpClip Studio vs SupoClip](#7-gap-analysis-upclip-studio-vs-supoclip)
8. [Step-by-Step Implementation Roadmap for UpClip Studio](#8-step-by-step-implementation-roadmap-for-upclip-studio)

---

## 1. Executive Summary & Architectural Comparison

**SupoClip** is an open-source, full-stack alternative to OpusClip. It takes long-form media (YouTube, Twitch VODs, Kick, local uploads) and transforms them into high-converting 9:16 vertical shorts with AI-driven face tracking, speech diarization, viral scoring, kinetic subtitles, and stock B-roll cutaways.

### High-Level Architecture Comparison

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SUPOCLIP ARCHITECTURE                           │
├────────────────────────────────────────────────────────────────────────┤
│ Frontend: Next.js 15 (App Router) + Tailwind CSS v4 + Radix UI         │
│ Backend:  FastAPI + SQLAlchemy + PostgreSQL + Redis (ARQ worker)       │
│ AI Layer: Pydantic AI (Multi-LLM: Gemini, Claude, GPT, Ollama)         │
│ CV/Audio: YuNet ONNX + OpenCV + AssemblyAI / Faster-Whisper + FFmpeg   │
│ B-Roll:   Pexels API integration with keyword query matching           │
│ Pubs:     Direct OAuth to YouTube, TikTok, Instagram                   │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│                      UPCLIP STUDIO (clipper 2.0)                       │
├────────────────────────────────────────────────────────────────────────┤
│ Frontend: Flask + Jinja2 + Custom CSS Glassmorphism + React Vite SPA   │
│ Backend:  Flask 3.1 + SQLite + SQLAlchemy (Local & Desktop friendly)   │
│ AI Layer: Multi-modal heuristics (Audio RMS, Motion, Face, Whisper)    │
│ CV/Audio: OpenCV Haar Cascade + PySceneDetect + libass FFmpeg          │
│ Assets:   Local SFX mixdown, watermarks, outro cards, B-rolls          │
│ Pubs:     Google OAuth 2.0 YouTube Creator Desk Scheduler              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. SupoClip UI/UX Theme & Design System

SupoClip uses a clean, modern creator interface powered by **Tailwind CSS v4** and **OKLCH Color Spaces**:

### Color Palette & Visual Language
* **Brand Primary:** `oklch(0.64 0.2 38)` (Vibrant warm coral-amber / neon orange).
* **Brand Soft:** `oklch(0.96 0.03 50)` (Light mode hover/tint) / `oklch(0.3 0.06 40)` (Dark mode accent).
* **Background & Canvas:**
  * Light Mode: Pure white `#FFFFFF` with canvas tone `oklch(0.985 0.002 75)`.
  * Dark Mode: Deep neutral charcoal `oklch(0.147 0.004 49.25)` and card surface `oklch(0.216 0.006 56.043)`.
* **Typography:**
  * Display / Headlines: **Syne** (bold, futuristic sans-serif).
  * Interface / Body: **Geist Sans** (ultra-legible tech sans).
  * Code / Monospace: **Geist Mono**.
  * Caption Bundled Fonts: **THEBOLDFONT**, **TikTokSans-Bold**, **Montserrat**, **Anton**, **Inter**, **Poppins**, **Bebas Neue**, **Oswald**.

---

## 3. Full Feature Matrix & New Features Breakdown

| Feature Area | SupoClip Feature | UpClip Studio Status | UpClip Studio Action |
| :--- | :--- | :--- | :--- |
| **Video Ingestion** | YouTube, Twitch VODs/Clips, Kick VODs, Direct Upload | YouTube (yt-dlp) + Local files | Add Twitch & Kick link parsers via yt-dlp |
| **Speech-to-Text** | AssemblyAI + Local Whisper fallback | OpenAI Whisper (Base/Small) | Keep Whisper; add AssemblyAI cloud option |
| **Workflows** | 5 Modes: Highlights, Series, Topic, Recap, Trailer | Single batch pipeline | Add Workflow Manager & Multi-prompt modes |
| **Viral Scoring** | LLM-based 4-Pillar Virality (0–100) + Hook type | Heuristic 5-Pillar formula | Combine LLM scoring with Audio/Visual heuristics |
| **Hook Titles** | Burned 3–9 word title on top safe area (first 3–5s) | Outro CTA & Watermarks | **Add Hook Title ASS Generator** |
| **Face Tracking** | YuNet ONNX Neural Face Detector (OpenCV FaceDetectorYN) | Haar Cascade / Basic FaceDetector | **Add YuNet ONNX model & detector** |
| **Multi-Speaker Framing**| Diarization mouth-motion matching & wide-shot cutting | Single center crop | **Add SpeakerFraming & Turn Snapping** |
| **Dynamic Layouts** | Single crop, Stacked call, Reaction corner, Blur-padded | 9:16, 4:5, 1:1 simple reframe | **Add Stacked & Reaction Layouts** |
| **Caption Presets** | 7 Presets with word_pop, word_box, glow, emoji, uppercase | 6 Presets (Hormozi, Beast, etc.) | **Adopt exact 7 Presets + parameters** |
| **Contextual Emojis** | Deterministic 150+ keyword map + rate limiter | Not implemented | **Port `emoji_captions.py`** |
| **Power Words** | Visual emphasis on superlatives, numbers, percentages | Basic highlight | **Port `POWER_WORDS` engine** |
| **B-Roll Cutaways** | Automatic Pexels stock video search & overlay | Local B-roll file upload | **Add Pexels API B-roll finder** |
| **Pacing Control** | Cut long pauses (configurable ms) + filler removal | SilenceDetector & filler cleanup | Already present; connect to UI sliders |
| **Social Publishing** | YouTube, TikTok, Instagram | YouTube OAuth Desk | Keep YouTube, add TikTok/Instagram stubs |

---

## 4. Exhaustive Caption Preset Catalog & ASS Rendering Mechanics

### 4.1. The 7 Production Presets
Defined in SupoClip's `caption_templates.py`:
1. **Default:** Yellow active word pop, contextual emojis, clean black border.
2. **Hormozi:** Bold green highlight with rounded green pill backing box behind active word, all uppercase.
3. **MrBeast:** Bright yellow text with red pop highlights and bold outline (stroke 5px).
4. **Minimal:** Subtle fade animation, 50% semi-transparent dark backing container.
5. **TikTok:** Official TikTok pink (`#FE2C55`) active word pop with drop shadow.
6. **Neon:** Electric cyan text with vibrant magenta highlight and soft neon glow (`\blur4`).
7. **Podcast:** Warm amber gold (`#FFB800`) highlight on dark 80% opacity pill background.

---

## 5. Clipping Methods & Advanced Video Layouts

1. **YuNet ONNX Neural Face Tracking:** Uses OpenCV `FaceDetectorYN` with `face_detection_yunet_2023mar.onnx` (<5ms CPU inference).
2. **Diarization Active-Speaker Framing:** Detects speaker changes, filters turns <1.2s, cuts 0.15s before speech starts, and switches to active speaker.
3. **Stacked 2-Tile Layout:** Places Speaker 1 in top 800px tile and Speaker 2 in bottom 800px tile; leaves 320px center gap for subtitles.
4. **Reaction Layout:** Detects streamer webcam in corner, splits into 640px reactor + 1280px source video.
5. **Blur-Padded Fallback:** High quality downscale with 25px Gaussian blur padding.

---

## 6. AI Viral Clip Selector, Prompts & Scoring Engine

1. **4-Pillar Score (0–100):** Hook (25) + Engagement (25) + Value (25) + Shareability (25).
2. **Hook Classification:** Detects if hook is question, statement, statistic, story, or contrast.
3. **Hook Title Burned Banner:** Creates 3–9 word high-impact headline burned on the top of the video with fade-in and scale pop.
4. **Windowed Sliding Analysis:** 12-minute chunks with 2-minute overlaps to process multi-hour podcasts and stream VODs.
5. **5 Workflows:** Highlights, Series, Topic, Recap, and Trailer.

---

## 7. Implementation Steps for UpClip Studio

See root file [`SUPOCLIP_FEATURE_BLUEPRINT_AND_INTEGRATION_PLAN.md`](../SUPOCLIP_FEATURE_BLUEPRINT_AND_INTEGRATION_PLAN.md) for full implementation details and code snippets.

