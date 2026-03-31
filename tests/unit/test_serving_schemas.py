from __future__ import annotations

import pytest

from src.serving.schemas import PayloadValidationError, PredictionRequest, swagger_input_example


def test_prediction_request_normalizes_payload() -> None:
    payload = swagger_input_example()

    request = PredictionRequest.from_dict(payload)

    model_payload = request.to_model_payload()
    assert model_payload["age"] == 63.0
    assert model_payload["num_vessels"] == 0.0
    assert model_payload["sex"] == "male"
    assert model_payload["chest_pain_type"] == "angina"
    assert model_payload["fasting_blood_sugar_gt_120"] == "true"
    assert model_payload["rest_ecg"] == "norm"
    assert model_payload["exercise_induced_angina"] == "fal"
    assert model_payload["thal"] == "norm"



def test_prediction_request_rejects_missing_fields() -> None:
    with pytest.raises(PayloadValidationError):
        PredictionRequest.from_dict({"input_data": {"age": 63}})


def test_prediction_request_rejects_unknown_category() -> None:
    payload = swagger_input_example()
    payload["input_data"]["sex"] = "unknown"

    with pytest.raises(PayloadValidationError):
        PredictionRequest.from_dict(payload)


def test_swagger_input_example_is_valid_request() -> None:
    request = PredictionRequest.from_dict(swagger_input_example())
    assert request.to_model_payload()["thal"] == "norm"
