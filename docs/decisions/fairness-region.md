# Fairness por Regiao

## Status

Bloqueado por dado indisponivel na etapa 3.

## Contexto

O requisito da disciplina menciona controle de vies por idade e região. O dataset bruto principal usado no projeto, `cleve.mod`, não contem atributo literal de região nem proxy aprovado no contrato atual.

## Decisão

A etapa 3 não calcula fairness por região. O projeto registra essa ausência explicitamente nos relatórios de auditoria, no model card e no tracking.

## Impacto

- qualquer afirmacao sobre fairness regional seria tecnicamente indevida no estado atual
- os artefatos da etapa 3 precisam diferenciar o que foi auditado do que continua pendente
- etapa 4 não deve promover gate de região sem ampliacao da base ou decisão formal sobre proxy

## Opcao recomendada para evolucao

Ampliar a etapa de dados para combinar multiplas origens do corpus UCI ou incorporar atributo externo aprovado, tratando a origem como proxy apenas se houver decisão arquitetural explicita.

## Proximo passo

Definir se o projeto:

- enriquecera o dado com região real
- ou ampliara a base para multiplas origens com proxy operacional aprovado
