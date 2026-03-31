from __future__ import annotations

import json
import platform
from pathlib import Path
from typing import Any

import mlflow
from mlflow.tracking import MlflowClient

from src.config import settings
from src.data.ingest_mod import build_ingestion_report, parse_mod_file


def configure_tracking(experiment_name: str | None = None) -> None:
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name or settings.mlflow_experiment_name)



def _dataset_lineage() -> dict[str, Any]:
    frame = parse_mod_file(settings.raw_data_path)
    return build_ingestion_report(frame, settings.raw_data_path)



def build_training_tags(dataset_hash: str) -> dict[str, str]:
    return {
        "dataset_hash": dataset_hash,
        "dataset_source": str(settings.raw_data_path),
        "parser_version": settings.parser_version,
        "preprocessing_version": settings.preprocessing_version,
        "target_definition": settings.target_definition,
        "fairness_policy_name": settings.fairness_policy_name,
        "python_version": platform.python_version(),
    }



def log_training_run(
    *,
    params: dict[str, Any],
    metrics: dict[str, float],
    artifact_paths: list[Path],
    model_path: Path,
    metadata_path: Path,
    run_name: str = "phase-4-release",
) -> str:
    configure_tracking()
    lineage = _dataset_lineage()
    dataset_hash = str(lineage["file_hash_sha256"])

    with mlflow.start_run(run_name=run_name) as run:
        mlflow.set_tags(build_training_tags(dataset_hash))
        mlflow.log_params({key: str(value) for key, value in params.items()})
        mlflow.log_metrics(metrics)

        if settings.ingestion_report_path.exists():
            mlflow.log_artifact(str(settings.ingestion_report_path), artifact_path="ingestion")

        for artifact_path in artifact_paths:
            if artifact_path.exists():
                mlflow.log_artifact(str(artifact_path), artifact_path="evaluation")

        if model_path.exists():
            mlflow.log_artifact(str(model_path), artifact_path="model")
        if metadata_path.exists():
            mlflow.log_artifact(str(metadata_path), artifact_path="model")

        lineage_path = metadata_path.parent / "dataset_lineage.json"
        lineage_path.write_text(json.dumps(lineage, indent=2), encoding="utf-8")
        mlflow.log_artifact(str(lineage_path), artifact_path="lineage")
        return run.info.run_id



def log_release_outcome(
    *,
    run_id: str,
    gate_report: dict[str, Any],
    artifact_paths: list[Path],
) -> None:
    client = MlflowClient(tracking_uri=settings.mlflow_tracking_uri)
    client.set_tag(run_id, "release_status", gate_report["status"])
    client.set_tag(
        run_id,
        "promotion_eligible",
        str(bool(gate_report["summary"]["promotion_eligible"])).lower(),
    )
    client.log_metric(
        run_id,
        "release_blocking_failures",
        float(gate_report["summary"]["blocking_failures"]),
    )
    client.log_metric(
        run_id,
        "release_active_alerts",
        float(gate_report["summary"]["active_alerts"]),
    )

    for artifact_path in artifact_paths:
        if artifact_path.exists():
            client.log_artifact(run_id, str(artifact_path), artifact_path="release")



def log_monitoring_run(
    *,
    params: dict[str, Any],
    metrics: dict[str, float],
    artifact_paths: list[Path],
    run_name: str = "phase-6-monitoring",
) -> str:
    configure_tracking(settings.monitoring_experiment_name)
    with mlflow.start_run(run_name=run_name) as run:
        mlflow.set_tags(
            {
                "monitoring_policy": "local_batch_v1",
                "python_version": platform.python_version(),
            }
        )
        mlflow.log_params({key: str(value) for key, value in params.items()})
        mlflow.log_metrics(metrics)
        for artifact_path in artifact_paths:
            if artifact_path.exists():
                mlflow.log_artifact(str(artifact_path), artifact_path="monitoring")
        return run.info.run_id
