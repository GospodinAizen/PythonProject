from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class VideoInfo:
    source: str
    width: int
    height: int
    fps: float
    frame_count: int
    duration_seconds: float
    codec: str


@dataclass(frozen=True, slots=True)
class FrameObservation:
    frame_id: int
    timestamp_seconds: float
    source_frame_number: int
    filename: str
    reason: str
    scene_score: float
    difference_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CandidateEvent:
    event_id: int
    timestamp_seconds: float
    event_type: str
    score: float
    frame_id: int
    evidence: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
