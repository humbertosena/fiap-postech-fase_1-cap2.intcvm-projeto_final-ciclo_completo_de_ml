from __future__ import annotations

import json
from pathlib import Path

import joblib
import pytest

from src.models.io import write_json
from src.monitoring.reference import build_monitoring_reference
from src.serving.model_store import LoadedApprovedModel


class DummyApprovedPipeline:
    def predict_proba(self, frame):
        probability = 0.82 if float(frame.iloc[0]["oldpeak"]) >= 2.0 else 0.21
        return [[1.0 - probability, probability]]


@pytest.fixture()
def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


@pytest.fixture()
def valid_prediction_payload() -> dict[str, object]:
    return {
        "input_data": {
            "age": 63,
            "sex": "male",
            "chest_pain_type": "typical",
            "resting_blood_pressure": 145,
            "cholesterol": 233,
            "fasting_blood_sugar_gt_120": "yes",
            "rest_ecg": "normal",
            "max_heart_rate": 150,
            "exercise_induced_angina": "no",
            "oldpeak": 2.3,
            "slope": "flat",
            "num_vessels": 0,
            "thal": "normal",
        }
    }


@pytest.fixture()
def monitoring_reference_file(tmp_path: Path) -> Path:
    reference_frame = {
        "age": [63.0, 55.0, 48.0],
        "resting_blood_pressure": [145.0, 132.0, 128.0],
        "cholesterol": [233.0, 210.0, 199.0],
        "max_heart_rate": [150.0, 160.0, 170.0],
        "oldpeak": [2.3, 1.2, 0.4],
        "num_vessels": [0.0, 1.0, 0.0],
        "sex": ["male", "female", "male"],
        "chest_pain_type": ["typical", "asymptomatic", "non_anginal"],
        "fasting_blood_sugar_gt_120": ["yes", "no", "no"],
        "rest_ecg": ["normal", "abnormal", "normal"],
        "exercise_induced_angina": ["no", "yes", "no"],
        "slope": ["flat", "upsloping", "flat"],
        "thal": ["normal", "fixed_defect", "normal"],
    }
    import pandas as pd

    reference = build_monitoring_reference(
        pd.DataFrame(reference_frame),
        prediction_scores=[0.82, 0.55, 0.21],
        decision_threshold=0.35,
    )
    path = tmp_path / "monitoring_reference.json"
    write_json(reference, path)
    return path


@pytest.fixture()
def approved_model_bundle(
    tmp_path: Path,
    monitoring_reference_file: Path,
) -> LoadedApprovedModel:
    model_path = tmp_path / "training_pipeline.joblib"
    joblib.dump(DummyApprovedPipeline(), model_path)
    return LoadedApprovedModel(
        model=joblib.load(model_path),
        model_name="logistic_regression",
        run_id="run-approved-123",
        run_label="20260326T010000Z",
        decision_threshold=0.35,
        model_path=model_path,
        manifest_path=tmp_path / "latest_approved_model.json",
        monitoring_reference_path=monitoring_reference_file,
    )


@pytest.fixture()
def approved_manifest_files(
    tmp_path: Path,
    monitoring_reference_file: Path,
) -> tuple[Path, Path, Path]:
    model_path = tmp_path / "training_pipeline.joblib"
    joblib.dump(DummyApprovedPipeline(), model_path)
    manifest_path = tmp_path / "latest_approved_model.json"
    manifest_payload = {
        "run_id": "run-approved-123",
        "run_label": "20260326T010000Z",
        "model_name": "logistic_regression",
        "model_path": str(model_path),
        "project_relative_model_path": str(model_path),
        "monitoring_reference_path": str(monitoring_reference_file),
        "project_relative_monitoring_reference_path": str(monitoring_reference_file),
        "model_metadata": {
            "decision_threshold": 0.35,
        },
        "metrics": {
            "decision_threshold": 0.35,
        },
    }
    manifest_path.write_text(json.dumps(manifest_payload), encoding="utf-8")
    return manifest_path, model_path, monitoring_reference_file
