from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src.config import settings
from src.data.ingest_mod import load_processed_dataset
from src.data.schema import (
    AGE_GROUP_BINS,
    AGE_GROUP_COLUMN,
    AGE_GROUP_LABELS,
    AUDIT_GROUP_COLUMNS,
    AUDIT_SOURCE_COLUMNS,
    MODEL_FEATURE_COLUMNS,
    MODEL_INPUT_CATEGORICAL_COLUMNS,
    MODEL_INPUT_NUMERIC_COLUMNS,
    PROCESSED_COLUMNS,
    TARGET_COLUMN,
)


@dataclass(frozen=True)
class DatasetBundle:
    features: pd.DataFrame
    target: pd.Series


@dataclass(frozen=True)
class SplitDataset:
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series


def build_audit_frame(frame: pd.DataFrame) -> pd.DataFrame:
    validated = validate_training_frame(frame)
    audit_frame = validated.loc[:, AUDIT_SOURCE_COLUMNS].copy()
    audit_frame[AGE_GROUP_COLUMN] = pd.cut(
        validated["age"],
        bins=AGE_GROUP_BINS,
        labels=AGE_GROUP_LABELS,
        right=False,
        include_lowest=True,
    ).astype("string")
    audit_frame["sex"] = audit_frame["sex"].astype("string")
    return audit_frame.loc[:, AUDIT_GROUP_COLUMNS].copy()



def validate_training_frame(frame: pd.DataFrame) -> pd.DataFrame:
    missing_columns = [column for column in PROCESSED_COLUMNS if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")

    validated = frame.copy()
    validated[TARGET_COLUMN] = pd.to_numeric(
        validated[TARGET_COLUMN],
        errors="raise",
    ).astype("int64")
    validated[list(MODEL_INPUT_NUMERIC_COLUMNS)] = validated[
        list(MODEL_INPUT_NUMERIC_COLUMNS)
    ].apply(pd.to_numeric, errors="coerce")

    categorical_frame = validated[list(MODEL_INPUT_CATEGORICAL_COLUMNS)].astype("object")
    validated[list(MODEL_INPUT_CATEGORICAL_COLUMNS)] = categorical_frame.where(
        categorical_frame.notna(),
        np.nan,
    )
    return validated



def load_training_frame(path: Path | None = None) -> pd.DataFrame:
    frame = load_processed_dataset(path or settings.processed_data_path)
    return validate_training_frame(frame)



def build_dataset_bundle(frame: pd.DataFrame) -> DatasetBundle:
    validated = validate_training_frame(frame)
    return DatasetBundle(
        features=validated.loc[:, MODEL_FEATURE_COLUMNS].copy(),
        target=validated.loc[:, TARGET_COLUMN].copy(),
    )



def split_training_dataset(
    frame: pd.DataFrame,
    *,
    test_size: float | None = None,
    random_state: int | None = None,
    stratify: bool = True,
) -> SplitDataset:
    dataset = build_dataset_bundle(frame)
    ratio = settings.train_test_split_ratio if test_size is None else test_size
    seed = settings.random_state if random_state is None else random_state
    stratify_target = dataset.target if stratify else None

    X_train, X_test, y_train, y_test = train_test_split(
        dataset.features,
        dataset.target,
        test_size=ratio,
        random_state=seed,
        stratify=stratify_target,
    )
    return SplitDataset(X_train=X_train, X_test=X_test, y_train=y_train, y_test=y_test)
