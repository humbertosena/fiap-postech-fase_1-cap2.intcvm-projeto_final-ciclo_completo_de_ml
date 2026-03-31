# API de Inferência

## Documentação OpenAPI

Com a aplicação rodando:

- Swagger UI: `GET /docs`
- OpenAPI JSON: `GET /openapi.json`

Observacao:

- a UI em `/docs` carrega os assets por CDN
- a especificacao em `/openapi.json` e servida localmente pela aplicacao

## Endpoint de Health

### `GET /health`

Retorna o estado operacional mínimo da API e se existe modelo aprovado disponivel para inferência.

Resposta exemplo com modelo carregado:

```json
{
  "status": "ok",
  "model_available": true,
  "model_name": "logistic_regression",
  "model_run_id": "4393a391e8cd4fa48f09f03737b554e5",
  "model_run_label": "20260325T004449Z"
}
```

Resposta exemplo sem modelo aprovado:

```json
{
  "status": "degraded",
  "model_available": false,
  "model_name": null,
  "model_run_id": null,
  "model_run_label": null
}
```

## Endpoint de Predicao

### `POST /predict`

O endpoint consome um objeto `input_data` alinhado ao contrato oficial de
features do pipeline treinado.

O contrato HTTP aceita aliases amigáveis e os normaliza internamente para o
vocabulário canônico do dataset.

Exemplos:

- `female -> fem`
- `typical -> angina`
- `asymptomatic -> asympt`
- `yes -> true`
- `no -> fal`
- `normal -> norm`
- `fixed_defect -> fix`
- `reversible_defect -> rev`

Payload exemplo:

```json
{
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
}
```

Resposta exemplo:

```json
{
  "request": {
    "input_data": {
      "age": 63.0,
      "sex": "male",
      "chest_pain_type": "angina",
      "resting_blood_pressure": 145.0,
      "cholesterol": 233.0,
      "fasting_blood_sugar_gt_120": "true",
      "rest_ecg": "norm",
      "max_heart_rate": 150.0,
      "exercise_induced_angina": "fal",
      "oldpeak": 2.3,
      "slope": "flat",
      "num_vessels": 0.0,
      "thal": "norm"
    }
  },
  "response": {
    "prediction": 1,
    "prediction_label": "sick",
    "positive_class_probability": 0.82,
    "decision_threshold": 0.35,
    "model_name": "logistic_regression",
    "model_run_id": "4393a391e8cd4fa48f09f03737b554e5",
    "model_run_label": "20260325T004449Z"
  }
}
```

## Erros

- `400`: payload invalido
- `503`: nenhum modelo aprovado disponivel no registro local

## Observacoes

- a API serve apenas o último modelo aprovado no registro local
- fairness não é recalculada em tempo de inferência
- o threshold retornado deve refletir o contrato do modelo aprovado
