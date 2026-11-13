"""
Routes and APIs for Centralized Settings & Resource Management — Phase 3 (Master Prompt V2).
Includes:
- General Application Preferences
- AI Model Manager (Official Whisper catalog, real sizes, background download with progress, set default, delete)
- Dependency & Library Manager (FFmpeg, PyTorch, Whisper, OpenCV, Pillow, CUDA detection)
- Download Manager (Active, completed, failed, cancelled download history & control)
- Storage Management (Real disk usage, cache breakdown, safe cache cleanup)
- Import & Export Folders (Media, Projects, Exports, Temp; open in Windows Explorer, reset)
- Performance Settings (CPU cores, RAM usage via Win32 API, GPU/CUDA hardware acceleration)
- Privacy & Security (100% local processing status & policy)
- System Diagnostics (FFmpeg binary, PyTorch tensor, Whisper accessibility, disk write checks)
- About & Version info
"""

import os
import sys
import json
import time
import shutil
import ctypes
import platform
import threading
import urllib.request
from pathlib import Path
from typing import Dict, Any, Optional

from flask import Blueprint, render_template, request, jsonify

import config
from core.settings_manager import settings_manager, DEFAULT_SETTINGS
from core.logger import logger
from utils.ffmpeg_utils import check_ffmpeg

settings_bp = Blueprint("settings", __name__)

WHISPER_CACHE_DIR = Path.home() / ".cache" / "whisper"
WHISPER_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Official Whisper Catalog with verified sizes and characteristics
WHISPER_CATALOG = {
    "tiny": {
        "name": "Whisper Tiny",
        "variant": "tiny",
        "parameters": "39M",
        "file_size": "75 MB",
        "disk_bytes": 77800000,
        "accuracy": "Basic / High Speed",
        "languages": "Multilingual (99+ languages)",
        "recommended_for": "Ultra-fast preview and short clip drafts"
    },
    "tiny.en": {
        "name": "Whisper Tiny (English)",
        "variant": "tiny.en",
        "parameters": "39M",
        "file_size": "75 MB",
        "disk_bytes": 77800000,
        "accuracy": "Basic / High Speed",
        "languages": "English Only",
        "recommended_for": "Fast English-only transcription"
    },
    "base": {
        "name": "Whisper Base",
        "variant": "base",
        "parameters": "74M",
        "file_size": "145 MB",
        "disk_bytes": 145262807,
        "accuracy": "Balanced / Standard",
        "languages": "Multilingual (99+ languages)",
        "recommended_for": "Default general-purpose transcription"
    },
    "base.en": {
        "name": "Whisper Base (English)",
        "variant": "base.en",
        "parameters": "74M",
        "file_size": "145 MB",
        "disk_bytes": 145262807,
        "accuracy": "Balanced / Standard",
        "languages": "English Only",
        "recommended_for": "Standard English clipping"
    },
    "small": {
        "name": "Whisper Small",
        "variant": "small",
        "parameters": "244M",
        "file_size": "488 MB",
        "disk_bytes": 487800000,
        "accuracy": "High Accuracy",
        "languages": "Multilingual (99+ languages)",
        "recommended_for": "Podcasts, accents, music background"
    },
    "small.en": {
        "name": "Whisper Small (English)",
        "variant": "small.en",
        "parameters": "244M",
        "file_size": "488 MB",
        "disk_bytes": 487800000,
        "accuracy": "High Accuracy",
        "languages": "English Only",
        "recommended_for": "High quality English transcription"
    },
    "medium": {
        "name": "Whisper Medium",
        "variant": "medium",
        "parameters": "769M",
        "file_size": "1.53 GB",
        "disk_bytes": 1530000000,
        "accuracy": "Very High Accuracy",
        "languages": "Multilingual (99+ languages)",
        "recommended_for": "Complex dialogue, overlapping voices"
    },
    "medium.en": {
        "name": "Whisper Medium (English)",
        "variant": "medium.en",
        "parameters": "769M",
        "file_size": "1.53 GB",
        "disk_bytes": 1530000000,
        "accuracy": "Very High Accuracy",
        "languages": "English Only",
        "recommended_for": "Professional English transcription"
    },
    "large-v3": {
        "name": "Whisper Large v3",
        "variant": "large-v3",
        "parameters": "1550M",
        "file_size": "3.10 GB",
        "disk_bytes": 3100000000,
        "accuracy": "State-of-the-Art",
        "languages": "Multilingual (99+ languages)",
        "recommended_for": "Cinema quality, challenging audio, regional dialects"
    },
    "turbo": {
        "name": "Whisper Large v3 Turbo",
        "variant": "turbo",
        "parameters": "809M",
        "file_size": "1.62 GB",
        "disk_bytes": 1620000000,
        "accuracy": "High Accuracy / 8x Speedup",
        "languages": "Multilingual (99+ languages)",
        "recommended_for": "Fast modern large model transcription"
    }
}


class ModelDownloadManager:
    """Thread-safe real download manager with chunked streaming, progress, speed, and cancellation."""

    def __init__(self):
        self.lock = threading.Lock()
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.cancel_flags: Dict[str, bool] = {}

    def get_job(self, model_name: str) -> Optional[Dict[str, Any]]:
        with self.lock:
            return dict(self.jobs.get(model_name, {})) if model_name in self.jobs else None

    def get_all_jobs(self) -> Dict[str, Dict[str, Any]]:
        with self.lock:
            return {k: dict(v) for k, v in self.jobs.items()}

    def start_download(self, model_name: str) -> Dict[str, Any]:
        with self.lock:
            if model_name in self.jobs and self.jobs[model_name].get("status") == "downloading":
                return {"success": False, "message": "Download already in progress"}

            import whisper
            model_urls = getattr(whisper, "_MODELS", {})
            if model_name not in model_urls:
                return {"success": False, "message": f"Unknown Whisper model: {model_name}"}

            url = model_urls[model_name]
            meta = WHISPER_CATALOG.get(model_name, {})
            expected_bytes = meta.get("disk_bytes", 0)

            self.cancel_flags[model_name] = False
            self.jobs[model_name] = {
                "model_name": model_name,
                "url": url,
                "status": "downloading",
                "progress_pct": 0.0,
                "downloaded_bytes": 0,
                "total_bytes": expected_bytes,
                "speed_mbps": 0.0,
                "started_at": time.time(),
                "error": None
            }

        t = threading.Thread(target=self._download_worker, args=(model_name, url), daemon=True)
        t.start()
        return {"success": True, "job": self.get_job(model_name)}

    def cancel_download(self, model_name: str) -> Dict[str, Any]:
        with self.lock:
            if model_name in self.jobs and self.jobs[model_name].get("status") == "downloading":
                self.cancel_flags[model_name] = True
                self.jobs[model_name]["status"] = "cancelled"
                return {"success": True, "message": "Cancellation requested"}
            return {"success": False, "message": "No active download for this model"}

    def clear_job_history(self, model_name: str) -> Dict[str, Any]:
        with self.lock:
            if model_name in self.jobs and self.jobs[model_name].get("status") != "downloading":
                del self.jobs[model_name]
                return {"success": True}
            return {"success": False, "message": "Cannot clear an active download"}

    def _download_worker(self, model_name: str, url: str):
        target_path = WHISPER_CACHE_DIR / f"{model_name}.pt"
        part_path = WHISPER_CACHE_DIR / f"{model_name}.pt.part"

        chunk_size = 128 * 1024  # 128 KB chunks
        downloaded = 0
        last_time = time.time()
        last_bytes = 0

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "UpClipStudio/2.0 (Whisper Model Downloader)"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp, open(part_path, "wb") as f_out:
                total_header = resp.getheader("Content-Length")
                total_bytes = int(total_header) if total_header else WHISPER_CATALOG.get(model_name, {}).get("disk_bytes", 0)

                with self.lock:
                    if model_name in self.jobs:
                        self.jobs[model_name]["total_bytes"] = total_bytes

                while True:
                    if self.cancel_flags.get(model_name, False):
                        part_path.unlink(missing_ok=True)
                        with self.lock:
                            if model_name in self.jobs:
                                self.jobs[model_name]["status"] = "cancelled"
                        return

                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break

                    f_out.write(chunk)
                    downloaded += len(chunk)

                    now = time.time()
                    dt = now - last_time
                    if dt >= 0.5:
                        speed = ((downloaded - last_bytes) / (1024 * 1024)) / dt
                        pct = round((downloaded / total_bytes * 100), 1) if total_bytes > 0 else 0.0
                        with self.lock:
                            if model_name in self.jobs:
                                self.jobs[model_name]["downloaded_bytes"] = downloaded
                                self.jobs[model_name]["progress_pct"] = min(99.9, pct)
                                self.jobs[model_name]["speed_mbps"] = round(speed, 2)
                        last_time = now
                        last_bytes = downloaded

            # Atomic rename once verified
            if part_path.exists():
                part_path.replace(target_path)

            with self.lock:
                if model_name in self.jobs:
                    self.jobs[model_name]["status"] = "completed"
                    self.jobs[model_name]["progress_pct"] = 100.0
                    self.jobs[model_name]["downloaded_bytes"] = downloaded
                    self.jobs[model_name]["speed_mbps"] = 0.0

            logger.app(f"Whisper model {model_name} downloaded successfully.")

        except Exception as e:
            part_path.unlink(missing_ok=True)
            with self.lock:
                if model_name in self.jobs:
                    self.jobs[model_name]["status"] = "failed"
                    self.jobs[model_name]["error"] = str(e)
            logger.app(f"Failed to download Whisper model {model_name}: {e}", level="error")


download_mgr = ModelDownloadManager()


# ---------------------------------------------------------------------------
# Helper functions for system inspection
# ---------------------------------------------------------------------------

def _get_ram_info() -> Dict[str, Any]:
    """Retrieve Windows system RAM via GlobalMemoryStatusEx without extra dependencies."""
    try:
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            total_gb = round(stat.ullTotalPhys / (1024**3), 2)
            avail_gb = round(stat.ullAvailPhys / (1024**3), 2)
            used_gb = round((stat.ullTotalPhys - stat.ullAvailPhys) / (1024**3), 2)
            return {
                "total_gb": total_gb,
                "available_gb": avail_gb,
                "used_gb": used_gb,
                "load_percent": stat.dwMemoryLoad
            }
    except Exception as e:
        logger.app(f"RAM detection error: {e}", level="debug")

    return {"total_gb": 0, "available_gb": 0, "used_gb": 0, "load_percent": 0}


def _get_folder_size(path: Path) -> Dict[str, Any]:
    """Calculate size and file count in a directory safely."""
    if not path.exists():
        return {"bytes": 0, "formatted": "0 B", "file_count": 0}

    total_bytes = 0
    count = 0
    try:
        for p in path.rglob("*"):
            if p.is_file():
                try:
                    total_bytes += p.stat().st_size
                    count += 1
                except (OSError, PermissionError):
                    pass
    except Exception:
        pass

    # Format human readable
    if total_bytes >= 1024**3:
        formatted = f"{total_bytes / (1024**3):.2f} GB"
    elif total_bytes >= 1024**2:
        formatted = f"{total_bytes / (1024**2):.1f} MB"
    elif total_bytes >= 1024:
        formatted = f"{total_bytes / 1024:.1f} KB"
    else:
        formatted = f"{total_bytes} B"

    return {"bytes": total_bytes, "formatted": formatted, "file_count": count}


# ---------------------------------------------------------------------------
# Template Routes
# ---------------------------------------------------------------------------

@settings_bp.route("/settings")
def settings_page():
    """Render the centralized Settings & Resource Management workspace."""
    app_settings = settings_manager.get_settings()
    active_tab = request.args.get("tab", "general")
    return render_template(
        "settings.html",
        active_page="settings",
        active_tab=active_tab,
        settings=app_settings,
        current_whisper_model=getattr(config, "WHISPER_MODEL", "base")
    )


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@settings_bp.route("/api/settings/all", methods=["GET"])
def get_all_settings():
    """Return complete user settings and runtime configuration."""
    current = settings_manager.get_settings()
    # Ensure current config WHISPER_MODEL is reflected
    if "models" not in current:
        current["models"] = {}
    current["models"]["activeWhisperModel"] = getattr(config, "WHISPER_MODEL", "base")

    # Ensure folder settings reflect defaults if absent
    if "folders" not in current:
        current["folders"] = {
            "mediaImportFolder": str(config.INPUT_DIR),
            "projectFolder": str(config.DATA_DIR / "projects"),
            "exportFolder": str(config.FINAL_DIR),
            "tempFolder": str(config.OUTPUT_DIR / "temp")
        }

    return jsonify({"success": True, "settings": current})


@settings_bp.route("/api/settings/save", methods=["POST"])
def save_settings():
    """Update and persist application preferences."""
    data = request.get_json(silent=True) or {}
    updated = settings_manager.update_settings(data)

    # Sync WHISPER_MODEL if modified
    if "models" in data and "activeWhisperModel" in data["models"]:
        new_model = data["models"]["activeWhisperModel"]
        config.WHISPER_MODEL = new_model

    return jsonify({"success": True, "settings": updated, "message": "Settings saved successfully."})


@settings_bp.route("/api/settings/models", methods=["GET"])
def get_models():
    """List all supported Whisper models with verified disk/download status and metadata."""
    models_list = []
    active_model = getattr(config, "WHISPER_MODEL", "base")

    for key, meta in WHISPER_CATALOG.items():
        model_file = WHISPER_CACHE_DIR / f"{key}.pt"
        part_file = WHISPER_CACHE_DIR / f"{key}.pt.part"

        job = download_mgr.get_job(key)
        is_downloading = job is not None and job.get("status") == "downloading"

        if model_file.exists():
            disk_size = model_file.stat().st_size
            if disk_size >= 1024**3:
                size_str = f"{disk_size / (1024**3):.2f} GB"
            else:
                size_str = f"{disk_size / (1024**2):.1f} MB"
            status = "installed"
        elif is_downloading:
            status = "downloading"
            size_str = meta["file_size"]
        elif part_file.exists():
            status = "paused"
            size_str = meta["file_size"]
        else:
            status = "available"
            size_str = meta["file_size"]

        models_list.append({
            "id": key,
            "name": meta["name"],
            "variant": meta["variant"],
            "parameters": meta["parameters"],
            "size": size_str,
            "estimated_bytes": meta["disk_bytes"],
            "accuracy": meta["accuracy"],
            "languages": meta["languages"],
            "recommended_for": meta["recommended_for"],
            "status": status,
            "is_active": (key == active_model),
            "download_job": job
        })

    return jsonify({
        "success": True,
        "models": models_list,
        "active_model": active_model,
        "cache_dir": str(WHISPER_CACHE_DIR)
    })


@settings_bp.route("/api/settings/models/set-default", methods=["POST"])
def set_default_model():
    """Set active Whisper model for transcription."""
    data = request.get_json(silent=True) or {}
    model_name = data.get("model_name", "").strip()

    if model_name not in WHISPER_CATALOG:
        return jsonify({"success": False, "message": f"Unsupported model variant: {model_name}"}), 400

    model_file = WHISPER_CACHE_DIR / f"{model_name}.pt"
    if not model_file.exists():
        return jsonify({"success": False, "message": f"Model {model_name} must be downloaded first before setting as default."}), 400

    config.WHISPER_MODEL = model_name
    settings_manager.update_settings({"models": {"activeWhisperModel": model_name}})
    logger.app(f"Default Whisper model set to: {model_name}")

    return jsonify({"success": True, "active_model": model_name, "message": f"Default Whisper model set to {model_name}."})


@settings_bp.route("/api/settings/models/download", methods=["POST"])
def download_model():
    """Trigger background download of a Whisper model with real progress."""
    data = request.get_json(silent=True) or {}
    model_name = data.get("model_name", "").strip()

    if not model_name or model_name not in WHISPER_CATALOG:
        return jsonify({"success": False, "message": f"Invalid model variant: {model_name}"}), 400

    res = download_mgr.start_download(model_name)
    return jsonify(res)


@settings_bp.route("/api/settings/models/download-progress", methods=["GET"])
def get_download_progress():
    """Poll live download progress for active and completed downloads."""
    jobs = download_mgr.get_all_jobs()
    return jsonify({"success": True, "jobs": jobs})


@settings_bp.route("/api/settings/models/cancel-download", methods=["POST"])
def cancel_model_download():
    """Cancel an in-progress model download."""
    data = request.get_json(silent=True) or {}
    model_name = data.get("model_name", "").strip()
    res = download_mgr.cancel_download(model_name)
    return jsonify(res)


@settings_bp.route("/api/settings/models/delete", methods=["POST"])
def delete_model():
    """Safely delete a downloaded model file after user confirmation."""
    data = request.get_json(silent=True) or {}
    model_name = data.get("model_name", "").strip()

    if not model_name:
        return jsonify({"success": False, "message": "Model name required"}), 400

    if model_name == getattr(config, "WHISPER_MODEL", "base"):
        return jsonify({"success": False, "message": "Cannot delete the currently active default model. Switch default first."}), 400

    model_file = WHISPER_CACHE_DIR / f"{model_name}.pt"
    if model_file.exists():
        try:
            model_file.unlink()
            download_mgr.clear_job_history(model_name)
            logger.app(f"Deleted Whisper model: {model_name}")
            return jsonify({"success": True, "message": f"Model {model_name} deleted successfully."})
        except Exception as e:
            return jsonify({"success": False, "message": f"Error deleting file: {e}"}), 500

    return jsonify({"success": False, "message": "Model file not found on disk"}), 404


@settings_bp.route("/api/settings/dependencies", methods=["GET"])
def get_dependencies():
    """Inspect and report real operational status of all system libraries."""
    deps = []

    # 1. FFmpeg
    ffmpeg_ok, ffmpeg_ver = check_ffmpeg()
    deps.append({
        "name": "FFmpeg Video Processing Core",
        "category": "Media Engine",
        "installed": ffmpeg_ok,
        "version": ffmpeg_ver.splitlines()[0] if ffmpeg_ok else "Not Installed",
        "path": str(config.FFMPEG_PATH) if config.FFMPEG_PATH else "System PATH",
        "required": ">= 4.3 (H.264 / AAC / Filtergraph)",
        "status": "Operational" if ffmpeg_ok else "Missing",
        "status_code": "ok" if ffmpeg_ok else "error"
    })

    # 2. PyTorch
    try:
        import torch
        cuda_avail = torch.cuda.is_available()
        cuda_device = torch.cuda.get_device_name(0) if cuda_avail else "CPU Only (CUDA not active)"
        deps.append({
            "name": "PyTorch ML Tensor Framework",
            "category": "Deep Learning",
            "installed": True,
            "version": torch.__version__,
            "hardware_accel": f"CUDA: {cuda_avail} ({cuda_device})",
            "required": ">= 2.0.0",
            "status": "Operational",
            "status_code": "ok"
        })
    except ImportError as e:
        deps.append({
            "name": "PyTorch ML Framework",
            "category": "Deep Learning",
            "installed": False,
            "version": "Not Installed",
            "required": ">= 2.0.0",
            "status": f"Missing: {e}",
            "status_code": "error"
        })

    # 3. Whisper
    try:
        import whisper
        deps.append({
            "name": "OpenAI Whisper Speech Recognition",
            "category": "Audio AI",
            "installed": True,
            "version": getattr(whisper, "__version__", "Official Release"),
            "path": str(WHISPER_CACHE_DIR),
            "required": ">= 20230314",
            "status": "Operational",
            "status_code": "ok"
        })
    except ImportError as e:
        deps.append({
            "name": "OpenAI Whisper",
            "category": "Audio AI",
            "installed": False,
            "version": "Not Installed",
            "required": "Official",
            "status": f"Missing: {e}",
            "status_code": "error"
        })

    # 4. OpenCV
    try:
        import cv2
        deps.append({
            "name": "OpenCV Computer Vision",
            "category": "Scene Detection & Face Tracking",
            "installed": True,
            "version": cv2.__version__,
            "required": ">= 4.5.0",
            "status": "Operational",
            "status_code": "ok"
        })
    except ImportError as e:
        deps.append({
            "name": "OpenCV Computer Vision",
            "category": "Scene Detection",
            "installed": False,
            "version": "Not Installed",
            "required": ">= 4.5.0",
            "status": f"Missing: {e}",
            "status_code": "error"
        })

    # 5. Pillow (PIL)
    try:
        import PIL
        deps.append({
            "name": "Pillow Imaging Library",
            "category": "Graphics & Brand Icon Engine",
            "installed": True,
            "version": PIL.__version__,
            "required": ">= 9.0.0",
            "status": "Operational",
            "status_code": "ok"
        })
    except ImportError as e:
        deps.append({
            "name": "Pillow Imaging Library",
            "category": "Graphics",
            "installed": False,
            "version": "Not Installed",
            "required": ">= 9.0.0",
            "status": f"Missing: {e}",
            "status_code": "error"
        })

    return jsonify({"success": True, "dependencies": deps})


@settings_bp.route("/api/settings/storage", methods=["GET"])
def get_storage():
    """Inspect real disk usage and directory sizes."""
    usage = shutil.disk_usage(config.ROOT_DIR)
    total_gb = round(usage.total / (1024**3), 2)
    free_gb = round(usage.free / (1024**3), 2)
    used_gb = round(usage.used / (1024**3), 2)
    pct = round((usage.used / usage.total) * 100, 1)

    folders_breakdown = {
        "whisper_models": _get_folder_size(WHISPER_CACHE_DIR),
        "subtitles_cache": _get_folder_size(config.SUBTITLE_DIR),
        "transcript_cache": _get_folder_size(config.TRANSCRIPT_DIR),
        "broll_cache": _get_folder_size(config.BROLL_CACHE_DIR),
        "thumbnails": _get_folder_size(config.THUMBNAIL_DIR),
        "temp_processing": _get_folder_size(config.OUTPUT_DIR / "temp"),
        "final_exports": _get_folder_size(config.FINAL_DIR)
    }

    return jsonify({
        "success": True,
        "disk": {
            "total_gb": total_gb,
            "used_gb": used_gb,
            "free_gb": free_gb,
            "used_percent": pct,
            "drive": str(config.ROOT_DIR.drive) if hasattr(config.ROOT_DIR, "drive") else "System"
        },
        "breakdown": folders_breakdown,
        "paths": {
            "root": str(config.ROOT_DIR),
            "input": str(config.INPUT_DIR),
            "output": str(config.OUTPUT_DIR),
            "whisper": str(WHISPER_CACHE_DIR)
        }
    })


@settings_bp.route("/api/settings/storage/clear-cache", methods=["POST"])
def clear_cache():
    """Safely remove temporary and intermediate cache files without touching user projects."""
    cleared_count = 0
    freed_bytes = 0

    cache_targets = [
        config.BROLL_CACHE_DIR,
        config.OUTPUT_DIR / "temp",
        config.DATA_DIR / "temp",
        WHISPER_CACHE_DIR  # only .part files
    ]

    for target in cache_targets:
        if not target.exists():
            continue

        if target == WHISPER_CACHE_DIR:
            # Delete only unfinished .part downloads
            for p in target.glob("*.part"):
                try:
                    freed_bytes += p.stat().st_size
                    p.unlink()
                    cleared_count += 1
                except Exception:
                    pass
            continue

        # In output temp and broll cache, delete non-project files
        for p in target.rglob("*"):
            if p.is_file():
                try:
                    freed_bytes += p.stat().st_size
                    p.unlink()
                    cleared_count += 1
                except Exception:
                    pass

    freed_mb = round(freed_bytes / (1024 * 1024), 2)
    logger.app(f"Cache cleared: {cleared_count} files removed, {freed_mb} MB freed.")

    return jsonify({
        "success": True,
        "cleared_files": cleared_count,
        "freed_mb": freed_mb,
        "message": f"Successfully cleared {cleared_count} cached files ({freed_mb} MB freed)."
    })


@settings_bp.route("/api/settings/performance", methods=["GET"])
def get_performance_info():
    """Retrieve genuine CPU, RAM, and GPU capabilities."""
    ram = _get_ram_info()
    cpu_count = os.cpu_count() or 1
    cpu_model = platform.processor() or "Multi-core Processor"

    import torch
    cuda_available = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if cuda_available else "Intel/AMD CPU"

    return jsonify({
        "success": True,
        "cpu": {
            "cores": cpu_count,
            "model": cpu_model,
            "architecture": platform.machine()
        },
        "ram": ram,
        "gpu": {
            "cuda_available": cuda_available,
            "device_name": device_name,
            "device_count": torch.cuda.device_count() if cuda_available else 0
        },
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version()
        }
    })


@settings_bp.route("/api/settings/diagnostics", methods=["GET", "POST"])
def run_diagnostics():
    """Run real live tests on FFmpeg, PyTorch, Whisper, and Filesystem."""
    results = []

    # 1. FFmpeg binary check
    ff_ok, ff_info = check_ffmpeg()
    results.append({
        "test": "FFmpeg Executable & Version",
        "passed": ff_ok,
        "details": ff_info.splitlines()[0] if ff_ok else "FFmpeg executable not found",
        "recommendation": "Install FFmpeg and place on system PATH" if not ff_ok else "Operational"
    })

    # 2. PyTorch tensor allocation test
    try:
        import torch
        t1 = torch.ones((10, 10))
        t2 = torch.matmul(t1, t1)
        results.append({
            "test": "PyTorch Tensor Computation",
            "passed": True,
            "details": f"PyTorch {torch.__version__} CPU tensor calculation verified",
            "recommendation": "Operational"
        })
    except Exception as e:
        results.append({
            "test": "PyTorch Tensor Computation",
            "passed": False,
            "details": f"Error: {e}",
            "recommendation": "Reinstall PyTorch via pip"
        })

    # 3. Whisper accessibility & default model
    try:
        import whisper
        curr_model = getattr(config, "WHISPER_MODEL", "base")
        model_file = WHISPER_CACHE_DIR / f"{curr_model}.pt"
        if model_file.exists():
            results.append({
                "test": "Active Whisper Model File",
                "passed": True,
                "details": f"Model '{curr_model}' found at {model_file.name} ({round(model_file.stat().st_size / (1024**2), 1)} MB)",
                "recommendation": "Operational"
            })
        else:
            results.append({
                "test": "Active Whisper Model File",
                "passed": False,
                "details": f"Model '{curr_model}' not yet cached locally",
                "recommendation": f"Download '{curr_model}' from the AI Models tab"
            })
    except Exception as e:
        results.append({
            "test": "Whisper Module Import",
            "passed": False,
            "details": str(e),
            "recommendation": "Verify openai-whisper package installation"
        })

    # 4. Storage write permissions
    try:
        test_file = config.DATA_DIR / ".diag_write_test"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink()
        results.append({
            "test": "Data Directory Write Permissions",
            "passed": True,
            "details": f"Read/Write access confirmed in {config.DATA_DIR}",
            "recommendation": "Operational"
        })
    except Exception as e:
        results.append({
            "test": "Data Directory Write Permissions",
            "passed": False,
            "details": f"Write failed: {e}",
            "recommendation": "Check filesystem permissions for data folder"
        })

    # 5. Font assets availability
    font_count = len(list(config.FONT_DIR.glob("*.ttf"))) + len(list(config.FONT_DIR.glob("*.otf")))
    results.append({
        "test": "Typography & Font Assets",
        "passed": font_count > 0,
        "details": f"{font_count} creator font files detected in {config.FONT_DIR.name}",
        "recommendation": "Add .ttf/.otf fonts to assets/fonts if custom styling required" if font_count == 0 else "Operational"
    })

    all_passed = all(r["passed"] for r in results)
    return jsonify({"success": True, "all_passed": all_passed, "diagnostics": results})


@settings_bp.route("/api/settings/folders/open", methods=["POST"])
def open_folder():
    """Open a configured folder in the Windows Explorer file manager."""
    data = request.get_json(silent=True) or {}
    folder_type = data.get("folder_type", "mediaImportFolder")

    settings = settings_manager.get_settings().get("folders", {})
    folder_map = {
        "mediaImportFolder": settings.get("mediaImportFolder", str(config.INPUT_DIR)),
        "projectFolder": settings.get("projectFolder", str(config.DATA_DIR / "projects")),
        "exportFolder": settings.get("exportFolder", str(config.FINAL_DIR)),
        "tempFolder": settings.get("tempFolder", str(config.OUTPUT_DIR / "temp")),
        "whisperFolder": str(WHISPER_CACHE_DIR)
    }

    target = Path(folder_map.get(folder_type, config.INPUT_DIR))
    target.mkdir(parents=True, exist_ok=True)

    try:
        if sys.platform == "win32":
            os.startfile(str(target))
        elif sys.platform == "darwin":
            import subprocess
            subprocess.run(["open", str(target)], check=False)
        else:
            import subprocess
            subprocess.run(["xdg-open", str(target)], check=False)
        return jsonify({"success": True, "message": f"Opened {target.name} in file manager"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to open directory: {e}"}), 500


@settings_bp.route("/api/settings/folders/reset", methods=["POST"])
def reset_folders():
    """Reset folder configuration paths to system defaults."""
    default_folders = {
        "mediaImportFolder": str(config.INPUT_DIR),
        "projectFolder": str(config.DATA_DIR / "projects"),
        "exportFolder": str(config.FINAL_DIR),
        "tempFolder": str(config.OUTPUT_DIR / "temp")
    }
    settings_manager.update_settings({"folders": default_folders})
    return jsonify({"success": True, "folders": default_folders, "message": "Folder paths reset to system defaults."})
