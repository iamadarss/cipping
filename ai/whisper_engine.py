import json
import threading
from pathlib import Path

import config


# Reusable module-level model cache so we don't re-load
# the Whisper model on every job (huge speedup for repeated runs).
_whisper_models = {}
_model_lock = threading.Lock()


def _get_model(model_name):
    """Load (and cache) a Whisper model once per process with thread safety."""
    if model_name not in _whisper_models:
        with _model_lock:
            if model_name not in _whisper_models:
                try:
                    print(f"Loading Whisper Model : {model_name}")
                except Exception:
                    pass
                import whisper
                _whisper_models[model_name] = whisper.load_model(model_name)
                try:
                    print(f"Whisper Model Loaded Successfully : {model_name}")
                except Exception:
                    pass
    return _whisper_models[model_name]


class WhisperEngine:

    def __init__(self, model_name="base"):
        self.model_name = model_name
        self.model = _get_model(model_name)

    # -------------------------------------

    def transcribe(self, video_path, language=None):
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Media file not found: {video_path}")
        if video_path.stat().st_size == 0:
            raise ValueError(f"Media file is empty (0 bytes): {video_path}")

        # Resolve whisper language code
        whisper_lang = None
        if language and language not in ("auto", None):
            whisper_lang = language
            if language in config.LANGUAGES:
                whisper_lang = config.LANGUAGES[language][1]

        kwargs = {}
        # Use GPU fp16 only when model is genuinely allocated on a CUDA device
        try:
            import torch
            model_device = getattr(self.model, "device", None)
            is_cuda_device = model_device is not None and str(model_device).startswith("cuda")
            if config.USE_GPU and is_cuda_device and torch.cuda.is_available():
                kwargs["fp16"] = True
            else:
                kwargs["fp16"] = False
        except Exception:
            kwargs["fp16"] = False

        if whisper_lang:
            kwargs["language"] = whisper_lang
            if whisper_lang in ("hi", "hindi"):
                kwargs["initial_prompt"] = "यह वीडियो हिंदी में है। कृपया केवल हिंदी और देवनागरी लिपि का प्रयोग करें।"

        # Suppress verbose progress output to prevent terminal encoding and buffer issues
        kwargs["verbose"] = False

        result = self.model.transcribe(
            str(video_path),
            **kwargs
        )

        transcript = []
        raw_segments = result.get("segments", []) if isinstance(result, dict) else (result or [])

        for segment in raw_segments:
            if not isinstance(segment, dict):
                continue
            text = str(segment.get("text", "") or "").strip()
            if not text:
                continue

            try:
                start_val = round(float(segment.get("start", 0.0) or 0.0), 2)
                end_val = round(float(segment.get("end", 0.0) or 0.0), 2)
            except (ValueError, TypeError):
                start_val = 0.0
                end_val = start_val + 2.0

            if end_val <= start_val:
                end_val = round(start_val + 1.0, 2)

            transcript.append({
                "start": start_val,
                "end": end_val,
                "text": text
            })

        return transcript

# -------------------------------------
    def transcribe_cached(self, video_path, cache_file, language=None):
        """
        Transcribe video, using a cached JSON transcript if it already exists
        AND matches the video file's current size, mtime, and requested language.
        """
        cache_file = Path(cache_file)
        video_path = Path(video_path)

        if cache_file.exists() and video_path.exists():
            try:
                v_stat = video_path.stat()
                c_stat = cache_file.stat()
                # If video was modified after cache was created, cache is stale!
                if c_stat.st_mtime >= v_stat.st_mtime:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        cached_raw = json.load(f)
                    if isinstance(cached_raw, dict) and "segments" in cached_raw:
                        cached_size = cached_raw.get("_meta_file_size")
                        cached_lang = cached_raw.get("_meta_language")
                        if (cached_size is None or cached_size == v_stat.st_size) and (cached_lang is None or cached_lang == language):
                            try:
                                print(f"[WHISPER] Using validated cached transcript: {cache_file.name}")
                            except Exception:
                                pass
                            return cached_raw["segments"]
                    elif isinstance(cached_raw, list):
                        try:
                            print(f"[WHISPER] Using cached transcript: {cache_file.name}")
                        except Exception:
                            pass
                        return cached_raw
                else:
                    try:
                        print(f"[WHISPER] Video modified since cache was created ({video_path.name}), re-transcribing...")
                    except Exception:
                        pass
            except Exception as e:
                try:
                    print(f"[WHISPER] Cache check note: {e}, re-transcribing...")
                except Exception:
                    pass

        transcript = self.transcribe(video_path, language=language)
        try:
            v_size = video_path.stat().st_size if video_path.exists() else 0
            payload = {
                "_meta_file_size": v_size,
                "_meta_language": language,
                "segments": transcript
            }
            self.save_json(payload, cache_file)
        except Exception:
            self.save_json(transcript, cache_file)
        return transcript

    # -------------------------------------

    def save_json(self, transcript, output_file):

        output_file = Path(output_file)

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                transcript,
                file,
                indent=4,
                ensure_ascii=False
            )

        try:
            print(f"Transcript Saved : {output_file.name}")
        except Exception:
            pass

    # -------------------------------------

    def load_json(self, json_file):

        with open(
            json_file,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)
            if isinstance(data, dict) and "segments" in data:
                return data["segments"]
            return data
