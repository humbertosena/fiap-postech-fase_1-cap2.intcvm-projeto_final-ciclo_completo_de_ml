from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.data.schema import (
    MODEL_FEATURE_COLUMNS,
    MODEL_INPUT_CATEGORICAL_COLUMNS,
    MODEL_INPUT_NUMERIC_COLUMNS,
)
from src.evaluation.reports import write_json
from src.models.io import load_json

REFERENCE_FILE_NAME = "monitoring_reference.json"


def _build_numeric_bins(series: pd.Series) -> list[float]:
    clean = pd.to_numeric(series, errors="coerce").dropna().astype(float)
    if clean.empty:
        return [float("-inf"), float("inf")]

    quantiles = np.quantile(clean, q=np.linspace(0.0, 1.0, 6))
    edges = sorted({float(value) for value in quantiles})
    if len(edges) == 1:
        edges = [edges[0] - 1.0, edges[0] + 1.0]
    return [float("-inf"), *edges[1:-1], float("inf")]



def _histogram_proportions(series: pd.Series, bins: list[float]) -> list[float]:
    clean = pd.to_numeric(series, errors="coerce").dropna().astype(float)
    if clean.empty:
        return [0.0] * (len(bins) - 1)
    counts, _ = np.histogram(clean, bins=np.asarray(bins, dtype=float))
    total = counts.sum()
    if total == 0:
        return [0.0] * len(counts)
    return [float(value / total) for value in counts]



def build_monitoring_reference(
    features: pd.DataFrame,
    *,
    prediction_scores: np.ndarray | None,
    decision_threshold: float,
) -> dict[str, Any]:
    feature_frame = features.loc[:, MODEL_FEATURE_COLUMNS].copy()
    payload: dict[str, Any] = {
        "decision_threshold": float(decision_threshold),
        "feature_count": int(len(feature_frame)),
        "numeric_features": {},
        "categorical_features": {},
        "score_distribution": None,
        "positive_prediction_rate": None,
    }

    for column in MODEL_INPUT_NUMERIC_COLUMNS:
        series = pd.to_numeric(feature_frame[column], errors="coerce")
        bins = _build_numeric_bins(series)
        payload["numeric_features"][column] = {
            "min": float(series.min()) if series.notna().any() else None,
            "max": float(series.max()) if series.notna().any() else None,
            "missing_rate": float(series.isna().mean()),
            "bins": bins,
            "bin_proportions": _histogram_proportions(series, bins),
        }

    for column in MODEL_INPUT_CATEGORICAL_COLUMNS:
        normalized = feature_frame[column].fillna("<missing>").astype(str)
        proportions = normalized.value_counts(normalize=True).sort_index()
        payload["categorical_features"][column] = {
            "categories": proportions.index.tolist(),
            "proportions": [float(value) for value in proportions.tolist()],
            "missing_rate": float(feature_frame[column].isna().mean()),
        }

    if prediction_scores is not None:
        score_series = pd.Series(np.asarray(prediction_scores, dtype=float), name="score")
        score_bins = _build_numeric_bins(score_series)
        payload["score_distribution"] = {
            "bins": score_bins,
            "bin_proportions": _histogram_proportions(score_series, score_bins),
            "mean": float(score_series.mean()),
        }
        payload["positive_prediction_rate"] = float((score_series >= decision_threshold).mean())

    return payload



def write_monitoring_reference(payload: dict[str, Any], path: Path) -> Path:
    return write_json(payload, path)



def load_monitoring_reference(path: Path) -> dict[str, Any]:
    return load_json(path)
