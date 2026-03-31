from __future__ import annotations

from typing import Any

from src.config import settings


def build_risk_summary(
    *,
    metrics: dict[str, float],
    fairness_report: dict[str, Any],
    threshold_selection: dict[str, Any],
) -> dict[str, Any]:
    fairness_alerts = fairness_report["alerts"]
    return {
        "model_scope": {
            "intended_use": (
                "Triagem cardiaca experimental para apoio tecnico em avaliacao de risco."
            ),
            "not_intended_for": "Diagnostico definitivo ou decisao clinica autonoma.",
        },
        "dataset_limitations": [
            "Dataset atual nao contem atributo real de regiao.",
            "Base pequena e de origem principal unica, sujeita a alta variancia por subgrupo.",
            "Fairness por idade e sexo e observacional, nao causal.",
        ],
        "model_limitations": [
            "Modelo atual e um baseline com LogisticRegression.",
            "Threshold foi calibrado em hold-out unico, sem validacao cruzada nesta fase.",
            "Nao ha comparacao sistematica de multiplos candidatos nesta etapa.",
        ],
        "operational_policy": {
            "decision_threshold": float(metrics["decision_threshold"]),
            "threshold_min_precision": float(settings.threshold_min_precision),
            "selected_by_threshold_tuning": bool(threshold_selection["used_precision_constraint"]),
            "fairness_policy": settings.fairness_policy_name,
            "fairness_alert_threshold": float(settings.fairness_alert_threshold),
        },
        "current_risks": {
            "global_recall": float(metrics["recall"]),
            "global_precision": float(metrics["precision"]),
            "fairness_alert_count": len(fairness_alerts),
            "requires_human_review": True,
        },
        "recommended_next_steps": [
            "Validar estabilidade do threshold com cross-validation ou bootstrap.",
            "Comparar baseline atual com candidatos alternativos antes de promover o modelo.",
            (
                "Expandir a base ou adicionar atributo/proxy aprovado para regiao antes de "
                "afirmar fairness regional."
            ),
        ],
    }



def build_model_card(
    *,
    metrics: dict[str, float],
    fairness_report: dict[str, Any],
    model_name: str,
) -> dict[str, Any]:
    return {
        "model_name": model_name,
        "model_family": "binary_classification",
        "development_stage": "phase_3_governance",
        "primary_metric": "recall",
        "decision_threshold": float(metrics["decision_threshold"]),
        "global_metrics": metrics,
        "audited_groups": fairness_report["policy"]["evaluated_groups"],
        "unavailable_dimensions": fairness_report["policy"]["unavailable_dimensions"],
        "fairness_summary": fairness_report["summary"],
        "usage_constraints": [
            "Uso apenas como apoio a triagem e analise tecnica interna.",
            "Nao usar como substituto de avaliacao clinica humana.",
        ],
    }
