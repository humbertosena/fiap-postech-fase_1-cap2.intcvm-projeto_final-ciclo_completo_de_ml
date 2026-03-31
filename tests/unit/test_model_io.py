from __future__ import annotations

from pathlib import Path

from src.models.io import load_json, load_model, save_model, write_json


def test_model_roundtrip(tmp_path: Path) -> None:
    payload = {"status": "ok"}
    path = tmp_path / "model.joblib"
    save_model(payload, path)
    loaded = load_model(path)
    assert loaded == payload



def test_write_json_roundtrip(tmp_path: Path) -> None:
    payload = {"status": "ok"}
    path = tmp_path / "payload.json"
    write_json(payload, path)
    assert load_json(path) == payload
