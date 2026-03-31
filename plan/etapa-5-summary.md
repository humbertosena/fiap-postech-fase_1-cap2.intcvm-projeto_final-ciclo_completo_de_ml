# Etapa 5 - Summary Tecnico, Comparacao com a Etapa 4, Estado Atual do Código e Evidencias

## Objetivo deste documento

Registrar o estado real da etapa 5 com base no código atual do repositório, comparando explicitamente o que existia ao final da etapa 4 com o que foi implementado na etapa 5.

Este documento descreve:

- o que mudou da etapa 4 para a etapa 5
- quais módulos passaram a cobrir serving, contrato HTTP e implantação local
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
- backlog executável em `plan/etapa-5-backlog-executável.md`
- summary da etapa 4 em `plan/etapa-4-summary.md`

## Resumo executivo

Na etapa 4, o projeto entregava um pipeline reproduzivel com fairness, gates automatizados de promocao, release rastreavel e registro local do último modelo aprovado. A etapa 5 mantem esse fluxo sem regressao e adiciona a camada de inferência: API `Flask` ativa, contrato HTTP formalizado, carregamento do modelo aprovado, testes de integração, meta inicial de latência e preparacao da conteinerização.

O que está operacional hoje na etapa 5:

- endpoint `GET /health` com estado operacional e metadados do modelo aprovado
- endpoint `POST /predict` com inferência real baseada no pipeline promovido
- carregamento do último modelo aprovado a partir de `models/registry/latest_approved_model.json`
- contrato HTTP validado para request e response
- testes de integração da API cobrindo sucesso, payload invalido e ausência de modelo aprovado
- smoke test de latência local com meta inicial documentada
- manifesto aprovado com paths relativos ao projeto, reduzindo acoplamento a path absoluto local
- `Dockerfile`, `.dockerignore` e job de packaging adicionados ao CI
- release renovado com sucesso após a implementacao da camada de serving

O que continua não implementado como funcionalidade final:

- validação manual completa do build e runtime Docker no ambiente atual
- registry compartilhado multiambiente para modelos
- monitoramento em produção, drift e retreinamento automatico
- mitigacao automatica dos gaps de fairness detectados
- fairness por região com dado real ou proxy aprovado
- observabilidade de produção, autenticação e controle de carga da API

## Comparacao Objetiva: Etapa 4 vs Etapa 5

### 1. Estado do treino e release

Na etapa 4:

- `src/models/train.py` e `src/models/release.py` treinavam, avaliavam gates e promoviam o último modelo aprovado
- o produto final da etapa era um run aprovado é um manifesto local de modelo elegivel para serving futuro

Na etapa 5:

- esse fluxo continua intacto e foi reutilizado como fonte oficial da inferência
- a API não cria um caminho paralelo de predicao; ela consome o resultado oficial do release
- o manifesto aprovado foi ampliado para incluir paths relativos ao projeto, melhorando a portabilidade para implantação local

### 2. Estado da inferência

Na etapa 4:

- `src/serving/app.py` ainda era scaffold e retornava `501`
- não existia carregamento real do modelo aprovado
- o projeto ainda não tinha contrato HTTP formal de predicao

Na etapa 5:

- `src/serving/app.py` passou a responder `GET /health` e `POST /predict`
- `src/serving/model_store.py` carrega o último modelo aprovado do registro local
- `src/serving/schemas.py` valida o payload de entrada e estrutura a resposta
- a predicao real usa o pipeline serializado promovido pela etapa 4

### 3. Estado da governança e contrato

Na etapa 4:

- o projeto tinha governança forte sobre treino e promocao, mas a camada de serving ainda não herdava formalmente esse contrato

Na etapa 5:

- o contrato da API passou a refletir o threshold aprovado é os identificadores do modelo promovido
- a API foi desenhada para servir apenas o último aprovado, nunca o último candidato arbitrario
- fairness continua fora do caminho online de inferência, preservando a separacao entre auditoria offline e serving online

### 4. Estado do tracking e registro

Na etapa 4:

- o registro local apontava para o modelo aprovado, com metadados e artefatos de release
- os paths do manifesto ainda podiam ficar acoplados ao ambiente local onde o release rodou

Na etapa 5:

- o manifesto aprovado passou a incluir `project_relative_model_path` e metadados relativos ao projeto
- o release foi executado novamente e validado após essa mudança
- a API real consumiu com sucesso o manifesto atualizado

### 5. Estado do CI/CD e packaging

Na etapa 4:

- o CI validava qualidade, avaliação, release e upload de artefatos
- não havia job específico para packaging da imagem

Na etapa 5:

- o workflow ganhou um job `packaging` para validar build do `Dockerfile`
- os testes de integração da API passaram a rodar junto da suite normal
- a conteinerização entrou no fluxo do projeto, ainda com ressalva na validação manual local completa

### 6. Estado da documentação

Na etapa 4:

- o projeto tinha baseline, threshold, fairness, risco e release documentados
- faltava documentar a API, o deployment local é a meta de latência

Na etapa 5:

- foram adicionados `docs/api.md` e `docs/deployment.md`
- `docs/decisions/latency-target.md` foi fechado com meta inicial
- `README.md`, `docs/architecture.md`, `docs/model-card.md` e `docs/model-risk.md` foram atualizados para refletir a camada de serving

### 7. Estado dos testes

Na etapa 4:

- a suite cobria config, ingestão, dataset, features, treino, avaliação, fairness, gates e registro local
- não havia testes de integração da API

Na etapa 5:

- foram criados testes de integração para `health` e `predict`
- foi criado teste de smoke de latência
- foram criados testes para `model_store` e validação de schemas HTTP
- a suite passou a validar comportamento do serviço sem depender do modelo real de produção

## Estrutura implementada na etapa 5

```text
src/
  serving/
    app.py                           -> API Flask com /health e /predict
    model_store.py                   -> carregamento do ultimo modelo aprovado
    schemas.py                       -> contrato HTTP de request e response
docs/
  api.md                             -> contrato da API
  deployment.md                      -> fluxo operacional local e Docker
  decisions/
    latency-target.md                -> meta inicial de latencia
tests/
  integration/
    test_serving_api.py              -> integracao da API
    test_latency_smoke.py            -> smoke test de latencia
  unit/
    test_model_store.py              -> carga do manifesto aprovado
    test_serving_schemas.py          -> validacao do contrato HTTP
Dockerfile                           -> empacotamento inicial da aplicacao
.dockerignore                        -> reducao do contexto de build
```

## Design implementado na etapa 5

### 1. Arquitetura logica atual

A arquitetura continua organizada em camadas, mas agora inclui serving real do modelo aprovado:

- `config`: centraliza parâmetros do projeto e paths oficiais do release
- `models`: treina, promove e registra o modelo elegivel para inferência
- `serving`: carrega o manifesto aprovado, valida payload e responde previsões HTTP
- `evaluation`: continua sendo a camada de métricas, fairness, risco e gates offline
- `tracking`: continua registrando o ciclo de treino e release no `MLflow`

### 2. Principios tecnicos observados no código atual

- a API serve somente o último modelo aprovado
- o serving não reimplementa pré-processamento manual; ele reutiliza o pipeline serializado
- o contrato HTTP herda o threshold aprovado como parte da resposta operacional
- fairness permanece offline e não polui o caminho critico da inferência
- o manifesto aprovado passou a ser menos fragil a mudanças de path local

## Definicoes implementadas na etapa 5

### 1. Camada de serving

Arquivos: `src/serving/app.py`, `src/serving/model_store.py` e `src/serving/schemas.py`

Capacidades implementadas:

- health check com estado operacional do modelo aprovado
- predicao real via `POST /predict`
- validação de payload
- resposta contendo:
  - classe prevista
  - label prevista
  - probabilidade positiva
  - threshold usado
  - `model_name`
  - `model_run_id`
  - `model_run_label`
- retorno `503` quando não houver modelo aprovado disponivel

### 2. Meta inicial de latência

Arquivo: `docs/decisions/latency-target.md`

Meta definida:

- `p95 < 100 ms` para `POST /predict`
- medida local, em processo único, via `Flask` test client
- objetivo de detectar regressao grosseira de inferência, não homologar produção

### 3. Conteinerizacao inicial

Arquivos: `Dockerfile`, `.dockerignore` e `.github/workflows/ci.yml`

Capacidades implementadas:

- imagem base Python `3.13-slim`
- instalacao simples via `pip install .`
- copy dos módulos e modelos locais necessários ao runtime
- job `packaging` no CI para build da imagem

## Evidencias de validação da etapa 5

Validacoes executadas com sucesso:

- `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check .`
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q`
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m src.models.release`
- smoke real da API com `Flask` test client usando o manifesto aprovado atualizado

Resultado da suite:

- `29 passed`
- `2 warnings` vindos de dependencias do `mlflow` e `pydantic`, sem bloqueio funcional

## Resultado operacional validado

Release renovado no `MLflow`:

- experimento: `phase-4-release`
- `run_id = 438c3b95fc3d4f89bcd61c5bf992bf80`
- status de release: `approved_with_alerts`
- promocao elegivel: `true`
- promovido no registro local: `true`

Smoke real da API com o modelo aprovado:

- `GET /health`: `200`
- `POST /predict`: `200`
- resposta validada:
  - `prediction = 1`
  - `prediction_label = sick`
  - `positive_class_probability = 0.650764275658532`
  - `decision_threshold = 0.35`
  - `model_run_id = 438c3b95fc3d4f89bcd61c5bf992bf80`

## Artefatos validados na etapa 5

Artefatos de serving e release relevantes:

- `models/registry/latest_approved_model.json`
- `models/registry/latest_candidate.json`
- `artifacts/training/20260327T120644Z/release_gate_report.json`
- `artifacts/training/20260327T120644Z/release_decision.txt`
- `artifacts/training/20260327T120644Z/model_card.json`
- `docs/api.md`
- `docs/deployment.md`
- `docs/decisions/latency-target.md`

## Riscos e limitações residuais

Mesmo com a etapa 5 implementada, ainda permanecem riscos relevantes:

1. a validação manual completa do `docker build` local continua dependente do daemon Docker fora do sandbox atual
2. o registro do modelo ainda e local ao workspace, não compartilhado entre ambientes
3. fairness por região continua indisponivel
4. os gaps de fairness continuam sendo alertas e não mitigacoes
5. a API ainda não possui monitoramento, autenticação, rate limiting ou observabilidade de produção
6. não ha retreinamento automatico ou monitoramento de drift
7. a meta de latência atual ainda e local e precisa ser reavaliada em ambiente conteinerizado real

## Conclusao

A etapa 5 foi implementada com sucesso no que diz respeito a ativacao da inferência real e ao acoplamento correto entre release e serving. O projeto deixa de ser apenas um pipeline que treina e promove modelos e passa a expor o modelo aprovado por meio de uma API concreta, com contrato definido, testes de integração e preparacao inicial para conteinerização.

Em termos praticos, a transição principal foi:

- Etapa 4: treino + fairness + risco + release rastreavel
- Etapa 5: treino + fairness + risco + release rastreavel + serving real + implantação inicial

## Proximo passo natural para a Etapa 6

A etapa 6 deve partir do estado real deixado pela etapa 5 e fechar o ciclo operacional, especialmente:

- monitorar disponibilidade e latência da API
- monitorar drift e qualidade de dados em inferência
- definir gatilhos de retreinamento
- fechar o ciclo entre serving, observabilidade e nova promocao de modelos
