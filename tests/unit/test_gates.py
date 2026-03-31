from __future__ import annotations

from src.evaluation.gates import evaluate_release_gates


def _training_result(
    *,
    recall: float = 0.8571,
    precision: float = 0.7059,
    alert_count: int = 2,
) -> dict[str, object]:
    return {
        "metrics": {
            "accuracy": 0.77,
            "precision": precision,
            "recall": recall,
            "f1": 0.77,
            "decision_threshold": 0.35,
        },
        "threshold_selection": {
            "selected_threshold": 0.35,
            "used_precision_constraint": True,
        },
        "fairness": {
            "policy": {
                "gap_alert_threshold": 0.15,
                "min_group_size": 10,
                "unavailable_dimensions": {
                    "region": "Dataset atual nao contem atributo literal de regiao."
                },
            },
            "summary": {
                "alert_count": alert_count,
                "limited_confidence_groups": [],
            },
            "group_gaps": {},
        },
    }



def test_release_gates_approve_with_alerts() -> None:
    report = evaluate_release_gates(_training_result())

    assert report["status"] == "approved_with_alerts"
    assert report["summary"]["promotion_eligible"] is True
    assert report["summary"]["blocking_failures"] == 0
    assert report["summary"]["active_alerts"] >= 1



def test_release_gates_block_on_low_recall() -> None:
    report = evaluate_release_gates(_training_result(recall=0.72, alert_count=0))

    assert report["status"] == "blocked"
    assert report["summary"]["promotion_eligible"] is False
    failed_checks = [check for check in report["blocking_checks"] if check["status"] == "failed"]
    assert any(check["name"] == "minimum_recall" for check in failed_checks)
