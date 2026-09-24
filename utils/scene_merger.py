"""
Scene Merger Utility for UpClip Studio.
Merges short detected scenes into legitimate, engaging clip lengths (60s+).
Eliminates tiny micro-clips and snaps scene boundaries to sentence endings
so speech is never cut off mid-sentence.
"""

from pathlib import Path
import config


class SceneMerger:
    def __init__(self, min_duration=None, max_duration=None):
        self.min_duration = float(min_duration or getattr(config, "MIN_CLIP_DURATION", 60.0))
        self.max_duration = float(max_duration or getattr(config, "MAX_CLIP_DURATION", 120.0))
        # Absolute floor below which a clip must never be produced (60s minimum)
        self.abs_min_duration = float(getattr(config, "MIN_DURATION", 60.0))

    def snap_to_sentence_boundaries(self, scenes, transcript=None):
        """
        Adjust scene end boundaries to align with natural sentence endings or speech pauses
        so spoken thoughts are never cut off in the middle of a sentence.
        """
        if not scenes or not transcript:
            return scenes

        sentence_enders = ('.', '?', '!', '।', '|', '\n', '...')

        for i, scene in enumerate(scenes):
            target_end = scene["end"]
            best_snap_end = None
            min_dist = float('inf')

            # Search transcript segments around target_end
            for seg_idx, seg in enumerate(transcript):
                s_start = float(seg.get("start", 0))
                s_end = float(seg.get("end", 0))
                text = (seg.get("text") or "").strip()

                # Case 1: Target end falls right inside this segment (cutting mid-sentence!)
                if s_start <= target_end <= s_end:
                    # Check if extending to s_end finishes a sentence
                    dist = abs(s_end - target_end)
                    if s_end - scene["start"] <= (self.max_duration + 15.0):
                        best_snap_end = s_end
                        break

                # Case 2: Segment finishes near target_end (within -3s to +10s) with sentence ender
                if abs(s_end - target_end) <= 8.0:
                    ends_sentence = any(text.endswith(p) for p in sentence_enders)
                    # Check if next segment has a natural pause/silence gap
                    has_pause = False
                    if seg_idx + 1 < len(transcript):
                        next_start = float(transcript[seg_idx + 1].get("start", s_end))
                        if next_start - s_end >= 0.35:
                            has_pause = True

                    if ends_sentence or has_pause:
                        dist = abs(s_end - target_end)
                        if dist < min_dist and (s_end - scene["start"]) >= (self.min_duration * 0.9):
                            min_dist = dist
                            best_snap_end = s_end

            if best_snap_end is not None:
                new_dur = round(best_snap_end - scene["start"], 2)
                # Only snap if it doesn't violate minimum duration
                if new_dur >= min(self.min_duration, 45.0) or len(scenes) == 1:
                    scene["end"] = round(best_snap_end, 2)
                    scene["duration"] = new_dur

                    # If there is a next scene, align its start to avoid overlap
                    if i + 1 < len(scenes):
                        scenes[i + 1]["start"] = scene["end"]
                        scenes[i + 1]["duration"] = round(scenes[i + 1]["end"] - scenes[i + 1]["start"], 2)

        return scenes

    def merge(self, scenes, transcript=None):
        """
        Merge adjacent scenes so that all clips have genuine, legitimate durations.
        Enforces a 60s+ minimum clip duration floor.
        """
        merged = []

        if not scenes:
            return merged

        # If only 1 scene exists, check duration
        if len(scenes) == 1:
            dur = scenes[0]["end"] - scenes[0]["start"]
            merged.append({
                "start": round(scenes[0]["start"], 2),
                "end": round(scenes[0]["end"], 2),
                "duration": round(dur, 2)
            })
            if transcript:
                merged = self.snap_to_sentence_boundaries(merged, transcript)
            return merged

        current_start = scenes[0]["start"]
        current_end = scenes[0]["end"]

        for scene in scenes[1:]:
            current_duration = current_end - current_start

            # Keep expanding current clip until target minimum duration (60s+) is reached
            if current_duration < self.min_duration:
                current_end = scene["end"]
                continue

            # If current clip would become too long if we add more, close it
            merged.append({
                "start": round(current_start, 2),
                "end": round(current_end, 2),
                "duration": round(current_end - current_start, 2)
            })

            current_start = scene["start"]
            current_end = scene["end"]

        # Handle the trailing / last segment
        if current_end > current_start:
            last_duration = current_end - current_start

            if merged:
                # If last segment is below minimum legitimate duration, merge with previous clip
                if last_duration < self.abs_min_duration:
                    prev = merged[-1]
                    # If merging doesn't excessively blow up max duration, merge it
                    if (current_end - prev["start"]) <= (self.max_duration + 30.0):
                        prev["end"] = round(current_end, 2)
                        prev["duration"] = round(current_end - prev["start"], 2)
                    else:
                        # If previous clip is already near max, and last segment is very tiny (<10s),
                        # absorb it into previous clip anyway to avoid producing an orphan micro-clip.
                        if last_duration < 15.0:
                            prev["end"] = round(current_end, 2)
                            prev["duration"] = round(current_end - prev["start"], 2)
                        else:
                            merged.append({
                                "start": round(current_start, 2),
                                "end": round(current_end, 2),
                                "duration": round(last_duration, 2)
                            })
                else:
                    merged.append({
                        "start": round(current_start, 2),
                        "end": round(current_end, 2),
                        "duration": round(last_duration, 2)
                    })
            else:
                # No previous clip was merged yet
                merged.append({
                    "start": round(current_start, 2),
                    "end": round(current_end, 2),
                    "duration": round(last_duration, 2)
                })

        # Apply sentence boundary snapping if transcript is provided
        if transcript:
            merged = self.snap_to_sentence_boundaries(merged, transcript)

        return merged