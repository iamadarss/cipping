import subprocess
import config


def check_ffmpeg():
    """
    Check whether FFmpeg executable is available.
    """

    try:

        result = subprocess.run(
            [config.FFMPEG_PATH, "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        version = result.stdout.splitlines()[0]

        return True, version

    except Exception as e:

        return False, str(e)


def generate_thumbnail(video_path, thumb_path):
    """
    Generate a video thumbnail using FFmpeg with robust fallback.
    """
    from pathlib import Path
    video_path = Path(video_path)
    thumb_path = Path(thumb_path)
    thumb_path.parent.mkdir(parents=True, exist_ok=True)

    if not video_path.exists():
        return False

    cmd = [
        config.FFMPEG_PATH,
        "-y",
        "-ss", "00:00:01",
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "2",
        str(thumb_path),
    ]

    try:
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        if thumb_path.exists() and thumb_path.stat().st_size > 0:
            return True

        # Fallback to 00:00:00 if video is shorter than 1 second
        cmd[2] = "00:00:00"
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        return thumb_path.exists() and thumb_path.stat().st_size > 0
    except Exception:
        return False