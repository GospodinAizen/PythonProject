from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import CandidateEvent, FrameObservation, VideoInfo


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(handle, value: dict[str, Any]) -> None:
    handle.write(json.dumps(value, ensure_ascii=False) + "\n")


class ExperienceStore:
    def __init__(self, database_path: Path) -> None:
        self.connection = sqlite3.connect(database_path)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS video_sessions (
                id INTEGER PRIMARY KEY, source TEXT NOT NULL, width INTEGER NOT NULL,
                height INTEGER NOT NULL, fps REAL NOT NULL, frame_count INTEGER NOT NULL,
                duration_seconds REAL NOT NULL, codec TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS observations (
                frame_id INTEGER PRIMARY KEY,
                session_id INTEGER NOT NULL REFERENCES video_sessions(id),
                timestamp_seconds REAL NOT NULL, source_frame_number INTEGER NOT NULL,
                filename TEXT NOT NULL, reason TEXT NOT NULL, scene_score REAL NOT NULL,
                difference_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS candidate_events (
                event_id INTEGER PRIMARY KEY,
                session_id INTEGER NOT NULL REFERENCES video_sessions(id),
                timestamp_seconds REAL NOT NULL, event_type TEXT NOT NULL,
                score REAL NOT NULL,
                frame_id INTEGER NOT NULL REFERENCES observations(frame_id),
                evidence TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_observations_time
                ON observations(timestamp_seconds);
            CREATE INDEX IF NOT EXISTS idx_events_time
                ON candidate_events(timestamp_seconds);
        """)
        self.connection.commit()
        self.session_id: int | None = None

    def add_session(self, info: VideoInfo) -> int:
        cursor = self.connection.execute(
            """INSERT INTO video_sessions
            (source, width, height, fps, frame_count, duration_seconds, codec)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (info.source, info.width, info.height, info.fps, info.frame_count,
             info.duration_seconds, info.codec),
        )
        self.session_id = int(cursor.lastrowid)
        self.connection.commit()
        return self.session_id

    def add_observation(self, item: FrameObservation) -> None:
        if self.session_id is None:
            raise RuntimeError("Create a session before adding observations")
        self.connection.execute(
            """INSERT INTO observations
            (frame_id, session_id, timestamp_seconds, source_frame_number,
             filename, reason, scene_score, difference_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (item.frame_id, self.session_id, item.timestamp_seconds,
             item.source_frame_number, item.filename, item.reason,
             item.scene_score, item.difference_hash),
        )

    def add_event(self, item: CandidateEvent) -> None:
        if self.session_id is None:
            raise RuntimeError("Create a session before adding events")
        self.connection.execute(
            """INSERT INTO candidate_events
            (event_id, session_id, timestamp_seconds, event_type, score, frame_id, evidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (item.event_id, self.session_id, item.timestamp_seconds,
             item.event_type, item.score, item.frame_id, item.evidence),
        )

    def commit(self) -> None:
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()
