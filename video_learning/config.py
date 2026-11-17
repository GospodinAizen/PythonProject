from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    sample_fps: float = 2.0
    scene_threshold: float = 0.30
    min_frame_gap_seconds: float = 0.20
    duplicate_hash_distance: int = 3
    signature_width: int = 160
    signature_height: int = 90
    jpeg_quality: int = 94
    log_every_seconds: float = 30.0

    def validate(self) -> None:
        if self.sample_fps <= 0:
            raise ValueError("sample_fps must be > 0")
        if not 0 < self.scene_threshold <= 1:
            raise ValueError("scene_threshold must be in (0, 1]")
        if self.min_frame_gap_seconds < 0:
            raise ValueError("min_frame_gap_seconds must be >= 0")
        if not 0 <= self.duplicate_hash_distance <= 64:
            raise ValueError("duplicate_hash_distance must be in [0, 64]")
        if min(self.signature_width, self.signature_height) < 16:
            raise ValueError("signature dimensions must be >= 16")
        if not 1 <= self.jpeg_quality <= 100:
            raise ValueError("jpeg_quality must be in [1, 100]")
        if self.log_every_seconds <= 0:
            raise ValueError("log_every_seconds must be > 0")
