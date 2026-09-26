"""
Viral Content Enhancer for UpClip Studio.
Provides high-impact automation for:
1. Channel Logo & Watermark burning (custom position, scale, opacity, margins)
2. Outro & Subscribe + Bell Icon CTA Card generation & timed overlay
3. Sound Effects (SFX) audio mixdown (whoosh, pop, chime, click) on caption transitions
4. B-Roll Video/Image Cutaway Overlay with speech audio preservation
"""

import os
import math
import subprocess
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

import config


class ViralEnhancer:
    def __init__(self):
        self.ffmpeg = str(getattr(config, "FFMPEG_PATH", "ffmpeg"))
        self.ffprobe = str(getattr(config, "FFPROBE_PATH", "ffprobe"))
        self.audio_dir = Path(getattr(config, "AUDIO_DIR", config.ROOT_DIR / "static" / "audio"))

    def get_video_info(self, video_path):
        """Probe video resolution, duration, and audio presence."""
        info = {"width": 1080, "height": 1920, "duration": 30.0, "has_audio": True}
        try:
            cmd = [
                self.ffprobe,
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,duration:format=duration",
                "-of", "json",
                str(video_path),
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            import json
            data = json.loads(res.stdout)
            streams = data.get("streams", [])
            if streams:
                v = streams[0]
                info["width"] = int(v.get("width") or 1080)
                info["height"] = int(v.get("height") or 1920)
                if v.get("duration"):
                    info["duration"] = float(v["duration"])
            if data.get("format", {}).get("duration"):
                info["duration"] = float(data["format"]["duration"])
        except Exception as e:
            print(f"[VIRAL_ENHANCER] Video probe notice: {e}")

        # Check audio stream
        try:
            cmd_a = [
                self.ffprobe,
                "-v", "error",
                "-select_streams", "a:0",
                "-show_entries", "stream=index",
                "-of", "csv=p=0",
                str(video_path),
            ]
            res_a = subprocess.run(cmd_a, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            info["has_audio"] = bool(res_a.stdout.strip())
        except Exception:
            pass

        return info

    def generate_text_watermark_image(self, text, output_path=None, font_size=36, opacity=0.8):
        """Generate high-contrast transparent PNG text watermark."""
        if output_path is None:
            temp_dir = config.OUTPUT_DIR / "temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            output_path = temp_dir / f"txt_wm_{int(time.time() * 1000)}.png"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            tfont = ImageFont.truetype("C:/Windows/Fonts/ariblk.ttf", font_size)
        except Exception:
            try:
                tfont = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", font_size)
            except Exception:
                tfont = ImageFont.load_default()

        dummy = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        ddraw = ImageDraw.Draw(dummy)
        bbox = ddraw.textbbox((0, 0), text, font=tfont)
        w = max(100, (bbox[2] - bbox[0]) + 30)
        h = max(40, (bbox[3] - bbox[1]) + 20)

        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Drop shadow
        draw.text((12, 12), text, fill=(0, 0, 0, int(180 * opacity)), font=tfont)
        # Foreground text
        draw.text((10, 10), text, fill=(255, 255, 255, int(255 * opacity)), font=tfont)
        img.save(output_path, "PNG")
        return output_path

    def generate_outro_cta_card(self, channel_name="UpClip Creator", handle="@creator", logo_path=None, output_path=None, card_width=860, card_height=240):
        """
        Dynamically draw a high-resolution, modern YouTube/Instagram style
        Subscribe & Bell Icon CTA Card using Pillow.
        """
        if output_path is None:
            temp_dir = config.OUTPUT_DIR / "temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            output_path = temp_dir / f"outro_card_{int(time.time() * 1000)}.png"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        card = Image.new("RGBA", (card_width, card_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(card)

        # 1. Glassmorphic Outer Card with subtle gradient & border
        draw.rounded_rectangle(
            [0, 0, card_width - 1, card_height - 1],
            radius=40,
            fill=(14, 16, 22, 235),
            outline=(255, 255, 255, 45),
            width=3
        )

        # 2. Font Loading with fallbacks
        def _get_font(size, bold=True):
            font_names = ["segoeuib.ttf", "arialbd.ttf", "ariblk.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]
            for fn in font_names:
                fp = Path("C:/Windows/Fonts") / fn
                if fp.exists():
                    try:
                        return ImageFont.truetype(str(fp), size)
                    except Exception:
                        pass
            return ImageFont.load_default()

        font_title = _get_font(40, bold=True)
        font_handle = _get_font(24, bold=False)
        font_btn = _get_font(28, bold=True)
        font_icon = _get_font(34, bold=True)

        # 3. Channel Avatar / Logo circle
        avatar_x = 40
        avatar_y = (card_height - 140) // 2
        avatar_size = 140

        avatar_drawn = False
        if logo_path and Path(logo_path).exists():
            try:
                logo_img = Image.open(logo_path).convert("RGBA")
                logo_img = logo_img.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
                # Circular mask
                mask = Image.new("L", (avatar_size, avatar_size), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse([0, 0, avatar_size, avatar_size], fill=255)
                card.paste(logo_img, (avatar_x, avatar_y), mask)
                # Outer ring
                draw.ellipse([avatar_x - 2, avatar_y - 2, avatar_x + avatar_size + 2, avatar_y + avatar_size + 2], outline=(255, 255, 255, 120), width=3)
                avatar_drawn = True
            except Exception as err:
                print(f"[VIRAL_ENHANCER] Logo load note: {err}")

        if not avatar_drawn:
            # Stylish default avatar gradient circle with initial letter
            draw.ellipse([avatar_x, avatar_y, avatar_x + avatar_size, avatar_y + avatar_size], fill=(239, 68, 68, 255), outline=(255, 255, 255, 150), width=3)
            init_letter = (channel_name[:1] if channel_name else "U").upper()
            draw.text((avatar_x + 48, avatar_y + 34), init_letter, fill=(255, 255, 255, 255), font=_get_font(60, bold=True))

        # 4. Channel Name & Handle
        text_x = avatar_x + avatar_size + 30
        draw.text((text_x, avatar_y + 22), channel_name[:22], fill=(255, 255, 255, 255), font=font_title)
        draw.text((text_x, avatar_y + 80), handle if handle.startswith("@") else f"@{handle}", fill=(160, 174, 192, 255), font=font_handle)

        # 5. Red Subscribe Pill Button
        btn_w = 210
        btn_h = 72
        btn_x = card_width - btn_w - 45
        btn_y = (card_height - btn_h) // 2

        # Red button background
        draw.rounded_rectangle(
            [btn_x, btn_y, btn_x + btn_w, btn_y + btn_h],
            radius=36,
            fill=(255, 0, 0, 255)
        )
        # Bell icon + SUBSCRIBE text
        draw.text((btn_x + 28, btn_y + 16), "🔔", fill=(255, 255, 255, 255), font=font_icon)
        draw.text((btn_x + 72, btn_y + 20), "SUBSCRIBE", fill=(255, 255, 255, 255), font=font_btn)

        card.save(output_path, "PNG")
        return output_path

    def composite_enhancements(
        self,
        input_video,
        output_video,
        watermark=None,
        outro_cta=None,
        sfx=None,
        b_rolls=None,
        captions=None,
    ):
        """
        Composite all active viral enhancements into the video stream via a unified FFmpeg execution.
        """
        input_video = Path(input_video)
        output_video = Path(output_video)
        output_video.parent.mkdir(parents=True, exist_ok=True)

        if not input_video.exists():
            raise FileNotFoundError(f"Input video not found: {input_video}")

        info = self.get_video_info(input_video)
        video_w = info["width"]
        video_h = info["height"]
        duration = info["duration"]

        temp_dir = config.OUTPUT_DIR / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_files = []

        # Determine if any video overlays exist
        video_inputs = [f"-i", str(input_video)]
        filter_chains = []
        last_v_stream = "[0:v]"
        current_input_index = 1

        # -------------------------------------------------------------
        # 1. B-Roll Video / Image Overlays
        # -------------------------------------------------------------
        if b_rolls and isinstance(b_rolls, list):
            for b_item in b_rolls:
                b_path_str = b_item.get("path") or b_item.get("file_path") or ""
                b_path = Path(b_path_str)
                if not b_path.exists():
                    continue

                b_start = max(0.0, float(b_item.get("start", 0.0)))
                b_end = min(duration, float(b_item.get("end", b_start + 3.0)))
                if b_end <= b_start:
                    continue

                b_mode = b_item.get("mode", "cutaway").lower() # cutaway (fullscreen) or pip (picture-in-picture)
                b_idx = current_input_index
                current_input_index += 1
                video_inputs.extend(["-i", str(b_path)])

                b_scaled = f"[b_scaled_{b_idx}]"
                if b_mode == "pip":
                    pip_w = int(video_w * 0.45)
                    pip_h = int(video_h * 0.35)
                    filter_chains.append(f"[{b_idx}:v]scale={pip_w}:{pip_h}:force_original_aspect_ratio=decrease,pad={pip_w}:{pip_h}:(ow-iw)/2:(oh-ih)/2:black{b_scaled}")
                    pip_x = int(video_w * 0.05)
                    pip_y = int(video_h * 0.05)
                    next_v = f"[v_broll_{b_idx}]"
                    filter_chains.append(f"{last_v_stream}{b_scaled}overlay=x={pip_x}:y={pip_y}:enable='between(t,{b_start:.2f},{b_end:.2f})'{next_v}")
                    last_v_stream = next_v
                else:
                    # Fullscreen cutaway overlay
                    filter_chains.append(f"[{b_idx}:v]scale={video_w}:{video_h}:force_original_aspect_ratio=increase,crop={video_w}:{video_h}{b_scaled}")
                    next_v = f"[v_broll_{b_idx}]"
                    filter_chains.append(f"{last_v_stream}{b_scaled}overlay=x=0:y=0:enable='between(t,{b_start:.2f},{b_end:.2f})'{next_v}")
                    last_v_stream = next_v

        # -------------------------------------------------------------
        # 2. Channel Logo / Watermark
        # -------------------------------------------------------------
        if watermark and watermark.get("enabled"):
            w_img_str = watermark.get("image_path") or watermark.get("path")
            w_text = watermark.get("text", "").strip()
            w_pos = (watermark.get("position") or "top_right").lower()
            w_scale_pct = float(watermark.get("scale", 15)) / 100.0  # 15% of video width
            w_opacity = float(watermark.get("opacity", 80)) / 100.0  # 80% opacity
            w_margin = int(watermark.get("margin", 40))

            logo_target_w = max(60, int(video_w * w_scale_pct))
            logo_img_path = None

            if w_img_str and Path(w_img_str).exists():
                logo_img_path = Path(w_img_str)
            elif w_text:
                # Generate text watermark PNG
                txt_card_path = temp_dir / f"txt_wm_{int(time.time() * 1000)}.png"
                temp_files.append(txt_card_path)
                self.generate_text_watermark_image(
                    text=w_text,
                    output_path=txt_card_path,
                    font_size=36,
                    opacity=w_opacity
                )
                logo_img_path = txt_card_path

            if logo_img_path and logo_img_path.exists():
                wm_idx = current_input_index
                current_input_index += 1
                video_inputs.extend(["-i", str(logo_img_path)])

                # Position math
                if "left" in w_pos:
                    calc_x = str(w_margin)
                elif "center" in w_pos:
                    calc_x = "(W-w)/2"
                else:
                    calc_x = f"W-w-{w_margin}"

                if "bottom" in w_pos:
                    calc_y = f"H-h-{w_margin}"
                elif "center" in w_pos:
                    calc_y = "(H-h)/2"
                else:
                    calc_y = str(w_margin)

                wm_scaled = f"[wm_scaled_{wm_idx}]"
                filter_chains.append(
                    f"[{wm_idx}:v]scale={logo_target_w}:-1,format=rgba,colorchannelmixer=aa={w_opacity:.2f}{wm_scaled}"
                )
                next_v = f"[v_wm_{wm_idx}]"
                filter_chains.append(f"{last_v_stream}{wm_scaled}overlay=x={calc_x}:y={calc_y}{next_v}")
                last_v_stream = next_v

        # -------------------------------------------------------------
        # 3. Outro & Subscribe + Bell Icon CTA Card
        # -------------------------------------------------------------
        if outro_cta and outro_cta.get("enabled"):
            outro_dur = max(2.0, min(8.0, float(outro_cta.get("duration", 4.0))))
            outro_start = max(0.0, duration - outro_dur)
            ch_name = outro_cta.get("channel_name", "UpClip Creator")
            handle = outro_cta.get("handle", "@creator")
            ch_logo = outro_cta.get("logo_path")

            # Desired card width in video coordinates (~85% of screen width)
            c_width = min(920, int(video_w * 0.85))
            c_height = int(c_width * 0.28)

            card_path = temp_dir / f"outro_card_{int(time.time() * 1000)}.png"
            temp_files.append(card_path)
            self.generate_outro_cta_card(
                channel_name=ch_name,
                handle=handle,
                logo_path=ch_logo,
                output_path=card_path,
                card_width=c_width,
                card_height=c_height
            )

            card_idx = current_input_index
            current_input_index += 1
            video_inputs.extend(["-i", str(card_path)])

            # Card position centered horizontally, lower-third vertically
            pos_x = "(W-w)/2"
            pos_y = f"H-h-{int(video_h * 0.16)}"

            card_scaled = f"[card_fade_{card_idx}]"
            # Fade in over 0.5 seconds at outro_start
            fade_expr = f"fade=t=in:st={outro_start:.2f}:d=0.5:alpha=1"
            filter_chains.append(f"[{card_idx}:v]format=rgba,{fade_expr}{card_scaled}")

            next_v = f"[v_outro_{card_idx}]"
            filter_chains.append(f"{last_v_stream}{card_scaled}overlay=x={pos_x}:y={pos_y}:enable='between(t,{outro_start:.2f},{duration:.2f})'{next_v}")
            last_v_stream = next_v

        # -------------------------------------------------------------
        # 4. Sound Effects (SFX) Track Generation
        # -------------------------------------------------------------
        sfx_inputs = []
        audio_filter_chains = []
        has_sfx = False

        if sfx and sfx.get("enabled"):
            sfx_type = (sfx.get("type") or "whoosh").lower()
            sfx_vol = float(sfx.get("volume", 75)) / 100.0

            # Match SFX wav file
            sfx_filename = "whoosh.wav"
            if "pop" in sfx_type:
                sfx_filename = "pop.wav"
            elif "chime" in sfx_type or "bell" in sfx_type:
                sfx_filename = "chime.wav"
            elif "click" in sfx_type:
                sfx_filename = "click.wav"

            sfx_file = self.audio_dir / sfx_filename
            if not sfx_file.exists():
                sfx_file = Path("static/audio") / sfx_filename

            if sfx_file.exists():
                # Collect cue timestamps from captions or intervals
                cues = []
                if captions and isinstance(captions, list) and len(captions) > 0:
                    freq = sfx.get("frequency", "major").lower()
                    for idx, c in enumerate(captions):
                        c_t = float(c.get("start", 0))
                        if c_t >= duration:
                            continue
                        if freq == "all":
                            cues.append(c_t)
                        elif freq == "every_other" and idx % 2 == 0:
                            cues.append(c_t)
                        elif freq == "major" and (idx == 0 or idx == len(captions) - 1 or idx % 3 == 0):
                            cues.append(c_t)
                else:
                    # Default: at start (0.2s) and outro (duration - 3.5s)
                    cues = [0.2]
                    if duration > 5.0:
                        cues.append(max(0.5, duration - 3.5))

                if cues:
                    has_sfx = True
                    # Build delayed SFX mix using adelay and amix
                    sfx_input_indices = []
                    for c_idx, cue_time in enumerate(cues[:8]): # max 8 sound cues per reel
                        ms_delay = int(round(cue_time * 1000))
                        s_idx = current_input_index
                        current_input_index += 1
                        video_inputs.extend(["-i", str(sfx_file)])
                        delayed_lbl = f"[sfx_del_{s_idx}]"
                        filter_chains.append(f"[{s_idx}:a]adelay={ms_delay}|{ms_delay},volume={sfx_vol:.2f}{delayed_lbl}")
                        sfx_input_indices.append(delayed_lbl)

                    if sfx_input_indices:
                        sfx_mix_lbl = "[sfx_submix]"
                        filter_chains.append(f"{''.join(sfx_input_indices)}amix=inputs={len(sfx_input_indices)}:dropout_transition=0:normalize=0{sfx_mix_lbl}")
                        # Mix sfx_submix with original video audio
                        if info["has_audio"]:
                            filter_chains.append(f"[0:a]{sfx_mix_lbl}amix=inputs=2:dropout_transition=0:normalize=0[a_final]")
                            final_audio_stream = "[a_final]"
                        else:
                            final_audio_stream = sfx_mix_lbl

        # -------------------------------------------------------------
        # Execute FFmpeg Filter Complex
        # -------------------------------------------------------------
        if not filter_chains:
            # Nothing to composite, copy as-is
            cmd = [self.ffmpeg, "-y", "-i", str(input_video), "-c", "copy", str(output_video)]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return output_video

        full_filter_str = ";".join(filter_chains)
        cmd = [
            self.ffmpeg,
            "-y",
            *video_inputs,
            "-filter_complex", full_filter_str,
            "-map", last_v_stream,
        ]

        if has_sfx and 'final_audio_stream' in locals():
            cmd.extend(["-map", final_audio_stream, "-c:a", "aac", "-b:a", "192k"])
        elif info["has_audio"]:
            cmd.extend(["-map", "0:a?", "-c:a", "copy"])

        cmd.extend([
            "-c:v", getattr(config, "VIDEO_CODEC", "libx264"),
            "-preset", "veryfast",
            "-crf", "22",
            str(output_video)
        ])

        print(f"[VIRAL_ENHANCER] Compositing enhancements ({len(filter_chains)} filters)...")
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            print(f"[VIRAL_ENHANCER] Enhancements rendered successfully: {output_video.name}")
            return output_video
        except subprocess.CalledProcessError as err:
            print(f"[VIRAL_ENHANCER] FFmpeg compositing error: {err.stderr}")
            # Fallback: if audio copy failed, re-encode audio
            try:
                cmd_retry = list(cmd)
                if "-c:a" in cmd_retry and "copy" in cmd_retry:
                    c_idx = cmd_retry.index("copy")
                    cmd_retry[c_idx] = "aac"
                subprocess.run(cmd_retry, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                return output_video
            except Exception:
                raise RuntimeError(f"Viral enhancer compositing failed: {err.stderr[:200]}")
        finally:
            for tf in temp_files:
                try:
                    if tf.exists():
                        tf.unlink()
                except Exception:
                    pass


viral_enhancer = ViralEnhancer()
