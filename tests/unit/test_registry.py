from __future__ import annotations

import json
from pathlib import Path

from src.config import settings
from src.models.registry import register_model_candidate


def test_register_model_candidate_writes_manifests(tmp_path: Path) -> None:
    original_registry_dir = settings.model_registry_dir
    object.__setattr__(settings, "model_registry_dir", tmp_path / "registry")
    try:
        metadata_path = tmp_path / "model_metadata.json"
        metadata_path.write_text(json.dumps({"dataset_hash": "abc123"}), encoding="utf-8")
        monitoring_reference_path = tmp_path / "monitoring_reference.json"
        monitoring_reference_path.write_text("{}", encoding="utf-8")

        training_result = {
            "run_id": "run-123",
            "run_label": "20260324T220000Z",
            "model_name": "logistic_regression",
            "metrics": {
                "recall": 0.8571,
                "precision": 0.7059,
                "decision_threshold": 0.35,
            },
            "fairness": {
                "summary": {
                    "alert_count": 1,
                    "groups_with_alerts": ["sex"],
                    "limited_confidence_groups": [],
                }
            },
            "artifacts": {
                "artifact_dir": str(tmp_path / "artifacts"),
                "model_path": str(tmp_path / "training_pipeline.joblib"),
                "model_metadata_path": str(metadata_path),
                "monitoring_reference_path": str(monitoring_reference_path),
            },
        }
        gate_report = {
            "status": "approved_with_alerts",
            "summary": {
                "promotion_eligible": True,
                "blocking_failures": 0,
                "active_alerts": 1,
            },
        }
        gate_report_path = tmp_path / "release_gate_report.json"
        gate_report_path.write_text(json.dumps(gate_report), encoding="utf-8")

        result = register_model_candidate(training_result, gate_report, gate_report_path)

        candidate_manifest = Path(str(result["candidate_manifest_path"]))
        approved_manifest = Path(str(result["approved_manifest_path"]))
        assert candidate_manifest.exists()
        assert approved_manifest.exists()
        assert result["promoted"] is True

        payload = json.loads(approved_manifest.read_text(encoding="utf-8"))
        assert payload["run_id"] == "run-123"
        assert payload["model_metadata"]["dataset_hash"] == "abc123"
        assert payload["monitoring_reference_path"] == str(monitoring_reference_path)
    finally:
        object.__setattr__(settings, "model_registry_dir", original_registry_dir)
