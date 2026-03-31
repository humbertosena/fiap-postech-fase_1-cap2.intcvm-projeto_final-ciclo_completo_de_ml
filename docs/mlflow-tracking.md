# Estratégia de Tracking com MLflow

## Objetivo

Usar `MLflow` como camada única de rastreabilidade para treino, auditoria, release e monitoramento local do modelo.

## Experimentos em uso

- treino e release: `phase-4-release`
- monitoramento: `phase-6-monitoring`

## Tracking URI Default

- `file:./mlruns`

## Tags Minimas por Execucao de Treino e Release

- `dataset_hash`
- `dataset_source`
- `parser_version`
- `preprocessing_version`
- `target_definition`
- `fairness_policy_name`
- `python_version`
- `release_status`
- `promotion_eligible`

## Parâmetros Minimos de Treino

- `algorithm`
- `random_state`
- `test_size`
- `feature_columns`
- `preprocessing_version`
- `decision_threshold`
- `threshold_min_precision`
- `fairness_policy_name`
- `fairness_alert_threshold`
- `fairness_groups`

## Métricas Minimas de Treino e Release

- `accuracy`
- `precision`
- `recall`
- `f1`
- `roc_auc`, quando aplicavel
- `fairness_age_group_recall_max_gap`
- `fairness_age_group_precision_max_gap`
- `fairness_age_group_false_negative_rate_max_gap`
- `fairness_sex_recall_max_gap`
- `fairness_sex_precision_max_gap`
- `fairness_sex_false_negative_rate_max_gap`
- `fairness_alert_count`
- `release_blocking_failures`
- `release_active_alerts`

## Parâmetros Minimos de Monitoramento

- `model_run_id`
- `model_run_label`
- `monitoring_min_sample_size`

## Métricas Minimas de Monitoramento

- `monitoring_prediction_count`
- `monitoring_error_rate`
- `monitoring_latency_p95_ms`
- `monitoring_drift_alert_count`
- `monitoring_retraining_recommended`

## Artefatos Minimos de Treino e Release

- relatorio de ingestão em JSON
- `metrics.json`
- `classification_report.json`
- `confusion_matrix.csv`
- `threshold_selection.json`
- `fairness_report.json`
- `fairness_summary.txt`
- `risk_summary.json`
- `model_card.json`
- `monitoring_reference.json`
- `release_gate_report.json`
- `release_decision.txt`
- pipeline serializado do modelo
- `model_metadata.json`
- `dataset_lineage.json`
- manifestos do registro local quando houver promocao

## Artefatos Minimos de Monitoramento

- `monitoring_report.json`
- `operational_summary.json`
- `data_quality_report.json`
- `drift_report.json`
- `trigger_report.json`
- `monitoring_summary.txt`

## Observacao

Como o projeto não usa `DVC`, a linhagem do dado continua dependendo de:

- imutabilidade do dado bruto
- hash do arquivo bruto
- versão do parser
- versão do pré-processamento
- referência estatística do treino aprovado
- registro desses metadados, da política de fairness, do status de release e do monitoramento no `MLflow`
