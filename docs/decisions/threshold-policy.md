# Politica de Threshold de Decisão

## Status

Aprovado para a etapa 2.

## Contexto

O baseline inicial da etapa 2 foi treinado com `LogisticRegression` e passou a suportar threshold tuning sobre as probabilidades previstas para a classe positiva.

No contexto do projeto FIAP HealthCare Plus, o sistema atua como etapa de triagem cardíaca. Nesse cenário, o custo de deixar passar um caso positivo e mais critico do que o custo de encaminhar um falso positivo para avaliação adicional.

A validação da etapa 2 comparou uma grade de thresholds entre `0.20` e `0.80`, com critério de selecao orientado por `recall`, mantendo piso mínimo de `precision` em `0.70`.

## Decisão

O threshold operacional aprovado para a etapa 2 e `0.35`.

Regra de selecao vigente:

- maximizar `recall`
- respeitar `precision >= 0.70`
- usar o threshold vencedor como regra padrão de classificação binaria no pipeline

## Evidencia da Decisão

Resultado com threshold padrão `0.50`:

- `precision = 0.7857`
- `recall = 0.7857`

Resultado com threshold aprovado `0.35`:

- `precision = 0.7059`
- `recall = 0.8571`

Interpretacao:

- o sistema passa a capturar mais casos positivos
- ha aumento controlado de falsos positivos
- o trade-off foi considerado aceitavel para triagem

## Impacto Tecnico

- o threshold deixa de ser detalhe implcito do modelo e passa a ser parâmetro de negócio
- o valor precisa ser rastreado em artefatos, metadados do modelo e `MLflow`
- alteracoes futuras de threshold exigem nova validação comparativa
- as etapas seguintes devem tratar esse threshold como parte do contrato de inferência

## Impacto de Negócio

Aceitar `0.35` implica assumir uma política mais sensivel na triagem:

- maior proteção contra falsos negativos
- maior volume de casos sinalizados para avaliação posterior
- necessidade de o fluxo downstream absorver o aumento de falsos positivos

## Proximo Passo

Reavaliar o threshold quando houver:

- novo modelo baseline
- nova estratégia de features
- mudança de requisito operacional para `precision` ou `recall`
- critério clinico mais formal para custo de erro
