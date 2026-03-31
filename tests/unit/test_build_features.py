from __future__ import annotations

from sklearn.linear_model import LogisticRegression

from src.features.build_features import build_feature_pipeline


def test_build_feature_pipeline_contains_preprocessor_and_model() -> None:
    pipeline = build_feature_pipeline(LogisticRegression())
    assert "preprocessor" in pipeline.named_steps
    assert "model" in pipeline.named_steps
