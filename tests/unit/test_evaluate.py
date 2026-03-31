from __future__ import annotations

from src.evaluation.evaluate import evaluate_pipeline


def test_evaluate_pipeline_returns_metrics() -> None:
    result = evaluate_pipeline()
    assert result["status"] == "evaluated"
    assert "metrics" in result
    assert "recall" in result["metrics"]
    assert "fairness" in result
    assert "policy" in result["fairness"]
