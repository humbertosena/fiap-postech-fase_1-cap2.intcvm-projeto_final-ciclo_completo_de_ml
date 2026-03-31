# Meta Inicial de Latência

## Status

Definida para a etapa 5.

## Contexto

A API de inferência entrou em operação local na etapa 5 e precisava de um alvo técnico inicial coerente com o baseline atual e com a validação em ambiente local.

## Decisão

A meta inicial da etapa 5 passa a ser:

- `p95 < 100 ms` para o endpoint `POST /predict`
- medida local em processo único, via `Flask` test client
- payload unitario, sem concorrencia e sem rede externa

## Justificativa

- o baseline atual e leve e roda com baixo custo computacional
- o objetivo desta etapa e detectar regressao grosseira de inferência, não homologar desempenho de produção
- uma meta local simples e suficiente para preparar refinamentos posteriores em ambiente conteinerizado e depois monitorado

## Evidencia Inicial

A validação da etapa 5 usa um teste de smoke de latência em `tests/integration/test_latency_smoke.py`.

## Limites da Decisão

- esse alvo não substitui medicao em container ou ambiente de produção
- o teste não mede latência de rede, concorrencia ou cold start externo
- o alvo deve ser reavaliado quando a API estiver conteinerizada e antes da etapa 6
