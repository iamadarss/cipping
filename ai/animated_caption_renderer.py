from pathlib import Path
import subprocess
import config
from ai.caption_templates import (
    get_template,
    get_all_templates,
    build_hook_title_ass,
    build_point_label_ass,
    hex_to_ass_color,
    CAPTION_TEMPLATES,
)
from ai.emoji_captions import annotate_caption_words, lookup_emoji, normalize_token


class AnimatedCaptionRenderer:

    def __init__(self):
        self.ffmpeg = config.FFMPEG_PATH

    # -----------------------------------------------
    # ASS time formatting  (H:MM:SS.cc)
    # -----------------------------------------------

    @staticmethod
    def _format_time(seconds):
        seconds = max(0.0, float(seconds))
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        sec = seconds % 60
        return f"{hours}:{minutes:02d}:{sec:05.2f}"

    # -----------------------------------------------
    # Hex color -> ASS &HBBGGRR format (and optional Alpha &HAABBGGRR&)
    # -----------------------------------------------

    @staticmethod
    def _to_ass_color(hex_color, alpha=0):
        """
        Convert #RRGGBB (or RRGGBB) to ASS &HAABBGGRR&.
        alpha: 0 (opaque) to 255 (fully transparent)
        """
        hex_color = (hex_color or "").strip().lstrip("#")
        alpha_hex = f"{max(0, min(255, int(alpha))):02X}"
        if len(hex_color) != 6:
            return f"&H{alpha_hex}FFFFFF&"
        try:
            r = hex_color[0:2]
            g = hex_color[2:4]
            b = hex_color[4:6]
            return f"&H{alpha_hex}{b}{g}{r}&"
        except Exception:
            return f"&H{alpha_hex}FFFFFF&"

    # -----------------------------------------------
    # Animation -> ASS override block (16 Professional Animations)
    # -----------------------------------------------

    @staticmethod
    def _animation_block(style, duration_ms=200):
        style = (style or "color_karaoke").lower().replace("-", "_").strip()

        # 1. Pop In (Dynamic scale overshoot)
        if style in ("pop_in", "soft_pop", "pop"):
            return r"{\fscx85\fscy85\t(0,120,\fscx106\fscy106)\t(120,200,\fscx100\fscy100)}"
        # 2. Bounce In (Elastic vertical bounce)
        if style in ("bounce_in", "bounce"):
            return r"{\fscy70\t(0,100,\fscy115)\t(100,180,\fscy95)\t(180,240,\fscy100)}"
        # 3. Smooth Fade
        if style in ("smooth_fade", "fade", "fade_in", "sentence_fade"):
            return r"{\fad(150,150)}"
        # 4. Slide Up
        if style in ("slide_up", "slide"):
            return r"{\fad(80,60)\fscy88\t(0,150,\fscy100)}"
        # 5. Slide Down
        if style == "slide_down":
            return r"{\fad(80,60)\fscy112\t(0,150,\fscy100)}"
        # 6. Zoom In
        if style in ("zoom_in", "zoom", "scale_in"):
            return r"{\fscx75\fscy75\t(0,160,\fscx100\fscy100)}"
        # 7. Zoom Out
        if style == "zoom_out":
            return r"{\fscx125\fscy125\t(0,160,\fscx100\fscy100)}"
        # 8. Typewriter
        if style == "typewriter":
            return r"{\fad(40,40)}"
        # 9. Word Reveal
        if style in ("word_reveal", "word_by_word"):
            return r"{\k80}"
        # 10. Karaoke Highlight
        if style in ("karaoke_highlight", "color_karaoke", "active_word_pill", "word_highlight"):
            return r"{\fad(80,80)}"
        # 11. Glow Pulse
        if style == "glow_pulse":
            return r"{\t(0,120,\bord4\blur6)\t(120,240,\bord2\blur2)}"
        # 12. Glitch
        if style == "glitch":
            return r"{\fscx108\fscy92\t(0,50,\fscx95\fscy105)\t(50,100,\fscx100\fscy100)}"
        # 13. Elastic Scale
        if style in ("elastic_scale", "emphasis_scale"):
            return r"{\fscx80\fscy80\t(0,140,\fscx112\fscy112)\t(140,220,\fscx98\fscy98)\t(220,280,\fscx100\fscy100)}"
        # 14. Blur Reveal
        if style == "blur_reveal":
            return r"{\blur8\t(0,180,\blur0)}"
        # 15. Split Reveal
        if style == "split_reveal":
            return r"{\fscx50\t(0,160,\fscx100)}"
        # 16. Tracking Reveal
        if style == "tracking_reveal":
            return r"{\fsp15\t(0,180,\fsp0)}"

        # Directional & utility animations
        if style == "fade_out":
            return r"{\fad(0,250)}"
        if style == "slide_left":
            return r"{\fad(80,60)\fscx88\t(0,150,\fscx100)}"
        if style == "slide_right":
            return r"{\fad(80,60)\fscx112\t(0,150,\fscx100)}"
        if style in ("character_reveal", "character_by_character"):
            return r"{\k40}"
        if style == "smooth_reveal":
            return r"{\alpha&HFF&\t(0,250,\alpha&H00&)}"
        if style == "none":
            return ""

        # Default fallback
        return r"{\fad(80,80)}"

    # -----------------------------------------------
    # Template -> preset options
    # -----------------------------------------------

    @staticmethod
    def _template_options(template):
        return get_template(template)

    # -----------------------------------------------
    # Merge template + user overrides
    # -----------------------------------------------

    @staticmethod
    def resolve_opts(opts=None, template=None):
        opts = dict(opts or {})
        if template:
            template_opts = AnimatedCaptionRenderer._template_options(template)
            template_opts.update(opts)
            return template_opts
        return opts

    # -----------------------------------------------
    # Build ASS header with configurable style
    # -----------------------------------------------

    def _build_header(self, opts, transcript=None):
        opts = opts or {}
        font = (
            opts.get("font_family")
            or opts.get("fontFamily")
            or opts.get("font")
            or config.SUBTITLE_FONT
        )

        # Detect Hindi / Devanagari Unicode codepoints and inject font fallback
        has_devanagari = False
        if transcript and isinstance(transcript, list):
            for item in transcript:
                t_str = str(item.get("text", ""))
                if any('\u0900' <= c <= '\u097f' for c in t_str):
                    has_devanagari = True
                    break
                for w in item.get("words", []):
                    w_str = str(w.get("text", ""))
                    if any('\u0900' <= c <= '\u097f' for c in w_str):
                        has_devanagari = True
                        break
        if has_devanagari and "devanagari" not in font.lower() and "segoe" not in font.lower():
            font = f"{font}, Segoe UI, Arial"
        elif "devanagari" in font.lower() or "mukta" in font.lower():
            font = f"{font}, Segoe UI, Mangal, Arial"
        elif "anton" in font.lower() or "bebas" in font.lower():
            font = f"{font}, Impact, Arial Black, Arial"
        elif "playfair" in font.lower() or "cormorant" in font.lower():
            font = f"{font}, Georgia, Times New Roman, serif"
        elif "montserrat" in font.lower() or "poppins" in font.lower():
            font = f"{font}, Inter, Arial, sans-serif"

        play_res_x = int(opts.get("play_res_x") or config.OUTPUT_WIDTH)
        play_res_y = int(opts.get("play_res_y") or config.OUTPUT_HEIGHT)

        # Scale factor between web preview coordinate system and render resolution.
        # In ASS (libass), TrueType fonts require a ~4.5x factor on 1080p (min_dim / 240.0)
        # to match the visual footprint of CSS typography on the mobile preview frame.
        min_dim = min(play_res_x, play_res_y)
        scale_ratio = max(1.0, min_dim / 240.0)
        stroke_ratio = max(1.0, min_dim / 360.0)

        try:
            raw_size = (
                opts.get("font_size")
                or opts.get("fontSize")
                or opts.get("size")
                or opts.get("caption_size")
                or 38
            )
            base_size = float(raw_size)
        except (TypeError, ValueError):
            base_size = 38.0

        # Scale font size proportionally to video resolution so rendered text matches preview screen size
        scaled_size = round(base_size * scale_ratio)
        size = max(28, min(int(scaled_size), int(play_res_y * 0.30)))

        # Primary text color & active highlight color
        text_color_hex = (
            opts.get("text_color")
            or opts.get("textColor")
            or opts.get("color")
            or "#FFFFFF"
        )
        active_color_hex = (
            opts.get("active_word_color")
            or opts.get("activeWordColor")
            or opts.get("highlight_color")
            or "#FBBF24"
        )

        # Check animation & highlight style
        anim_name = (opts.get("animation") or "pop").lower()
        if anim_name == "none":
            primary_ass = self._to_ass_color(text_color_hex)
            secondary_ass = self._to_ass_color(text_color_hex)
        else:
            primary_ass = self._to_ass_color(active_color_hex)
            secondary_ass = self._to_ass_color(text_color_hex)

        # Background mode / opacity
        bg_mode = (opts.get("bg_mode") or opts.get("bgMode") or "none").lower()
        if bg_mode == "none":
            bg_opacity = 0.0
        else:
            raw_bg_opacity = opts.get("background_opacity", opts.get("bgOpacity", 0.0))
            try:
                bg_opacity = float(raw_bg_opacity)
                if bg_opacity > 1.0:
                    bg_opacity = bg_opacity / 100.0
            except (TypeError, ValueError):
                bg_opacity = 0.65 if bg_mode in ("solid", "semi") else 0.0

        bg_alpha = int((1.0 - max(0.0, min(1.0, bg_opacity))) * 255)
        bg_hex = (
            opts.get("background_color")
            or opts.get("backgroundColor")
            or opts.get("bgColor")
            or opts.get("background")
            or "#000000"
        )
        back_ass = self._to_ass_color(bg_hex, alpha=bg_alpha)

        # Outline color & width
        outline_hex = (
            opts.get("outline_color")
            or opts.get("outlineColor")
            or opts.get("strokeColor")
            or "#000000"
        )
        outline_enabled = opts.get("outline_enabled", opts.get("strokeEnabled", True))
        if not outline_enabled:
            outline_w = 0
            outline_ass = self._to_ass_color(outline_hex, alpha=255)
        else:
            try:
                raw_outline = float(opts.get("outline_width", opts.get("strokeWidth", opts.get("outline", 3.5))))
            except (TypeError, ValueError):
                raw_outline = 3.5
            outline_w = max(1, round(raw_outline * stroke_ratio)) if raw_outline > 0 else 0
            outline_ass = self._to_ass_color(outline_hex, alpha=0)

        # Shadow color & blur/offset
        shadow_hex = (
            opts.get("shadow_color")
            or opts.get("shadowColor")
            or "#000000"
        )
        shadow_enabled = opts.get("shadow_enabled", True)
        if not shadow_enabled:
            shadow_w = 0
            shadow_ass = self._to_ass_color(shadow_hex, alpha=255)
        else:
            try:
                raw_shadow = float(opts.get("shadow_blur", opts.get("shadowBlur", opts.get("shadow", 2.0))))
            except (TypeError, ValueError):
                raw_shadow = 2.0
            shadow_w = max(1, round(raw_shadow * stroke_ratio)) if raw_shadow > 0 else 0
            shadow_ass = self._to_ass_color(shadow_hex, alpha=0)

        # Bold & Italic flags
        try:
            font_weight = int(opts.get("font_weight", opts.get("fontWeight", opts.get("weight", 800))))
        except (TypeError, ValueError):
            font_weight = 800
        bold_flag = -1 if font_weight >= 600 else 0
        italic_flag = -1 if bool(opts.get("italic", False)) else 0

        # Scale factor (100 = default)
        try:
            raw_scale = float(opts.get("scale", 100))
            if 0 < raw_scale <= 5.0:
                scale_factor = round(raw_scale * 100)
            else:
                scale_factor = round(raw_scale)
        except (TypeError, ValueError):
            scale_factor = 100

        # Letter spacing
        try:
            raw_spacing = float(opts.get("letter_spacing", opts.get("letterSpacing", opts.get("spacing", 0))))
            spacing = round(raw_spacing * scale_ratio)
        except (TypeError, ValueError):
            spacing = 0

        # BorderStyle: 1 = outline with drop shadow; 3 = opaque box (if bg_opacity >= 0.15)
        border_style = 3 if bg_opacity >= 0.15 else 1

        # Alignment calculation (ASS: 1=bot-left, 2=bot-center, 3=bot-right, 4=mid-left, 5=mid-center, 6=mid-right, 7=top-left, 8=top-center, 9=top-right)
        align_horiz = (opts.get("text_align") or opts.get("textAlign") or opts.get("alignment") or "center").lower()
        if align_horiz == "left":
            col_offset = 0
        elif align_horiz == "right":
            col_offset = 2
        else:  # center
            col_offset = 1

        position = (opts.get("position") or "bottom").lower()

        # Vertical margin calculation (support posYPercent from Caption Studio & platform safe zones)
        pos_y_pct = opts.get("posYPercent", opts.get("pos_y_percent"))
        if pos_y_pct is not None:
            try:
                py = float(pos_y_pct)
                if position == "top" or py <= 35:
                    alignment = 7 + col_offset
                    margin_v = max(40, int(py / 100.0 * play_res_y) - int(size / 2))
                elif position in ("middle", "center") or (45 <= py <= 55):
                    alignment = 4 + col_offset
                    margin_v = 0
                else:
                    alignment = 1 + col_offset
                    margin_v = max(40, int((100.0 - py) / 100.0 * play_res_y) - int(size / 2))
            except (TypeError, ValueError):
                alignment = 1 + col_offset
                margin_v = 280 if play_res_y >= 1280 else 100
        else:
            if position == "top":
                base_row = 7
                alignment = base_row + col_offset
                try:
                    raw_mv = int(opts.get("margin_v", opts.get("margin_y", 0)))
                except (TypeError, ValueError):
                    raw_mv = 0
                margin_v = raw_mv if raw_mv > 0 else (120 if play_res_y >= 1280 else 50)
            elif position in ("middle", "center"):
                base_row = 4
                alignment = base_row + col_offset
                margin_v = 0
            else:  # bottom or lower_third
                base_row = 1
                alignment = base_row + col_offset
                try:
                    raw_mv = int(opts.get("margin_v", opts.get("margin_y", 0)))
                except (TypeError, ValueError):
                    raw_mv = 0
                if play_res_y >= 1280:
                    margin_v = max(raw_mv, 280) if raw_mv > 0 else 280
                else:
                    margin_v = max(raw_mv, 60) if raw_mv > 0 else 60
                if position == "lower_third":
                    margin_v = max(margin_v, 360 if play_res_y >= 1280 else 140)

        try:
            raw_ml = float(opts.get("margin_l", opts.get("margin_x", 30)))
            raw_mr = float(opts.get("margin_r", 30))
        except (TypeError, ValueError):
            raw_ml = 30.0
            raw_mr = 30.0
        margin_l = max(20, round(raw_ml * scale_ratio))
        margin_r = max(20, round(raw_mr * scale_ratio))

        return f"""[Script Info]
ScriptType: v4.00+
WrapStyle: 2
ScaledBorderAndShadow: yes
PlayResX: {play_res_x}
PlayResY: {play_res_y}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,{font},{size},{primary_ass},{secondary_ass},{outline_ass},{back_ass},{bold_flag},{italic_flag},0,0,{scale_factor},{scale_factor},{spacing},0,{border_style},{outline_w},{shadow_w},{alignment},{margin_l},{margin_r},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    # -----------------------------------------------
    # Prepare kinetic, non-overlapping subtitle chunks
    # -----------------------------------------------

    def _prepare_kinetic_chunks(self, transcript, max_words=4):
        """
        Split long sentences into short 3-4 word kinetic chunks
        and enforce strict non-overlapping timestamps so no two lines ever collide.
        """
        raw_chunks = []

        for item in transcript:
            seg_start = float(item.get("start", 0))
            seg_end = float(item.get("end", 0))
            text = (item.get("text") or "").replace("\n", " ").strip()
            if not text or seg_end <= seg_start:
                continue

            words_data = item.get("words")
            if words_data and isinstance(words_data, list) and len(words_data) > 0:
                # Group word timestamps into chunks of at most max_words
                curr_group = []
                for w in words_data:
                    curr_group.append(w)
                    w_t = w.get("text", "").strip()
                    ends_sentence = any(w_t.endswith(p) for p in (".", "!", "?", "।", "|"))
                    if len(curr_group) >= max_words or ends_sentence:
                        c_start = float(curr_group[0].get("start", seg_start))
                        c_end = float(curr_group[-1].get("end", seg_end))
                        if c_end > c_start:
                            raw_chunks.append({
                                "start": c_start,
                                "end": c_end,
                                "text": " ".join(x.get("text", "") for x in curr_group).strip(),
                                "words": list(curr_group)
                            })
                        curr_group = []
                if curr_group:
                    c_start = float(curr_group[0].get("start", seg_start))
                    c_end = float(curr_group[-1].get("end", seg_end))
                    if c_end > c_start:
                        raw_chunks.append({
                            "start": c_start,
                            "end": c_end,
                            "text": " ".join(x.get("text", "") for x in curr_group).strip(),
                            "words": list(curr_group)
                        })
            else:
                words = text.split()
                if not words:
                    continue
                # Split into slices of max_words
                groups = [words[i:i + max_words] for i in range(0, len(words), max_words)]
                total_dur = max(0.4, seg_end - seg_start)
                step_dur = total_dur / len(groups)
                for g_idx, grp in enumerate(groups):
                    g_start = seg_start + g_idx * step_dur
                    g_end = seg_start + (g_idx + 1) * step_dur
                    raw_chunks.append({
                        "start": g_start,
                        "end": g_end,
                        "text": " ".join(grp),
                        "words": []
                    })

        if not raw_chunks:
            return []

        # Sort strictly by start time
        raw_chunks.sort(key=lambda c: c["start"])

        # Enforce strict non-overlapping intervals and sequential gap
        sanitized = []
        prev_end = 0.0
        for i, chunk in enumerate(raw_chunks):
            start = round(chunk["start"], 2)
            if start < prev_end:
                start = round(prev_end + 0.04, 2)

            end = round(chunk["end"], 2)
            if end <= start:
                end = round(start + 0.4, 2)

            # Cap excessive line linger (max 2.2s per 3-4 word chunk)
            if end - start > 2.2:
                end = round(start + 2.2, 2)

            if i + 1 < len(raw_chunks):
                next_start = round(raw_chunks[i + 1]["start"], 2)
                # If next chunk would start at or before current end, clamp current end
                if next_start <= end:
                    end = round(max(start + 0.15, next_start - 0.05), 2)

            chunk["start"] = start
            chunk["end"] = end
            if chunk["end"] > chunk["start"]:
                sanitized.append(chunk)
                prev_end = chunk["end"]

        return sanitized

    # -----------------------------------------------
    # Build ASS dialogue with accurate word-by-word \k timing
    # -----------------------------------------------

    def _build_dialogue(self, transcript, opts):
        anim_name = opts.get("animation", "pop")
        anim = self._animation_block(anim_name)
        lines = []

        # Check casing (support uppercase template flag)
        text_case = (
            opts.get("text_case")
            or opts.get("textCase")
            or opts.get("casing")
            or ("uppercase" if opts.get("uppercase") else "normal")
        ).lower()

        # Check glow effect
        glow_enabled = bool(opts.get("glow", False))
        glow_color = opts.get("glow_color") or "#70C8FF"
        glow_blur = int(opts.get("glow_blur") or 6)
        if glow_enabled:
            glow_ass = self._to_ass_color(glow_color)
            glow_tag = r"{\blur%d\bord3\3c%s}" % (glow_blur, glow_ass)
        else:
            glow_tag = ""

        two_line = bool(opts.get("two_line_hierarchy", False))
        preset_id = (opts.get("id") or "").lower()

        # Contextual emoji flag
        enable_emoji = bool(opts.get("emoji", True))

        def _apply_case(t):
            if not t:
                return t
            if text_case == "uppercase":
                return t.upper()
            if text_case == "capitalize":
                return t.capitalize()
            if text_case == "title":
                return t.title()
            if text_case == "lowercase":
                return t.lower()
            return t

        # Check if manual coordinates were supplied
        pos_override = ""
        if opts.get("use_manual_pos") and "pos_x" in opts and "pos_y" in opts:
            try:
                px = int(opts["pos_x"])
                py = int(opts["pos_y"])
                pos_override = r"{\pos(%d,%d)}" % (px, py)
            except Exception:
                pos_override = ""

        # Break long sentences into short kinetic chunks (2-4 words or user-configured chunk) with strict non-overlap
        max_words = int(
            opts.get("words_per_chunk")
            or opts.get("words_per_line")
            or opts.get("max_words_per_line")
            or 4
        )
        chunks = self._prepare_kinetic_chunks(transcript, max_words=max_words)

        for chunk in chunks:
            start = chunk["start"]
            end = chunk["end"]
            text = chunk["text"]
            dur_total_cs = max(1, int((end - start) * 100))

            words_data = chunk.get("words")
            if anim_name == "none":
                # Static subtitle line without karaoke wipes
                dialogue = (
                    f"Dialogue: 0,{self._format_time(start)},{self._format_time(end)},"
                    f"Caption,,0,0,0,,{pos_override}{glow_tag}{_apply_case(text)}"
                )
                lines.append(dialogue)
                continue

            # Contextual emoji annotations
            emoji_map = {}
            if enable_emoji and words_data and len(words_data) > 0:
                try:
                    emoji_map, _ = annotate_caption_words(words_data, enable_emoji=True)
                except Exception:
                    emoji_map = {}

            if words_data and len(words_data) > 0:
                karaoke_parts = []
                w_durs = []
                for w in words_data:
                    w_s = float(w.get("start", start))
                    w_e = float(w.get("end", end))
                    w_durs.append(max(1, int((w_e - w_s) * 100)))

                sum_d = sum(w_durs) or 1
                scaled_durs = [max(1, int((d / sum_d) * dur_total_cs)) for d in w_durs]
                diff = dur_total_cs - sum(scaled_durs)
                scaled_durs[-1] = max(1, scaled_durs[-1] + diff)

                for w_idx, (w, d_cs) in enumerate(zip(words_data, scaled_durs)):
                    w_text = _apply_case(w.get("text", "").strip())
                    if w_idx in emoji_map:
                        w_text = f"{w_text} {emoji_map[w_idx]}"
                    if w_text:
                        karaoke_parts.append(r"{\k%d}%s" % (d_cs, w_text))
            else:
                words = text.split()
                if not words:
                    continue
                word_dicts = [{"text": w} for w in words]
                emoji_map = {}
                if enable_emoji:
                    try:
                        emoji_map, _ = annotate_caption_words(word_dicts, enable_emoji=True)
                    except Exception:
                        emoji_map = {}

                per_word_cs = max(1, dur_total_cs // len(words))
                karaoke_parts = []
                for idx, w in enumerate(words):
                    cs = per_word_cs if idx < len(words) - 1 else max(1, dur_total_cs - per_word_cs * (len(words) - 1))
                    w_text = _apply_case(w)
                    if idx in emoji_map:
                        w_text = f"{w_text} {emoji_map[idx]}"
                    karaoke_parts.append(r"{\k%d}%s" % (cs, w_text))

            # Apply two-line hierarchy formatting if requested by preset
            if two_line and len(karaoke_parts) >= 2:
                if preset_id == "cinematic_creator":
                    split_idx = max(1, len(karaoke_parts) // 2)
                    line1 = r"{\fscx82\fscy82\c&H00FFFFFF&}" + " ".join(karaoke_parts[:split_idx])
                    line2 = r"\N{\fscx135\fscy135\c&H00FFD880&\blur8\bord3\3c&H00FF8800&}" + " ".join(karaoke_parts[split_idx:])
                    karaoke = f"{line1} {line2}"
                elif preset_id == "bold_keyword_yellow":
                    line1 = r"{\fscx140\fscy140\c&H0000EAFF&\bord3.5\3c&H00000000&}" + karaoke_parts[0]
                    line2 = r"\N{\fscx100\fscy100\c&H00FFFFFF&}" + " ".join(karaoke_parts[1:])
                    karaoke = f"{line1} {line2}"
                elif preset_id == "modern_kinetic_cyan":
                    if len(karaoke_parts) >= 3:
                        line1 = r"{\fscx85\fscy85\c&H00FFFFFF&}" + karaoke_parts[0]
                        line2 = r"\N{\fscx135\fscy135\c&H00FFFF00&\blur4}" + karaoke_parts[1]
                        line3 = r"\N{\fscx100\fscy100\c&H00FFFFFF&}" + " ".join(karaoke_parts[2:])
                        karaoke = f"{line1} {line2} {line3}"
                    else:
                        line1 = r"{\fscx88\fscy88\c&H00FFFFFF&}" + karaoke_parts[0]
                        line2 = r"\N{\fscx135\fscy135\c&H00FFFF00&}" + karaoke_parts[1]
                        karaoke = f"{line1} {line2}"
                elif preset_id == "editorial_layered":
                    line1 = r"{\fscx130\fscy130\c&H00E9F6FD&}" + karaoke_parts[0]
                    line2 = r"\N{\i1\c&H00E9F6FD&}" + " ".join(karaoke_parts[1:])
                    karaoke = f"{line1} {line2}"
                else:
                    split_idx = max(1, len(karaoke_parts) // 2)
                    karaoke = " ".join(karaoke_parts[:split_idx]) + r"\N" + " ".join(karaoke_parts[split_idx:])
            else:
                karaoke = " ".join(karaoke_parts)

            dialogue = (
                f"Dialogue: 0,{self._format_time(start)},{self._format_time(end)},"
                f"Caption,,0,0,0,,{pos_override}{glow_tag}{anim}{karaoke}"
            )
            lines.append(dialogue)

        return "\n".join(lines)

    # -----------------------------------------------
    # Build full ASS subtitle string
    # -----------------------------------------------

    def build_ass(self, transcript, opts=None, template=None):
        opts = self.resolve_opts(opts, template)
        hook_title = opts.get("hook_title") or opts.get("headline") or opts.get("hookTitle")
        point_labels = opts.get("point_labels") or opts.get("points") or []
        hook_style_line = ""
        hook_dialogue_lines = []
        point_style_line = ""
        point_dialogue_lines = []

        w = int(opts.get("play_res_x") or config.OUTPUT_WIDTH)
        h = int(opts.get("play_res_y") or config.OUTPUT_HEIGHT)
        dur = float(opts.get("duration") or 30.0)
        if transcript and isinstance(transcript, list) and len(transcript) > 0:
            last_end = float(transcript[-1].get("end", dur))
            dur = max(dur, last_end)

        if hook_title:
            try:
                hook_style_line, hook_dialogue_lines = build_hook_title_ass(
                    hook_title, opts, video_width=w, video_height=h, output_duration=dur
                )
            except Exception:
                pass

        if point_labels:
            try:
                point_style_line, point_dialogue_lines = build_point_label_ass(
                    point_labels, opts, video_width=w, video_height=h, output_duration=dur,
                    hook_end=4.0 if hook_title else 0.0
                )
            except Exception:
                pass

        header = self._build_header(opts, transcript=transcript)
        extra_styles = []
        if hook_style_line:
            extra_styles.append(hook_style_line)
        if point_style_line:
            extra_styles.append(point_style_line)
        if extra_styles:
            header = header.replace("[Events]", "\n".join(extra_styles) + "\n[Events]")

        dialogue = self._build_dialogue(transcript, opts)
        top_lines = []
        if hook_dialogue_lines:
            top_lines.extend(hook_dialogue_lines)
        if point_dialogue_lines:
            top_lines.extend(point_dialogue_lines)
        if top_lines:
            dialogue = "\n".join(top_lines) + "\n" + dialogue

        return header + "\n" + dialogue + "\n"

    # -----------------------------------------------
    # Save ASS to file
    # -----------------------------------------------

    def save_ass(self, transcript, output_file, opts=None, template=None):
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        ass = self.build_ass(transcript, opts, template)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(ass)
        return output_file

    # -----------------------------------------------
    # Render animated captions into the video
    # -----------------------------------------------

    def render(
        self,
        input_video,
        transcript,
        output_video,
        opts=None,
        template=None,
    ):
        input_video = Path(input_video)
        output_video = Path(output_video)
        output_video.parent.mkdir(parents=True, exist_ok=True)

        if not input_video.exists():
            raise FileNotFoundError(input_video)

        # Merge template + user overrides
        merged_opts = self.resolve_opts(opts, template)

        # Detect video dimensions if not explicitly given to ensure ASS matches aspect ratio
        if "play_res_x" not in merged_opts or "play_res_y" not in merged_opts:
            try:
                ffprobe_bin = getattr(config, "FFPROBE_PATH", None) or "ffprobe"
                cmd = [
                    str(ffprobe_bin),
                    "-v", "error",
                    "-select_streams", "v:0",
                    "-show_entries", "stream=width,height",
                    "-of", "csv=p=0:s=x",
                    str(input_video),
                ]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if res.returncode == 0 and "x" in res.stdout:
                    w, h = res.stdout.strip().split("x")[:2]
                    merged_opts["play_res_x"] = int(w)
                    merged_opts["play_res_y"] = int(h)
            except Exception:
                pass

        # Build & save the ASS file
        ass_dir = config.SUBTITLE_DIR
        ass_file = ass_dir / f"{output_video.stem}_captions.ass"
        self.save_ass(transcript, ass_file, merged_opts)

        # Windows path escaping for the ASS filter
        ass_path = str(ass_file.resolve()).replace("\\", "/").replace(":", "\\:")

        # Try preserving audio stream (-c:a copy) first
        command = [
            self.ffmpeg,
            "-y",
            "-i", str(input_video),
            "-vf", f"ass='{ass_path}'",
            "-c:v", config.VIDEO_CODEC,
            "-preset", "veryfast",
            "-crf", "23",
            "-c:a", "copy",
            str(output_video),
        ]

        print("=" * 60)
        print("Rendering Animated Captions with FFmpeg...")
        print("=" * 60)

        try:
            subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            print("[SUCCESS] Animated Captions Rendered Successfully:", output_video)
            return output_video
        except subprocess.CalledProcessError:
            # Fallback with audio re-encode in case copy fails
            try:
                command[command.index("copy")] = config.AUDIO_CODEC
                subprocess.run(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True,
                )
                print("[SUCCESS] Animated Captions Rendered Successfully (audio fallback):", output_video)
                return output_video
            except subprocess.CalledProcessError as e:
                print("[ERROR] Animated Caption Rendering Failed:", e)
                return None
