from __future__ import annotations

from typing import Any

import pandas as pd

from src.data.schema import MODEL_INPUT_CATEGORICAL_COLUMNS, MODEL_INPUT_NUMERIC_COLUMNS


def build_data_quality_report(
    inference_events: list[dict[str, Any]],
    api_events: list[dict[str, Any]],
    reference: dict[str, Any],
) -> dict[str, Any]:
    total_inference_events = len(inference_events)
    total_api_events = len(api_events)
    prediction_failures = [
        event for event in api_events if event["event_type"] == "prediction_failed"
    ]
    prediction_completions = [
        event for event in api_events if event["event_type"] == "prediction_completed"
    ]
    invalid_requests = [
        event for event in prediction_failures if event.get("status_code") == 400
    ]

    if total_inference_events == 0:
        return {
            "summary": {
                "sample_size": 0,
                "api_event_count": total_api_events,
                "prediction_completed_count": len(prediction_completions),
                "prediction_failed_count": len(prediction_failures),
                "invalid_request_rate": 0.0,
            },
            "numeric_features": {},
            "categorical_features": {},
            "alerts": [
                {
                    "severity": "warning",
                    "type": "insufficient_data",
                    "message": "No inference events available for data quality analysis.",
                }
            ],
        }

    feature_frame = pd.DataFrame([event["features"] for event in inference_events])
    numeric_reference = reference.get("numeric_features", {})
    categorical_reference = reference.get("categorical_features", {})

    numeric_features: dict[str, Any] = {}
    alerts: list[dict[str, Any]] = []
    for column in MODEL_INPUT_NUMERIC_COLUMNS:
        series = pd.to_numeric(feature_frame[column], errors="coerce")
        reference_bounds = numeric_reference.get(column, {})
        lower = reference_bounds.get("min")
        upper = reference_bounds.get("max")
        out_of_range_mask = pd.Series(False, index=series.index)
        if lower is not None:
            out_of_range_mask |= series < float(lower)
        if upper is not None:
            out_of_range_mask |= series > float(upper)
        numeric_features[column] = {
            "missing_rate": float(series.isna().mean()),
            "out_of_range_rate": float(out_of_range_mask.mean()),
        }
        if float(out_of_range_mask.mean()) > 0.0:
            alerts.append(
                {
                    "severity": "warning",
                    "type": "numeric_out_of_range",
                    "feature": column,
                    "value": float(out_of_range_mask.mean()),
                }
            )

    categorical_features: dict[str, Any] = {}
    for column in MODEL_INPUT_CATEGORICAL_COLUMNS:
        normalized = feature_frame[column].fillna("<missing>").astype(str)
        known_categories = set(categorical_reference.get(column, {}).get("categories", []))
        if known_categories:
            unknown_mask = ~normalized.isin(known_categories)
        else:
            unknown_mask = pd.Series(False, index=normalized.index)
        categorical_features[column] = {
            "missing_rate": float(feature_frame[column].isna().mean()),
            "unknown_category_rate": float(unknown_mask.mean()),
        }
        if float(unknown_mask.mean()) > 0.0:
            alerts.append(
                {
                    "severity": "warning",
                    "type": "unknown_category",
                    "feature": column,
                    "value": float(unknown_mask.mean()),
                }
            )

    invalid_request_rate = (
        float(len(invalid_requests) / len(prediction_failures))
        if prediction_failures
        else 0.0
    )

    return {
        "summary": {
            "sample_size": total_inference_events,
            "api_event_count": total_api_events,
            "prediction_completed_count": len(prediction_completions),
            "prediction_failed_count": len(prediction_failures),
            "invalid_request_rate": invalid_request_rate,
        },
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "alerts": alerts,
    }
