# Architecture

## Data flow

OBS recording -> sequential decoder -> analysis cadence -> visual signatures -> periodic/keyframe selection -> JPEG + JSONL + SQLite + report.

## Responsibilities
- Ingestion owns source metadata and source timestamps.
- Vision primitives produce numerical similarity scores, not semantic labels.
- Pipeline coordinates extraction and persistence.
- Storage keeps an auditable record of observations.
- Future OCR and object detectors should emit evidence-backed observations, not game commands.
- Event inference must distinguish observed, inferred, and unknown, and attach confidence plus source frame references.

## Sampling
A 60 FPS recording is decoded sequentially. Visual analysis defaults to 5 FPS; periodic retention defaults to 2 FPS. Significant visual changes may add keyframes. This is a practical compromise, not a guarantee that every brief event is captured.

## Scene-change limitations
Histogram distance can rise because of camera rotation, particles, combat effects, lighting, UI overlays, or a real scene transition. Never label a candidate as NPC interaction or quest completion without dedicated OCR/detection evidence.

## Video-only limitation
A screen recording does not uniquely identify key presses, mouse buttons, exact world position, or intention. Route learning should use stable visual landmarks and uncertainty-aware relative motion rather than pretending to recover hidden game state.

## Milestones
1. Contact sheets and human review of keyframes.
2. OCR for dialogue, mob name/HP labels, inventory stats, and server notifications.
3. NPC/mob detection and object tracking.
4. Verified event graph with confidence and provenance.
5. Persistent quest, item-evaluation, mob-location, and route knowledge.
