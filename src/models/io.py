from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib


def save_model(model: Any, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    return path



def load_model(path: Path) -> Any:
    return joblib.load(path)



def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))



def write_json(payload: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path



def write_model_metadata(metadata: dict[str, Any], path: Path) -> Path:
    return write_json(metadata, path)
