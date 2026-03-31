from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.data.schema import MODEL_INPUT_CATEGORICAL_COLUMNS, MODEL_INPUT_NUMERIC_COLUMNS


def build_preprocessor(*, scale_numeric: bool = True) -> ColumnTransformer:
    numeric_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))

    categorical_steps = [
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ]

    return ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline(steps=numeric_steps),
                list(MODEL_INPUT_NUMERIC_COLUMNS),
            ),
            (
                "categorical",
                Pipeline(steps=categorical_steps),
                list(MODEL_INPUT_CATEGORICAL_COLUMNS),
            ),
        ]
    )
