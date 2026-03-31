# Politica de Fairness

## Status

Aprovado para a etapa 3.

## Contexto

O projeto entrou na etapa 3 com um pipeline de treino já funcional, threshold operacional aprovado em `0.35` e requisito de governança que exige evidencia de vies e limitações. O dataset atual permite auditoria observacional por idade e sexo, mas não contem atributo literal de região.

## Decisão

A política operacional de fairness da etapa 3 passa a ser:

- auditar os grupos `age_group` e `sex`
- calcular por grupo: `precision`, `recall`, `f1`, `false_negative_rate` e `false_positive_rate`
- emitir alerta quando a diferenca absoluta maxima entre grupos para uma metrica ultrapassar `0.15`
- marcar grupos com menos de `10` amostras como evidencia de baixa confiança
- registrar explicitamente que região permanece indisponivel no dado atual

## Interpretacao

Os resultados de fairness da etapa 3 são observacionais e servem para auditoria técnica interna. Eles não provam causalidade, nem autorizam afirmar ausência de vies clínicos ou populacionais.

## Impacto Tecnico

- fairness passa a fazer parte do artefato oficial de cada run
- o run de treinamento registra gaps agregados no `MLflow`
- o threshold operacional `0.35` precisa ser refletido nas métricas segmentadas
- gates futuros da etapa 4 devem partir desses calculos, não de regras novas paralelas

## Preparacao para Gates da Etapa 4

Checks já prontos para promocao futura:

- alerta informativo imediato: qualquer `fairness_*_max_gap > 0.15`
- alerta informativo imediato: `fairness_alert_count > 0`
- gate bloqueante futuro recomendado: `recall` global abaixo do mínimo aprovado pelo projeto
- gate bloqueante futuro recomendado: fairness por região só após dado ou proxy aprovado

## Proximo Passo

Reavaliar a política quando houver:

- ampliacao da base com atributo ou proxy aprovado de região
- troca de baseline ou novo threshold operacional
- definicao institucional de limites normativos diferentes para gaps
