from __future__ import annotations

from sklearn.base import ClassifierMixin
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from src.config import settings


def get_baseline_estimator(model_name: str | None = None) -> ClassifierMixin:
    selected = model_name or settings.baseline_model_name

    if selected == "logistic_regression":
        return LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=settings.random_state,
        )

    if selected == "random_forest":
        return RandomForestClassifier(
            n_estimators=300,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=settings.random_state,
        )

    raise ValueError(f"Unsupported baseline model: {selected}")
