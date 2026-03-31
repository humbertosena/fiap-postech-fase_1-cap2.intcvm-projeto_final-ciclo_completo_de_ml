from __future__ import annotations

from typing import Any

import numpy as np


def build_operational_summary(
    api_events: list[dict[str, Any]],
    inference_events: list[dict[str, Any]],
) -> dict[str, Any]:
    prediction_events = [event for event in api_events if event["endpoint"] == "/predict"]
    completed_events = [
        event for event in prediction_events if event["event_type"] == "prediction_completed"
    ]
    failed_events = [
        event for event in prediction_events if event["event_type"] == "prediction_failed"
    ]
    latency_values = [float(event["latency_ms"]) for event in completed_events]
    total_predictions = len(completed_events)
    total_failures = len(failed_events)
    total_requests = total_predictions + total_failures
    positive_predictions = sum(int(event["prediction"]) for event in inference_events)

    return {
        "api_event_count": len(api_events),
        "prediction_count": total_predictions,
        "prediction_failure_count": total_failures,
        "error_rate": float(total_failures / total_requests) if total_requests else 0.0,
        "latency_p50_ms": float(np.percentile(latency_values, 50)) if latency_values else 0.0,
        "latency_p95_ms": float(np.percentile(latency_values, 95)) if latency_values else 0.0,
        "positive_prediction_rate": (
            float(positive_predictions / total_predictions) if total_predictions else 0.0
        ),
    }



def build_monitoring_summary_text(report: dict[str, Any]) -> str:
    lines = [
        f"Status: {report['triggers']['status']}",
        f"Prediction count: {report['operational_summary']['prediction_count']}",
        f"Error rate: {report['operational_summary']['error_rate']:.4f}",
        f"Latency p95 ms: {report['operational_summary']['latency_p95_ms']:.2f}",
        f"Data quality alerts: {len(report['data_quality']['alerts'])}",
        f"Drift alerts: {report['drift']['summary']['drift_alert_count']}",
        (
            "Retraining recommended: "
            f"{report['triggers']['summary']['retraining_recommended']}"
        ),
    ]
    if report["triggers"]["retraining_reasons"]:
        reasons = ", ".join(report["triggers"]["retraining_reasons"])
        lines.append(f"Retraining reasons: {reasons}")
    return "\n".join(lines)
