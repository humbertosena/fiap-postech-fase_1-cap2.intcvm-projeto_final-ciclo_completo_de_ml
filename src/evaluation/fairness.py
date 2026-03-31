from __future__ import annotations

from typing import Any

import pandas as pd

from src.config import settings
from src.data.dataset import build_audit_frame
from src.data.schema import AUDIT_GROUP_COLUMNS
from src.evaluation.metrics import (
    compute_classification_metrics,
    compute_error_rates,
    extract_confusion_counts,
)

FAIRNESS_METRICS = (
    "precision",
    "recall",
    "f1",
    "false_negative_rate",
    "false_positive_rate",
)
UNAVAILABLE_DIMENSIONS = {
    "region": "Dataset atual nao contem atributo literal de regiao."
}


def build_audit_groups(frame: pd.DataFrame) -> pd.DataFrame:
    if set(AUDIT_GROUP_COLUMNS).issubset(frame.columns):
        return frame.loc[:, AUDIT_GROUP_COLUMNS].copy()
    return build_audit_frame(frame)


def _normalize_series(values: Any) -> pd.Series:
    series = pd.Series(values).reset_index(drop=True)
    if str(series.dtype).startswith("int"):
        return series.astype("int64")
    return series


def _group_metrics(
    group_frame: pd.DataFrame,
    *,
    group_name: str,
    group_value: str,
) -> dict[str, Any]:
    y_true = group_frame["y_true"]
    y_pred = group_frame["y_pred"]
    metrics = compute_classification_metrics(y_true, y_pred)
    error_rates = compute_error_rates(y_true, y_pred)
    confusion_counts = extract_confusion_counts(y_true, y_pred)
    sample_size = int(len(group_frame))
    positive_count = int(y_true.sum())
    negative_count = int(sample_size - positive_count)

    payload = {
        "group": group_name,
        "value": str(group_value),
        "sample_size": sample_size,
        "positive_count": positive_count,
        "negative_count": negative_count,
        **metrics,
        **error_rates,
        "confusion_counts": confusion_counts,
        "low_support": sample_size < settings.fairness_min_group_size,
    }
    return payload


def evaluate_group_fairness(
    audit_frame: pd.DataFrame,
    y_true: Any,
    y_pred: Any,
) -> dict[str, list[dict[str, Any]]]:
    groups = build_audit_groups(audit_frame).reset_index(drop=True).copy()
    groups["y_true"] = _normalize_series(y_true)
    groups["y_pred"] = _normalize_series(y_pred)

    report: dict[str, list[dict[str, Any]]] = {}
    for group_column in AUDIT_GROUP_COLUMNS:
        grouped_metrics: list[dict[str, Any]] = []
        for group_value, group_frame in groups.groupby(group_column, dropna=False):
            grouped_metrics.append(
                _group_metrics(
                    group_frame.reset_index(drop=True),
                    group_name=group_column,
                    group_value="missing" if pd.isna(group_value) else str(group_value),
                )
            )
        grouped_metrics.sort(key=lambda item: item["value"])
        report[group_column] = grouped_metrics
    return report


def calculate_group_gaps(
    grouped_metrics: dict[str, list[dict[str, Any]]],
) -> dict[str, dict[str, dict[str, Any]]]:
    gaps: dict[str, dict[str, dict[str, Any]]] = {}
    for group_name, entries in grouped_metrics.items():
        group_gap: dict[str, dict[str, Any]] = {}
        for metric_name in FAIRNESS_METRICS:
            values = [(entry["value"], float(entry[metric_name])) for entry in entries]
            max_group, max_value = max(values, key=lambda item: item[1])
            min_group, min_value = min(values, key=lambda item: item[1])
            group_gap[metric_name] = {
                "max_gap": float(max_value - min_value),
                "highest_group": str(max_group),
                "highest_value": float(max_value),
                "lowest_group": str(min_group),
                "lowest_value": float(min_value),
                "alert": bool((max_value - min_value) > settings.fairness_alert_threshold),
            }
        gaps[group_name] = group_gap
    return gaps


def summarize_fairness_alerts(
    gap_summary: dict[str, dict[str, dict[str, Any]]],
) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    for group_name, metrics in gap_summary.items():
        for metric_name, summary in metrics.items():
            if summary["alert"]:
                alerts.append(
                    {
                        "group": group_name,
                        "metric": metric_name,
                        "max_gap": float(summary["max_gap"]),
                        "threshold": float(settings.fairness_alert_threshold),
                        "highest_group": summary["highest_group"],
                        "lowest_group": summary["lowest_group"],
                    }
                )
    return alerts


def build_fairness_report(
    audit_frame: pd.DataFrame,
    y_true: Any,
    y_pred: Any,
    *,
    decision_threshold: float,
) -> dict[str, Any]:
    grouped_metrics = evaluate_group_fairness(audit_frame, y_true, y_pred)
    gap_summary = calculate_group_gaps(grouped_metrics)
    alerts = summarize_fairness_alerts(gap_summary)
    return {
        "policy": {
            "name": settings.fairness_policy_name,
            "decision_threshold": float(decision_threshold),
            "gap_alert_threshold": float(settings.fairness_alert_threshold),
            "min_group_size": int(settings.fairness_min_group_size),
            "evaluated_groups": list(AUDIT_GROUP_COLUMNS),
            "unavailable_dimensions": UNAVAILABLE_DIMENSIONS,
        },
        "group_metrics": grouped_metrics,
        "group_gaps": gap_summary,
        "alerts": alerts,
        "summary": {
            "alert_count": len(alerts),
            "groups_with_alerts": sorted({alert["group"] for alert in alerts}),
            "limited_confidence_groups": sorted(
                {
                    f"{entry['group']}::{entry['value']}"
                    for entries in grouped_metrics.values()
                    for entry in entries
                    if entry["low_support"]
                }
            ),
        },
    }


def extract_fairness_mlflow_metrics(
    fairness_report: dict[str, Any],
) -> dict[str, float]:
    metrics: dict[str, float] = {}
    metric_aliases = {
        "precision": "precision",
        "recall": "recall",
        "false_negative_rate": "false_negative_rate",
    }
    for group_name, metric_summaries in fairness_report["group_gaps"].items():
        for metric_name, alias in metric_aliases.items():
            metrics[f"fairness_{group_name}_{alias}_max_gap"] = float(
                metric_summaries[metric_name]["max_gap"]
            )
    metrics["fairness_alert_count"] = float(fairness_report["summary"]["alert_count"])
    return metrics


def build_fairness_executive_summary(fairness_report: dict[str, Any]) -> str:
    lines = [
        f"Politica: {fairness_report['policy']['name']}",
        f"Threshold: {fairness_report['policy']['decision_threshold']:.2f}",
        f"Alertas: {fairness_report['summary']['alert_count']}",
    ]
    if fairness_report["alerts"]:
        lines.append("Principais gaps acima do limite:")
        for alert in fairness_report["alerts"]:
            lines.append(
                "- "
                f"{alert['group']}::{alert['metric']} gap={alert['max_gap']:.4f} "
                f"({alert['lowest_group']} -> {alert['highest_group']})"
            )
    else:
        lines.append("Nenhum gap acima do limite configurado.")

    if fairness_report["summary"]["limited_confidence_groups"]:
        lines.append(
            "Grupos com baixa amostra: "
            + ", ".join(fairness_report["summary"]["limited_confidence_groups"])
        )
    lines.append("Regiao: nao calculada por ausencia do atributo no dataset atual.")
    return "\n".join(lines)
