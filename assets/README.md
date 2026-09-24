# 🎨 UpClip Studio Assets Guide

This directory stores reusable creative assets, branding files, typography, and audio tracks used across the UpClip Studio rendering pipeline, Video Editor, and Caption Studio.

---

## 📁 Directory Structure & Supported Formats

### 1. `fonts/`
- **Purpose**: Custom TTF/OTF typography used by `AnimatedCaptionRenderer`, `SubtitleRenderer`, and Graphic Overlays.
- **Recommended Formats**: `.ttf`, `.otf`
- **Popular Fonts for Shorts**:
  - `TheBoldFont.ttf` (MrBeast / Alex Hormozi style)
  - `Montserrat-ExtraBold.ttf`
  - `KomikaAxis.ttf`
  - `BebasNeue.ttf`

### 2. `overlays/`
- **Purpose**: Static and transparent motion graphics, lower-thirds, progress bars, channel logos, and stickers.
- **Recommended Formats**: `.png` (with alpha transparency), `.webp`, `.svg`
- **Optimal Canvas Resolution**: 1080x1920 (9:16 vertical)

### 3. `music/`
- **Purpose**: Royalty-free background audio tracks, ambient music, and sound effects for automatic audio mixing via `AudioMixer`.
- **Recommended Formats**: `.mp3`, `.wav`, `.m4a`
- **Usage**: Background volume is auto-ducked during speech segments.

### 4. `intro/`
- **Purpose**: Reusable channel branding intros or visual hooks prepended to generated clips.
- **Recommended Formats**: `.mp4`, `.mov` (1080x1920 vertical or 1920x1080 landscape)

### 5. `outro/`
- **Purpose**: Call-to-action cards (Subscribe / Follow / Like) appended to the end of exported shorts.
- **Recommended Formats**: `.mp4`, `.mov`

---

*Note: Large media assets placed here should be royalty-free and optimized for fast FFmpeg rendering.*
