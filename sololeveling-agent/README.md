# SoloLeveling Agent — Video Learning

A local-first, video-only experience extraction toolkit for Minecraft Java 1.8.8 recordings.

**Scope:** analyzes recordings only. It does not connect to Minecraft, send inputs, automate gameplay, or interact with a game server.

## Features
- Source metadata and frame-accurate timestamps.
- Configurable periodic sampling plus visual-change keyframes.
- Near-duplicate suppression using difference hash.
- SQLite index, JSONL observations/events, and run report.
- Modular design ready for OCR, object detection, and event inference.

## Requirements
Python 3.10+, OpenCV, NumPy, PyYAML.

## Install (Windows 11 / PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Run
```powershell
python -m sololeveling_video --video recordings/session.mp4
```

Optional:
```powershell
python -m sololeveling_video --video recordings/session.mp4 --output dataset/session_001 --sample-fps 2 --analysis-fps 5 --scene-threshold 0.34
```

## Output
- frames/: retained JPEG keyframes
- video_info.json: source metadata and config
- observations.jsonl: timestamped frame records
- events.jsonl: visual-change candidates
- experience.sqlite3: queryable index
- report.json: processing summary and limitations

## Interpretation limits
This is visual observation, not behavioral cloning. Video alone cannot uniquely reveal keyboard/mouse inputs, exact world coordinates, or intent. A visual-change candidate is not a semantic event. OCR, object detection, and verified labels are later milestones.

## Development
```powershell
pytest
ruff check .
```

See docs/architecture.md for design details.
