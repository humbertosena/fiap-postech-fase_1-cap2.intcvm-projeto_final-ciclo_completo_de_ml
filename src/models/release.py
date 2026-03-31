from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.evaluation.gates import evaluate_release_gates
from src.evaluation.reports import write_json, write_text
from src.models.registry import register_model_candidate
from src.models.train import train_model
from src.tracking import log_release_outcome

RELEASE_GATE_REPORT_NAME = "release_gate_report.json"
RELEASE_DECISION_NAME = "release_decision.txt"

def _build_decision_summary(gate_report: dict[str, Any], promoted: bool) -> str:
    lines = [
        f"Status: {gate_report['status']}",
        f"Elegivel para promocao: {gate_report['summary']['promotion_eligible']}",
        f"Promovido no registro local: {promoted}",
        f"Falhas bloqueantes: {gate_report['summary']['blocking_failures']}",
        f"Alertas ativos: {gate_report['summary']['active_alerts']}",
    ]
    return "\n".join(lines)

def run_release_pipeline(
    *,
    log_to_mlflow: bool = True,
    fail_on_blocked: bool = True,
) -> dict[str, Any]:
    training_result = train_model(log_to_mlflow=log_to_mlflow)
    gate_report = evaluate_release_gates(training_result)

    artifact_dir = Path(training_result["artifacts"]["artifact_dir"])
    gate_report_path = write_json(gate_report, artifact_dir / RELEASE_GATE_REPORT_NAME)

    registry_result = register_model_candidate(training_result, gate_report, gate_report_path)
    decision_summary = _build_decision_summary(gate_report, bool(registry_result["promoted"]))
    decision_path = write_text(decision_summary, artifact_dir / RELEASE_DECISION_NAME)

    if training_result["run_id"]:
        artifact_paths = [
            gate_report_path,
            decision_path,
            Path(str(registry_result["candidate_manifest_path"])),
        ]
        approved_manifest_path = Path(str(registry_result["approved_manifest_path"]))
        if bool(registry_result["promoted"]) and approved_manifest_path.exists():
            artifact_paths.append(approved_manifest_path)
        log_release_outcome(
            run_id=training_result["run_id"],
            gate_report=gate_report,
            artifact_paths=artifact_paths,
        )

    result = {
        "status": "released" if gate_report["summary"]["promotion_eligible"] else "blocked",
        "training": training_result,
        "release_gates": gate_report,
        "registry": registry_result,
        "artifacts": {
            "release_gate_report_path": str(gate_report_path),
            "release_decision_path": str(decision_path),
        },
    }

    if fail_on_blocked and gate_report["status"] == "blocked":
        raise SystemExit(1)
    return result



def main() -> None:
    result = run_release_pipeline()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except SystemExit as exc:
        if exc.code not in (None, 0):
            print(json.dumps({"status": "blocked", "exit_code": exc.code}, indent=2))
        raise
