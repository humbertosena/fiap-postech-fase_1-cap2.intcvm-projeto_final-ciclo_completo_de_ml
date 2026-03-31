from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.config import settings

LATEST_CANDIDATE_NAME = "latest_candidate.json"
APPROVED_MODEL_NAME = "latest_approved_model.json"



def _load_metadata(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))



def get_registry_path(name: str) -> Path:
    return settings.model_registry_dir / name



def _relative_to_project(path_value: str) -> str:
    path = Path(path_value)
    try:
        return str(path.resolve().relative_to(settings.project_root))
    except ValueError:
        return str(path)



def build_registry_record(
    training_result: dict[str, Any],
    gate_report: dict[str, Any],
    gate_report_path: Path,
) -> dict[str, Any]:
    model_metadata_path = Path(training_result["artifacts"]["model_metadata_path"])
    model_metadata = _load_metadata(model_metadata_path)
    artifact_dir = Path(training_result["artifacts"]["artifact_dir"])
    monitoring_reference_path = str(
        training_result["artifacts"].get("monitoring_reference_path", "")
    )
    return {
        "status": gate_report["status"],
        "promotion_eligible": bool(gate_report["summary"]["promotion_eligible"]),
        "promoted_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "run_id": training_result["run_id"],
        "run_label": training_result["run_label"],
        "model_name": training_result["model_name"],
        "model_path": training_result["artifacts"]["model_path"],
        "project_relative_model_path": _relative_to_project(
            training_result["artifacts"]["model_path"]
        ),
        "model_metadata_path": training_result["artifacts"]["model_metadata_path"],
        "project_relative_model_metadata_path": _relative_to_project(
            training_result["artifacts"]["model_metadata_path"]
        ),
        "artifact_dir": str(artifact_dir),
        "project_relative_artifact_dir": _relative_to_project(str(artifact_dir)),
        "release_gate_report_path": str(gate_report_path),
        "project_relative_release_gate_report_path": _relative_to_project(
            str(gate_report_path)
        ),
        "monitoring_reference_path": monitoring_reference_path,
        "project_relative_monitoring_reference_path": (
            _relative_to_project(monitoring_reference_path)
            if monitoring_reference_path
            else None
        ),
        "metrics": dict(training_result["metrics"]),
        "fairness_summary": dict(training_result["fairness"]["summary"]),
        "model_metadata": model_metadata,
    }



def write_registry_record(record: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return path



def register_model_candidate(
    training_result: dict[str, Any],
    gate_report: dict[str, Any],
    gate_report_path: Path,
) -> dict[str, str | bool]:
    registry_dir = settings.model_registry_dir
    candidate_path = registry_dir / LATEST_CANDIDATE_NAME
    approved_path = registry_dir / APPROVED_MODEL_NAME

    record = build_registry_record(training_result, gate_report, gate_report_path)
    write_registry_record(record, candidate_path)

    promoted = False
    if gate_report["summary"]["promotion_eligible"]:
        write_registry_record(record, approved_path)
        promoted = True

    return {
        "candidate_manifest_path": str(candidate_path),
        "approved_manifest_path": str(approved_path),
        "promoted": promoted,
    }
