from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import cv2
import numpy as np

from .models import VideoInfo


class VideoReadError(RuntimeError):
    """Raised when a source video cannot be inspected or decoded."""


def inspect_video(path: Path) -> tuple[cv2.VideoCapture, VideoInfo]:
    if not path.is_file():
        raise FileNotFoundError(f"Video does not exist: {path}")

    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        capture.release()
        raise VideoReadError(f"OpenCV could not open: {path}")

    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = float(capture.get(cv2.CAP_PROP_FPS))
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fourcc = int(capture.get(cv2.CAP_PROP_FOURCC))

    if width <= 0 or height <= 0 or fps <= 0 or frame_count <= 0:
        capture.release()
        raise VideoReadError("Video metadata is incomplete or invalid")

    codec = "".join(chr((fourcc >> (8 * i)) & 255) for i in range(4)).strip()
    info = VideoInfo(
        source=str(path.resolve()), width=width, height=height, fps=fps,
        frame_count=frame_count, duration_seconds=frame_count / fps,
        codec=codec or "unknown",
    )
    return capture, info


def iter_sampled_frames(
    capture: cv2.VideoCapture, fps: float, analysis_fps: float
) -> Iterator[tuple[int, float, np.ndarray]]:
    """Decode sequentially and yield at a stable source-frame cadence."""
    stride = max(1, round(fps / analysis_fps))
    frame_number = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        if frame_number % stride == 0:
            yield frame_number, frame_number / fps, frame
        frame_number += 1
