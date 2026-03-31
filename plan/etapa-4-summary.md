# Etapa 4 - Summary Tecnico, Comparacao com a Etapa 3, Estado Atual do Código e Evidencias

## Objetivo deste documento

Registrar o estado real da etapa 4 com base no código atual do repositório, comparando explicitamente o que existia ao final da etapa 3 com o que foi implementado na etapa 4.

Este documento descreve:

- o que mudou da etapa 3 para a etapa 4
- quais módulos passaram a cobrir gates, promocao e automacao via CI/CD
- quais decisões arquiteturais foram formalizadas nesta etapa
- quais evidencias de validação existem hoje
- quais limitações e riscos continuam abertos para as etapas seguintes

## Escopo analisado

- código em `src/`
- testes em `tests/`
- configuração do projeto em `pyproject.toml` e `.env.example`
- documentação complementar em `docs/`
- workflow em `.github/workflows/ci.yml`
- artefatos gerados em `artifacts/training/`, `models/` e `mlruns/`
- backlog executável em `plan/etapa-4-backlog-executável.md`
- summary da etapa 3 em `plan/etapa-3-summary.md`

## Resumo executivo

Na etapa 3, o projeto entregava um pipeline reproduzivel de treinamento com fairness, relatórios de risco e governança rastreavel no mesmo run. A etapa 4 mantem esse fluxo técnico sem regressao e adiciona uma camada operacional: gates automatizados de promocao, decisão formal de release, registro local do último candidato e do último aprovado, e workflow de CI/CD capaz de executar qualidade, avaliação e release de forma automatizada.

O que está operacional hoje na etapa 4:

- workflow de CI com jobs separados para qualidade, validação e release
- avaliação oficial automatizada em pipeline de CI/CD
- gates bloqueantes sobre desempenho e conformidade do threshold aprovado
- alertas informativos sobre fairness e indisponibilidade de região
- `release_gate_report.json` e `release_decision.txt` gerados por run
- registro local do último candidato em `models/registry/latest_candidate.json`
- registro local do último aprovado em `models/registry/latest_approved_model.json`
- tags e métricas de release registradas no `MLflow`
- teste automatizado cobrindo a camada de gates e registro
- validação fim a fim executada com sucesso

O que continua não implementado como funcionalidade final:

- fairness por região com dado real ou proxy aprovado
- mitigacao automatica dos gaps de fairness detectados
- validação cruzada para estabilidade de threshold e fairness
- comparacao sistematica entre multiplos modelos candidatos
- API `Flask` carregando o modelo aprovado como interface real de inferência
- monitoramento em produção por segmento

## Comparacao Objetiva: Etapa 3 vs Etapa 4

### 1. Estado do treino

Na etapa 3:

- `src/models/train.py` treinava, auditava fairness, gerava risco e registrava tudo no `MLflow`
- o resultado principal era técnico: métricas, fairness, risco e artefatos de governança
- ainda não existia decisão automatizada de promocao

Na etapa 4:

- `src/models/train.py` continua sendo o nucleo do treino oficial
- o treino passou a alimentar um pipeline de release em `src/models/release.py`
- o resultado do run agora pode ser promovido ou bloqueado por gates objetivos
- a decisão operacional deixa de ser manual e passa a ser produzida pelo código

### 2. Estado da avaliação

Na etapa 3:

- a avaliação devolvia métricas globais e bloco de fairness
- a governança era observacional e não tinha efeito automatizado sobre promocao

Na etapa 4:

- a avaliação oficial continua retornando métricas e fairness sem regressao funcional
- esses resultados agora alimentam a camada de gates em `src/evaluation/gates.py`
- a etapa 4 separa claramente:
  - checks bloqueantes de promocao
  - alertas informativos de governança

### 3. Estado da governança e gates

Na etapa 3:

- fairness e risco eram artefatos formais, mas ainda sem decisão operacional automatizada
- a documentação preparava a promocao futura desses checks para gates

Na etapa 4:

- a política de gates foi formalizada em `docs/decisions/release-gate-policy.md`
- foram implementados gates bloqueantes para:
  - `recall >= 0.80`
  - `precision >= 0.70`
  - `decision_threshold == 0.35`
  - respeito ao piso mínimo de `precision` durante o threshold tuning
- fairness continua influenciando o release como alerta, não como bloqueio automatico
- a indisponibilidade de fairness por região também passou a virar alerta operacional explicito

### 4. Estado do tracking

Na etapa 3:

- o `MLflow` registrava dado, pré-processamento, métricas globais, fairness, risco e artefatos do modelo

Na etapa 4:

- o `MLflow` continua cobrindo toda a linhagem e auditoria da etapa 3
- o run passou a registrar também o resultado operacional do release
- foram adicionadas tags de release:
  - `release_status`
  - `promotion_eligible`
- foram adicionadas métricas de release:
  - `release_blocking_failures`
  - `release_active_alerts`
- artefatos de release passaram a ser publicados no mesmo run

### 5. Estado do CI/CD

Na etapa 3:

- o repositório estava tecnicamente preparado para promover fairness e governança a gates na etapa 4
- o workflow de CI ainda validava principalmente qualidade e treino

Na etapa 4:

- `.github/workflows/ci.yml` foi reorganizado em jobs separados:
  - `quality`
  - `validation`
  - `release`
- o release roda apenas em `push` para `main`
- o workflow publica artefatos de avaliação e release
- a automacao do projeto deixa de ser apenas validação técnica e passa a incluir decisão de promocao

### 6. Estado da documentação

Na etapa 3:

- o projeto já tinha baseline, threshold, fairness e risco documentados
- faltava documentar a política de promocao automatizada

Na etapa 4:

- foi criada a ADR de política de gates e promocao
- `README.md`, `docs/architecture.md`, `docs/mlflow-tracking.md`, `docs/model-risk.md` e `docs/model-card.md` foram atualizados para refletir o fluxo de release
- o backlog da etapa 4 foi registrado como concluído

### 7. Estado dos testes

Na etapa 3:

- a suite cobria config, ingestão, dataset, features, treino, avaliação, serializacao e fairness
- não havia testes para a logica de release e registro local

Na etapa 4:

- foi criado `tests/unit/test_gates.py`
- foi criado `tests/unit/test_registry.py`
- a suite agora valida:
  - aprovação com alertas
  - bloqueio por quebra de recall mínimo
  - escrita dos manifestos do registro local

## Estrutura implementada na etapa 4

```text
.github/
  workflows/
    ci.yml                           -> qualidade, validacao e release
artifacts/
  training/
    <run_label>/
      metrics.json                   -> metricas globais do run
      classification_report.json     -> relatorio detalhado por classe
      confusion_matrix.csv           -> matriz de confusao global
      threshold_selection.json       -> comparacao de thresholds e threshold escolhido
      fairness_report.json           -> auditoria segmentada por grupo
      fairness_summary.txt           -> resumo executivo da auditoria
      risk_summary.json              -> resumo de risco do modelo no run
      model_card.json                -> model card do run
      release_gate_report.json       -> decisao estruturada de gates
      release_decision.txt           -> resumo textual da decisao de release
models/
  <run_label>/
    training_pipeline.joblib         -> pipeline completo serializado
    model_metadata.json              -> metadados do modelo, threshold e fairness
    dataset_lineage.json             -> linhagem do dataset do run
  registry/
    latest_candidate.json            -> ultimo candidato avaliado pelo release
    latest_approved_model.json       -> ultimo candidato promovido
src/
  config.py                          -> configuracao ampliada para gates e registro local
  tracking.py                        -> tracking com tags, metricas e artefatos de release
  evaluation/
    gates.py                         -> checks bloqueantes e alertas informativos
    evaluate.py                      -> avaliacao executavel oficial
  models/
    train.py                         -> treino oficial que continua alimentando o release
    release.py                       -> pipeline de release com gates e promocao
    registry.py                      -> registro local de candidato e aprovado
tests/
  unit/
    test_gates.py                    -> testes da camada de gates
    test_registry.py                 -> testes da camada de registro local
```

## Design implementado na etapa 4

### 1. Arquitetura logica atual

A arquitetura continua organizada em camadas, mas a camada operacional passa a incluir promocao rastreavel:

- `config`: centraliza parâmetros de treino, threshold, fairness, gates e paths de registro local
- `data`: preserva parser e contrato oficial de treino
- `features`: preserva pré-processamento consistente entre treino e inferência futura
- `models`: treina, serializa, avalia gates, decide release e registra candidato/aprovado
- `evaluation`: calcula métricas globais, fairness, risco e gates operacionais
- `tracking`: registra desempenho, auditoria e status de release no `MLflow`
- `serving`: permanece como scaffold para etapas posteriores

### 2. Principios tecnicos observados no código atual

- a etapa 4 reutiliza o treino oficial da etapa 3, em vez de criar um fluxo paralelo
- o release não altera a política de fairness nem a política de threshold; ele aplica gates sobre o contrato aprovado
- fairness continua sendo evidencia observacional e não mitigacao automatica
- a promocao local depende exclusivamente do resultado dos gates codificados
- a ausência de região continua tratada como limitacao formal e agora também como alerta operacional

## Definicoes implementadas na etapa 4

### 1. Configuracao centralizada ampliada

Arquivo: `src/config.py`

Novos campos relevantes adicionados na etapa 4:

- `approved_decision_threshold`
- `release_gate_min_recall`
- `release_gate_min_precision`
- `model_registry_dir`

Defaults atuais relevantes:

- `MLFLOW_EXPERIMENT_NAME=phase-4-release`
- `APPROVED_DECISION_THRESHOLD=0.35`
- `RELEASE_GATE_MIN_RECALL=0.8`
- `RELEASE_GATE_MIN_PRECISION=0.7`
- `MODEL_REGISTRY_DIR=./models/registry`

### 2. Camada de gates

Arquivo: `src/evaluation/gates.py`

Capacidades implementadas:

- separacao entre checks bloqueantes e checks informativos
- avaliação automatizada do contrato mínimo de promocao
- classificação final do release em:
  - `approved`
  - `approved_with_alerts`
  - `blocked`
- exposicao de contadores agregados para tracking

Checks bloqueantes atuais:

- `minimum_recall`
- `minimum_precision`
- `approved_threshold_lock`
- `threshold_precision_constraint`

Checks informativos atuais:

- `fairness_gap_alerts`
- `limited_confidence_groups`
- `region_fairness_unavailable`

### 3. Pipeline de release

Arquivo: `src/models/release.py`

Capacidades implementadas:

- execução do treino oficial
- avaliação dos gates sobre o resultado treinado
- persistencia do `release_gate_report.json`
- persistencia do `release_decision.txt`
- atualização do registro local
- registro do resultado operacional no `MLflow`
- falha com `exit code 1` quando o release fica `blocked`

### 4. Registro local de candidato e aprovado

Arquivo: `src/models/registry.py`

Capacidades implementadas:

- escrita de manifesto do último candidato
- escrita de manifesto do último aprovado quando elegivel para promocao
- persistencia de métricas, resumo de fairness, metadados do modelo e referência ao gate report

## Evidencias de validação da etapa 4

Validacoes executadas com sucesso:

- `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check .`
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q`
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m src.evaluation.evaluate`
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m src.models.release`

Resultado da suite:

- `20 passed`
- `2 warnings` vindos de dependencias do `mlflow` e `pydantic`, sem bloqueio funcional

## Resultado operacional validado

Run registrado no `MLflow`:

- experimento: `phase-4-release`
- `run_id = 4393a391e8cd4fa48f09f03737b554e5`
- status de release: `approved_with_alerts`
- promocao elegivel: `true`
- promovido no registro local: `true`

Métricas globais validadas no release:

- `accuracy = 0.7704918032786885`
- `precision = 0.7058823529411765`
- `recall = 0.8571428571428571`
- `f1 = 0.7741935483870968`
- `roc_auc = 0.8766233766233767`
- `decision_threshold = 0.35`

Resultado dos gates:

- checks bloqueantes: `4` aprovados, `0` falhas
- checks informativos ativos: `2`
- alertas ativos:
  - gaps de fairness acima do limite configurado
  - fairness por região indisponivel no dataset atual

## Artefatos validados na etapa 4

Artefatos do run validado:

- `artifacts/training/20260325T004449Z/metrics.json`
- `artifacts/training/20260325T004449Z/classification_report.json`
- `artifacts/training/20260325T004449Z/confusion_matrix.csv`
- `artifacts/training/20260325T004449Z/threshold_selection.json`
- `artifacts/training/20260325T004449Z/fairness_report.json`
- `artifacts/training/20260325T004449Z/fairness_summary.txt`
- `artifacts/training/20260325T004449Z/risk_summary.json`
- `artifacts/training/20260325T004449Z/model_card.json`
- `artifacts/training/20260325T004449Z/release_gate_report.json`
- `artifacts/training/20260325T004449Z/release_decision.txt`
- `models/20260325T004449Z/training_pipeline.joblib`
- `models/20260325T004449Z/model_metadata.json`
- `models/20260325T004449Z/dataset_lineage.json`
- `models/registry/latest_candidate.json`
- `models/registry/latest_approved_model.json`

## Riscos e limitações residuais

Mesmo com a etapa 4 concluída, ainda permanecem riscos relevantes:

1. fairness por região continua indisponivel por ausência de atributo ou proxy aprovado
2. os gaps de fairness foram promovidos a alerta, mas não foram mitigados
3. o threshold `0.35` continua validado por hold-out único, sem validação cruzada
4. o registro local do modelo ainda não é um registry compartilhado multiambiente
5. a API de inferência ainda não carrega o último modelo aprovado
6. não ha monitoramento de drift, data quality em produção ou retreinamento automatico
7. a política de latência ainda não foi convertida em alvo técnico mensuravel

## Conclusao

A etapa 4 foi implementada com sucesso e elevou o projeto de um pipeline reproduzivel com governança para um pipeline reproduzivel com governança e decisão operacional automatizada. O sistema agora não responde apenas como o modelo performa e como esse desempenho se distribui entre grupos auditaveis, mas também se o resultado pode ou não ser promovido sob regras técnicas explicitas e rastreaveis.

Em termos praticos, a transição principal foi:

- Etapa 3: treino + fairness + risco + governança rastreavel
- Etapa 4: treino + fairness + risco + governança rastreavel + gates automatizados + release rastreavel

## Proximo passo natural para a Etapa 5

A etapa 5 deve partir do estado real deixado pela etapa 4 e transformar o modelo aprovado em interface operacional de inferência, especialmente:

- carregar o último modelo aprovado a partir do registro local
- ativar a API `Flask` como serviço real de predicao
- adicionar testes de integração da API com o pipeline serializado
- preparar a conteinerização com Docker sobre o fluxo de release já validado
