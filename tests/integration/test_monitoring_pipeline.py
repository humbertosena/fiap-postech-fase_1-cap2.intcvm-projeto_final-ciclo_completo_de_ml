from __future__ import annotations

import json
from pathlib import Path

from src.config import settings
from src.monitoring.run_monitoring import run_monitoring
from src.monitoring.store import read_jsonl
from src.serving.app import create_app
from src.serving.model_store import LoadedApprovedModel


def test_run_monitoring_generates_reports(
    approved_model_bundle: LoadedApprovedModel,
    valid_prediction_payload: dict[str, object],
    monkeypatch,
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "latest_approved_model.json"
    api_events_path = tmp_path / "api_events.jsonl"
    inference_events_path = tmp_path / "inference_events.jsonl"
    monitoring_artifact_dir = tmp_path / "monitoring"

    manifest_payload = {
        "run_id": approved_model_bundle.run_id,
        "run_label": approved_model_bundle.run_label,
        "model_name": approved_model_bundle.model_name,
        "model_path": str(approved_model_bundle.model_path),
        "project_relative_model_path": str(approved_model_bundle.model_path),
        "monitoring_reference_path": str(approved_model_bundle.monitoring_reference_path),
        "project_relative_monitoring_reference_path": str(
            approved_model_bundle.monitoring_reference_path
        ),
        "model_metadata": {"decision_threshold": approved_model_bundle.decision_threshold},
        "metrics": {"decision_threshold": approved_model_bundle.decision_threshold},
    }
    manifest_path.write_text(json.dumps(manifest_payload), encoding="utf-8")

    monkeypatch.setattr("src.serving.monitoring.get_api_events_path", lambda: api_events_path)
    monkeypatch.setattr(
        "src.serving.monitoring.get_inference_events_path",
        lambda: inference_events_path,
    )
    monkeypatch.setattr(
        "src.monitoring.run_monitoring.get_api_events_path",
        lambda: api_events_path,
    )
    monkeypatch.setattr(
        "src.monitoring.run_monitoring.get_inference_events_path",
        lambda: inference_events_path,
    )
    monkeypatch.setattr("src.serving.model_store.get_approved_manifest_path", lambda: manifest_path)

    original_monitoring_artifact_dir = settings.monitoring_artifact_dir
    object.__setattr__(settings, "monitoring_artifact_dir", monitoring_artifact_dir)
    try:
        app = create_app(model_loader=lambda: approved_model_bundle)
        client = app.test_client()
        client.post("/predict", json=valid_prediction_payload)
        client.post("/predict", json=valid_prediction_payload)

        report = run_monitoring(log_to_mlflow=False)

        assert report["operational_summary"]["prediction_count"] == 2
        assert Path(report["event_paths"]["api_events_path"]) == api_events_path
        assert Path(report["event_paths"]["inference_events_path"]) == inference_events_path
        assert read_jsonl(api_events_path)
        assert read_jsonl(inference_events_path)
        assert report["triggers"]["status"] in {"healthy", "retraining_recommended"}
    finally:
        object.__setattr__(settings, "monitoring_artifact_dir", original_monitoring_artifact_dir)
