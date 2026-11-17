from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    sample_fps: float = 2.0
    analysis_fps: float = 5.0
    scene_threshold: float = 0.34
    duplicate_threshold: int = 5
    min_frame_gap_seconds: float = 0.20
    jpeg_quality: int = 94

    def validate(self) -> None:
        if self.sample_fps <= 0 or self.analysis_fps <= 0:
            raise ValueError("Sampling rates must be positive")
        if self.analysis_fps < self.sample_fps:
            raise ValueError("analysis_fps must be >= sample_fps")
        if not 0 < self.scene_threshold < 1:
            raise ValueError("scene_threshold must be between 0 and 1")
        if not 0 <= self.duplicate_threshold <= 64:
            raise ValueError("duplicate_threshold must be in [0, 64]")
        if self.min_frame_gap_seconds < 0:
            raise ValueError("min_frame_gap_seconds cannot be negative")
        if not 1 <= self.jpeg_quality <= 100:
            raise ValueError("jpeg_quality must be in [1, 100]")


@dataclass(frozen=True, slots=True)
class RunPaths:
    root: Path
    frames: Path
    observations: Path
    events: Path
    database: Path
    metadata: Path
    report: Path

    @classmethod
    def create(cls, root: Path) -> "RunPaths":
        root.mkdir(parents=True, exist_ok=True)
        frames = root / "frames"
        frames.mkdir(parents=True, exist_ok=True)
        return cls(root, frames, root / "observations.jsonl",
                   root / "events.jsonl", root / "experience.sqlite3",
                   root / "video_info.json", root / "report.json")
