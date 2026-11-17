import argparse
import logging
from pathlib import Path

from video_learning.config import PipelineConfig
from video_learning.pipeline import run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="SoloLeveling video learning pipeline")
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=Path("dataset/session_001"))
    parser.add_argument("--sample-fps", type=float, default=2.0)
    parser.add_argument("--scene-threshold", type=float, default=0.30)
    parser.add_argument("--min-frame-gap", type=float, default=0.20)
    parser.add_argument("--duplicate-distance", type=int, default=3)
    parser.add_argument("--jpeg-quality", type=int, default=94)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    config = PipelineConfig(
        sample_fps=args.sample_fps, scene_threshold=args.scene_threshold,
        min_frame_gap_seconds=args.min_frame_gap,
        duplicate_hash_distance=args.duplicate_distance, jpeg_quality=args.jpeg_quality,
    )
    try:
        report = run_pipeline(args.video, args.output, config)
    except (OSError, RuntimeError, ValueError) as exc:
        logging.error("%s", exc)
        return 2
    logging.info("Retained frames: %d", report["results"]["retained_frames"])
    logging.info("Report: %s", (args.output / "report.json").resolve())
    return 0
