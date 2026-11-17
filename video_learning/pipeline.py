from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2

from video_learning.config import PipelineConfig
from video_learning.models import FrameObservation
from video_learning.storage import ObservationStore
from video_learning.video import VideoSource
from video_learning.vision import hash_distance, histogram_distance, visual_signature

log = logging.getLogger(__name__)


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def run_pipeline(video_path: Path, output_dir: Path,
                 config: PipelineConfig | None = None) -> dict:
    config = config or PipelineConfig()
    config.validate()
    output_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(exist_ok=True)
    jsonl_path = output_dir / "observations.jsonl"
    db_path = output_dir / "observations.sqlite3"
    started = time.perf_counter()

    with VideoSource(video_path) as source:
        meta = source.metadata
        assert meta is not None
        _write_json(output_dir / "video_info.json", meta.to_dict())

        interval = 1.0 / config.sample_fps
        next_sample = 0.0
        previous_hist = previous_hash = None
        last_saved = float("-inf")
        decoded = saved = scene_candidates = duplicates = 0
        last_log = 0.0

        with ObservationStore(jsonl_path, db_path) as store:
            while True:
                frame = source.read()
                if frame is None:
                    break
                timestamp = decoded / meta.fps
                if timestamp + 1e-9 >= next_sample:
                    next_sample += interval
                    hist, phash, hash_hex = visual_signature(
                        frame, config.signature_width, config.signature_height
                    )
                    score = histogram_distance(previous_hist, hist)
                    scene_change = previous_hist is not None and score >= config.scene_threshold
                    duplicate = hash_distance(previous_hash, phash) <= config.duplicate_hash_distance
                    gap_ok = timestamp - last_saved >= config.min_frame_gap_seconds

                    if not duplicate and gap_ok:
                        reason = "scene_change" if scene_change else "periodic_sample"
                        filename = f"frame_{saved:06d}_{timestamp:010.3f}.jpg"
                        destination = frames_dir / filename
                        if not cv2.imwrite(str(destination), frame,
                                           [cv2.IMWRITE_JPEG_QUALITY, config.jpeg_quality]):
                            raise RuntimeError(f"Could not write frame: {destination}")
                        store.add(FrameObservation(
                            frame_id=saved, timestamp_seconds=round(timestamp, 3),
                            source_frame_number=decoded, filename=filename,
                            reason=reason, scene_difference=round(score, 6),
                            perceptual_hash=hash_hex,
                        ))
                        saved += 1
                        last_saved = timestamp
                        scene_candidates += int(scene_change)
                    else:
                        duplicates += int(duplicate)
                    previous_hist, previous_hash = hist, phash

                decoded += 1
                if timestamp - last_log >= config.log_every_seconds:
                    log.info("Progress %.1f%% | retained %d",
                             min(100.0, timestamp / meta.duration_seconds * 100), saved)
                    last_log = timestamp

        elapsed = time.perf_counter() - started
        report = {
            "schema_version": 1,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "input": meta.to_dict(),
            "config": {
                "sample_fps": config.sample_fps,
                "scene_threshold": config.scene_threshold,
                "min_frame_gap_seconds": config.min_frame_gap_seconds,
                "duplicate_hash_distance": config.duplicate_hash_distance,
                "jpeg_quality": config.jpeg_quality,
            },
            "results": {
                "decoded_frames": decoded, "retained_frames": saved,
                "candidate_scene_changes": scene_candidates,
                "near_duplicate_skips": duplicates,
                "processing_seconds": round(elapsed, 3),
            },
            "artifacts": {
                "frames": str(frames_dir), "jsonl": str(jsonl_path),
                "sqlite": str(db_path), "video_info": str(output_dir / "video_info.json"),
            },
            "caveat": "Visual changes are candidates, not semantic actions or scene labels.",
        }
        _write_json(output_dir / "report.json", report)
        log.info("Done: retained %d of %d decoded frames in %.1fs", saved, decoded, elapsed)
        return report
