from pathlib import Path
import subprocess
import config


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
    # Animation -> ASS override block
    # -----------------------------------------------

    @staticmethod
    def _animation_block(style, duration_ms=300):
        style = (style or "pop").lower().replace("-", "_")
        if style in ("fade", "fade_in"):
            return r"{\fad(150,150)}"
        if style == "fade_out":
            return r"{\fad(0,250)}"
        if style == "bounce":
            return r"{\move(0,0)\t(0,200,\fay-0.08)\t(200,400,\fay0)}"
        if style in ("slide", "slide_up"):
            return r"{\move(0,35,0,0,0,200)}"
        if style == "slide_down":
            return r"{\move(0,-35,0,0,0,200)}"
        if style == "slide_left":
            return r"{\move(40,0,0,0,0,200)}"
        if style == "slide_right":
            return r"{\move(-40,0,0,0,0,200)}"
        if style in ("scale_in", "zoom"):
            return r"{\fscx75\fscy75\t(0,180,\fscx100\fscy100)}"
        if style == "pop":
            return r"{\fscx80\fscy80\t(0,120,\fscx112\fscy112)\t(120,200,\fscx100\fscy100)}"
        if style in ("word_reveal", "word_by_word"):
            return r"{\k80}"
        if style in ("character_reveal", "character_by_character"):
            return r"{\k40}"
        if style == "smooth_reveal":
            return r"{\alpha&HFF&\t(0,250,\alpha&H00&)}"
        if style == "none":
            return ""
        # Default fallback: pop
        return r"{\fscx82\fscy82\t(0,140,\fscx100\fscy100)}"

    # -----------------------------------------------
    # Template -> preset options
    # -----------------------------------------------

    @staticmethod
    def _template_options(template):
        template = (template or "hormozi_pop").lower()
        templates = {
            "hormozi_pop": {
                "font": "Arial Black", "size": 42, "weight": 900, "color": "#FFFFFF",
                "highlight_color": "#FFDD00", "background": "#000000", "background_opacity": 0.0,
                "outline": 4, "shadow": 4, "position": "bottom", "margin_v": 75, "animation": "pop",
                "description": "Alex Hormozi Viral Style — Yellow punch, bold black outline, high-energy pop"
            },
            "beast_glow": {
                "font": "Arial Black", "size": 44, "weight": 900, "color": "#FFFFFF",
                "highlight_color": "#39FF14", "background": "#000000", "background_opacity": 0.0,
                "outline": 5, "shadow": 6, "position": "bottom", "margin_v": 80, "animation": "bounce",
                "description": "MrBeast Style — Electric lime neon active word with heavy punchy stroke"
            },
            "red_punch": {
                "font": "Arial Black", "size": 42, "weight": 900, "color": "#FFFFFF",
                "highlight_color": "#FF2A2A", "background": "#000000", "background_opacity": 0.0,
                "outline": 4, "shadow": 5, "position": "bottom", "margin_v": 75, "animation": "pop",
                "description": "High Drama / Breaking News — Fiery red highlight on crisp white text"
            },
            "clean_gold": {
                "font": "Inter", "size": 36, "weight": 700, "color": "#FFFFFF",
                "highlight_color": "#F59E0B", "background": "#0F172A", "background_opacity": 0.45,
                "outline": 2, "shadow": 3, "position": "bottom", "margin_v": 70, "animation": "fade_in",
                "description": "Luxury Gold — Podcast & business minimal aesthetic with warm amber highlight"
            },
            "neon_cyber": {
                "font": "Montserrat", "size": 40, "weight": 800, "color": "#FFFFFF",
                "highlight_color": "#D946EF", "background": "#000000", "background_opacity": 0.0,
                "outline": 3, "shadow": 5, "position": "bottom", "margin_v": 75, "animation": "pop",
                "description": "Cyberpunk Neon — Vibrant fuchsia glow for modern gaming/tech reels"
            },
            "karaoke_pill": {
                "font": "Inter", "size": 34, "weight": 700, "color": "#FFFFFF",
                "highlight_color": "#38BDF8", "background": "#000000", "background_opacity": 0.70,
                "outline": 0, "shadow": 0, "position": "bottom", "margin_v": 65, "animation": "none",
                "description": "Karaoke Pill — Smooth rounded backdrop container with electric cyan highlight"
            },
            # Aliases & backward compatibility
            "tiktok_pop": {
                "font": "Arial Black", "size": 42, "weight": 900, "color": "#FFFFFF",
                "highlight_color": "#FFDD00", "background": "#000000", "background_opacity": 0.0,
                "outline": 4, "shadow": 4, "position": "bottom", "margin_v": 75, "animation": "pop"
            },
            "clean": {
                "font": "Inter", "size": 32, "weight": 700, "color": "#FFFFFF",
                "highlight_color": "#38BDF8", "background": "#000000", "background_opacity": 0.0,
                "outline": 1, "shadow": 2, "position": "bottom", "margin_v": 70, "animation": "fade_in"
            },
            "bold": {
                "font": "Anton", "size": 44, "weight": 800, "color": "#FFFFFF",
                "highlight_color": "#F43F5E", "background": "#000000", "background_opacity": 0.0,
                "outline": 4, "shadow": 6, "position": "bottom", "margin_v": 60, "animation": "bounce"
            },
            "minimal": {
                "font": "DM Sans", "size": 28, "weight": 600, "color": "#FFFFFF",
                "highlight_color": "#FFFFFF", "background": "#000000", "background_opacity": 0.0,
                "outline": 0, "shadow": 2, "position": "bottom", "margin_v": 80, "animation": "none"
            },
            "creator": {
                "font": "Poppins", "size": 36, "weight": 800, "color": "#FFFFFF",
                "highlight_color": "#22D3EE", "background": "#0F172A", "background_opacity": 0.5,
                "outline": 2, "shadow": 4, "position": "bottom", "margin_v": 60, "animation": "pop"
            },
            "podcast": {
                "font": "Montserrat", "size": 34, "weight": 800, "color": "#FFFFFF",
                "highlight_color": "#FBBF24", "background": "#000000", "background_opacity": 0.7,
                "outline": 0, "shadow": 3, "position": "lower_third", "margin_v": 130, "animation": "fade_in"
            },
            "news": {
                "font": "Arial Black", "size": 36, "weight": 900, "color": "#FFFFFF",
                "highlight_color": "#EF4444", "background": "#1E293B", "background_opacity": 0.85,
                "outline": 2, "shadow": 4, "position": "bottom", "margin_v": 50, "animation": "slide_up"
            },
            "gaming": {
                "font": "Bebas Neue", "size": 48, "weight": 900, "color": "#00FF66",
                "highlight_color": "#FF0055", "background": "#000000", "background_opacity": 0.0,
                "outline": 4, "shadow": 8, "position": "bottom", "margin_v": 60, "animation": "pop"
            },
            "dynamic": {
                "font": "Plus Jakarta Sans", "size": 38, "weight": 800, "color": "#FFFFFF",
                "highlight_color": "#A855F7", "background": "#000000", "background_opacity": 0.0,
                "outline": 3, "shadow": 5, "position": "bottom", "margin_v": 60, "animation": "pop"
            },
            "classic": {
                "font": "Arial", "size": 32, "weight": 700, "color": "#FFFFFF",
                "highlight_color": "#FFD700", "background": "#000000", "background_opacity": 0.0,
                "outline": 3, "shadow": 3, "position": "bottom", "margin_v": 60, "animation": "pop"
            }
        }
        return templates.get(template, templates["hormozi_pop"])

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

    def _build_header(self, opts):
        opts = opts or {}
        font = (
            opts.get("font_family")
            or opts.get("fontFamily")
            or opts.get("font")
            or config.SUBTITLE_FONT
        )
        try:
            raw_size = (
                opts.get("font_size")
                or opts.get("fontSize")
                or opts.get("size")
                or opts.get("caption_size")
                or 34
            )
            size = int(raw_size)
        except (TypeError, ValueError):
            size = 34

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

        # Background / outline color & opacity
        raw_bg_opacity = opts.get("background_opacity", opts.get("bgOpacity", 0.0))
        try:
            bg_opacity = float(raw_bg_opacity)
            if bg_opacity > 1.0:
                bg_opacity = bg_opacity / 100.0
        except (TypeError, ValueError):
            bg_opacity = 0.0
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
                outline_w = int(opts.get("outline_width", opts.get("strokeWidth", opts.get("outline", 3))))
            except (TypeError, ValueError):
                outline_w = 3
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
                shadow_w = int(opts.get("shadow_blur", opts.get("shadowBlur", opts.get("shadow", 2))))
            except (TypeError, ValueError):
                shadow_w = 2
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
            spacing = int(opts.get("letter_spacing", opts.get("letterSpacing", opts.get("spacing", 0))))
        except (TypeError, ValueError):
            spacing = 0

        # BorderStyle: 1 = outline with drop shadow; 3 = opaque box (if bg_opacity >= 0.15)
        border_style = 3 if bg_opacity >= 0.15 else 1

        # Alignment calculation (ASS: 1=bot-left, 2=bot-center, 3=bot-right, 4=mid-left, 5=mid-center, 6=mid-right, 7=top-left, 8=top-center, 9=top-right)
        align_horiz = (opts.get("text_align") or opts.get("textAlign") or opts.get("alignment") or "center").lower()
        position = (opts.get("position") or "bottom").lower()

        if position == "top":
            base_row = 7
        elif position in ("middle", "center"):
            base_row = 4
        else:  # bottom or lower_third
            base_row = 1

        if align_horiz == "left":
            col_offset = 0
        elif align_horiz == "right":
            col_offset = 2
        else:  # center
            col_offset = 1

        alignment = base_row + col_offset

        play_res_x = int(opts.get("play_res_x") or config.OUTPUT_WIDTH)
        play_res_y = int(opts.get("play_res_y") or config.OUTPUT_HEIGHT)

        # Vertical margin calculation (support posYPercent from Caption Studio)
        pos_y_pct = opts.get("posYPercent", opts.get("pos_y_percent"))
        if pos_y_pct is not None:
            try:
                py = float(pos_y_pct)
                if position == "top":
                    margin_v = max(20, int(py / 100.0 * play_res_y))
                elif position in ("middle", "center"):
                    margin_v = 0
                else:
                    margin_v = max(20, int((100.0 - py) / 100.0 * play_res_y))
            except (TypeError, ValueError):
                margin_v = 60
        else:
            try:
                margin_v = int(opts.get("margin_v", opts.get("margin_y", 60)))
                if position == "lower_third":
                    margin_v = max(margin_v, 140)
            except (TypeError, ValueError):
                margin_v = 60

        try:
            margin_l = int(opts.get("margin_l", opts.get("margin_x", 30)))
            margin_r = int(opts.get("margin_r", 30))
        except (TypeError, ValueError):
            margin_l = 30
            margin_r = 30

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

        # Check if manual coordinates were supplied
        pos_override = ""
        if opts.get("use_manual_pos") and "pos_x" in opts and "pos_y" in opts:
            try:
                px = int(opts["pos_x"])
                py = int(opts["pos_y"])
                pos_override = r"{\pos(%d,%d)}" % (px, py)
            except Exception:
                pos_override = ""

        # Break long sentences into short kinetic chunks (2-4 words) with strict non-overlap
        chunks = self._prepare_kinetic_chunks(transcript, max_words=4)

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
                    f"Caption,,0,0,0,,{pos_override}{text}"
                )
                lines.append(dialogue)
                continue

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

                for w, d_cs in zip(words_data, scaled_durs):
                    w_text = w.get("text", "").strip()
                    if w_text:
                        karaoke_parts.append(r"{\k%d}%s" % (d_cs, w_text))
                karaoke = " ".join(karaoke_parts)
            else:
                words = text.split()
                if not words:
                    continue
                per_word_cs = max(1, dur_total_cs // len(words))
                karaoke_parts = []
                for idx, w in enumerate(words):
                    cs = per_word_cs if idx < len(words) - 1 else max(1, dur_total_cs - per_word_cs * (len(words) - 1))
                    karaoke_parts.append(r"{\k%d}%s" % (cs, w))
                karaoke = " ".join(karaoke_parts)

            dialogue = (
                f"Dialogue: 0,{self._format_time(start)},{self._format_time(end)},"
                f"Caption,,0,0,0,,{pos_override}{anim}{karaoke}"
            )
            lines.append(dialogue)

        return "\n".join(lines)

    # -----------------------------------------------
    # Build full ASS subtitle string
    # -----------------------------------------------

    def build_ass(self, transcript, opts=None, template=None):
        opts = self.resolve_opts(opts, template)
        header = self._build_header(opts)
        dialogue = self._build_dialogue(transcript, opts)
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
