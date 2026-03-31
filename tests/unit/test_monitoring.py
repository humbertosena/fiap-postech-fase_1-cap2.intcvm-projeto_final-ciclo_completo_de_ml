from __future__ import annotations

from src.monitoring.data_quality import build_data_quality_report
from src.monitoring.drift import build_drift_report
from src.monitoring.reporting import build_operational_summary
from src.monitoring.triggers import evaluate_monitoring_triggers


def test_monitoring_reports_detect_drift_and_quality_issues() -> None:
    reference = {
        "numeric_features": {
            "age": {
                "min": 40.0,
                "max": 70.0,
                "bins": [float("-inf"), 50.0, 60.0, float("inf")],
                "bin_proportions": [0.3, 0.4, 0.3],
            },
            "resting_blood_pressure": {
                "min": 110.0,
                "max": 150.0,
                "bins": [float("-inf"), 120.0, 140.0, float("inf")],
                "bin_proportions": [0.3, 0.4, 0.3],
            },
            "cholesterol": {
                "min": 150.0,
                "max": 260.0,
                "bins": [float("-inf"), 200.0, 240.0, float("inf")],
                "bin_proportions": [0.3, 0.4, 0.3],
            },
            "max_heart_rate": {
                "min": 120.0,
                "max": 180.0,
                "bins": [float("-inf"), 140.0, 160.0, float("inf")],
                "bin_proportions": [0.3, 0.4, 0.3],
            },
            "oldpeak": {
                "min": 0.0,
                "max": 4.0,
                "bins": [float("-inf"), 1.0, 2.0, float("inf")],
                "bin_proportions": [0.3, 0.4, 0.3],
            },
            "num_vessels": {
                "min": 0.0,
                "max": 3.0,
                "bins": [float("-inf"), 1.0, 2.0, float("inf")],
                "bin_proportions": [0.5, 0.3, 0.2],
            },
        },
        "categorical_features": {
            "sex": {"categories": ["female", "male"], "proportions": [0.4, 0.6]},
            "chest_pain_type": {"categories": ["typical"], "proportions": [1.0]},
            "fasting_blood_sugar_gt_120": {
                "categories": ["no", "yes"],
                "proportions": [0.5, 0.5],
            },
            "rest_ecg": {"categories": ["normal"], "proportions": [1.0]},
            "exercise_induced_angina": {"categories": ["no"], "proportions": [1.0]},
            "slope": {"categories": ["flat"], "proportions": [1.0]},
            "thal": {"categories": ["normal"], "proportions": [1.0]},
        },
        "score_distribution": {
            "bins": [float("-inf"), 0.3, 0.6, float("inf")],
            "bin_proportions": [0.4, 0.4, 0.2],
        },
        "positive_prediction_rate": 0.4,
    }
    inference_events = [
        {
            "prediction": 1,
            "positive_class_probability": 0.95,
            "features": {
                "age": 72.0,
                "resting_blood_pressure": 170.0,
                "cholesterol": 290.0,
                "max_heart_rate": 118.0,
                "oldpeak": 4.5,
                "num_vessels": 3.0,
                "sex": "male",
                "chest_pain_type": "atypical",
                "fasting_blood_sugar_gt_120": "yes",
                "rest_ecg": "normal",
                "exercise_induced_angina": "no",
                "slope": "flat",
                "thal": "reversible_defect",
            },
        },
        {
            "prediction": 1,
            "positive_class_probability": 0.91,
            "features": {
                "age": 75.0,
                "resting_blood_pressure": 168.0,
                "cholesterol": 295.0,
                "max_heart_rate": 119.0,
                "oldpeak": 4.2,
                "num_vessels": 3.0,
                "sex": "male",
                "chest_pain_type": "atypical",
                "fasting_blood_sugar_gt_120": "yes",
                "rest_ecg": "normal",
                "exercise_induced_angina": "no",
                "slope": "flat",
                "thal": "reversible_defect",
            },
        },
    ]
    api_events = [
        {
            "event_type": "prediction_completed",
            "endpoint": "/predict",
            "latency_ms": 10.0,
            "status_code": 200,
        },
        {
            "event_type": "prediction_completed",
            "endpoint": "/predict",
            "latency_ms": 12.0,
            "status_code": 200,
        },
    ]

    operational_summary = build_operational_summary(api_events, inference_events)
    quality_report = build_data_quality_report(inference_events, api_events, reference)
    drift_report = build_drift_report(inference_events, reference)
    trigger_report = evaluate_monitoring_triggers(
        operational_summary,
        quality_report,
        drift_report,
    )

    assert quality_report["numeric_features"]["age"]["out_of_range_rate"] > 0.0
    assert quality_report["categorical_features"]["thal"]["unknown_category_rate"] > 0.0
    assert drift_report["summary"]["drift_alert_count"] > 0
    assert trigger_report["summary"]["alert_count"] > 0
