from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _path_from_env(env_name: str, default: Path) -> Path:
    raw_value = os.getenv(env_name)
    if raw_value is None:
        return default.resolve()

    candidate = Path(raw_value)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    return candidate.resolve()



def _float_from_env(env_name: str, default: float) -> float:
    raw_value = os.getenv(env_name)
    return default if raw_value is None else float(raw_value)



def _int_from_env(env_name: str, default: int) -> int:
    raw_value = os.getenv(env_name)
    return default if raw_value is None else int(raw_value)


@dataclass(frozen=True)
class ProjectSettings:
    project_root: Path
    raw_data_path: Path
    data_dictionary_path: Path
    processed_data_path: Path
    ingestion_report_path: Path
    training_artifact_dir: Path
    model_artifact_dir: Path
    monitoring_artifact_dir: Path
    monitoring_event_dir: Path
    mlflow_tracking_uri: str
    parser_version: str
    preprocessing_version: str
    target_definition: str
    train_test_split_ratio: float
    random_state: int
    mlflow_experiment_name: str
    baseline_model_name: str
    positive_label: int
    decision_threshold: float
    threshold_min_precision: float
    approved_decision_threshold: float
    fairness_policy_name: str
    fairness_alert_threshold: float
    fairness_min_group_size: int
    release_gate_min_recall: float
    release_gate_min_precision: float
    model_registry_dir: Path
    monitoring_experiment_name: str
    monitoring_drift_psi_threshold: float
    monitoring_category_diff_threshold: float
    monitoring_score_diff_threshold: float
    monitoring_positive_rate_diff_threshold: float
    monitoring_min_sample_size: int
    monitoring_max_error_rate: float
    monitoring_max_invalid_request_rate: float
    monitoring_max_missing_rate: float
    monitoring_max_latency_p95_ms: float

    def as_dict(self) -> dict[str, str]:
        return {
            "project_root": str(self.project_root),
            "raw_data_path": str(self.raw_data_path),
            "data_dictionary_path": str(self.data_dictionary_path),
            "processed_data_path": str(self.processed_data_path),
            "ingestion_report_path": str(self.ingestion_report_path),
            "training_artifact_dir": str(self.training_artifact_dir),
            "model_artifact_dir": str(self.model_artifact_dir),
            "monitoring_artifact_dir": str(self.monitoring_artifact_dir),
            "monitoring_event_dir": str(self.monitoring_event_dir),
            "mlflow_tracking_uri": self.mlflow_tracking_uri,
            "parser_version": self.parser_version,
            "preprocessing_version": self.preprocessing_version,
            "target_definition": self.target_definition,
            "train_test_split_ratio": str(self.train_test_split_ratio),
            "random_state": str(self.random_state),
            "mlflow_experiment_name": self.mlflow_experiment_name,
            "baseline_model_name": self.baseline_model_name,
            "positive_label": str(self.positive_label),
            "decision_threshold": str(self.decision_threshold),
            "threshold_min_precision": str(self.threshold_min_precision),
            "approved_decision_threshold": str(self.approved_decision_threshold),
            "fairness_policy_name": self.fairness_policy_name,
            "fairness_alert_threshold": str(self.fairness_alert_threshold),
            "fairness_min_group_size": str(self.fairness_min_group_size),
            "release_gate_min_recall": str(self.release_gate_min_recall),
            "release_gate_min_precision": str(self.release_gate_min_precision),
            "model_registry_dir": str(self.model_registry_dir),
            "monitoring_experiment_name": self.monitoring_experiment_name,
            "monitoring_drift_psi_threshold": str(self.monitoring_drift_psi_threshold),
            "monitoring_category_diff_threshold": str(self.monitoring_category_diff_threshold),
            "monitoring_score_diff_threshold": str(self.monitoring_score_diff_threshold),
            "monitoring_positive_rate_diff_threshold": str(
                self.monitoring_positive_rate_diff_threshold
            ),
            "monitoring_min_sample_size": str(self.monitoring_min_sample_size),
            "monitoring_max_error_rate": str(self.monitoring_max_error_rate),
            "monitoring_max_invalid_request_rate": str(self.monitoring_max_invalid_request_rate),
            "monitoring_max_missing_rate": str(self.monitoring_max_missing_rate),
            "monitoring_max_latency_p95_ms": str(self.monitoring_max_latency_p95_ms),
        }


settings = ProjectSettings(
    project_root=PROJECT_ROOT,
    raw_data_path=_path_from_env(
        "RAW_DATA_PATH", PROJECT_ROOT / "data" / "raw" / "heart+disease" / "cleve.mod"
    ),
    data_dictionary_path=_path_from_env(
        "DATA_DICTIONARY_PATH",
        PROJECT_ROOT / "data" / "raw" / "heart+disease" / "heart-disease.names",
    ),
    processed_data_path=_path_from_env(
        "PROCESSED_DATA_PATH", PROJECT_ROOT / "data" / "processed" / "heart_disease_cleveland.csv"
    ),
    ingestion_report_path=_path_from_env(
        "INGESTION_REPORT_PATH", PROJECT_ROOT / "artifacts" / "data_ingestion_report.json"
    ),
    training_artifact_dir=_path_from_env(
        "TRAINING_ARTIFACT_DIR", PROJECT_ROOT / "artifacts" / "training"
    ),
    model_artifact_dir=_path_from_env("MODEL_ARTIFACT_DIR", PROJECT_ROOT / "models"),
    monitoring_artifact_dir=_path_from_env(
        "MONITORING_ARTIFACT_DIR", PROJECT_ROOT / "artifacts" / "monitoring"
    ),
    monitoring_event_dir=_path_from_env(
        "MONITORING_EVENT_DIR", PROJECT_ROOT / "artifacts" / "monitoring" / "events"
    ),
    mlflow_tracking_uri=os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns"),
    parser_version=os.getenv("PARSER_VERSION", "0.1.0"),
    preprocessing_version=os.getenv("PREPROCESSING_VERSION", "1.0.0"),
    target_definition=os.getenv("TARGET_DEFINITION", "buff=0,sick=1"),
    train_test_split_ratio=_float_from_env("TRAIN_TEST_SPLIT_RATIO", 0.2),
    random_state=_int_from_env("RANDOM_STATE", 42),
    mlflow_experiment_name=os.getenv("MLFLOW_EXPERIMENT_NAME", "phase-4-release"),
    baseline_model_name=os.getenv("BASELINE_MODEL_NAME", "logistic_regression"),
    positive_label=_int_from_env("POSITIVE_LABEL", 1),
    decision_threshold=_float_from_env("DECISION_THRESHOLD", 0.5),
    threshold_min_precision=_float_from_env("THRESHOLD_MIN_PRECISION", 0.7),
    approved_decision_threshold=_float_from_env("APPROVED_DECISION_THRESHOLD", 0.35),
    fairness_policy_name=os.getenv("FAIRNESS_POLICY_NAME", "max_gap_alert_0.15"),
    fairness_alert_threshold=_float_from_env("FAIRNESS_ALERT_THRESHOLD", 0.15),
    fairness_min_group_size=_int_from_env("FAIRNESS_MIN_GROUP_SIZE", 10),
    release_gate_min_recall=_float_from_env("RELEASE_GATE_MIN_RECALL", 0.8),
    release_gate_min_precision=_float_from_env("RELEASE_GATE_MIN_PRECISION", 0.7),
    model_registry_dir=_path_from_env("MODEL_REGISTRY_DIR", PROJECT_ROOT / "models" / "registry"),
    monitoring_experiment_name=os.getenv("MONITORING_EXPERIMENT_NAME", "phase-6-monitoring"),
    monitoring_drift_psi_threshold=_float_from_env("MONITORING_DRIFT_PSI_THRESHOLD", 0.2),
    monitoring_category_diff_threshold=_float_from_env(
        "MONITORING_CATEGORY_DIFF_THRESHOLD", 0.15
    ),
    monitoring_score_diff_threshold=_float_from_env("MONITORING_SCORE_DIFF_THRESHOLD", 0.1),
    monitoring_positive_rate_diff_threshold=_float_from_env(
        "MONITORING_POSITIVE_RATE_DIFF_THRESHOLD", 0.15
    ),
    monitoring_min_sample_size=_int_from_env("MONITORING_MIN_SAMPLE_SIZE", 20),
    monitoring_max_error_rate=_float_from_env("MONITORING_MAX_ERROR_RATE", 0.05),
    monitoring_max_invalid_request_rate=_float_from_env(
        "MONITORING_MAX_INVALID_REQUEST_RATE", 0.1
    ),
    monitoring_max_missing_rate=_float_from_env("MONITORING_MAX_MISSING_RATE", 0.1),
    monitoring_max_latency_p95_ms=_float_from_env("MONITORING_MAX_LATENCY_P95_MS", 100.0),
)
