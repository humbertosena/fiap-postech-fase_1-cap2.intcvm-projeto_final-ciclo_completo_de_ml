# Baseline do MVP

## Status

Definido para a etapa 2.

## Modelo Inicial

- `LogisticRegression`

## Justificativa

- baseline simples, explicavel e reproduzivel
- custo computacional baixo
- adequado para validar o pipeline fim a fim antes de expandir para modelos mais complexos

## Metrica Principal

- `recall`

## Métricas Secundarias

- `precision`
- `f1`
- `accuracy`
- `roc_auc`, quando aplicavel

## Decisão Operacional Complementar

- threshold aprovado para a etapa 2: `0.35`
- política de selecao: maximizar `recall` com `precision >= 0.70`
- documento de referência: `docs/decisions/threshold-policy.md`
