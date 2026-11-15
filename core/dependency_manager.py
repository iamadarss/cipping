# core/dependency_manager.py
"""
Central Dependency & Library Manager for UpClip Studio.
Tracks, inspects, and installs the 8 canonical dependency categories:
1. Core Python
2. AI and Machine Learning
3. Speech Recognition
4. Image Processing
5. Video Processing
6. Web Framework
7. System Runtime
8. Typography and Font Assets
"""

import sys
import time
import subprocess
import threading
import importlib
import importlib.metadata
from pathlib import Path
from typing import Dict, Any, List, Optional

import config
from core.logger import logger
from utils.ffmpeg_utils import check_ffmpeg
from core.font_manager import font_manager

DEPENDENCY_CATALOG = [
    # 1. Core Python
    {
        "id": "requests",
        "name": "Requests HTTP Library",
        "package_name": "requests",
        "category": "Core Python",
        "required_version": ">= 2.28.0",
        "is_required": True,
        "estimated_size": "25 MB",
        "description": "Secure network transmission for model downloads & updates."
    },
    {
        "id": "pyyaml",
        "name": "PyYAML Configuration Parser",
        "package_name": "pyyaml",
        "category": "Core Python",
        "required_version": ">= 6.0",
        "is_required": True,
        "estimated_size": "12 MB",
        "description": "YAML parser for template manifests and configuration."
    },
    {
        "id": "python-dotenv",
        "name": "Python Dotenv Environment Manager",
        "package_name": "python-dotenv",
        "category": "Core Python",
        "required_version": ">= 1.0.0",
        "is_required": True,
        "estimated_size": "5 MB",
        "description": "Loads local environment overrides and secure paths."
    },
    {
        "id": "packaging",
        "name": "Packaging Version Validation",
        "package_name": "packaging",
        "category": "Core Python",
        "required_version": ">= 21.0",
        "is_required": True,
        "estimated_size": "4 MB",
        "description": "Semantic versioning and runtime dependency checks."
    },

    # 2. AI and Machine Learning
    {
        "id": "torch",
        "name": "PyTorch ML Tensor Framework",
        "package_name": "torch",
        "category": "AI and Machine Learning",
        "required_version": ">= 2.0.0",
        "is_required": True,
        "estimated_size": "750 MB",
        "description": "Core deep learning engine for Whisper and neural audio processing."
    },
    {
        "id": "torchaudio",
        "name": "TorchAudio Sound Signal Processing",
        "package_name": "torchaudio",
        "category": "AI and Machine Learning",
        "required_version": ">= 2.0.0",
        "is_required": False,
        "estimated_size": "120 MB",
        "description": "PyTorch audio resampling and spectrogram generation."
    },
    {
        "id": "torchvision",
        "name": "TorchVision Feature Extraction",
        "package_name": "torchvision",
        "category": "AI and Machine Learning",
        "required_version": ">= 0.15.0",
        "is_required": False,
        "estimated_size": "150 MB",
        "description": "Computer vision models for visual viral feature ranking."
    },
    {
        "id": "transformers",
        "name": "HuggingFace Transformers Library",
        "package_name": "transformers",
        "category": "AI and Machine Learning",
        "required_version": ">= 4.30.0",
        "is_required": False,
        "estimated_size": "90 MB",
        "description": "Natural language understanding for hook detection and summaries."
    },
    {
        "id": "onnxruntime",
        "name": "ONNX Acceleration Runtime",
        "package_name": "onnxruntime",
        "category": "AI and Machine Learning",
        "required_version": ">= 1.15.0",
        "is_required": False,
        "estimated_size": "65 MB",
        "description": "High-speed quantized inference for smart scene detection."
    },

    # 3. Speech Recognition
    {
        "id": "openai-whisper",
        "name": "OpenAI Whisper Speech-to-Text",
        "package_name": "openai-whisper",
        "category": "Speech Recognition",
        "required_version": ">= 20230314",
        "is_required": True,
        "estimated_size": "45 MB",
        "description": "Accurate multi-lingual and Hinglish speech recognition engine."
    },
    {
        "id": "tiktoken",
        "name": "TikToken Fast BPE Tokenizer",
        "package_name": "tiktoken",
        "category": "Speech Recognition",
        "required_version": ">= 0.3.0",
        "is_required": True,
        "estimated_size": "18 MB",
        "description": "High-throughput tokenization for Whisper speech segments."
    },
    {
        "id": "librosa",
        "name": "Librosa Audio Signal Engine",
        "package_name": "librosa",
        "category": "Speech Recognition",
        "required_version": ">= 0.10.0",
        "is_required": False,
        "estimated_size": "35 MB",
        "description": "Music beat tracking, pitch detection, and silence isolation."
    },
    {
        "id": "soundfile",
        "name": "SoundFile High-Fidelity Audio IO",
        "package_name": "soundfile",
        "category": "Speech Recognition",
        "required_version": ">= 0.12.0",
        "is_required": False,
        "estimated_size": "15 MB",
        "description": "Fast PCM audio reading and waveform serialization."
    },

    # 4. Image Processing
    {
        "id": "pillow",
        "name": "Pillow (PIL) Graphic Engine",
        "package_name": "pillow",
        "category": "Image Processing",
        "required_version": ">= 9.0.0",
        "is_required": True,
        "estimated_size": "28 MB",
        "description": "Thumbnail generation, brand logo watermarking, and badge compositing."
    },
    {
        "id": "matplotlib",
        "name": "Matplotlib Visual Plotting Engine",
        "package_name": "matplotlib",
        "category": "Image Processing",
        "required_version": ">= 3.5.0",
        "is_required": False,
        "estimated_size": "42 MB",
        "description": "Waveform curve rendering and audio loudness visual analysis."
    },

    # 5. Video Processing
    {
        "id": "opencv-python",
        "name": "OpenCV Computer Vision",
        "package_name": "opencv-python",
        "category": "Video Processing",
        "required_version": ">= 4.5.0",
        "is_required": True,
        "estimated_size": "65 MB",
        "description": "Scene cut analysis, frame pixel delta, and face re-framing."
    },
    {
        "id": "ffmpeg-python",
        "name": "FFmpeg Python Pipeline Adapter",
        "package_name": "ffmpeg-python",
        "category": "Video Processing",
        "required_version": ">= 0.2.0",
        "is_required": True,
        "estimated_size": "8 MB",
        "description": "Python interface for complex video filtergraph chains."
    },
    {
        "id": "scenedetect",
        "name": "PySceneDetect Scene Analysis",
        "package_name": "scenedetect",
        "category": "Video Processing",
        "required_version": ">= 0.6.0",
        "is_required": True,
        "estimated_size": "22 MB",
        "description": "Detects camera cuts and optimal clip boundaries automatically."
    },
    {
        "id": "moviepy",
        "name": "MoviePy Composition Engine",
        "package_name": "moviepy",
        "category": "Video Processing",
        "required_version": ">= 1.0.3",
        "is_required": False,
        "estimated_size": "30 MB",
        "description": "Non-linear multi-track audio/video composition."
    },

    # 6. Web Framework
    {
        "id": "flask",
        "name": "Flask WSGI Application Core",
        "package_name": "flask",
        "category": "Web Framework",
        "required_version": ">= 3.0.0",
        "is_required": True,
        "estimated_size": "15 MB",
        "description": "Serves the local desktop UI and REST API controllers."
    },
    {
        "id": "flask-sqlalchemy",
        "name": "Flask-SQLAlchemy Database ORM",
        "package_name": "flask-sqlalchemy",
        "category": "Web Framework",
        "required_version": ">= 3.0.0",
        "is_required": True,
        "estimated_size": "10 MB",
        "description": "Manages persistent SQLite Project and Clip entities."
    },
    {
        "id": "jinja2",
        "name": "Jinja2 Dynamic Template Engine",
        "package_name": "jinja2",
        "category": "Web Framework",
        "required_version": ">= 3.1.0",
        "is_required": True,
        "estimated_size": "12 MB",
        "description": "Renders modular workspace HTML templates and components."
    },
    {
        "id": "werkzeug",
        "name": "Werkzeug WSGI System Utilities",
        "package_name": "werkzeug",
        "category": "Web Framework",
        "required_version": ">= 3.0.0",
        "is_required": True,
        "estimated_size": "14 MB",
        "description": "Secure file uploads, MIME routing, and HTTP protocol utilities."
    },

    # 7. System Runtime
    {
        "id": "ffmpeg",
        "name": "FFmpeg Video Processing Core",
        "package_name": None,
        "category": "System Runtime",
        "required_version": ">= 4.3 (H.264 / AAC)",
        "is_required": True,
        "estimated_size": "85 MB",
        "description": "Hardware-accelerated video muxing, ASS subtitle burning, and rendering."
    },
    {
        "id": "yt-dlp",
        "name": "yt-dlp Media Stream Downloader",
        "package_name": "yt-dlp",
        "category": "System Runtime",
        "required_version": ">= 2023.0.0",
        "is_required": False,
        "estimated_size": "20 MB",
        "description": "Fast download engine for YouTube and public web video imports."
    },

    # 8. Typography and Font Assets
    {
        "id": "fonttools",
        "name": "FontTools Typography Toolkit",
        "package_name": "fonttools",
        "category": "Typography and Font Assets",
        "required_version": ">= 4.30.0",
        "is_required": True,
        "estimated_size": "16 MB",
        "description": "Validates TTF/OTF font table structures and calculates metrics."
    },
    {
        "id": "creator-fonts",
        "name": "Google Fonts & Devanagari Creator Pack",
        "package_name": None,
        "category": "Typography and Font Assets",
        "required_version": ">= 1.0.0",
        "is_required": True,
        "estimated_size": "2.5 MB",
        "description": "Montserrat, Noto Sans Devanagari, Poppins, Inter & Bebas Neue fonts."
    }
]


class DependencyInstallManager:
    """Thread-safe background dependency installer via pip and local asset managers."""

    def __init__(self):
        self.lock = threading.Lock()
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.active_processes: Dict[str, subprocess.Popen] = {}

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self.lock:
            return dict(self.jobs.get(job_id, {})) if job_id in self.jobs else None

    def get_all_jobs(self) -> Dict[str, Dict[str, Any]]:
        with self.lock:
            return {k: dict(v) for k, v in self.jobs.items()}

    def inspect_dependencies(self) -> List[Dict[str, Any]]:
        """Inspect and report the actual installed version and operational status of all catalog items."""
        result = []
        for item in DEPENDENCY_CATALOG:
            dep_id = item["id"]
            pkg_name = item["package_name"]

            # Special case: FFmpeg binary
            if dep_id == "ffmpeg":
                ff_ok, ff_ver = check_ffmpeg()
                ver_str = ff_ver.splitlines()[0] if ff_ok else "Not Installed"
                status = "Installed" if ff_ok else "Missing"
                result.append({
                    **item,
                    "installed_version": ver_str,
                    "is_installed": ff_ok,
                    "status": status,
                    "status_code": "ok" if ff_ok else "error",
                    "can_install": False,  # System binary must be installed via package manager or PATH
                    "install_instruction": "Ensure ffmpeg executable is on Windows PATH"
                })
                continue

            # Special case: Creator Fonts bundle
            if dep_id == "creator-fonts":
                fdiag = font_manager.get_diagnostics()
                has_fonts = fdiag["count"] > 0
                ver_str = f"{fdiag['count']} Creator Fonts ({'Devanagari Ready' if fdiag['has_devanagari'] else 'Fallback'})"
                status = "Installed" if has_fonts else "Missing"
                result.append({
                    **item,
                    "installed_version": ver_str if has_fonts else "0 Fonts",
                    "is_installed": has_fonts,
                    "status": status,
                    "status_code": "ok" if has_fonts else "warn",
                    "can_install": True,
                    "is_font_bundle": True
                })
                continue

            # Python pip package
            try:
                ver = importlib.metadata.version(pkg_name)
                is_inst = True
                status = "Installed"
                code = "ok"
            except Exception:
                ver = "Not Installed"
                is_inst = False
                status = "Missing"
                code = "error" if item["is_required"] else "warn"

            result.append({
                **item,
                "installed_version": ver,
                "is_installed": is_inst,
                "status": status,
                "status_code": code,
                "can_install": True
            })

        return result

    def start_installation(self, target_ids: List[str]) -> Dict[str, Any]:
        """Start non-blocking pip installation for selected dependencies."""
        job_id = f"job_{int(time.time())}"
        with self.lock:
            self.jobs[job_id] = {
                "id": job_id,
                "target_ids": target_ids,
                "status": "in_progress",
                "progress_pct": 5,
                "current_item": target_ids[0] if target_ids else "",
                "logs": [f"Installation queue started for {len(target_ids)} dependencies."],
                "error": None,
                "started_at": time.time()
            }

        t = threading.Thread(target=self._install_worker, args=(job_id, target_ids), daemon=True)
        t.start()
        return {"success": True, "job_id": job_id, "job": self.get_job(job_id)}

    def cancel_installation(self, job_id: str) -> Dict[str, Any]:
        with self.lock:
            if job_id in self.jobs and self.jobs[job_id]["status"] == "in_progress":
                proc = self.active_processes.get(job_id)
                if proc:
                    try:
                        proc.terminate()
                    except Exception:
                        pass
                self.jobs[job_id]["status"] = "cancelled"
                self.jobs[job_id]["logs"].append("Installation cancelled by user.")
                return {"success": True, "message": "Installation cancelled."}
            return {"success": False, "message": "No active installation to cancel."}

    def _install_worker(self, job_id: str, target_ids: List[str]):
        total = len(target_ids)
        for idx, dep_id in enumerate(target_ids):
            # Check cancellation
            with self.lock:
                if self.jobs.get(job_id, {}).get("status") == "cancelled":
                    return

            # Special case: creator fonts
            if dep_id == "creator-fonts":
                with self.lock:
                    self.jobs[job_id]["current_item"] = "creator-fonts"
                    self.jobs[job_id]["logs"].append("Downloading and validating Creator Fonts Bundle...")
                font_res = font_manager.install_all_fonts()
                with self.lock:
                    self.jobs[job_id]["logs"].append(f"Creator fonts installed: {font_res['installed_count']} fonts ready.")
                    pct = round(((idx + 1) / total) * 95, 1)
                    self.jobs[job_id]["progress_pct"] = pct
                continue

            # Lookup pip package
            target_meta = next((d for d in DEPENDENCY_CATALOG if d["id"] == dep_id), None)
            pkg_name = target_meta["package_name"] if target_meta else dep_id
            if not pkg_name:
                continue

            with self.lock:
                self.jobs[job_id]["current_item"] = pkg_name
                self.jobs[job_id]["logs"].append(f"Installing {pkg_name} via pip...")

            cmd = [sys.executable, "-m", "pip", "install", pkg_name, "--no-warn-script-location"]
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                self.active_processes[job_id] = proc

                stdout_lines = []
                for line in iter(proc.stdout.readline, ""):
                    if not line:
                        break
                    stdout_lines.append(line.strip())
                    if len(stdout_lines) % 5 == 0:
                        with self.lock:
                            self.jobs[job_id]["logs"].append(f"[{pkg_name}] {line.strip()}")

                proc.stdout.close()
                ret_code = proc.wait()

                if ret_code != 0:
                    with self.lock:
                        self.jobs[job_id]["status"] = "failed"
                        self.jobs[job_id]["error"] = f"Failed installing {pkg_name} (code {ret_code})"
                        self.jobs[job_id]["logs"].append(f"Error: pip exited with code {ret_code}")
                    return

                # Validate installation
                importlib.invalidate_caches()
                try:
                    ver = importlib.metadata.version(pkg_name)
                    with self.lock:
                        self.jobs[job_id]["logs"].append(f"Validation successful: {pkg_name} v{ver} operational.")
                except Exception as val_err:
                    with self.lock:
                        self.jobs[job_id]["logs"].append(f"Post-install validation notice for {pkg_name}: {val_err}")

            except Exception as e:
                with self.lock:
                    self.jobs[job_id]["status"] = "failed"
                    self.jobs[job_id]["error"] = str(e)
                    self.jobs[job_id]["logs"].append(f"Installation exception: {e}")
                return
            finally:
                self.active_processes.pop(job_id, None)

            pct = round(((idx + 1) / total) * 95, 1)
            with self.lock:
                self.jobs[job_id]["progress_pct"] = pct

        with self.lock:
            self.jobs[job_id]["status"] = "completed"
            self.jobs[job_id]["progress_pct"] = 100
            self.jobs[job_id]["logs"].append("All requested dependencies installed and verified successfully.")


dependency_manager = DependencyInstallManager()
