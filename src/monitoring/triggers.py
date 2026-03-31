from __future__ import annotations

from typing import Any

from src.config import settings


def evaluate_monitoring_triggers(
    operational_summary: dict[str, Any],
    data_quality_report: dict[str, Any],
    drift_report: dict[str, Any],
) -> dict[str, Any]:
    alerts: list[dict[str, Any]] = []
    retraining_reasons: list[str] = []
    sample_size = int(operational_summary.get("prediction_count", 0))
    sufficient_sample = sample_size >= settings.monitoring_min_sample_size

    error_rate = float(operational_summary.get("error_rate", 0.0))
    if error_rate > settings.monitoring_max_error_rate:
        alerts.append({"severity": "critical", "type": "error_rate", "value": error_rate})
        retraining_reasons.append("operational_error_rate")

    invalid_request_rate = float(data_quality_report["summary"].get("invalid_request_rate", 0.0))
    if invalid_request_rate > settings.monitoring_max_invalid_request_rate:
        alerts.append(
            {
                "severity": "warning",
                "type": "invalid_request_rate",
                "value": invalid_request_rate,
            }
        )

    p95_latency = float(operational_summary.get("latency_p95_ms", 0.0))
    if p95_latency > settings.monitoring_max_latency_p95_ms:
        alerts.append({"severity": "warning", "type": "latency_p95_ms", "value": p95_latency})

    for feature_name, payload in data_quality_report.get("numeric_features", {}).items():
        missing_rate = float(payload.get("missing_rate", 0.0))
        if missing_rate > settings.monitoring_max_missing_rate:
            alerts.append(
                {
                    "severity": "warning",
                    "type": "missing_rate",
                    "feature": feature_name,
                    "value": missing_rate,
                }
            )

    for alert in drift_report.get("alerts", []):
        alert_type = str(alert.get("type"))
        value = float(alert.get("value", 0.0))
        if (
            alert_type in {"numeric_drift", "score_drift"}
            and value >= settings.monitoring_drift_psi_threshold
        ):
            alerts.append(dict(alert))
            if sufficient_sample:
                retraining_reasons.append(alert_type)
        elif (
            alert_type == "categorical_drift"
            and value >= settings.monitoring_category_diff_threshold
        ):
            alerts.append(dict(alert))
            if sufficient_sample:
                retraining_reasons.append(alert_type)
        elif (
            alert_type == "positive_rate_shift"
            and value >= settings.monitoring_positive_rate_diff_threshold
        ):
            alerts.append(dict(alert))
            if sufficient_sample:
                retraining_reasons.append(alert_type)

    deduplicated_reasons = sorted(set(retraining_reasons))
    status = "retraining_recommended" if deduplicated_reasons else "healthy"
    if sample_size == 0:
        status = "insufficient_data"

    return {
        "status": status,
        "summary": {
            "sample_size": sample_size,
            "sufficient_sample": sufficient_sample,
            "alert_count": len(alerts),
            "retraining_recommended": bool(deduplicated_reasons),
        },
        "alerts": alerts,
        "retraining_reasons": deduplicated_reasons,
    }
