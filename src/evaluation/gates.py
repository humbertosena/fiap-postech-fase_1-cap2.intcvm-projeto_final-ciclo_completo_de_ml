from __future__ import annotations

from typing import Any

from src.config import settings

APPROVED_RELEASE_STATUSES = {"approved", "approved_with_alerts"}


def _build_check(
    *,
    name: str,
    status: str,
    message: str,
    details: dict[str, Any],
) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "message": message,
        "details": details,
    }


def _blocking_checks(training_result: dict[str, Any]) -> list[dict[str, Any]]:
    metrics = training_result["metrics"]
    threshold_selection = training_result["threshold_selection"]
    checks: list[dict[str, Any]] = []

    recall_value = float(metrics["recall"])
    checks.append(
        _build_check(
            name="minimum_recall",
            status="passed" if recall_value >= settings.release_gate_min_recall else "failed",
            message=(
                f"Recall {recall_value:.4f} atende ao minimo "
                f"{settings.release_gate_min_recall:.4f}."
                if recall_value >= settings.release_gate_min_recall
                else (
                    f"Recall {recall_value:.4f} abaixo do minimo "
                    f"{settings.release_gate_min_recall:.4f}."
                )
            ),
            details={
                "actual": recall_value,
                "expected_min": float(settings.release_gate_min_recall),
            },
        )
    )

    precision_value = float(metrics["precision"])
    checks.append(
        _build_check(
            name="minimum_precision",
            status=(
                "passed"
                if precision_value >= settings.release_gate_min_precision
                else "failed"
            ),
            message=(
                f"Precision {precision_value:.4f} atende ao minimo "
                f"{settings.release_gate_min_precision:.4f}."
                if precision_value >= settings.release_gate_min_precision
                else (
                    f"Precision {precision_value:.4f} abaixo do minimo "
                    f"{settings.release_gate_min_precision:.4f}."
                )
            ),
            details={
                "actual": precision_value,
                "expected_min": float(settings.release_gate_min_precision),
            },
        )
    )

    decision_threshold = float(metrics["decision_threshold"])
    threshold_locked = abs(decision_threshold - settings.approved_decision_threshold) < 1e-9
    checks.append(
        _build_check(
            name="approved_threshold_lock",
            status="passed" if threshold_locked else "failed",
            message=(
                f"Threshold operacional {decision_threshold:.2f} respeita o contrato aprovado."
                if threshold_locked
                else (
                    f"Threshold operacional {decision_threshold:.2f} difere do contrato aprovado "
                    f"{settings.approved_decision_threshold:.2f}."
                )
            ),
            details={
                "actual": decision_threshold,
                "expected": float(settings.approved_decision_threshold),
            },
        )
    )

    used_precision_constraint = bool(threshold_selection["used_precision_constraint"])
    checks.append(
        _build_check(
            name="threshold_precision_constraint",
            status="passed" if used_precision_constraint else "failed",
            message=(
                "Threshold vencedor respeitou o piso minimo de precision."
                if used_precision_constraint
                else (
                    "Threshold vencedor foi escolhido sem conseguir respeitar "
                    "o piso minimo de precision."
                )
            ),
            details={
                "used_precision_constraint": used_precision_constraint,
                "expected": True,
            },
        )
    )
    return checks


def _alert_checks(training_result: dict[str, Any]) -> list[dict[str, Any]]:
    fairness = training_result["fairness"]
    summary = fairness["summary"]
    policy = fairness["policy"]
    checks: list[dict[str, Any]] = []

    alert_count = int(summary["alert_count"])
    checks.append(
        _build_check(
            name="fairness_gap_alerts",
            status="alert" if alert_count > 0 else "passed",
            message=(
                f"Foram encontrados {alert_count} alertas de fairness acima do limite configurado."
                if alert_count > 0
                else "Nenhum alerta de fairness acima do limite configurado."
            ),
            details={
                "alert_count": alert_count,
                "gap_alert_threshold": float(policy["gap_alert_threshold"]),
            },
        )
    )

    limited_confidence_groups = list(summary["limited_confidence_groups"])
    checks.append(
        _build_check(
            name="limited_confidence_groups",
            status="alert" if limited_confidence_groups else "passed",
            message=(
                "Existem grupos com baixa amostra na auditoria."
                if limited_confidence_groups
                else "Nenhum grupo com baixa amostra na auditoria."
            ),
            details={
                "groups": limited_confidence_groups,
                "min_group_size": int(policy["min_group_size"]),
            },
        )
    )

    unavailable_dimensions = dict(policy["unavailable_dimensions"])
    region_unavailable = "region" in unavailable_dimensions
    checks.append(
        _build_check(
            name="region_fairness_unavailable",
            status="alert" if region_unavailable else "passed",
            message=(
                "Fairness por regiao continua indisponivel no dataset atual."
                if region_unavailable
                else "Fairness por regiao disponivel para auditoria."
            ),
            details={
                "unavailable_dimensions": unavailable_dimensions,
            },
        )
    )
    return checks


def evaluate_release_gates(training_result: dict[str, Any]) -> dict[str, Any]:
    blocking_checks = _blocking_checks(training_result)
    alert_checks = _alert_checks(training_result)

    blocking_failures = [check for check in blocking_checks if check["status"] == "failed"]
    active_alerts = [check for check in alert_checks if check["status"] == "alert"]

    if blocking_failures:
        status = "blocked"
    elif active_alerts:
        status = "approved_with_alerts"
    else:
        status = "approved"

    return {
        "status": status,
        "summary": {
            "promotion_eligible": status in APPROVED_RELEASE_STATUSES,
            "blocking_failures": len(blocking_failures),
            "active_alerts": len(active_alerts),
        },
        "blocking_checks": blocking_checks,
        "alert_checks": alert_checks,
    }
