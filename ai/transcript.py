"""
Unified Transcript Manager & Text Intelligence Engine for UpClip Studio.
Handles transcript parsing, time-slicing for clips, keyword search with timestamps,
filler-word cleaning, and multi-format conversion (JSON, SRT, VTT, TXT).
"""

import json
import re
from pathlib import Path


class TranscriptManager:
    def __init__(self, data=None):
        """
        Initialize TranscriptManager with either:
        - Whisper result dictionary: {"text": str, "segments": list, "language": str}
        - List of segments: [{"start": float, "end": float, "text": str}]
        - Path to JSON/SRT/VTT file
        """
        self.segments = []
        self.language = "en"
        self.full_text = ""

        if data:
            self.load(data)

    def load(self, source):
        """Load transcript data from dict, list, or file path."""
        if isinstance(source, (str, Path)):
            p = Path(source)
            if p.exists():
                ext = p.suffix.lower()
                if ext == ".json":
                    with open(p, "r", encoding="utf-8") as f:
                        source = json.load(f)
                elif ext in [".srt", ".vtt"]:
                    return self._load_from_subtitle_file(p)

        if isinstance(source, dict):
            self.segments = source.get("segments", [])
            self.language = source.get("language", "en")
            self.full_text = source.get("text", "")
            if not self.full_text and self.segments:
                self.full_text = " ".join(s.get("text", "").strip() for s in self.segments)
        elif isinstance(source, list):
            self.segments = source
            self.full_text = " ".join(s.get("text", "").strip() for s in self.segments)

        return self

    def _load_from_subtitle_file(self, path):
        """Parse SRT or VTT file into standard segment structures."""
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        segments = []
        # Pattern for timestamp arrows
        blocks = re.split(r"\n\s*\n", content.strip())
        for block in blocks:
            lines = [line.strip() for line in block.split("\n") if line.strip()]
            if not lines:
                continue
            for i, line in enumerate(lines):
                if "-->" in line:
                    parts = line.split("-->")
                    start_sec = self._parse_timestamp(parts[0].strip())
                    end_sec = self._parse_timestamp(parts[1].strip())
                    text = " ".join(lines[i + 1:])
                    segments.append({
                        "start": start_sec,
                        "end": end_sec,
                        "text": text
                    })
                    break

        self.segments = segments
        self.full_text = " ".join(s["text"] for s in segments)
        return self

    def _parse_timestamp(self, ts):
        """Convert HH:MM:SS,mmm or MM:SS.mmm to float seconds."""
        ts = ts.replace(",", ".")
        parts = ts.split(":")
        if len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        return float(ts)

    def slice(self, start_time, end_time, relative_timestamps=False):
        """
        Extract only the transcript segments and words falling within [start_time, end_time].
        If relative_timestamps=True, adjusts timestamps so clip start is 0.0s.

        Returns:
            list of segment dicts: [{"start": float, "end": float, "text": str}]
        """
        sliced = []
        for seg in self.segments:
            s_start = float(seg.get("start", 0.0))
            s_end = float(seg.get("end", s_start + 1.0))

            # Check overlap
            if s_end > start_time and s_start < end_time:
                clipped_start = max(start_time, s_start)
                clipped_end = min(end_time, s_end)
                text = seg.get("text", "").strip()

                time_offset = start_time if relative_timestamps else 0.0
                out_start = round(clipped_start - time_offset, 2)
                out_end = round(clipped_end - time_offset, 2)

                entry = {
                    "start": out_start,
                    "end": out_end,
                    "text": text
                }
                if "words" in seg and isinstance(seg["words"], list):
                    sliced_words = []
                    for w in seg["words"]:
                        ws = float(w.get("start", s_start))
                        we = float(w.get("end", s_end))
                        if we > start_time and ws < end_time:
                            sliced_words.append({
                                "start": round(max(0.0, ws - time_offset), 2),
                                "end": round(max(0.0, we - time_offset), 2),
                                "text": w.get("text", "").strip(),
                            })
                    if sliced_words:
                        entry["words"] = sliced_words

                sliced.append(entry)

        return sliced

    def get_text_in_range(self, start_time, end_time):
        """Get combined speech text within a specific time window."""
        segments = self.slice(start_time, end_time)
        return " ".join(s["text"] for s in segments).strip()

    def search(self, query):
        """
        Search for words or phrases in the transcript.

        Returns:
            list of matches with timestamp occurrences:
            [{"start": float, "end": float, "text": str, "context": str}]
        """
        if not query:
            return []

        q = query.lower()
        matches = []
        for seg in self.segments:
            text = seg.get("text", "")
            if q in text.lower():
                matches.append({
                    "start": seg.get("start", 0.0),
                    "end": seg.get("end", 0.0),
                    "text": text,
                    "match": query
                })
        return matches

    def clean_filler_words(self, custom_fillers=None):
        """
        Remove common conversational hesitation filler words ('um', 'uh', 'you know').
        Returns cleaned full text.
        """
        fillers = custom_fillers or ["um", "uh", "er", "ah", "you know", "like basically"]
        text = self.full_text
        for filler in fillers:
            pattern = re.compile(rf"\b{re.escape(filler)}\b,?", re.IGNORECASE)
            text = pattern.sub("", text)
        return re.sub(r"\s+", " ", text).strip()

    def get_stats(self):
        """Return comprehensive metadata stats about the transcript."""
        total_duration = 0.0
        if self.segments:
            total_duration = max(float(s.get("end", 0.0)) for s in self.segments)

        words = self.full_text.split()
        word_count = len(words)
        words_per_sec = round(word_count / total_duration, 2) if total_duration > 0 else 0.0

        return {
            "duration": round(total_duration, 2),
            "word_count": word_count,
            "segment_count": len(self.segments),
            "words_per_second": words_per_sec,
            "language": self.language
        }

    def save_json(self, output_path):
        """Save transcript as standard JSON file."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "language": self.language,
            "text": self.full_text,
            "segments": self.segments,
            "stats": self.get_stats()
        }
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return p
