from __future__ import annotations

import pandas as pd

from src.data.dataset import build_audit_frame, load_training_frame
from src.evaluation.fairness import (
    build_fairness_executive_summary,
    build_fairness_report,
    calculate_group_gaps,
    evaluate_group_fairness,
    extract_fairness_mlflow_metrics,
)


def test_build_audit_frame_derives_expected_groups() -> None:
    frame = load_training_frame().head(4)
    audit = build_audit_frame(frame)

    assert list(audit.columns) == ["age_group", "sex"]
    assert audit.iloc[0]["age_group"] == "55_64"
    assert audit.iloc[3]["age_group"] == "lt_45"



def test_evaluate_group_fairness_returns_metrics_per_group() -> None:
    audit = pd.DataFrame(
        {
            "age": [40.0, 40.0, 58.0, 58.0],
            "sex": ["male", "male", "fem", "fem"],
            "target": [0, 1, 0, 1],
            "resting_blood_pressure": [120.0, 120.0, 140.0, 140.0],
            "cholesterol": [200.0, 200.0, 230.0, 230.0],
            "max_heart_rate": [150.0, 150.0, 130.0, 130.0],
            "oldpeak": [1.0, 1.0, 2.0, 2.0],
            "num_vessels": [0.0, 0.0, 1.0, 1.0],
            "chest_pain_type": ["typical", "typical", "asymptomatic", "asymptomatic"],
            "fasting_blood_sugar_gt_120": ["no", "no", "yes", "yes"],
            "rest_ecg": ["normal", "normal", "abnormal", "abnormal"],
            "exercise_induced_angina": ["no", "no", "yes", "yes"],
            "slope": ["upsloping", "upsloping", "flat", "flat"],
            "thal": ["normal", "normal", "reversible", "reversible"],
            "diagnosis_label": ["buff", "sick", "buff", "sick"],
            "diagnosis_code": ["<50", ">50_1", "<50", ">50_1"],
        }
    )
    grouped = evaluate_group_fairness(audit, [0, 1, 0, 1], [0, 1, 1, 1])

    assert set(grouped) == {"age_group", "sex"}
    lt_45 = next(item for item in grouped["age_group"] if item["value"] == "lt_45")
    assert lt_45["sample_size"] == 2
    assert lt_45["recall"] == 1.0
    assert lt_45["false_positive_rate"] == 0.0

    gap_summary = calculate_group_gaps(grouped)
    assert gap_summary["sex"]["precision"]["max_gap"] >= 0.0



def test_build_fairness_report_and_mlflow_metrics() -> None:
    audit = pd.DataFrame(
        {
            "age": [40.0, 41.0, 58.0, 59.0],
            "sex": ["male", "male", "fem", "fem"],
            "target": [0, 1, 0, 1],
            "resting_blood_pressure": [120.0, 122.0, 138.0, 140.0],
            "cholesterol": [200.0, 210.0, 230.0, 240.0],
            "max_heart_rate": [150.0, 148.0, 132.0, 130.0],
            "oldpeak": [1.0, 1.1, 2.0, 2.2],
            "num_vessels": [0.0, 0.0, 1.0, 1.0],
            "chest_pain_type": ["typical", "typical", "asymptomatic", "asymptomatic"],
            "fasting_blood_sugar_gt_120": ["no", "no", "yes", "yes"],
            "rest_ecg": ["normal", "normal", "abnormal", "abnormal"],
            "exercise_induced_angina": ["no", "no", "yes", "yes"],
            "slope": ["upsloping", "upsloping", "flat", "flat"],
            "thal": ["normal", "normal", "reversible", "reversible"],
            "diagnosis_label": ["buff", "sick", "buff", "sick"],
            "diagnosis_code": ["<50", ">50_1", "<50", ">50_1"],
        }
    )
    report = build_fairness_report(audit, [0, 1, 0, 1], [0, 1, 1, 1], decision_threshold=0.35)

    assert report["policy"]["decision_threshold"] == 0.35
    assert report["policy"]["unavailable_dimensions"]["region"]
    assert "age_group" in report["group_metrics"]
    assert report["summary"]["alert_count"] >= 0

    mlflow_metrics = extract_fairness_mlflow_metrics(report)
    assert "fairness_age_group_recall_max_gap" in mlflow_metrics

    summary = build_fairness_executive_summary(report)
    assert "Regiao: nao calculada" in summary
