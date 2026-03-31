# Monitoring

## Objetivo

Fechar o ciclo operacional do serviço com uma trilha local auditavel de requests, inferencias, qualidade de dados, drift e gatilhos de retreinamento.

## Contrato Operacional

Eventos emitidos pela API:

- `request_received`
- `prediction_completed`
- `prediction_failed`
- `model_unavailable`
- `health_checked`

Campos minimos por evento operacional:

- `timestamp_utc`
- `event_type`
- `request_id`
- `endpoint`
- `status_code`
- `latency_ms`
- `model_name`
- `model_run_id`
- `model_run_label`

Campos minimos por evento de inferência:

- `timestamp_utc`
- `request_id`
- `prediction`
- `prediction_label`
- `positive_class_probability`
- `decision_threshold`
- `features`

## Persistencia Local

Arquivos canonicos:

- `artifacts/monitoring/events/api_events.jsonl`
- `artifacts/monitoring/events/inference_events.jsonl`

Relatorios batch por execução:

- `artifacts/monitoring/<run_label>/monitoring_report.json`
- `artifacts/monitoring/<run_label>/operational_summary.json`
- `artifacts/monitoring/<run_label>/data_quality_report.json`
- `artifacts/monitoring/<run_label>/drift_report.json`
- `artifacts/monitoring/<run_label>/trigger_report.json`
- `artifacts/monitoring/<run_label>/monitoring_summary.txt`

## Referencia de Drift

A referência e gerada no treino aprovado e salva em `artifacts/training/<run_label>/monitoring_reference.json`.

Ela contem:

- bins e proporções para features numericas
- distribuicoes de categorias observadas no treino
- distribuição de score prevista
- taxa de positivos prevista na referência

## Checks Implementados

Data quality:

- taxa de missing por feature numerica e categorica
- taxa de valores fora de faixa com base na referência de treino
- taxa de categorias desconhecidas
- taxa de requests invalidos no endpoint

Drift:

- PSI para features numericas
- diferenca absoluta maxima para features categoricas
- PSI da distribuição de score
- diferenca da taxa de positivos previstos

## Gatilhos

A rotina batch classifica o estado atual como:

- `healthy`
- `insufficient_data`
- `retraining_recommended`

Nesta etapa, o gatilho abre investigacao e recomendação de retreinamento. Ele não troca o modelo automaticamente.

## Comandos Oficiais

Gerar release local e API:

```bash
uv run python -m src.models.release
uv run python -m src.serving.app
```

Gerar relatorio batch de monitoramento:

```bash
uv run python -m src.monitoring.run_monitoring
```
