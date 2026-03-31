from __future__ import annotations

from src.models.train import train_model


def test_train_model_returns_real_metrics() -> None:
    result = train_model(log_to_mlflow=False)
    assert result["status"] == "trained"
    assert result["metrics"]["recall"] >= 0.0
    assert result["metrics"]["precision"] >= 0.0
    assert result["metrics"]["f1"] >= 0.0
    assert 0.0 <= result["metrics"]["decision_threshold"] <= 1.0
    assert result["threshold_selection"]["selected_threshold"] == result["metrics"][
        "decision_threshold"
    ]
    assert result["artifacts"]["threshold_summary_path"]
    assert result["fairness"]["policy"]["decision_threshold"] == result["metrics"][
        "decision_threshold"
    ]
    assert "fairness_report_path" in result["artifacts"]
    assert "risk_summary_path" in result["artifacts"]
    assert "monitoring_reference_path" in result["artifacts"]
