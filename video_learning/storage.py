import json
import sqlite3
from pathlib import Path

from video_learning.models import FrameObservation


class ObservationStore:
    """Write observations to append-friendly JSONL and indexed SQLite."""

    def __init__(self, jsonl_path: Path, database_path: Path) -> None:
        self.connection = sqlite3.connect(database_path)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS observations (
                frame_id INTEGER PRIMARY KEY,
                timestamp_seconds REAL NOT NULL,
                source_frame_number INTEGER NOT NULL,
                filename TEXT NOT NULL,
                reason TEXT NOT NULL,
                scene_difference REAL NOT NULL,
                perceptual_hash TEXT NOT NULL
            )"""
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_observation_time "
            "ON observations(timestamp_seconds)"
        )
        self.connection.commit()
        self.jsonl = jsonl_path.open("w", encoding="utf-8")

    def add(self, item: FrameObservation) -> None:
        data = item.to_dict()
        self.jsonl.write(json.dumps(data, ensure_ascii=False) + "\n")
        self.connection.execute(
            "INSERT INTO observations VALUES (?, ?, ?, ?, ?, ?, ?)",
            (item.frame_id, item.timestamp_seconds, item.source_frame_number,
             item.filename, item.reason, item.scene_difference, item.perceptual_hash),
        )
        self.connection.commit()

    def close(self) -> None:
        if not self.jsonl.closed:
            self.jsonl.flush()
            self.jsonl.close()
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
