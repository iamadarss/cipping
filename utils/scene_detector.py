from pathlib import Path
import time

from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector


class ProgressSceneManager(SceneManager):
    """
    Extended SceneManager that notifies a progress_callback periodically
    with current video time (seconds) and the number of scenes detected so far.
    """
    def __init__(self, progress_callback=None, report_interval=5.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.progress_callback = progress_callback
        self.report_interval = report_interval
        self._last_report = -report_interval

    def _process_frame(self, position, frame_im, callback):
        cuts = super()._process_frame(position, frame_im, callback)
        if self.progress_callback and position is not None:
            try:
                curr_sec = position.seconds if hasattr(position, "seconds") else position.get_seconds()
                if curr_sec - self._last_report >= self.report_interval:
                    self._last_report = curr_sec
                    cuts_count = len(self._cutting_list) if hasattr(self, "_cutting_list") else 0
                    self.progress_callback(curr_sec, cuts_count)
            except Exception:
                pass
        return cuts


class SceneDetector:

    def __init__(self, video_path):
        self.video_path = Path(video_path)

    def detect_scenes(self, threshold=27.0, progress_callback=None, frame_skip=1):
        """
        Detect scenes using PySceneDetect with real-time progress callbacks and frame skip optimization.

        Args:
            threshold: Scene change threshold (default: 27.0)
            progress_callback: Callable(curr_seconds, cuts_count)
            frame_skip: Frames to skip between evaluations (default: 1 for 2x faster detection)
        """
        video = open_video(str(self.video_path))
        scene_manager = ProgressSceneManager(progress_callback=progress_callback, report_interval=5.0)

        scene_manager.add_detector(
            ContentDetector(threshold=threshold)
        )

        scene_manager.detect_scenes(video, frame_skip=frame_skip)

        scene_list = scene_manager.get_scene_list()

        scenes = []

        for scene in scene_list:
            start = scene[0].seconds if hasattr(scene[0], "seconds") else scene[0].get_seconds()
            end = scene[1].seconds if hasattr(scene[1], "seconds") else scene[1].get_seconds()

            scenes.append(
                {
                    "start": start,
                    "end": end,
                    "duration": end - start
                }
            )

        return scenes