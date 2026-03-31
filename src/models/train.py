from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.config import settings
from src.data.dataset import load_training_frame, split_training_dataset
from src.data.ingest_mod import build_ingestion_report, parse_mod_file
from src.evaluation.fairness import (
    build_fairness_executive_summary,
    build_fairness_report,
    extract_fairness_mlflow_metrics,
)
from src.evaluation.metrics import (
    apply_threshold,
    build_classification_report,
    build_confusion_matrix,
    compute_classification_metrics,
    select_threshold_by_recall,
)
from src.evaluation.reports import write_confusion_matrix_csv, write_json, write_text
from src.evaluation.risk import build_model_card, build_risk_summary
from src.features.build_features import build_feature_pipeline
from src.models.baseline import get_baseline_estimator
from src.models.io import save_model, write_model_metadata
from src.monitoring.reference import (
    REFERENCE_FILE_NAME,
    build_monitoring_reference,
    write_monitoring_reference,
)
from src.tracking import log_training_run


@dataclass(frozen=True)
class TrainingArtifacts:
    run_label: str
    artifact_dir: Path
    model_path: Path
    model_metadata_path: Path
    metrics_path: Path
    classification_report_path: Path
    confusion_matrix_path: Path
    threshold_summary_path: Path
    fairness_report_path: Path
    fairness_summary_path: Path
    risk_summary_path: Path
    model_card_path: Path
    monitoring_reference_path: Path



def _build_run_label() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")



def _build_artifact_paths(run_label: str) -> TrainingArtifacts:
    artifact_dir = settings.training_artifact_dir / run_label
    model_dir = settings.model_artifact_dir / run_label
    return TrainingArtifacts(
        run_label=run_label,
        artifact_dir=artifact_dir,
        model_path=model_dir / "training_pipeline.joblib",
        model_metadata_path=model_dir / "model_metadata.json",
        metrics_path=artifact_dir / "metrics.json",
        classification_report_path=artifact_dir / "classification_report.json",
        confusion_matrix_path=artifact_dir / "confusion_matrix.csv",
        threshold_summary_path=artifact_dir / "threshold_selection.json",
        fairness_report_path=artifact_dir / "fairness_report.json",
        fairness_summary_path=artifact_dir / "fairness_summary.txt",
        risk_summary_path=artifact_dir / "risk_summary.json",
        model_card_path=artifact_dir / "model_card.json",
        monitoring_reference_path=artifact_dir / REFERENCE_FILE_NAME,
    )



def _prediction_scores(model: Any, X_test: Any) -> Any | None:
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X_test)
        return probabilities[:, 1]
    if hasattr(model, "decision_function"):
        return model.decision_function(X_test)
    return None



def _build_threshold_grid() -> list[float]:
    return [round(step / 100, 2) for step in range(20, 81, 5)]



def train_model(log_to_mlflow: bool = True) -> dict[str, Any]:
    frame = load_training_frame()
    split = split_training_dataset(frame)

    estimator = get_baseline_estimator()
    pipeline = build_feature_pipeline(estimator)
    pipeline.fit(split.X_train, split.y_train)

    scores = _prediction_scores(pipeline, split.X_test)
    selected_threshold = settings.decision_threshold
    threshold_selection: dict[str, Any] = {
        "selected_threshold": float(selected_threshold),
        "min_precision": settings.threshold_min_precision,
        "used_precision_constraint": False,
        "threshold_grid": [],
    }

    if scores is None:
        predictions = pipeline.predict(split.X_test)
    else:
        threshold_selection = select_threshold_by_recall(
            split.y_test,
            scores,
            candidate_thresholds=_build_threshold_grid(),
            min_precision=settings.threshold_min_precision,
        )
        selected_threshold = float(threshold_selection["selected_threshold"])
        predictions = apply_threshold(scores, selected_threshold)

    metrics = compute_classification_metrics(split.y_test, predictions, y_score=scores)
    metrics["decision_threshold"] = float(selected_threshold)
    classification_report = build_classification_report(split.y_test, predictions)
    confusion = build_confusion_matrix(split.y_test, predictions)

    audit_source = frame.loc[split.X_test.index]
    fairness_report = build_fairness_report(
        audit_source,
        split.y_test,
        predictions,
        decision_threshold=selected_threshold,
    )
    fairness_summary = build_fairness_executive_summary(fairness_report)
    risk_summary = build_risk_summary(
        metrics=metrics,
        fairness_report=fairness_report,
        threshold_selection=threshold_selection,
    )
    model_card = build_model_card(
        metrics=metrics,
        fairness_report=fairness_report,
        model_name=settings.baseline_model_name,
    )

    artifacts = _build_artifact_paths(_build_run_label())
    write_json(metrics, artifacts.metrics_path)
    write_json(classification_report, artifacts.classification_report_path)
    write_confusion_matrix_csv(confusion, artifacts.confusion_matrix_path)
    write_json(threshold_selection, artifacts.threshold_summary_path)
    write_json(fairness_report, artifacts.fairness_report_path)
    write_text(fairness_summary, artifacts.fairness_summary_path)
    write_json(risk_summary, artifacts.risk_summary_path)
    write_json(model_card, artifacts.model_card_path)
    save_model(pipeline, artifacts.model_path)

    reference_scores = _prediction_scores(pipeline, split.X_train)
    monitoring_reference = build_monitoring_reference(
        split.X_train,
        prediction_scores=reference_scores,
        decision_threshold=selected_threshold,
    )
    write_monitoring_reference(monitoring_reference, artifacts.monitoring_reference_path)

    lineage = build_ingestion_report(parse_mod_file(settings.raw_data_path), settings.raw_data_path)
    metadata = {
        "run_label": artifacts.run_label,
        "algorithm": settings.baseline_model_name,
        "dataset_hash": lineage["file_hash_sha256"],
        "random_state": settings.random_state,
        "train_test_split_ratio": settings.train_test_split_ratio,
        "preprocessing_version": settings.preprocessing_version,
        "target_definition": settings.target_definition,
        "decision_threshold": selected_threshold,
        "threshold_min_precision": settings.threshold_min_precision,
        "fairness_policy_name": settings.fairness_policy_name,
        "fairness_alert_threshold": settings.fairness_alert_threshold,
        "audited_groups": fairness_report["policy"]["evaluated_groups"],
        "monitoring_reference_path": str(artifacts.monitoring_reference_path),
    }
    write_model_metadata(metadata, artifacts.model_metadata_path)

    mlflow_metrics = metrics | extract_fairness_mlflow_metrics(fairness_report)
    params = {
        "algorithm": settings.baseline_model_name,
        "random_state": settings.random_state,
        "test_size": settings.train_test_split_ratio,
        "preprocessing_version": settings.preprocessing_version,
        "feature_columns": ",".join(split.X_train.columns.tolist()),
        "decision_threshold": selected_threshold,
        "threshold_min_precision": settings.threshold_min_precision,
        "fairness_policy_name": settings.fairness_policy_name,
        "fairness_alert_threshold": settings.fairness_alert_threshold,
        "fairness_groups": ",".join(fairness_report["policy"]["evaluated_groups"]),
    }

    run_id = None
    if log_to_mlflow:
        run_id = log_training_run(
            params=params,
            metrics=mlflow_metrics,
            artifact_paths=[
                artifacts.metrics_path,
                artifacts.classification_report_path,
                artifacts.confusion_matrix_path,
                artifacts.threshold_summary_path,
                artifacts.fairness_report_path,
                artifacts.fairness_summary_path,
                artifacts.risk_summary_path,
                artifacts.model_card_path,
                artifacts.monitoring_reference_path,
            ],
            model_path=artifacts.model_path,
            metadata_path=artifacts.model_metadata_path,
        )

    return {
        "status": "trained",
        "run_id": run_id,
        "run_label": artifacts.run_label,
        "model_name": settings.baseline_model_name,
        "metrics": metrics,
        "fairness": {
            "summary": fairness_report["summary"],
            "policy": fairness_report["policy"],
            "alerts": fairness_report["alerts"],
            "group_gaps": fairness_report["group_gaps"],
        },
        "threshold_selection": threshold_selection,
        "artifacts": {
            "artifact_dir": str(artifacts.artifact_dir),
            "model_path": str(artifacts.model_path),
            "model_metadata_path": str(artifacts.model_metadata_path),
            "metrics_path": str(artifacts.metrics_path),
            "classification_report_path": str(artifacts.classification_report_path),
            "confusion_matrix_path": str(artifacts.confusion_matrix_path),
            "threshold_summary_path": str(artifacts.threshold_summary_path),
            "fairness_report_path": str(artifacts.fairness_report_path),
            "fairness_summary_path": str(artifacts.fairness_summary_path),
            "risk_summary_path": str(artifacts.risk_summary_path),
            "model_card_path": str(artifacts.model_card_path),
            "monitoring_reference_path": str(artifacts.monitoring_reference_path),
        },
        "split": {
            "train_rows": int(len(split.X_train)),
            "test_rows": int(len(split.X_test)),
        },
    }



def main() -> None:
    print(json.dumps(train_model(), indent=2))


if __name__ == "__main__":
    main()
