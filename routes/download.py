"""Download route - serves generated output files."""

import io
import os
import re
import html
import json
import subprocess
import sys
import zipfile
import urllib.request
from urllib.parse import urlparse
from datetime import datetime

import config
from pathlib import Path

import threading
import time
import uuid
from flask import Blueprint, send_from_directory, send_file, jsonify, request

try:
    import yt_dlp
except Exception:  # pragma: no cover
    yt_dlp = None

download_bp = Blueprint("download", __name__, url_prefix="/download")


def safe_send(directory, filename, as_attachment=True):
    """Send a file from a directory, guarding against path traversal and encoding differences."""
    import urllib.parse
    import unicodedata

    filename = Path(filename).name
    dir_path = Path(directory)
    if not dir_path.exists():
        return jsonify({"success": False, "error": "Directory not found"}), 404

    # 1. Direct match
    file_path = dir_path / filename
    if file_path.exists() and file_path.is_file():
        return send_from_directory(str(directory), filename, as_attachment=as_attachment)

    # 2. URL-unquoted match
    unquoted = urllib.parse.unquote(filename)
    unquoted_path = dir_path / unquoted
    if unquoted_path.exists() and unquoted_path.is_file():
        return send_from_directory(str(directory), unquoted, as_attachment=as_attachment)

    # 3. Unicode NFC vs NFD and cp1252 fallback match
    target_norm = unicodedata.normalize("NFC", unquoted)
    for f in dir_path.iterdir():
        if not f.is_file():
            continue
        f_norm = unicodedata.normalize("NFC", f.name)
        if f_norm == target_norm:
            return send_from_directory(str(directory), f.name, as_attachment=as_attachment)
        for enc in ("cp1252", "latin-1"):
            try:
                if unicodedata.normalize("NFC", f.name.encode(enc).decode("utf-8")) == target_norm:
                    return send_from_directory(str(directory), f.name, as_attachment=as_attachment)
            except Exception:
                pass

    return jsonify({"success": False, "error": "File not found"}), 404


@download_bp.route("/input/<path:filename>")
def input_file(filename):
    return safe_send(config.INPUT_DIR, filename)


@download_bp.route("/thumbnail/<path:filename>")
def thumbnail(filename):
    """Serve generated thumbnail images safely with Unicode, cp1252, and on-demand fallback support."""
    import unicodedata
    import urllib.parse
    from flask import current_app

    # Guard against directory traversal
    filename = Path(filename).name
    config.THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

    file_path = config.THUMBNAIL_DIR / filename

    # 1. Direct match on disk
    if file_path.exists() and file_path.is_file():
        return send_from_directory(str(config.THUMBNAIL_DIR), filename)

    # 2. URL-unquoted match
    unquoted = urllib.parse.unquote(filename)
    unquoted_path = config.THUMBNAIL_DIR / unquoted
    if unquoted_path.exists() and unquoted_path.is_file():
        return send_from_directory(str(config.THUMBNAIL_DIR), unquoted)

    # 3. Unicode normalized match (NFC vs NFD)
    target_norm = unicodedata.normalize("NFC", unquoted)
    for f in config.THUMBNAIL_DIR.iterdir():
        if not f.is_file():
            continue
        f_norm = unicodedata.normalize("NFC", f.name)
        if f_norm == target_norm:
            return send_from_directory(str(config.THUMBNAIL_DIR), f.name)
        # Check cp1252 / latin-1 decoding match (disk file was saved with mojibake)
        for enc in ("cp1252", "latin-1"):
            try:
                if unicodedata.normalize("NFC", f.name.encode(enc).decode("utf-8")) == target_norm:
                    return send_from_directory(str(config.THUMBNAIL_DIR), f.name)
            except Exception:
                pass

    # 3b. Check if target requested is mojibake of a clean disk file
    for enc in ("cp1252", "latin-1"):
        try:
            cand = target_norm.encode("utf-8").decode(enc)
            cand_path = config.THUMBNAIL_DIR / cand
            if cand_path.exists() and cand_path.is_file():
                return send_from_directory(str(config.THUMBNAIL_DIR), cand)
        except Exception:
            pass

    # 4. On-demand generation from source video if thumbnail was missing
    if filename.endswith("_thumb.jpg") or unquoted.endswith("_thumb.jpg"):
        stem = unquoted[:-10] if unquoted.endswith("_thumb.jpg") else filename[:-10]
        stem_norm = unicodedata.normalize("NFC", stem)
        for search_dir in (config.INPUT_DIR, config.FINAL_DIR, config.CLIPS_DIR):
            if not search_dir.exists():
                continue
            for candidate in search_dir.iterdir():
                if not candidate.is_file() or candidate.suffix.lower() not in {".mp4", ".mov", ".mkv", ".webm", ".avi"}:
                    continue
                cand_stem = unicodedata.normalize("NFC", candidate.stem)
                matched = (cand_stem == stem_norm)
                if not matched:
                    for enc in ("cp1252", "latin-1"):
                        try:
                            if unicodedata.normalize("NFC", cand_stem.encode(enc).decode("utf-8")) == stem_norm:
                                matched = True
                                break
                            if unicodedata.normalize("NFC", stem_norm.encode(enc).decode("utf-8")) == cand_stem:
                                matched = True
                                break
                        except Exception:
                            pass
                if matched:
                    from utils.ffmpeg_utils import generate_thumbnail
                    if generate_thumbnail(candidate, file_path):
                        return send_from_directory(str(config.THUMBNAIL_DIR), filename)
                    break

    current_app.logger.warning("Thumbnail not found: %s", filename)
    return jsonify({"success": False, "error": "Thumbnail not found"}), 404


@download_bp.route("/final/<filename>")
def final_video(filename):
    return safe_send(config.FINAL_DIR, filename)


@download_bp.route("/subtitle/<filename>")
@download_bp.route("/subtitles/<filename>")
def subtitle(filename):
    return safe_send(config.SUBTITLE_DIR, filename)


@download_bp.route("/transcript/<filename>")
def transcript(filename):
    return safe_send(config.TRANSCRIPT_DIR, filename)


@download_bp.route("/clip/<filename>")
def clip(filename):
    return safe_send(config.CLIPS_DIR, filename)


@download_bp.route("/clip/captions/<filename>")
def clip_caption(filename):
    """Serve per-clip animated caption videos."""
    cap_dir = config.CLIPS_DIR / "captions"
    cap_dir.mkdir(parents=True, exist_ok=True)
    return safe_send(cap_dir, filename)


@download_bp.route("/clip/stream/<filename>")
def clip_stream(filename):
    """Stream a clip for in-browser preview (supports range requests)."""
    filename = Path(filename).name
    file_path = config.CLIPS_DIR / filename
    if not file_path.exists():
        return jsonify({"success": False, "error": "File not found"}), 404
    return send_from_directory(str(config.CLIPS_DIR), filename, as_attachment=False)


@download_bp.route("/frame/<filename>")
def frame(filename):
    return safe_send(config.FRAMES_DIR, filename)


@download_bp.route("/all")
def download_all():
    """
    Download all generated clips as a single ZIP archive.
    """
    clips = sorted(
        [p for p in config.CLIPS_DIR.glob("*.mp4") if p.is_file()],
        key=lambda p: p.name,
    )

    if not clips:
        return jsonify({"success": False, "error": "No clips available"}), 404

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for clip in clips:
            zf.write(clip, arcname=clip.name)

    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="clips.zip",
    )


@download_bp.route("/export/<filename>")
def export(filename):
    """
    Re-encode a clip / final video at the requested quality preset.
    ?quality=360p|720p|1080p|original
    """
    filename = Path(filename).name
    quality_key = request.args.get("quality", config.DEFAULT_QUALITY)

    preset = config.QUALITY_PRESETS.get(
        quality_key,
        config.QUALITY_PRESETS[config.DEFAULT_QUALITY]
    )
    label, max_w, max_h, bitrate = preset

    # Locate the source file (clips dir first, then final dir)
    source = config.CLIPS_DIR / filename
    base_dir = config.CLIPS_DIR
    if not source.exists():
        source = config.FINAL_DIR / filename
        base_dir = config.FINAL_DIR

    if not source.exists():
        return jsonify({"success": False, "error": "File not found"}), 404

    # If original quality, just send the file directly.
    if max_w is None or max_h is None:
        return safe_send(base_dir, filename)

    output_buffer = io.BytesIO()
    output_path = config.OUTPUT_DIR / f"_export_{filename}"

    command = [
        config.FFMPEG_PATH,
        "-y",
        "-i", str(source),
        "-vf", f"scale={max_w}:{max_h}:force_original_aspect_ratio=decrease",
        "-c:v", config.VIDEO_CODEC,
        "-preset", "veryfast",
        "-crf", "23",
        "-c:a", config.AUDIO_CODEC,
        str(output_path),
    ]

    # Add bitrate cap if provided
    if bitrate:
        command.insert(-1, "-b:v")
        command.insert(-1, bitrate)

    try:
        subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        if not output_path.exists():
            return jsonify({"success": False, "error": "Export failed"}), 500

        # Stream the generated file back and clean it up.
        result = send_file(
            str(output_path),
            mimetype="video/mp4",
            as_attachment=True,
            download_name=f"{Path(filename).stem}_{label}.mp4",
        )
        try:
            output_path.unlink()
        except Exception:
            pass
        return result
    except subprocess.CalledProcessError:
        try:
            output_path.unlink()
        except Exception:
            pass
        return jsonify({"success": False, "error": "Export failed"}), 500


def _is_valid_youtube_url(value):
    if not value or not isinstance(value, str):
        return False
    cleaned = value.strip()
    if not cleaned:
        return False
    try:
        parsed = urlparse(cleaned)
        host = (parsed.netloc or "").lower()
        path = (parsed.path or "").lower()
        return (
            "youtube.com" in host or "youtu.be" in host or "youtube-nocookie.com" in host
        ) and ("watch" in path or "shorts" in path or "embed" in path or "playlist" in path or path != "")
    except Exception:
        return False


def _find_downloaded_file(directory: Path, preferred_name: str | None = None) -> Path | None:
    """Find the newest downloaded file, even when yt-dlp sanitizes the title."""
    if not directory.exists():
        return None

    files = [
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in {".mp4", ".webm", ".mkv", ".avi", ".mov", ".m4a", ".mp3", ".wav", ".flv"}
    ]
    if not files:
        return None

    if preferred_name:
        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", preferred_name).strip("._") or "youtube_video"
        match = next((p for p in files if p.name.startswith(f"{safe_name}.") or p.stem == safe_name), None)
        if match:
            return match

    return max(files, key=lambda p: p.stat().st_mtime)


def _format_size(size_bytes):
    """Format file size in human-readable form."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


_active_downloads = {}
_downloads_lock = threading.Lock()


def _format_duration(seconds):
    """Format duration in H:MM:SS or M:SS."""
    if not seconds:
        return "0:00"
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def _format_views(count):
    """Format view count with K/M abbreviation."""
    if not count:
        return "0 views"
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M views"
    if count >= 1_000:
        return f"{count / 1_000:.1f}K views"
    return f"{count:,} views"


LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "pt": "Portuguese",
    "ru": "Russian",
    "zh": "Chinese",
    "zh-Hans": "Chinese (Simplified)",
    "zh-Hant": "Chinese (Traditional)",
    "ar": "Arabic",
    "bn": "Bengali",
    "pa": "Punjabi",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "ur": "Urdu",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "id": "Indonesian",
}


def _get_lang_label(code: str) -> str:
    """Return human readable label for a language code."""
    if not code:
        return "Unknown"
    base = code.split("-")[0].lower()
    name = LANGUAGE_NAMES.get(code) or LANGUAGE_NAMES.get(base) or code.upper()
    if "-" in code and code not in LANGUAGE_NAMES:
        return f"{name} ({code})"
    return name


def _json3_to_srt(json_data):
    """Convert YouTube JSON3 caption events into standard SRT subtitles."""
    events = json_data.get("events", []) if isinstance(json_data, dict) else []
    srt_lines = []
    idx = 1
    for ev in events:
        segs = ev.get("segs", [])
        text = "".join(s.get("utf8", "") for s in segs).strip()
        if not text:
            continue
        text = html.unescape(text)
        start_ms = ev.get("tStartMs", 0)
        dur_ms = ev.get("dDurationMs", 2000)
        end_ms = start_ms + dur_ms

        def ms_to_time(ms):
            s, ms = divmod(int(ms), 1000)
            m, s = divmod(s, 60)
            h, m = divmod(m, 60)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

        srt_lines.append(f"{idx}\n{ms_to_time(start_ms)} --> {ms_to_time(end_ms)}\n{text}\n")
        idx += 1
    return "\n".join(srt_lines)


def _json3_to_vtt(json_data):
    """Convert YouTube JSON3 caption events into standard WebVTT subtitles."""
    events = json_data.get("events", []) if isinstance(json_data, dict) else []
    vtt_lines = ["WEBVTT\n"]
    for ev in events:
        segs = ev.get("segs", [])
        text = "".join(s.get("utf8", "") for s in segs).strip()
        if not text:
            continue
        text = html.unescape(text)
        start_ms = ev.get("tStartMs", 0)
        dur_ms = ev.get("dDurationMs", 2000)
        end_ms = start_ms + dur_ms

        def ms_to_vtt_time(ms):
            s, ms = divmod(int(ms), 1000)
            m, s = divmod(s, 60)
            h, m = divmod(m, 60)
            return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

        vtt_lines.append(f"{ms_to_vtt_time(start_ms)} --> {ms_to_vtt_time(end_ms)}\n{text}\n")
    return "\n".join(vtt_lines)


def _vtt_to_srt(vtt_text):
    """Convert WebVTT text into standard SRT."""
    lines = vtt_text.splitlines()
    blocks = []
    current_block = []
    for line in lines:
        if line.startswith("WEBVTT") or line.startswith("NOTE"):
            continue
        if line.strip() == "":
            if current_block:
                blocks.append(current_block)
                current_block = []
        else:
            current_block.append(line)
    if current_block:
        blocks.append(current_block)

    srt_entries = []
    idx = 1
    for block in blocks:
        ts_idx = -1
        for i, l in enumerate(block):
            if "-->" in l:
                ts_idx = i
                break
        if ts_idx == -1:
            continue
        ts_line = block[ts_idx]
        m = re.search(r"(\d{1,2}:)?(\d{2}:\d{2}[\.,]\d{3})\s*-->\s*(\d{1,2}:)?(\d{2}:\d{2}[\.,]\d{3})", ts_line)
        if not m:
            continue
        def fix_ts(h, rest):
            rest = rest.replace(".", ",")
            if not h:
                return "00:" + rest
            h = h.rstrip(":")
            return f"{int(h):02d}:{rest}"

        start_ts = fix_ts(m.group(1), m.group(2))
        end_ts = fix_ts(m.group(3), m.group(4))
        content = "\n".join(block[ts_idx + 1:])
        content = re.sub(r"<[^>]+>", "", content).strip()
        if content:
            srt_entries.append(f"{idx}\n{start_ts} --> {end_ts}\n{content}\n")
            idx += 1
    return "\n".join(srt_entries)


def _xml_to_srt(xml_text: str) -> str:
    """Convert YouTube XML/srv1/srv2/srv3/ttml timedtext into standard SRT."""
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(xml_text)
        srt_lines = []
        idx = 1
        for node in root.findall(".//text"):
            start_s = float(node.attrib.get("start", 0))
            dur_s = float(node.attrib.get("dur", 2))
            end_s = start_s + dur_s
            text = html.unescape("".join(node.itertext())).strip()
            if not text:
                continue

            def sec_to_time(s):
                sec, ms = divmod(s, 1.0)
                sec = int(sec)
                ms = int(ms * 1000)
                m, sec = divmod(sec, 60)
                h, m = divmod(m, 60)
                return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"

            srt_lines.append(f"{idx}\n{sec_to_time(start_s)} --> {sec_to_time(end_s)}\n{text}\n")
            idx += 1
        return "\n".join(srt_lines)
    except Exception:
        return ""


def _fetch_youtube_captions_direct(info: dict, target_lang: str = "en", output_format: str = "srt", output_path=None):
    """
    Directly and reliably download subtitles from YouTube metadata with anti-429 resilience.
    Uses browser impersonation headers and automatic native original track fallback.
    """
    manual_subs = info.get("subtitles") or {}
    auto_subs = info.get("automatic_captions") or {}

    if not manual_subs and not auto_subs:
        return None

    # Step 1: Find candidate track
    selected_track = None
    selected_lang = None

    # A) Try exact manual track
    if target_lang in manual_subs:
        selected_track = manual_subs[target_lang]
        selected_lang = target_lang
    else:
        # B) Try base manual track (e.g. 'en-US' -> 'en')
        for l, fmts in manual_subs.items():
            if l.split("-")[0] == target_lang.split("-")[0]:
                selected_track = fmts
                selected_lang = l
                break

    # C) If not in manual, check auto-captions
    if not selected_track:
        if target_lang in auto_subs:
            selected_track = auto_subs[target_lang]
            selected_lang = target_lang
        else:
            for l, fmts in auto_subs.items():
                if l.split("-")[0] == target_lang.split("-")[0]:
                    selected_track = fmts
                    selected_lang = l
                    break

    # Find the original native track for fallback
    orig_track = None
    orig_lang = None
    for l, fmts in auto_subs.items():
        if fmts and "tlang=" not in fmts[0].get("url", ""):
            orig_track = fmts
            orig_lang = l
            break
    if not orig_track and manual_subs:
        orig_lang, orig_track = list(manual_subs.items())[0]

    # Helper to download and parse a track
    def try_download_track(fmts):
        if not fmts:
            return None
        # Prefer json3 or vtt
        best_fmt = next((f for f in fmts if f.get("ext") == "json3"), None)
        is_json = True
        if not best_fmt:
            best_fmt = next((f for f in fmts if f.get("ext") == "vtt"), fmts[0])
            is_json = best_fmt.get("ext") == "json3" or "fmt=json3" in best_fmt.get("url", "")

        url = best_fmt.get("url")
        if not url:
            return None

        # Add headers to avoid 429
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": "https://www.youtube.com/",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
            "Accept": "*/*"
        }
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                raw_bytes = resp.read()
                raw_text = raw_bytes.decode("utf-8", errors="ignore")
                if is_json or raw_text.strip().startswith("{"):
                    data = json.loads(raw_text)
                    if output_format == "vtt":
                        return _json3_to_vtt(data)
                    return _json3_to_srt(data)
                elif raw_text.startswith("WEBVTT"):
                    if output_format == "srt":
                        return _vtt_to_srt(raw_text)
                    return raw_text
                elif "<transcript" in raw_text or "<text" in raw_text:
                    parsed_srt = _xml_to_srt(raw_text)
                    if output_format == "vtt":
                        return _vtt_to_srt(parsed_srt) if parsed_srt else raw_text
                    return parsed_srt
                else:
                    if output_format == "vtt":
                        return _vtt_to_srt(raw_text)
                    return raw_text
        except Exception as e:
            print(f"[SUBTITLE_DIRECT] Download attempt failed for URL: {e}")
            return None

    # Attempt 1: Try the selected track
    caption_content = None
    if selected_track:
        caption_content = try_download_track(selected_track)

    # Attempt 2: If attempt 1 failed (e.g. 429 on auto-translate), fallback to native original track!
    if not caption_content and orig_track and orig_track != selected_track:
        print(f"[SUBTITLE_DIRECT] Fallback to original native track ({orig_lang})")
        caption_content = try_download_track(orig_track)

    # Attempt 3: If still nothing, try first available track
    if not caption_content:
        all_tracks = list(manual_subs.values()) + list(auto_subs.values())
        for tr in all_tracks[:3]:
            caption_content = try_download_track(tr)
            if caption_content:
                break

    if not caption_content:
        return None

    # Write to target_path if provided
    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(caption_content, encoding="utf-8")
        return out_p

    return caption_content


def _extract_available_subtitles(info: dict) -> list[dict]:
    """Extract list of available subtitle tracks (manual and auto) with metadata."""
    subs_map = {}

    # 1. Manual subtitles (highest priority)
    for lang, fmts in (info.get("subtitles") or {}).items():
        if not lang or lang.startswith("live_"):
            continue
        label = _get_lang_label(lang)
        subs_map[lang] = {
            "lang": lang,
            "label": label,
            "is_auto": False,
            "is_original": True,
            "display": f"{label} (Manual)",
        }

    # 2. Automatic captions
    for lang, fmts in (info.get("automatic_captions") or {}).items():
        if not lang or lang.startswith("live_"):
            continue
        if lang not in subs_map:
            label = _get_lang_label(lang)
            # Detect if this is the native audio track (no tlang in URL)
            is_orig = False
            if fmts and isinstance(fmts, list) and len(fmts) > 0:
                first_url = fmts[0].get("url", "")
                if "tlang=" not in first_url:
                    is_orig = True

            if is_orig:
                display_str = f"{label} (Original Audio)"
            else:
                display_str = f"{label} (Auto-generated)"

            subs_map[lang] = {
                "lang": lang,
                "label": label,
                "is_auto": True,
                "is_original": is_orig,
                "display": display_str,
            }

    def sort_key(item):
        orig_prio = 0 if item.get("is_original") else 1
        manual_prio = 0 if not item.get("is_auto") else 1
        code = item["lang"].lower()
        lang_prio = 0 if code.startswith("en") else (1 if code.startswith("hi") else 2)
        return (orig_prio, manual_prio, lang_prio, item["label"])

    sub_list = sorted(subs_map.values(), key=sort_key)
    return sub_list


@download_bp.route("/analyze", methods=["POST"])
def analyze_youtube_url():
    """Analyze a YouTube URL to retrieve metadata, available formats, subtitles, and playlist info."""
    payload = request.get_json(silent=True) or {}
    url = payload.get("url", "").strip()

    if not _is_valid_youtube_url(url):
        return jsonify({"success": False, "error": "Please enter a valid YouTube URL."}), 400

    if yt_dlp is None:
        return jsonify({"success": False, "error": "YouTube downloader engine is not available."}), 500

    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": "in_playlist",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            return jsonify({"success": False, "error": "Could not extract video metadata from URL."}), 400

        is_playlist = "entries" in info
        title = info.get("title") or "YouTube Video"
        channel = info.get("uploader") or info.get("channel") or "YouTube Creator"
        duration = info.get("duration") or 0
        duration_str = _format_duration(duration)
        view_count = info.get("view_count") or 0
        view_count_str = _format_views(view_count)
        # Detect highest-resolution thumbnail and aspect ratio
        raw_thumbs = info.get("thumbnails") or []
        thumbnail = info.get("thumbnail") or ""
        thumb_width = None
        thumb_height = None

        if raw_thumbs:
            # Sort by area (width * height), preference, then width
            def _thumb_score(t):
                w = t.get("width") or 0
                h = t.get("height") or 0
                p = t.get("preference") or 0
                return (w * h, p, w)

            sorted_thumbs = sorted(raw_thumbs, key=_thumb_score, reverse=True)
            for t in sorted_thumbs:
                t_url = t.get("url")
                if t_url and ("http://" in t_url or "https://" in t_url):
                    thumbnail = t_url
                    thumb_width = t.get("width")
                    thumb_height = t.get("height")
                    break

        video_w = info.get("width")
        video_h = info.get("height")
        is_vertical = False
        if thumb_width and thumb_height:
            is_vertical = (thumb_height > thumb_width)
        elif video_w and video_h:
            is_vertical = (video_h > video_w)

        thumb_res_str = ""
        if thumb_width and thumb_height:
            thumb_res_str = f"{thumb_width} × {thumb_height}"
        elif video_w and video_h:
            thumb_res_str = f"{video_w} × {video_h}"

        # Extract available captions / subtitles
        subtitles = _extract_available_subtitles(info)
        has_subtitles = len(subtitles) > 0
        default_sub_lang = "en"
        if subtitles:
            # Pick first original/manual track as default to avoid 429 translation errors
            orig_match = next((s["lang"] for s in subtitles if s.get("is_original")), None)
            default_sub_lang = orig_match or subtitles[0]["lang"]

        # Calculate estimated sizes based on duration
        dur_mins = max(1, duration // 60)
        formats = [
            {"id": "1080p", "label": "1080p Full HD", "ext": "MP4", "size": f"~{dur_mins * 22} MB", "type": "video", "recommended": True},
            {"id": "720p", "label": "720p HD", "ext": "MP4", "size": f"~{dur_mins * 12} MB", "type": "video"},
            {"id": "480p", "label": "480p SD", "ext": "MP4", "size": f"~{dur_mins * 7} MB", "type": "video"},
            {"id": "360p", "label": "360p", "ext": "MP4", "size": f"~{dur_mins * 4} MB", "type": "video"},
            {"id": "mp3", "label": "MP3 Audio (192k)", "ext": "MP3", "size": f"~{max(1, dur_mins * 1.5):.1f} MB", "type": "audio"},
            {"id": "m4a", "label": "M4A AAC (256k)", "ext": "M4A", "size": f"~{max(1, dur_mins * 1.8):.1f} MB", "type": "audio"},
            {"id": "wav", "label": "WAV Lossless", "ext": "WAV", "size": f"~{dur_mins * 10} MB", "type": "audio"},
        ]

        playlist_entries = []
        if is_playlist:
            for i, entry in enumerate(info.get("entries", [])[:50], 1):
                if entry:
                    playlist_entries.append({
                        "index": i,
                        "id": entry.get("id"),
                        "title": entry.get("title", f"Video {i}"),
                        "duration": entry.get("duration") or 0,
                        "duration_str": _format_duration(entry.get("duration") or 0),
                        "url": entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}",
                    })

        if config.FFMPEG_PATH and Path(config.FFMPEG_PATH).exists():
            ydl_opts["ffmpeg_location"] = str(config.FFMPEG_PATH)

        return jsonify({
            "success": True,
            "is_playlist": is_playlist,
            "title": title,
            "channel": channel,
            "duration": duration,
            "duration_str": duration_str,
            "view_count": view_count,
            "view_count_str": view_count_str,
            "thumbnail": thumbnail,
            "thumbnail_width": thumb_width,
            "thumbnail_height": thumb_height,
            "thumbnail_resolution": thumb_res_str,
            "is_vertical": is_vertical,
            "formats": formats,
            "playlist_entries": playlist_entries,
            "video_count": len(playlist_entries) if is_playlist else 1,
            "has_subtitles": has_subtitles,
            "subtitles": subtitles,
            "default_subtitle_lang": default_sub_lang,
        })
    except Exception as exc:
        err_msg = str(exc)
        if "bot" in err_msg.lower() or "confirm you're not a bot" in err_msg.lower():
            err_msg = "YouTube bot detection triggered. Try again later or check network connection."
        elif "private video" in err_msg.lower():
            err_msg = "This video is private."
        elif "unavailable" in err_msg.lower():
            err_msg = "Video is unavailable or removed."
        return jsonify({"success": False, "error": f"Failed to analyze URL: {err_msg}"}), 400


def _execute_download(task_id, ydl_opts, url, fmt, quality, download_subtitles=False, subtitle_format="srt", subtitle_lang="en"):
    """Background download worker with progress updates and subtitle capture."""
    with _downloads_lock:
        if task_id not in _active_downloads:
            return
        _active_downloads[task_id]["status"] = "downloading"

    def progress_hook(d):
        with _downloads_lock:
            if task_id not in _active_downloads:
                return
            t = _active_downloads[task_id]
            if t.get("cancelled"):
                raise Exception("Download cancelled by user")
            status = d.get("status")
            if status == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes") or 0
                speed = d.get("speed") or 0
                eta = d.get("eta") or 0
                if total > 0:
                    t["percent"] = round((downloaded / total) * 100, 1)
                    t["downloaded_str"] = _format_size(downloaded)
                    t["total_str"] = _format_size(total)
                else:
                    t["downloaded_str"] = _format_size(downloaded)
                if speed > 0:
                    t["speed_str"] = f"{_format_size(speed)}/s"
                if eta:
                    t["eta_str"] = f"{int(eta // 60):02d}:{int(eta % 60):02d}"

    ydl_opts["progress_hooks"] = [progress_hook]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        title = (info or {}).get("title", "youtube_video")
        match = _find_downloaded_file(config.INPUT_DIR, title)
        with _downloads_lock:
            t = _active_downloads[task_id]
            t["status"] = "completed"
            t["percent"] = 100.0
            if match:
                t["filename"] = match.name
                t["path"] = f"/download/input/{match.name}"
                t["size_str"] = _format_size(match.stat().st_size)

            # Check for subtitle files if subtitles were requested
            if download_subtitles or fmt == "subtitles":
                sub_stem = match.stem if match else (re.sub(r"[^A-Za-z0-9._-]+", "_", title).strip("._") or "youtube_media")
                clean_sub_name = f"{sub_stem}.{subtitle_format}"
                clean_input_sub = config.INPUT_DIR / clean_sub_name
                clean_output_sub = config.SUBTITLE_DIR / clean_sub_name

                # Use resilient direct subtitle fetcher
                if info and (not clean_input_sub.exists() or clean_input_sub.stat().st_size == 0):
                    _fetch_youtube_captions_direct(info, subtitle_lang, subtitle_format, clean_input_sub)

                if clean_input_sub.exists() and clean_input_sub.stat().st_size > 0:
                    try:
                        import shutil
                        config.SUBTITLE_DIR.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(clean_input_sub, clean_output_sub)
                    except Exception:
                        pass

                    t["subtitle_file"] = clean_input_sub.name
                    t["subtitle_path"] = f"/download/input/{clean_input_sub.name}"
                    t["has_subtitles"] = True
                    if fmt == "subtitles":
                        t["filename"] = clean_input_sub.name
                        t["path"] = f"/download/input/{clean_input_sub.name}"
                        t["size_str"] = _format_size(clean_input_sub.stat().st_size)
    except Exception as exc:
        err_msg = str(exc)
        if "bot" in err_msg.lower() or "confirm you're not a bot" in err_msg.lower():
            err_msg = "YouTube bot detection triggered. Try again later or use another URL."
        elif "private video" in err_msg.lower():
            err_msg = "This video is private."
        elif "unavailable" in err_msg.lower():
            err_msg = "Video is unavailable or removed."
        elif "cancelled by user" in err_msg.lower():
            err_msg = "Download cancelled by user."
        with _downloads_lock:
            t = _active_downloads[task_id]
            t["status"] = "cancelled" if "cancelled by user" in str(exc).lower() else "error"
            t["error"] = err_msg


@download_bp.route("/youtube", methods=["POST"])
def download_youtube_video():
    """Download a YouTube video, audio, or captions to the input folder for later processing."""
    payload = request.get_json(silent=True) or {}
    url = payload.get("url", "").strip()
    fmt = payload.get("format", "video")  # "video", "audio", or "subtitles"
    quality = payload.get("quality", "best")  # "best", "1080p", "720p", "480p", "360p"
    audio_format = payload.get("audio_format", "mp3")  # mp3, m4a, wav, flac
    limit = payload.get("limit")  # max videos for batch downloads
    is_async = payload.get("async", True)
    title_hint = payload.get("title", "YouTube Video")
    download_subtitles = payload.get("download_subtitles", False)
    subtitle_lang = payload.get("subtitle_lang", "en")
    subtitle_format = payload.get("subtitle_format", "srt")

    if not _is_valid_youtube_url(url):
        return jsonify({"success": False, "error": "Please provide a valid YouTube URL."}), 400

    if yt_dlp is None:
        return jsonify({"success": False, "error": "YouTube downloader is not installed."}), 500

    config.INPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_template = str(config.INPUT_DIR / "%(title)s.%(ext)s")

    # Build format selection based on user choice with DASH stream support
    if fmt == "audio":
        codec_map = {"mp3": "mp3", "m4a": "m4a", "wav": "wav", "flac": "flac"}
        codec = codec_map.get(audio_format, "mp3")
        quality_map = {"mp3": "192", "m4a": "256", "wav": "320", "flac": "0"}
        format_selector = "bestaudio/best"
        postprocessors = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": codec,
            "preferredquality": quality_map.get(codec, "192"),
        }]
        merge_format = None
    elif fmt == "subtitles":
        format_selector = None
        postprocessors = []
        merge_format = None
    else:
        quality_map = {
            "best": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
            "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]/best",
        }
        format_selector = quality_map.get(quality, quality_map["best"])
        postprocessors = []
        merge_format = "mp4"

    ydl_opts = {
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": False,
        "postprocessors": postprocessors,
    }
    if format_selector:
        ydl_opts["format"] = format_selector
    if merge_format:
        ydl_opts["merge_output_format"] = merge_format

    # Subtitles are downloaded cleanly and resiliently by _fetch_youtube_captions_direct in _execute_download
    ydl_opts["writesubtitles"] = False
    ydl_opts["writeautomaticsub"] = False

    if config.FFMPEG_PATH and Path(config.FFMPEG_PATH).exists():
        ydl_opts["ffmpeg_location"] = str(config.FFMPEG_PATH)

    if limit:
        ydl_opts["noplaylist"] = False
        ydl_opts["playlist_items"] = f"1-{limit}"

    task_id = str(uuid.uuid4())[:8]
    task_info = {
        "id": task_id,
        "url": url,
        "title": title_hint,
        "format": fmt,
        "quality": quality,
        "download_subtitles": download_subtitles,
        "subtitle_lang": subtitle_lang,
        "status": "queued",
        "percent": 0.0,
        "speed_str": "0 KB/s",
        "eta_str": "--:--",
        "downloaded_str": "0 B",
        "total_str": "--",
        "filename": None,
        "path": None,
        "subtitle_file": None,
        "error": None,
        "created_at": time.time(),
    }

    with _downloads_lock:
        _active_downloads[task_id] = task_info

    if is_async:
        # Run in background thread
        thread = threading.Thread(
            target=_execute_download,
            args=(task_id, ydl_opts, url, fmt, quality, download_subtitles, subtitle_format, subtitle_lang),
            daemon=True,
        )
        thread.start()
        return jsonify({
            "success": True,
            "task_id": task_id,
            "message": "Download task queued.",
            "title": title_hint,
            "download_subtitles": download_subtitles,
        })

    # Synchronous execution fallback for legacy callers
    _execute_download(task_id, ydl_opts, url, fmt, quality, download_subtitles, subtitle_format, subtitle_lang)
    final_task = _active_downloads.get(task_id, {})
    if final_task.get("status") == "completed":
        return jsonify({
            "success": True,
            "message": "Download completed successfully.",
            "filename": final_task.get("filename"),
            "path": final_task.get("path"),
            "subtitle_file": final_task.get("subtitle_file"),
            "size": final_task.get("size_str", "Unknown"),
            "format": fmt,
            "quality": quality,
        })
    else:
        return jsonify({"success": False, "error": final_task.get("error", "Download failed.")}), 500


@download_bp.route("/subtitles-only", methods=["POST"])
def download_subtitles_only():
    """Download only the caption/subtitle file (.srt/.vtt) for a YouTube video within seconds with anti-429 protection."""
    payload = request.get_json(silent=True) or {}
    url = payload.get("url", "").strip()
    subtitle_lang = payload.get("subtitle_lang", "en")
    subtitle_format = (payload.get("subtitle_format") or "srt").lower()
    title_hint = payload.get("title", "youtube_video")

    if not _is_valid_youtube_url(url):
        return jsonify({"success": False, "error": "Please provide a valid YouTube URL."}), 400

    if yt_dlp is None:
        return jsonify({"success": False, "error": "YouTube downloader is not installed."}), 500

    config.INPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.SUBTITLE_DIR.mkdir(parents=True, exist_ok=True)

    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }
        if config.FFMPEG_PATH and Path(config.FFMPEG_PATH).exists():
            ydl_opts["ffmpeg_location"] = str(config.FFMPEG_PATH)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            return jsonify({"success": False, "error": "Could not extract video metadata from URL."}), 400

        video_title = info.get("title") or title_hint or "youtube_captions"
        safe_title = re.sub(r"[^A-Za-z0-9._-]+", "_", video_title).strip("._") or "youtube_captions"

        clean_sub_name = f"{safe_title}.{subtitle_format}"
        clean_input_path = config.INPUT_DIR / clean_sub_name
        clean_output_path = config.SUBTITLE_DIR / clean_sub_name

        # Direct, anti-429 resilient fetcher with browser headers and original-track fallback
        result = _fetch_youtube_captions_direct(
            info=info,
            target_lang=subtitle_lang,
            output_format=subtitle_format,
            output_path=clean_input_path,
        )

        if not result or not clean_input_path.exists() or clean_input_path.stat().st_size == 0:
            return jsonify({"success": False, "error": "No subtitles or captions could be retrieved for this video."}), 404

        import shutil
        shutil.copy2(clean_input_path, clean_output_path)

        return jsonify({
            "success": True,
            "filename": clean_input_path.name,
            "download_url": f"/download/input/{clean_input_path.name}",
            "size": _format_size(clean_input_path.stat().st_size),
            "message": f"Caption file ({clean_input_path.name}) downloaded successfully.",
        })
    except Exception as exc:
        err_msg = str(exc)
        if "bot" in err_msg.lower() or "confirm you're not a bot" in err_msg.lower():
            err_msg = "YouTube bot detection triggered. Try again later or use another URL."
        elif "private video" in err_msg.lower():
            err_msg = "This video is private."
        elif "unavailable" in err_msg.lower():
            err_msg = "Video is unavailable or removed."
        return jsonify({"success": False, "error": f"Failed to download captions: {err_msg}"}), 500


@download_bp.route("/progress/<string:task_id>", methods=["GET"])
def get_download_progress(task_id):
    """Poll progress for an active download task."""
    with _downloads_lock:
        task = _active_downloads.get(task_id)
        if not task:
            return jsonify({"success": False, "error": "Task not found"}), 404
        return jsonify({"success": True, "task": task})


@download_bp.route("/queue", methods=["GET"])
def get_download_queue():
    """Get all active and recent download tasks."""
    with _downloads_lock:
        # Return recent tasks sorted by creation time
        tasks = sorted(
            _active_downloads.values(),
            key=lambda x: x.get("created_at", 0),
            reverse=True,
        )
        return jsonify({"success": True, "queue": tasks[:20]})


@download_bp.route("/cancel/<string:task_id>", methods=["POST"])
def cancel_download(task_id):
    """Cancel an active download task."""
    with _downloads_lock:
        if task_id in _active_downloads:
            _active_downloads[task_id]["cancelled"] = True
            _active_downloads[task_id]["status"] = "cancelled"
            return jsonify({"success": True, "message": "Download cancelled."})
        return jsonify({"success": False, "error": "Task not found."}), 404


@download_bp.route("/list")
def list_files():
    """List all available generated outputs."""
    data = {
        "input": [p.name for p in config.INPUT_DIR.glob("*") if p.is_file()],
        "thumbnails": [p.name for p in config.THUMBNAIL_DIR.glob("*") if p.is_file()],
        "final": [p.name for p in config.FINAL_DIR.glob("*") if p.is_file()],
        "subtitles": [p.name for p in config.SUBTITLE_DIR.glob("*") if p.is_file()],
        "transcripts": [p.name for p in config.TRANSCRIPT_DIR.glob("*") if p.is_file()],
        "clips": [p.name for p in config.CLIPS_DIR.glob("*") if p.is_file()],
    }
    return jsonify({"success": True, "files": data})


@download_bp.route("/downloaded")
def list_downloaded():
    """List all downloaded YouTube videos and captions with metadata."""
    config.INPUT_DIR.mkdir(parents=True, exist_ok=True)
    video_exts = {".mp4", ".webm", ".mkv", ".avi", ".mov", ".m4a", ".mp3", ".wav", ".flv"}
    sub_exts = {".srt", ".vtt"}
    files = []

    # Map available subtitle files by stem
    sub_files_by_stem = {}
    for p in config.INPUT_DIR.iterdir():
        if p.is_file() and p.suffix.lower() in sub_exts:
            clean_stem = re.sub(r"\.[a-z]{2,3}(-[A-Za-z]+)?$", "", p.stem)
            sub_files_by_stem[p.stem] = p
            sub_files_by_stem[clean_stem] = p

    for p in sorted(config.INPUT_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        if ext in video_exts or ext in sub_exts:
            stat = p.stat()
            is_audio = ext in {".mp3", ".wav", ".m4a"}
            is_sub = ext in sub_exts

            has_caption = False
            caption_file = None
            caption_url = None

            if not is_sub:
                sub_match = sub_files_by_stem.get(p.stem)
                if not sub_match:
                    direct_srt = config.INPUT_DIR / f"{p.stem}.srt"
                    direct_vtt = config.INPUT_DIR / f"{p.stem}.vtt"
                    if direct_srt.exists():
                        sub_match = direct_srt
                    elif direct_vtt.exists():
                        sub_match = direct_vtt
                if sub_match and sub_match.exists():
                    has_caption = True
                    caption_file = sub_match.name
                    caption_url = f"/download/input/{sub_match.name}"

            files.append({
                "name": p.name,
                "size": _format_size(stat.st_size),
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                "path": f"/download/input/{p.name}",
                "stream_path": f"/download/input/stream/{p.name}" if not is_sub else None,
                "is_audio": is_audio,
                "is_subtitle": is_sub,
                "has_caption": has_caption,
                "caption_file": caption_file,
                "caption_url": caption_url,
            })
    return jsonify({"success": True, "files": files})


@download_bp.route("/input/stream/<filename>")
def input_stream(filename):
    """Stream a downloaded input file for in-browser preview."""
    filename = Path(filename).name
    file_path = config.INPUT_DIR / filename
    if not file_path.exists():
        return jsonify({"success": False, "error": "File not found"}), 404
    return send_from_directory(str(config.INPUT_DIR), filename, as_attachment=False)


@download_bp.route("/delete", methods=["POST"])
def delete_downloaded():
    """Delete a downloaded file from the input directory."""
    payload = request.get_json(silent=True) or {}
    filename = Path(payload.get("filename", "")).name
    if not filename:
        return jsonify({"success": False, "error": "No filename provided"}), 400

    file_path = config.INPUT_DIR / filename
    if not file_path.exists():
        return jsonify({"success": False, "error": "File not found"}), 404

    try:
        file_path.unlink()
        return jsonify({"success": True, "message": f"Deleted {filename}"})
    except Exception as exc:
        return jsonify({"success": False, "error": f"Delete failed: {exc}"}), 500


@download_bp.route("/delete-all", methods=["POST"])
def delete_all_downloads():
    """Delete all downloaded media in the input directory."""
    try:
        deleted = []
        for item in sorted(config.INPUT_DIR.iterdir(), key=lambda p: p.name):
            if item.is_file():
                item.unlink()
                deleted.append(item.name)
        return jsonify({"success": True, "deleted": deleted, "count": len(deleted)})
    except Exception as exc:
        return jsonify({"success": False, "error": f"Delete all failed: {exc}"}), 500


@download_bp.route("/rename", methods=["POST"])
def rename_downloaded():
    """Rename a downloaded file in the input directory."""
    payload = request.get_json(silent=True) or {}
    old_name = Path(payload.get("old_name", "")).name
    new_name = Path(payload.get("new_name", "")).name

    if not old_name or not new_name:
        return jsonify({"success": False, "error": "Both old and new names required"}), 400

    # Sanitize new name
    new_name = re.sub(r"[^A-Za-z0-9._-]+", "_", new_name).strip("._")
    if not new_name:
        return jsonify({"success": False, "error": "Invalid new name"}), 400

    # Preserve extension
    old_ext = Path(old_name).suffix
    if not Path(new_name).suffix:
        new_name += old_ext

    old_path = config.INPUT_DIR / old_name
    new_path = config.INPUT_DIR / new_name

    if not old_path.exists():
        return jsonify({"success": False, "error": "File not found"}), 404
    if new_path.exists():
        return jsonify({"success": False, "error": "A file with that name already exists"}), 400

    try:
        old_path.rename(new_path)
        return jsonify({
            "success": True,
            "message": f"Renamed to {new_name}",
            "filename": new_name,
            "path": f"/download/input/{new_name}",
        })
    except Exception as exc:
        return jsonify({"success": False, "error": f"Rename failed: {exc}"}), 500


@download_bp.route("/open-folder")
def open_folder():
    """Open the input folder in the system file explorer."""
    try:
        folder = str(config.INPUT_DIR)
        if os.name == "nt":  # Windows
            os.startfile(folder)  # type: ignore
        elif os.name == "posix":  # macOS/Linux
            if sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
        return jsonify({"success": True, "message": "Folder opened in file explorer"})
    except Exception as exc:
        return jsonify({"success": False, "error": f"Could not open folder: {exc}"}), 500
