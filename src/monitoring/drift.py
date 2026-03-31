from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.data.schema import MODEL_INPUT_CATEGORICAL_COLUMNS, MODEL_INPUT_NUMERIC_COLUMNS

_EPSILON = 1e-6



def _psi(reference: list[float], observed: list[float]) -> float:
    total = 0.0
    for expected, actual in zip(reference, observed, strict=False):
        expected_value = max(float(expected), _EPSILON)
        actual_value = max(float(actual), _EPSILON)
        total += (actual_value - expected_value) * np.log(actual_value / expected_value)
    return float(total)



def _numeric_bin_proportions(series: pd.Series, bins: list[float]) -> list[float]:
    clean = pd.to_numeric(series, errors="coerce").dropna().astype(float)
    if clean.empty:
        return [0.0] * (len(bins) - 1)
    counts, _ = np.histogram(clean, bins=np.asarray(bins, dtype=float))
    total = counts.sum()
    if total == 0:
        return [0.0] * len(counts)
    return [float(value / total) for value in counts]



def build_drift_report(
    inference_events: list[dict[str, Any]],
    reference: dict[str, Any],
) -> dict[str, Any]:
    sample_size = len(inference_events)
    if sample_size == 0:
        return {
            "summary": {"sample_size": 0, "drift_alert_count": 0},
            "numeric_features": {},
            "categorical_features": {},
            "score": None,
            "alerts": [
                {
                    "severity": "warning",
                    "type": "insufficient_data",
                    "message": "No inference events available for drift analysis.",
                }
            ],
        }

    feature_frame = pd.DataFrame([event["features"] for event in inference_events])
    score_series = pd.Series(
        [event.get("positive_class_probability") for event in inference_events],
        dtype="float64",
    )
    prediction_series = pd.Series(
        [event["prediction"] for event in inference_events],
        dtype="int64",
    )

    alerts: list[dict[str, Any]] = []
    numeric_report: dict[str, Any] = {}
    for column in MODEL_INPUT_NUMERIC_COLUMNS:
        metadata = reference.get("numeric_features", {}).get(column, {})
        bins = metadata.get("bins") or [float("-inf"), float("inf")]
        observed_proportions = _numeric_bin_proportions(feature_frame[column], bins)
        reference_proportions = metadata.get("bin_proportions", [0.0] * (len(bins) - 1))
        psi = _psi(reference_proportions, observed_proportions)
        missing_rate = float(
            pd.to_numeric(feature_frame[column], errors="coerce").isna().mean()
        )
        numeric_report[column] = {
            "psi": psi,
            "missing_rate": missing_rate,
        }
        if psi >= 0.2:
            alerts.append(
                {
                    "severity": "warning",
                    "type": "numeric_drift",
                    "feature": column,
                    "value": psi,
                }
            )

    categorical_report: dict[str, Any] = {}
    for column in MODEL_INPUT_CATEGORICAL_COLUMNS:
        metadata = reference.get("categorical_features", {}).get(column, {})
        reference_categories = metadata.get("categories", [])
        reference_proportions = metadata.get("proportions", [])
        observed_distribution = (
            feature_frame[column]
            .fillna("<missing>")
            .astype(str)
            .value_counts(normalize=True)
        )
        reference_distribution = dict(
            zip(reference_categories, reference_proportions, strict=False)
        )
        categories = sorted(set(reference_distribution) | set(observed_distribution.index))
        max_abs_diff = 0.0
        for category in categories:
            observed_value = float(observed_distribution.get(category, 0.0))
            reference_value = float(reference_distribution.get(category, 0.0))
            diff = abs(observed_value - reference_value)
            max_abs_diff = max(max_abs_diff, diff)
        categorical_report[column] = {"max_abs_diff": float(max_abs_diff)}
        if max_abs_diff >= 0.15:
            alerts.append(
                {
                    "severity": "warning",
                    "type": "categorical_drift",
                    "feature": column,
                    "value": float(max_abs_diff),
                }
            )

    score_report = None
    score_reference = reference.get("score_distribution")
    if score_reference is not None:
        observed_proportions = _numeric_bin_proportions(
            score_series,
            score_reference["bins"],
        )
        score_psi = _psi(score_reference["bin_proportions"], observed_proportions)
        positive_rate = float(prediction_series.mean()) if len(prediction_series) else 0.0
        positive_rate_diff = abs(
            positive_rate - float(reference.get("positive_prediction_rate") or 0.0)
        )
        score_report = {
            "psi": score_psi,
            "positive_rate": positive_rate,
            "positive_rate_diff": positive_rate_diff,
        }
        if score_psi >= 0.2:
            alerts.append(
                {
                    "severity": "warning",
                    "type": "score_drift",
                    "feature": "positive_class_probability",
                    "value": score_psi,
                }
            )
        if positive_rate_diff >= 0.15:
            alerts.append(
                {
                    "severity": "warning",
                    "type": "positive_rate_shift",
                    "feature": "prediction",
                    "value": positive_rate_diff,
                }
            )

    return {
        "summary": {
            "sample_size": sample_size,
            "drift_alert_count": len(alerts),
        },
        "numeric_features": numeric_report,
        "categorical_features": categorical_report,
        "score": score_report,
        "alerts": alerts,
    }
