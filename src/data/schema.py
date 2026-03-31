from dataclasses import dataclass

EXPECTED_TOKEN_COUNT = 15
TARGET_NEGATIVE_LABEL = "buff"
TARGET_POSITIVE_LABEL = "sick"
TARGET_COLUMN = "target"

RAW_COLUMNS = (
    "age",
    "sex",
    "chest_pain_type",
    "resting_blood_pressure",
    "cholesterol",
    "fasting_blood_sugar_gt_120",
    "rest_ecg",
    "max_heart_rate",
    "exercise_induced_angina",
    "oldpeak",
    "slope",
    "num_vessels",
    "thal",
    "diagnosis_label",
    "diagnosis_code",
)

NUMERIC_COLUMNS = (
    "age",
    "resting_blood_pressure",
    "cholesterol",
    "max_heart_rate",
    "oldpeak",
    "num_vessels",
)

CATEGORICAL_COLUMNS = (
    "sex",
    "chest_pain_type",
    "fasting_blood_sugar_gt_120",
    "rest_ecg",
    "exercise_induced_angina",
    "slope",
    "thal",
    "diagnosis_label",
    "diagnosis_code",
)

PROCESSED_COLUMNS = RAW_COLUMNS + (TARGET_COLUMN,)
LEAKAGE_COLUMNS = ("diagnosis_label", "diagnosis_code", TARGET_COLUMN)
MODEL_INPUT_NUMERIC_COLUMNS = NUMERIC_COLUMNS
MODEL_INPUT_CATEGORICAL_COLUMNS = (
    "sex",
    "chest_pain_type",
    "fasting_blood_sugar_gt_120",
    "rest_ecg",
    "exercise_induced_angina",
    "slope",
    "thal",
)
MODEL_FEATURE_COLUMNS = MODEL_INPUT_NUMERIC_COLUMNS + MODEL_INPUT_CATEGORICAL_COLUMNS
AUDIT_SOURCE_COLUMNS = ("age", "sex")
AUDIT_GROUP_COLUMNS = ("age_group", "sex")
AGE_GROUP_COLUMN = "age_group"
AGE_GROUP_BINS = (0.0, 45.0, 55.0, 65.0, float("inf"))
AGE_GROUP_LABELS = ("lt_45", "45_54", "55_64", "65_plus")


@dataclass(frozen=True)
class ColumnDefinition:
    name: str
    dtype: str
    description: str
    nullable: bool


COLUMN_DEFINITIONS = (
    ColumnDefinition("age", "float", "Age in years.", False),
    ColumnDefinition("sex", "string", "Biological sex as represented in the dataset.", False),
    ColumnDefinition("chest_pain_type", "string", "Chest pain category.", False),
    ColumnDefinition("resting_blood_pressure", "float", "Resting blood pressure.", False),
    ColumnDefinition("cholesterol", "float", "Serum cholesterol.", False),
    ColumnDefinition(
        "fasting_blood_sugar_gt_120",
        "string",
        "Whether fasting blood sugar is above 120 mg/dl.",
        False,
    ),
    ColumnDefinition("rest_ecg", "string", "Resting ECG result.", False),
    ColumnDefinition("max_heart_rate", "float", "Maximum heart rate achieved.", False),
    ColumnDefinition(
        "exercise_induced_angina", "string", "Whether exercise induced angina was observed.", False
    ),
    ColumnDefinition("oldpeak", "float", "ST depression induced by exercise.", False),
    ColumnDefinition("slope", "string", "Slope of peak exercise ST segment.", False),
    ColumnDefinition("num_vessels", "float", "Number of colored vessels.", True),
    ColumnDefinition("thal", "string", "Thalassemia category.", True),
    ColumnDefinition("diagnosis_label", "string", "High level label.", False),
    ColumnDefinition("diagnosis_code", "string", "Compact diagnosis code.", False),
    ColumnDefinition(
        AGE_GROUP_COLUMN,
        "string",
        "Age band used only for fairness auditing.",
        False,
    ),
    ColumnDefinition(TARGET_COLUMN, "int", "Binary target derived from diagnosis_label.", False),
)
