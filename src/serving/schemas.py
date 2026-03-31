from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from src.data.schema import MODEL_FEATURE_COLUMNS

_REQUIRED_FIELDS = set(MODEL_FEATURE_COLUMNS)
_NUMERIC_FIELDS = {
    "age",
    "resting_blood_pressure",
    "cholesterol",
    "max_heart_rate",
    "oldpeak",
    "num_vessels",
}
_OPTIONAL_FIELDS = {"num_vessels", "thal"}
_CATEGORY_ALIASES = {
    "sex": {
        "female": "fem",
        "fem": "fem",
        "male": "male",
    },
    "chest_pain_type": {
        "typical": "angina",
        "angina": "angina",
        "atypical": "abnang",
        "abnormal_angina": "abnang",
        "abnang": "abnang",
        "asymptomatic": "asympt",
        "asympt": "asympt",
        "non_anginal": "notang",
        "notang": "notang",
    },
    "fasting_blood_sugar_gt_120": {
        "yes": "true",
        "true": "true",
        "no": "fal",
        "false": "fal",
        "fal": "fal",
    },
    "rest_ecg": {
        "normal": "norm",
        "norm": "norm",
        "abnormal": "abn",
        "abn": "abn",
        "hypertrophy": "hyp",
        "hyp": "hyp",
    },
    "exercise_induced_angina": {
        "yes": "true",
        "true": "true",
        "no": "fal",
        "false": "fal",
        "fal": "fal",
    },
    "slope": {
        "upsloping": "up",
        "up": "up",
        "flat": "flat",
        "downsloping": "down",
        "down": "down",
    },
    "thal": {
        "normal": "norm",
        "norm": "norm",
        "fixed_defect": "fix",
        "fix": "fix",
        "reversible_defect": "rev",
        "rev": "rev",
    },
}


class PayloadValidationError(ValueError):
    pass


@dataclass(slots=True, frozen=True)
class PredictionInput:
    age: float
    sex: str
    chest_pain_type: str
    resting_blood_pressure: float
    cholesterol: float
    fasting_blood_sugar_gt_120: str
    rest_ecg: str
    max_heart_rate: float
    exercise_induced_angina: str
    oldpeak: float
    slope: str
    num_vessels: float | None
    thal: str | None

    def to_model_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class PredictionRequest:
    input_data: PredictionInput

    @staticmethod
    def _normalize_category(field_name: str, value: Any) -> str:
        normalized = str(value).strip().lower()
        aliases = _CATEGORY_ALIASES.get(field_name)
        if aliases is None:
            return normalized
        if normalized not in aliases:
            raise PayloadValidationError(
                f"Field '{field_name}' contains unsupported category '{value}'."
            )
        return aliases[normalized]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PredictionRequest":
        if not isinstance(payload, dict):
            raise PayloadValidationError("Payload must be a JSON object.")

        raw_input = payload.get("input_data")
        if not isinstance(raw_input, dict):
            raise PayloadValidationError("Field 'input_data' must be a JSON object.")

        missing_fields = sorted(_REQUIRED_FIELDS - set(raw_input))
        if missing_fields:
            raise PayloadValidationError(
                f"Missing required input fields: {', '.join(missing_fields)}."
            )

        unknown_fields = sorted(set(raw_input) - _REQUIRED_FIELDS)
        if unknown_fields:
            raise PayloadValidationError(
                f"Unknown input fields: {', '.join(unknown_fields)}."
            )

        normalized: dict[str, Any] = {}
        for field_name in MODEL_FEATURE_COLUMNS:
            value = raw_input[field_name]
            if value in (None, "") and field_name in _OPTIONAL_FIELDS:
                normalized[field_name] = None
                continue
            if value in (None, ""):
                raise PayloadValidationError(
                    f"Field '{field_name}' must not be null or empty."
                )
            if field_name in _NUMERIC_FIELDS:
                try:
                    normalized[field_name] = float(value)
                except (TypeError, ValueError) as exc:
                    raise PayloadValidationError(
                        f"Field '{field_name}' must be numeric."
                    ) from exc
                continue
            normalized[field_name] = cls._normalize_category(field_name, value)

        return cls(input_data=PredictionInput(**normalized))

    def to_model_payload(self) -> dict[str, Any]:
        return self.input_data.to_model_payload()

    def to_dict(self) -> dict[str, Any]:
        return {"input_data": self.to_model_payload()}


@dataclass(slots=True, frozen=True)
class PredictionResponse:
    prediction: int
    prediction_label: str
    positive_class_probability: float | None
    decision_threshold: float
    model_name: str
    model_run_id: str
    model_run_label: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class HealthResponse:
    status: str
    model_available: bool
    model_name: str | None
    model_run_id: str | None
    model_run_label: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class ErrorResponse:
    error: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def swagger_input_example() -> dict[str, Any]:
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
