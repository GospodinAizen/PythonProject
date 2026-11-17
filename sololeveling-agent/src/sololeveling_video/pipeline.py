from __future__ import annotations

import logging
import time
from dataclasses import asdict
from pathlib import Path

import cv2

from .config import PipelineConfig, RunPaths
from .models import CandidateEvent, FrameObservation
from .storage import ExperienceStore, append_jsonl, write_json
from .video import inspect_video, iter_sampled_frames
from .vision import color_histogram, difference_hash, hash_distance, scene_difference

log = logging.getLogger(__name__)


def run_pipeline(
    video_path: Path, output_dir: Path, config: PipelineConfig | None = None
) -> dict:
    config = config or PipelineConfig()
    config.validate()
    paths = RunPaths.create(output_dir)
    capture, info = inspect_video(video_path)
    store = ExperienceStore(paths.database)
    started = time.monotonic()

    kept = 0
    candidate_events = 0
    event_id = 0
    last_saved_time = -config.min_frame_gap_seconds
    last_saved_hash: int | None = None
    previous_hist = None
    next_periodic_time = 0.0

    write_json(paths.metadata, {
        "video": asdict(info), "pipeline_version": "0.1.0", "config": asdict(config)
    })
    store.add_session(info)

    try:
        with paths.observations.open("w", encoding="utf-8") as obs_file, \
             paths.events.open("w", encoding="utf-8") as event_file:
            for source_frame, timestamp, frame in iter_sampled_frames(
                capture, info.fps, config.analysis_fps
            ):
                histogram = color_histogram(frame)
                current_hash = difference_hash(frame)
                score = scene_difference(previous_hist, histogram)
                changed = previous_hist is not None and score >= config.scene_threshold
                duplicate = (
                    last_saved_hash is not None
                    and hash_distance(last_saved_hash, current_hash) <= config.duplicate_threshold
                )
                periodic_due = timestamp + 1e-6 >= next_periodic_time
                gap_ok = timestamp - last_saved_time >= config.min_frame_gap_seconds

                if periodic_due:
                    next_periodic_time += 1.0 / config.sample_fps

                if gap_ok and ((periodic_due and not duplicate) or changed):
                    reason = "scene_change" if changed else "periodic_sample"
                    frame_id = kept
                    filename = f"frame_{frame_id:07d}_{timestamp:010.3f}.jpg"
                    target = paths.frames / filename
                    written = cv2.imwrite(
                        str(target), frame,
                        [cv2.IMWRITE_JPEG_QUALITY, config.jpeg_quality],
                    )
                    if not written:
                        raise OSError(f"Could not write frame: {target}")

                    item = FrameObservation(
                        frame_id, round(timestamp, 3), source_frame, filename,
                        reason, round(score, 6), f"{current_hash:016x}",
                    )
                    store.add_observation(item)
                    append_jsonl(obs_file, item.to_dict())
                    kept += 1
                    last_saved_time = timestamp
                    last_saved_hash = current_hash

                    if changed:
                        event = CandidateEvent(
                            event_id, round(timestamp, 3), "visual_change_candidate",
                            round(score, 6), frame_id,
                            f"HSV histogram distance={score:.5f}",
                        )
                        store.add_event(event)
                        append_jsonl(event_file, event.to_dict())
                        event_id += 1
                        candidate_events += 1

                previous_hist = histogram

                if source_frame and source_frame % max(1, int(info.fps * 30)) == 0:
                    log.info(
                        "Progress %.1f%% | frames %d | candidate events %d",
                        timestamp / info.duration_seconds * 100, kept, candidate_events,
                    )
        store.commit()
    finally:
        capture.release()
        store.close()

    elapsed = time.monotonic() - started
    report = {
        "status": "completed", "source": info.source,
        "duration_seconds": info.duration_seconds,
        "source_resolution": f"{info.width}x{info.height}",
        "source_fps": info.fps, "frames_saved": kept,
        "candidate_events": candidate_events,
        "processing_seconds": round(elapsed, 3),
        "output_directory": str(paths.root.resolve()),
        "artifacts": {
            "frames": str(paths.frames), "observations": str(paths.observations),
            "events": str(paths.events), "sqlite": str(paths.database),
            "metadata": str(paths.metadata),
        },
        "limitations": [
            "Visual-change candidates are not semantic event labels.",
            "Video-only observations cannot uniquely recover keyboard or mouse inputs.",
            "Camera motion and combat effects can trigger scene-change candidates.",
        ],
    }
    write_json(paths.report, report)
    log.info("Finished: %d frames, %d candidate events in %.1fs",
             kept, candidate_events, elapsed)
    return report
