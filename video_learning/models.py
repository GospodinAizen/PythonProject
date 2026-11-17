from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class VideoMetadata:
    source: str
    width: int
    height: int
    fps: float
    frame_count: int
    duration_seconds: float
    codec: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FrameObservation:
    frame_id: int
    timestamp_seconds: float
    source_frame_number: int
    filename: str
    reason: str
    scene_difference: float
    perceptual_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
