from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.config import settings
from src.evaluation.reports import write_json, write_text
from src.monitoring.data_quality import build_data_quality_report
from src.monitoring.drift import build_drift_report
from src.monitoring.reference import load_monitoring_reference
from src.monitoring.reporting import build_monitoring_summary_text, build_operational_summary
from src.monitoring.store import get_api_events_path, get_inference_events_path, read_jsonl
from src.monitoring.triggers import evaluate_monitoring_triggers
from src.serving.model_store import load_approved_model
from src.tracking import log_monitoring_run


@dataclass(frozen=True)
class MonitoringArtifacts:
    run_label: str
    artifact_dir: Path
    monitoring_report_path: Path
    operational_summary_path: Path
    data_quality_report_path: Path
    drift_report_path: Path
    trigger_report_path: Path
    summary_path: Path



def _build_run_label() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")



def _build_artifacts(run_label: str) -> MonitoringArtifacts:
    artifact_dir = settings.monitoring_artifact_dir / run_label
    return MonitoringArtifacts(
        run_label=run_label,
        artifact_dir=artifact_dir,
        monitoring_report_path=artifact_dir / "monitoring_report.json",
        operational_summary_path=artifact_dir / "operational_summary.json",
        data_quality_report_path=artifact_dir / "data_quality_report.json",
        drift_report_path=artifact_dir / "drift_report.json",
        trigger_report_path=artifact_dir / "trigger_report.json",
        summary_path=artifact_dir / "monitoring_summary.txt",
    )



def run_monitoring(*, log_to_mlflow: bool = True) -> dict[str, Any]:
    approved_model = load_approved_model()
    if approved_model.monitoring_reference_path is None:
        raise FileNotFoundError(
            "Monitoring reference path not available in approved model manifest."
        )

    api_events = read_jsonl(get_api_events_path())
    inference_events = read_jsonl(get_inference_events_path())
    reference = load_monitoring_reference(approved_model.monitoring_reference_path)

    operational_summary = build_operational_summary(api_events, inference_events)
    data_quality_report = build_data_quality_report(inference_events, api_events, reference)
    drift_report = build_drift_report(inference_events, reference)
    trigger_report = evaluate_monitoring_triggers(
        operational_summary,
        data_quality_report,
        drift_report,
    )

    artifacts = _build_artifacts(_build_run_label())
    write_json(operational_summary, artifacts.operational_summary_path)
    write_json(data_quality_report, artifacts.data_quality_report_path)
    write_json(drift_report, artifacts.drift_report_path)
    write_json(trigger_report, artifacts.trigger_report_path)

    report = {
        "run_label": artifacts.run_label,
        "model_name": approved_model.model_name,
        "model_run_id": approved_model.run_id,
        "model_run_label": approved_model.run_label,
        "event_paths": {
            "api_events_path": str(get_api_events_path()),
            "inference_events_path": str(get_inference_events_path()),
        },
        "operational_summary": operational_summary,
        "data_quality": data_quality_report,
        "drift": drift_report,
        "triggers": trigger_report,
    }
    write_json(report, artifacts.monitoring_report_path)
    write_text(build_monitoring_summary_text(report), artifacts.summary_path)

    monitoring_run_id = None
    if log_to_mlflow:
        monitoring_run_id = log_monitoring_run(
            params={
                "model_run_id": approved_model.run_id,
                "model_run_label": approved_model.run_label,
                "monitoring_min_sample_size": settings.monitoring_min_sample_size,
            },
            metrics={
                "monitoring_prediction_count": float(operational_summary["prediction_count"]),
                "monitoring_error_rate": float(operational_summary["error_rate"]),
                "monitoring_latency_p95_ms": float(operational_summary["latency_p95_ms"]),
                "monitoring_drift_alert_count": float(
                    drift_report["summary"]["drift_alert_count"]
                ),
                "monitoring_retraining_recommended": float(
                    trigger_report["summary"]["retraining_recommended"]
                ),
            },
            artifact_paths=[
                artifacts.monitoring_report_path,
                artifacts.operational_summary_path,
                artifacts.data_quality_report_path,
                artifacts.drift_report_path,
                artifacts.trigger_report_path,
                artifacts.summary_path,
            ],
        )

    report["monitoring_run_id"] = monitoring_run_id
    return report



def main() -> None:
    print(json.dumps(run_monitoring(), indent=2))


if __name__ == "__main__":
    main()
