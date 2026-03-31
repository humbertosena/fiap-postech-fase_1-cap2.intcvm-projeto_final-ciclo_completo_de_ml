# Deployment Local

## Pre-requisito

Antes de subir a API, o workspace deve conter um manifesto de modelo aprovado em `models/registry/latest_approved_model.json`.

Fluxo mínimo:

```bash
uv run python -m src.models.release
```

## Subir a API localmente

```bash
uv run python -m src.serving.app
```

A API sobe em `http://127.0.0.1:8000`.

## Health Check

```bash
curl http://127.0.0.1:8000/health
```

## Predicao

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
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
      "thal": "normal"
    }
  }'
```

## Monitoramento Batch

Depois de gerar trafego local suficiente, execute:

```bash
uv run python -m src.monitoring.run_monitoring
```

Isso consolida:

- sumario operacional
- qualidade de dados
- drift
- gatilhos de investigacao e retreinamento

## Docker

Build:

```bash
docker build -t fiap-healthcare-plus-mlops:latest .
```

Run:

```bash
docker run --rm -p 8000:8000 fiap-healthcare-plus-mlops:latest
```

## Limitações

- o manifesto aprovado e local ao workspace
- a imagem não substitui um registry compartilhado de modelos
- o monitoramento continua local ao projeto
- recomendação de retreinamento não promove modelo automaticamente
