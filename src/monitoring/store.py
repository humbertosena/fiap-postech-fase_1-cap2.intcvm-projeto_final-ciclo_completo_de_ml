from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.config import settings

API_EVENTS_FILE_NAME = "api_events.jsonl"
INFERENCE_EVENTS_FILE_NAME = "inference_events.jsonl"


def ensure_monitoring_dirs() -> None:
    settings.monitoring_artifact_dir.mkdir(parents=True, exist_ok=True)
    settings.monitoring_event_dir.mkdir(parents=True, exist_ok=True)



def get_api_events_path() -> Path:
    ensure_monitoring_dirs()
    return settings.monitoring_event_dir / API_EVENTS_FILE_NAME



def get_inference_events_path() -> Path:
    ensure_monitoring_dirs()
    return settings.monitoring_event_dir / INFERENCE_EVENTS_FILE_NAME



def append_jsonl(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, sort_keys=True))
        stream.write("\n")
    return path



def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped:
            rows.append(json.loads(stripped))
    return rows
