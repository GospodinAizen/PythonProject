# SoloLeveling Video Learning Engine

Модульный offline-first конвейер анализа записей Minecraft Java 1.8.8 (OBS, 1920×1080/60 FPS). Первая версия извлекает ключевые кадры, ищет визуальные изменения, удаляет почти одинаковые изображения и сохраняет наблюдения в JSONL и SQLite.

> Важно: смена изображения — только визуальный кандидат, а не доказательство события. По одному видео нельзя надёжно восстановить нажатые клавиши, намерение или точные 3D-координаты.

## Быстрый старт (Windows 11 / PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
python -m video_learning --video recordings\session.mp4 --output dataset\session_001
```

Положи исходные видео в `recordings/` (они исключены из Git). Результаты записываются в `dataset/` (тоже исключена из Git).

## Параметры

```powershell
python -m video_learning --help
python -m video_learning --video recordings\session.mp4 --output dataset\test --sample-fps 2 --scene-threshold 0.30 --jpeg-quality 94
pytest
```

- Декодирование идёт последовательно, чтобы не полагаться на неточные seek-позиции MP4.
- `sample-fps` задаёт частоту анализа, а не исходную частоту видео.
- Гистограмма HSV оценивает визуальную разницу; dHash фильтрует почти одинаковые кадры.
- SQLite хранит индексированные наблюдения; JSONL удобен для последующей пакетной обработки.

## Структура

- `video_learning/config.py` — настройки и валидация
- `video_learning/video.py` — безопасное открытие и декодирование
- `video_learning/vision.py` — визуальные сигнатуры и сравнение
- `video_learning/storage.py` — JSONL + SQLite
- `video_learning/pipeline.py` — конвейер
- `video_learning/cli.py` — CLI
- `tests/` — тесты

## Дальнейшие этапы

1. OCR по областям интерфейса (диалоги, названия мобов, HP, инвентарь).
2. Детекция NPC/мобов и трекинг объектов.
3. Извлечение событий с разделением фактов и гипотез и оценкой уверенности.
4. База знаний квестов, предметов, локаций и маршрутов.

Используй автоматизацию только там, где она разрешена правилами сервера. Этот репозиторий анализирует записи и не содержит обхода античита.
