from __future__ import annotations

from sklearn.base import ClassifierMixin
from sklearn.pipeline import Pipeline

from src.features.preprocessing import build_preprocessor


def build_feature_pipeline(
    estimator: ClassifierMixin,
    *,
    scale_numeric: bool = True,
) -> Pipeline:
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor(scale_numeric=scale_numeric)),
            ("model", estimator),
        ]
    )
