# Politica de Gates e Promocao

## Status

Aprovado para a etapa 4.

## Contexto

A etapa 3 deixou o projeto com métricas globais, threshold aprovado e auditoria de fairness operacional. Faltava transformar esse estado em critério automatizavel de CI/CD para decidir se um run pode ser promovido como candidato aprovado.

## Decisão

A etapa 4 passa a aplicar os seguintes checks automatizados:

### Checks bloqueantes

- `recall >= 0.80`
- `precision >= 0.70`
- `decision_threshold == 0.35`
- o threshold vencedor precisa respeitar o piso mínimo de `precision`

### Checks informativos

- qualquer alerta de fairness acima do limite configurado
- grupos com baixa amostra
- indisponibilidade de fairness por região

## Regra de promocao

- `approved`: todos os checks bloqueantes passam e não ha alertas ativos
- `approved_with_alerts`: todos os checks bloqueantes passam, mas existem alertas informativos
- `blocked`: pelo menos um check bloqueante falha

Runs `approved` e `approved_with_alerts` podem ser promovidos para o registro local do projeto. Runs `blocked` não podem ser promovidos.

## Impacto Tecnico

- a promocao deixa de ser manual
- o workflow de CI passa a executar treino, gates e registro local do modelo
- o resultado da decisão passa a ser publicado em artefatos e tags do `MLflow`
- fairness continua observacional nesta etapa e gera alerta, não bloqueio automatico

## Proximo Passo

Reavaliar os limites quando houver:

- novo baseline oficial
- nova política de threshold
- ampliacao da base com atributo ou proxy aprovado de região
- definicao institucional de gates normativos para fairness
