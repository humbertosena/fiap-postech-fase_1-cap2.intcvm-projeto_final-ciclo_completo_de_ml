from __future__ import annotations

from src.data.dataset import load_training_frame, split_training_dataset
from src.data.schema import MODEL_FEATURE_COLUMNS, TARGET_COLUMN


def test_training_frame_contains_expected_columns() -> None:
    frame = load_training_frame()
    assert TARGET_COLUMN in frame.columns
    assert set(MODEL_FEATURE_COLUMNS).issubset(frame.columns)



def test_split_is_reproducible() -> None:
    frame = load_training_frame()
    first = split_training_dataset(frame, random_state=42)
    second = split_training_dataset(frame, random_state=42)

    assert first.X_train.equals(second.X_train)
    assert first.X_test.equals(second.X_test)
    assert first.y_train.equals(second.y_train)
    assert first.y_test.equals(second.y_test)
