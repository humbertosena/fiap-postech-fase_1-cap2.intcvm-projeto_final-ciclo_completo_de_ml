from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def write_json(payload: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def write_text(content: str, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def write_confusion_matrix_csv(matrix: Any, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(
        matrix,
        index=["actual_0", "actual_1"],
        columns=["pred_0", "pred_1"],
    )
    frame.to_csv(path, index=True)
    return path
