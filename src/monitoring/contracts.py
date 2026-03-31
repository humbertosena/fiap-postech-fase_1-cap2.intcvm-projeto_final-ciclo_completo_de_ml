from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from src.data.schema import MODEL_FEATURE_COLUMNS

API_EVENT_TYPES = frozenset(
    {
        "request_received",
        "prediction_completed",
        "prediction_failed",
        "model_unavailable",
        "health_checked",
    }
)


@dataclass(slots=True, frozen=True)
class ApiMonitoringEvent:
    timestamp_utc: str
    event_type: str
    request_id: str
    endpoint: str
    status_code: int
    latency_ms: float
    model_name: str | None
    model_run_id: str | None
    model_run_label: str | None
    error_type: str | None = None
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["latency_ms"] = float(self.latency_ms)
        return payload


@dataclass(slots=True, frozen=True)
class InferenceMonitoringEvent:
    timestamp_utc: str
    request_id: str
    endpoint: str
    model_name: str
    model_run_id: str
    model_run_label: str
    prediction: int
    prediction_label: str
    positive_class_probability: float | None
    decision_threshold: float
    features: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["decision_threshold"] = float(self.decision_threshold)
        if self.positive_class_probability is not None:
            payload["positive_class_probability"] = float(self.positive_class_probability)
        return payload


@dataclass(slots=True, frozen=True)
class MonitoringSnapshotPaths:
    api_events_path: str
    inference_events_path: str


def sanitize_features_for_monitoring(features: dict[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for column in MODEL_FEATURE_COLUMNS:
        value = features.get(column)
        if value is None:
            sanitized[column] = None
            continue
        if isinstance(value, float):
            sanitized[column] = round(value, 6)
            continue
        sanitized[column] = value
    return sanitized
