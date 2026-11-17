from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from .config import PipelineConfig
from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sl-video",
        description="Extract timestamped visual observations from gameplay recordings.",
    )
    parser.add_argument("--video", required=True, type=Path, help="Input OBS video")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--sample-fps", type=float, default=2.0)
    parser.add_argument("--analysis-fps", type=float, default=5.0)
    parser.add_argument("--scene-threshold", type=float, default=0.34)
    parser.add_argument("--duplicate-threshold", type=int, default=5)
    parser.add_argument("--jpeg-quality", type=int, default=94)
    parser.add_argument("--verbose", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    output = args.output or Path("dataset") / args.video.stem
    config = PipelineConfig(
        sample_fps=args.sample_fps, analysis_fps=args.analysis_fps,
        scene_threshold=args.scene_threshold,
        duplicate_threshold=args.duplicate_threshold,
        jpeg_quality=args.jpeg_quality,
    )
    try:
        report = run_pipeline(args.video, output, config)
    except (OSError, ValueError, RuntimeError) as exc:
        logging.error("%s", exc)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0
