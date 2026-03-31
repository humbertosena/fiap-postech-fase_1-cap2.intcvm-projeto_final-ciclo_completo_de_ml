from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def compute_classification_metrics(
    y_true: Any,
    y_pred: Any,
    *,
    y_score: Any | None = None,
) -> dict[str, float]:
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }

    if y_score is not None:
        metrics["roc_auc"] = float(roc_auc_score(y_true, y_score))

    return metrics



def build_classification_report(y_true: Any, y_pred: Any) -> dict[str, Any]:
    return classification_report(y_true, y_pred, output_dict=True, zero_division=0)



def build_confusion_matrix(y_true: Any, y_pred: Any) -> np.ndarray:
    return confusion_matrix(y_true, y_pred, labels=[0, 1])


def extract_confusion_counts(y_true: Any, y_pred: Any) -> dict[str, int]:
    matrix = build_confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = matrix.ravel()
    return {
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
    }


def compute_error_rates(y_true: Any, y_pred: Any) -> dict[str, float]:
    counts = extract_confusion_counts(y_true, y_pred)
    negative_total = counts["true_negative"] + counts["false_positive"]
    positive_total = counts["true_positive"] + counts["false_negative"]
    false_positive_rate = counts["false_positive"] / negative_total if negative_total else 0.0
    false_negative_rate = counts["false_negative"] / positive_total if positive_total else 0.0
    return {
        "false_positive_rate": float(false_positive_rate),
        "false_negative_rate": float(false_negative_rate),
    }



def apply_threshold(y_score: Any, threshold: float) -> np.ndarray:
    scores = np.asarray(y_score, dtype=float)
    return (scores >= threshold).astype(int)



def select_threshold_by_recall(
    y_true: Any,
    y_score: Any,
    *,
    candidate_thresholds: list[float],
    min_precision: float,
) -> dict[str, Any]:
    evaluations: list[dict[str, float]] = []

    for threshold in candidate_thresholds:
        predictions = apply_threshold(y_score, threshold)
        metrics = compute_classification_metrics(y_true, predictions, y_score=y_score)
        evaluations.append(
            {
                "threshold": float(threshold),
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "f1": metrics["f1"],
                "accuracy": metrics["accuracy"],
            }
        )

    eligible = [item for item in evaluations if item["precision"] >= min_precision]
    ranked = eligible if eligible else evaluations
    best = max(
        ranked,
        key=lambda item: (item["recall"], item["f1"], item["precision"], -item["threshold"]),
    )

    return {
        "selected_threshold": best["threshold"],
        "min_precision": float(min_precision),
        "used_precision_constraint": bool(eligible),
        "threshold_grid": evaluations,
    }
