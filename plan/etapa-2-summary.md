# Etapa 2 - Summary Tecnico, Comparacao com a Etapa 1, Estado Atual do Código e Evidencias

## Objetivo deste documento

Registrar o estado real da etapa 2 com base no código atual do repositório, comparando explicitamente o que existia ao final da etapa 1 com o que foi implementado na etapa 2.

Este documento descreve:

- o que mudou da etapa 1 para a etapa 2
- quais contratos e módulos deixaram de ser placeholder e passaram a ser funcionais
- quais decisões arquiteturais foram materializadas no código
- quais evidencias de validação existem hoje
- quais limitações e riscos ainda permanecem para as etapas seguintes

## Escopo analisado

- código em `src/`
- testes em `tests/`
- configuração do projeto em `pyproject.toml` e `.env.example`
- documentação complementar em `docs/`
- artefatos gerados em `artifacts/training/`, `models/` e `mlruns/`
- backlog executável em `plan/etapa-2-backlog-executável.md`
- summary da etapa 1 em `plan/etapa-1-summary.md`

## Resumo executivo

Na etapa 1, o projeto entregava a base estrutural, o parser do dataset e placeholders para treino, features e avaliação. A etapa 2 transforma essa base em um pipeline real de treinamento supervisionado, com pré-processamento versionado, split reproduzivel, baseline oficial, avaliação automatizada, serializacao do pipeline treinado e rastreabilidade ampliada no `MLflow`.

O que está realmente operacional hoje na etapa 2:

- contrato explicito de treino e avaliação sobre o dataset processado
- remocao de colunas com vazamento de alvo do conjunto de features
- split reproduzivel com `random_state=42` e estratificacao por `target`
- pré-processamento com `ColumnTransformer`, imputacao e codificacao categorica
- baseline real com `LogisticRegression`
- avaliação com métricas de classificação, matriz de confusao e classification report
- threshold tuning orientado por `recall`
- threshold operacional aprovado em `0.35`
- serializacao do pipeline completo com `joblib`
- registro de parâmetros, métricas, artefatos e metadados no `MLflow`
- testes automatizados cobrindo treino, avaliação, dataset, features e IO do modelo
- validação fim a fim executada com sucesso

O que ainda não está implementado como funcionalidade de negócio final:

- fairness operacional por região e idade
- comparacao sistematica entre multiplos modelos candidatos
- inferência real pela API `Flask`
- gates de aprovação de modelo em CI/CD
- monitoramento, drift e retreinamento automatico
- meta formal de latência

## Comparacao Objetiva: Etapa 1 vs Etapa 2

### 1. Estado do treino

Na etapa 1:

- `src/models/train.py` era um placeholder
- o treino apenas carregava o dataset processado e devolvia metadados simples
- não havia algoritmo de ML real
- não havia split entre treino e teste

Na etapa 2:

- `src/models/train.py` executa treino real de ponta a ponta
- existe baseline oficial com `LogisticRegression`
- o pipeline faz split reproduzivel, pré-processamento, treino, avaliação e persistencia
- o comando `uv run python -m src.models.train` produz artefatos concretos e registra um run no `MLflow`

### 2. Estado do pré-processamento

Na etapa 1:

- `src/features/build_features.py` apenas retornava uma copia do dataframe
- não havia separacao formal entre colunas numericas, categoricas e alvo para treino

Na etapa 2:

- o pré-processamento foi encapsulado em `src/features/preprocessing.py`
- o projeto usa `ColumnTransformer` + `Pipeline`
- colunas numericas recebem imputacao por mediana e escalonamento opcional
- colunas categoricas recebem imputacao por frequência e `OneHotEncoder`
- o pré-processamento foi acoplado ao modelo no mesmo pipeline serializado

### 3. Estado da avaliação

Na etapa 1:

- `src/evaluation/evaluate.py` era placeholder
- todas as métricas vinham como `None`

Na etapa 2:

- a avaliação calcula `accuracy`, `precision`, `recall`, `f1` e `roc_auc`
- a avaliação gera `classification_report.json`
- a avaliação gera `confusion_matrix.csv`
- a avaliação registra o threshold de decisão usado no run

### 4. Estado da rastreabilidade

Na etapa 1:

- o `MLflow` era usado de forma minima para bootstrap
- o foco era apenas ligar hash do dataset, parser e relatorio de ingestão a um run simples

Na etapa 2:

- o tracking passou a cobrir o pipeline de treino real
- o run registra parâmetros do experimento, métricas, artefatos de avaliação, artefatos de modelo e linhagem do dataset
- o threshold de decisão passou a ser rastreado como parte do contrato do modelo

### 5. Estado dos artefatos de modelo

Na etapa 1:

- a pasta `models/` era apenas reservada
- não existia serializacao de modelo treinado

Na etapa 2:

- o pipeline treinado e serializado em `joblib`
- metadados do modelo são persistidos em JSON
- a linhagem do dataset do run e persistida junto ao modelo

### 6. Estado dos testes

Na etapa 1:

- havia testes para configuração e ingestão
- não havia teste real do pipeline de treinamento

Na etapa 2:

- foram adicionados testes para contrato de dataset
- testes para montagem do pipeline de features
- testes para treino com métricas reais
- testes para avaliação
- testes para round-trip de serializacao do modelo

## Estrutura implementada na etapa 2

```text
artifacts/
  data_ingestion_report.json       -> relatorio oficial da etapa 1 preservado
  training/
    <run_label>/
      metrics.json                 -> metricas do run
      classification_report.json   -> relatorio detalhado por classe
      confusion_matrix.csv         -> matriz de confusao
      threshold_selection.json     -> comparacao de thresholds e threshold escolhido
models/
  <run_label>/
    training_pipeline.joblib       -> pipeline completo serializado
    model_metadata.json            -> metadados do modelo
    dataset_lineage.json           -> linhagem do dataset do run
src/
  config.py                        -> configuracao ampliada para treino e threshold
  tracking.py                      -> tracking da etapa 2 no MLflow
  data/
    dataset.py                     -> contrato de treino e split
    ingest_mod.py                  -> parser oficial preservado da etapa 1
    schema.py                      -> schema ampliado com colunas de modelo e leakage
  features/
    preprocessing.py               -> preprocessamento real
    build_features.py              -> pipeline de features + modelo
  models/
    baseline.py                    -> selecao do baseline
    train.py                       -> treino fim a fim
    io.py                          -> persistencia e carga do modelo
  evaluation/
    metrics.py                     -> metricas e threshold tuning
    reports.py                     -> persistencia de relatorios
    evaluate.py                    -> avaliacao executavel
tests/
  unit/
    test_config.py
    test_ingest_mod.py
    test_dataset.py
    test_build_features.py
    test_train.py
    test_evaluate.py
    test_model_io.py
```

## Design implementado na etapa 2

### 1. Arquitetura logica atual

O projeto continua organizado em camadas, mas a camada de ML deixou de ser scaffold e passou a ser funcional:

- `config`: centraliza paths e parâmetros de treino, threshold e tracking
- `data`: define parser, schema, contrato de treino e split reproduzivel
- `features`: encapsula pré-processamento consistente entre treino e inferência futura
- `models`: seleciona baseline, treina, serializa e expõe artefatos
- `evaluation`: calcula métricas e materializa relatórios de validação
- `tracking`: registra a execução completa no `MLflow`
- `serving`: permanece como scaffold para a etapa 5

### 2. Principios tecnicos observados no código atual

- o parser oficial da etapa 1 continua sendo a única entrada valida do dado processado
- o treino consome apenas o dataset processado oficial
- colunas de diagnóstico bruto foram removidas das features para evitar leakage
- pré-processamento e modelo vivem no mesmo pipeline serializado
- threshold de decisão passou a ser tratado como parâmetro de negócio rastreavel
- a rastreabilidade agora cobre dado, pré-processamento, treino, avaliação e artefatos

## Definicoes implementadas na etapa 2

### 1. Configuracao centralizada ampliada

Arquivo: `src/config.py`

Novos campos relevantes adicionados em relacao a etapa 1:

- `training_artifact_dir`
- `preprocessing_version`
- `train_test_split_ratio`
- `random_state`
- `mlflow_experiment_name`
- `baseline_model_name`
- `positive_label`
- `decision_threshold`
- `threshold_min_precision`

Defaults atuais relevantes:

- `TRAINING_ARTIFACT_DIR=./artifacts/training`
- `PREPROCESSING_VERSION=1.0.0`
- `TRAIN_TEST_SPLIT_RATIO=0.2`
- `RANDOM_STATE=42`
- `MLFLOW_EXPERIMENT_NAME=phase-2-training`
- `BASELINE_MODEL_NAME=logistic_regression`
- `DECISION_THRESHOLD=0.5` como default configuravel
- `THRESHOLD_MIN_PRECISION=0.7`

Observacao importante:

- o threshold default configuravel existe, mas a política aprovada da etapa 2 escolhe `0.35` via threshold tuning para o baseline validado

### 2. Contrato de treino sobre o dataset processado

Arquivo: `src/data/dataset.py`

Definicoes materializadas:

- `DatasetBundle`
- `SplitDataset`
- `validate_training_frame()`
- `load_training_frame()`
- `build_dataset_bundle()`
- `split_training_dataset()`

Comportamentos relevantes:

- valida colunas obrigatorias do dataset processado
- converte alvo para inteiro
- converte colunas numericas para numérico
- normaliza colunas categoricas para formato compativel com `scikit-learn`
- executa split reproduzivel com opcao de estratificacao

### 3. Controle de leakage

Arquivo: `src/data/schema.py`

A etapa 2 materializou um ponto critico que ainda não existia na etapa 1 como regra operacional de treino:

- `diagnosis_label` e `diagnosis_code` foram explicitamente retiradas do conjunto de features do modelo
- `MODEL_INPUT_NUMERIC_COLUMNS`, `MODEL_INPUT_CATEGORICAL_COLUMNS` e `MODEL_FEATURE_COLUMNS` formalizam o contrato do modelo

Impacto:

- evita que o modelo aprenda diretamente a partir de colunas que codificam o diagnóstico
- torna o baseline defensavel tecnicamente

### 4. Preprocessamento versionado

Arquivos:

- `src/features/preprocessing.py`
- `src/features/build_features.py`

Implementacao atual:

- `SimpleImputer(strategy="median")` para numericas
- `StandardScaler()` opcional para numericas
- `SimpleImputer(strategy="most_frequent")` para categoricas
- `OneHotEncoder(handle_unknown="ignore")` para categoricas
- composicao com `ColumnTransformer` e `Pipeline`

### 5. Baseline oficial e treino

Arquivos:

- `src/models/baseline.py`
- `src/models/train.py`

Implementacao atual:

- baseline oficial: `LogisticRegression`
- opcao secundaria preparada: `RandomForestClassifier`
- `LogisticRegression` configurada com:
  - `max_iter=1000`
  - `class_weight="balanced"`
  - `random_state=42`

Fluxo implementado em `train_model()`:

1. carrega dataset processado
2. executa split reproduzivel
3. monta pipeline de pré-processamento + modelo
4. treina o baseline
5. obtém scores
6. escolhe threshold por política de `recall`
7. calcula métricas finais
8. gera artefatos locais
9. serializa o pipeline
10. registra o run no `MLflow`

### 6. Threshold tuning orientado por recall

Arquivos:

- `src/evaluation/metrics.py`
- `src/models/train.py`
- `docs/decisions/threshold-policy.md`

Definicoes atuais:

- grade de thresholds de `0.20` a `0.80` com passo `0.05`
- critério de selecao:
  - maximizar `recall`
  - respeitar `precision >= 0.70`
- threshold operacional aprovado: `0.35`

Efeito em relacao ao threshold padrão `0.50`:

- `recall` subiu de `0.7857` para `0.8571`
- `precision` caiu de `0.7857` para `0.7059`

Interpretacao:

- o sistema ficou mais sensivel para triagem
- o projeto aceitou conscientemente aumento controlado de falsos positivos para reduzir falsos negativos

### 7. Avaliacao e relatórios

Arquivos:

- `src/evaluation/metrics.py`
- `src/evaluation/reports.py`
- `src/evaluation/evaluate.py`

Saídas geradas por run:

- `metrics.json`
- `classification_report.json`
- `confusion_matrix.csv`
- `threshold_selection.json`

Métricas atualmente calculadas:

- `accuracy`
- `precision`
- `recall`
- `f1`
- `roc_auc`
- `decision_threshold`

### 8. Persistencia do pipeline treinado

Arquivos:

- `src/models/io.py`
- `src/models/train.py`

Implementado:

- serializacao do pipeline com `joblib`
- persistencia de `model_metadata.json`
- persistencia de `dataset_lineage.json`

Impacto:

- o modelo deixa de ser efemero em memoria
- a etapa 5 pode consumir o mesmo pipeline serializado sem reimplementar pré-processamento fora do artefato

### 9. Tracking ampliado no MLflow

Arquivo: `src/tracking.py`

A etapa 2 amplia o tracking da etapa 1 com:

- experimento `phase-2-training`
- tags de dado e pré-processamento
- parâmetros de treino
- métricas do modelo
- artefatos de avaliação
- artefatos de modelo
- linhagem do dataset por run

## Evidencias de validação da etapa 2

A validação foi executada com:

- `uv run ruff check .`
- `uv run pytest -q`
- `uv run python -m src.models.train`

Resultado observado:

- lint: aprovado
- testes: `14 passed`
- treino fim a fim: aprovado

Warnings observados nos testes:

- 2 warnings de dependencias do `mlflow` e `pydantic`
- não representam falha funcional do código do projeto neste momento

## Evidencias operacionais do baseline validado

Run validado com threshold tuning:

- `run_id = 7fab9f53d97a427fbd5931cc30cf5aa0`
- `algorithm = logistic_regression`
- `dataset_hash = a1d2a0369d138b45a761522e897f34dc49d779a1b8f7c323dd9732d632ecc83d`
- `decision_threshold = 0.35`

Métricas do run validado:

- `accuracy = 0.7704918032786885`
- `precision = 0.7058823529411765`
- `recall = 0.8571428571428571`
- `f1 = 0.7741935483870968`
- `roc_auc = 0.8766233766233767`

Artefatos observados:

- `artifacts/training/20260324T042330Z/metrics.json`
- `artifacts/training/20260324T042330Z/classification_report.json`
- `artifacts/training/20260324T042330Z/confusion_matrix.csv`
- `artifacts/training/20260324T042330Z/threshold_selection.json`
- `models/20260324T042330Z/training_pipeline.joblib`
- `models/20260324T042330Z/model_metadata.json`
- `models/20260324T042330Z/dataset_lineage.json`

## Riscos e limitações residuais

Mesmo com a etapa 2 concluída, ainda permanecem riscos relevantes:

1. não ha comparacao sistematica entre modelos candidatos
2. o threshold foi aprovado com base em um baseline é um split hold-out único, sem validação cruzada
3. fairness por região continua bloqueada pela ausência do atributo no dataset atual
4. a API de inferência ainda não consome o pipeline serializado
5. não existem gates de promocao automatica por metrica no CI/CD
6. não ha monitoramento de drift, data quality em produção ou retreinamento automatico
7. a política de latência ainda não foi convertida em alvo técnico mensuravel

## Conclusao

A etapa 2 fecha a principal lacuna deixada pela etapa 1: o projeto deixa de ser apenas um bootstrap corporativo com parser e scaffolding e passa a ser um pipeline funcional de treinamento e avaliação de modelo.

Em termos de maturidade do código, a transição foi:

- de placeholders para fluxo executável
- de rastreabilidade minima para tracking de treino real
- de estrutura pronta para ML para implementacao real de ML
- de preparacao para inferência futura para serializacao concreta do pipeline

A etapa 2 não fecha o ciclo completo de MLOps, mas entrega a primeira versão tecnicamente defensavel do nucleo de treinamento do projeto.

O próximo salto de maturidade está na etapa 3, com fairness, auditoria e governança sobre o modelo que agora já existe de forma real e reproduzivel.
