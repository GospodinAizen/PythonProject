import logging
from pathlib import Path

import cv2

from video_learning.models import VideoMetadata

log = logging.getLogger(__name__)


class VideoSource:
    """Context-managed sequential decoder. Always releases the native capture."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.capture: cv2.VideoCapture | None = None
        self.metadata: VideoMetadata | None = None

    def __enter__(self) -> "VideoSource":
        if not self.path.is_file():
            raise FileNotFoundError(f"Video does not exist: {self.path}")
        cap = cv2.VideoCapture(str(self.path))
        if not cap.isOpened():
            cap.release()
            raise RuntimeError(f"OpenCV cannot open video: {self.path}")
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if width <= 0 or height <= 0 or fps <= 0 or count <= 0:
            cap.release()
            raise RuntimeError("Video metadata is invalid or unsupported")
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec = "".join(chr((fourcc >> (8 * i)) & 255) for i in range(4)).strip()
        self.capture = cap
        self.metadata = VideoMetadata(
            source=str(self.path.resolve()), width=width, height=height,
            fps=fps, frame_count=count, duration_seconds=count / fps,
            codec=codec or None,
        )
        log.info("Input: %dx%d @ %.3f FPS; %.1fs", width, height, fps, count / fps)
        return self

    def read(self):
        if self.capture is None:
            raise RuntimeError("VideoSource is not open")
        ok, frame = self.capture.read()
        return frame if ok else None

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.capture is not None:
            self.capture.release()
            self.capture = None
