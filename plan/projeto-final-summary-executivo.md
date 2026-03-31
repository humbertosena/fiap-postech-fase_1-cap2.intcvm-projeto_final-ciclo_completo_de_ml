# Projeto Final - Summary Executivo

> **AVISO IMPORTANTE**
>
> Este repositório é um **exercício de aula** desenvolvido para fins exclusivamente acadêmicos no contexto do curso de pós-graduação da FIAP. Os dados utilizados são **públicos**. O processo de treinamento descrito é de **mera experimentação** e não passou por nenhuma validação de especialista da area cardíaca. Qualquer referência à empresa, produto ou serviço (como "FIAP HealthCare Plus") é uma **simulacao fictícia** criada para fins didáticos. **Não utilize nenhuma informação deste repositório para fins clínicos, médicos ou de diagnóstico.**

## Visão Geral

O projeto evoluiu de um bootstrap técnico para um ciclo completo de MLOps local e reproduzivel para triagem cardíaca. Ao final da implementacao, o repositório entrega ingestão controlada do dado legado, pipeline real de treinamento, auditoria de fairness e risco, gates automatizados de release, API `Flask` com inferência real, conteinerização inicial e monitoramento operacional com gatilhos rastreaveis de retreinamento.

O desenvolvimento do projeto foi assistido pela OpenAI Codex, utilizada como apoio técnico na estruturação, implementacao, revisão documental e consolidação dos artefatos de entrega.

## Resultado Final Entregue

O estado final do projeto inclui:

- parser versionado do dataset `cleve.mod`
- dataset processado canonico e relatorio de ingestão com hash do dado bruto
- pipeline treinavel com pré-processamento versionado e baseline oficial `LogisticRegression`
- threshold operacional aprovado em `0.35`, orientado por `recall`
- artefatos completos de avaliação, fairness, risco e model card por run
- release automatizado com gates objetivos e registro local do último modelo aprovado
- API `Flask` com `GET /health` e `POST /predict`
- carregamento exclusivo do último modelo aprovado
- `Dockerfile` e validação de packaging no CI
- monitoramento local com eventos estruturados, relatórios batch de qualidade e drift e política de gatilhos para retreinamento
- rastreabilidade de treino, release e monitoramento no `MLflow`

## Linha do Tempo Executiva por Etapa

### Etapa 1

Entregou a fundacao do projeto:

- estrutura corporativa do repositório
- configuração centralizada
- parser oficial do dado legado
- dataset processado e relatorio de ingestão
- CI inicial com `uv`, `ruff` e `pytest`

### Etapa 2

Transformou a base em pipeline real de ML:

- split reproduzivel
- pré-processamento com `ColumnTransformer`
- baseline oficial com `LogisticRegression`
- treino, avaliação e serializacao do pipeline
- threshold tuning e aprovação do threshold `0.35`

### Etapa 3

Adicionou governança e auditoria:

- fairness por `age_group` e `sex`
- relatórios de fairness por run
- relatorio de risco
- model card inicial

### Etapa 4

Automatizou a promocao do modelo:

- gates de release
- decisão automatizada de promocao
- registro local do candidato e do aprovado
- workflow de CI/CD com qualidade, validação e release

### Etapa 5

Ativou a inferência operacional:

- API `Flask` real
- contrato HTTP formalizado
- carregamento do último modelo aprovado
- smoke de latência local
- conteinerização inicial

### Etapa 6

Fechou o ciclo pos-deploy:

- telemetria estruturada da API
- persistencia de eventos de inferência
- referência estatística do treino aprovado
- monitoramento batch de qualidade e drift
- gatilhos rastreaveis de retreinamento

## Estado Atual do Produto

### O que está pronto

- fluxo local reproduzivel de ingestão a monitoramento
- validação automatizada por testes e lint
- promocao rastreavel do modelo aprovado
- inferência real via API
- pacote documental suficiente para demonstrar arquitetura, risco, governança e operação

### O que ainda e limitacao assumida

- fairness por região continua indisponivel por falta do atributo no dado
- baseline ainda simples, sem comparacao sistematica entre candidatos
- retreinamento não é automatico
- monitoramento continua local, sem plataforma externa
- labels de produção não existem, entao drift não prova sozinho degradação clinica
- a API ainda não implementa autenticação nem protecoes operacionais mais fortes

## Principais Decisões Arquiteturais Consolidadas

- código executável centralizado em `src/`
- tracking único com `MLflow`
- baseline oficial atual: `LogisticRegression`
- threshold operacional aprovado: `0.35`
- fairness oficial auditada por `sex` e `age_group`
- release bloqueado por desempenho mínimo e conformidade do threshold
- serving sempre usa o último modelo aprovado
- monitoramento abre recomendação de retreinamento, não troca automatica de modelo

## Evidencias de Validacao Disponiveis

O repositório possui evidencias automatizadas de que o fluxo final está operacional:

- `ruff check` passando
- `pytest` passando
- release real executado com promocao no registro local
- API respondendo `health` e `predict`
- monitoramento batch executado com artefatos gerados

## Leitura Executiva do Resultado

O projeto não termina em um notebook nem em um treino isolado. Ele entrega um fluxo completo de MLOps local, com governança minima, rastreabilidade, release controlado, inferência operacional e observabilidade suficiente para demonstrar maturidade técnica dentro do escopo definido.

## Recomendacao de Entrega

Para leitura final por avaliação ou handoff, a sequencia recomendada e:

1. `README.md`
2. `docs/README.md`
3. `docs/entrega-final.md`
4. `plan/projeto-final-summary-executivo.md`
5. `plan/etapa-6-summary.md`
