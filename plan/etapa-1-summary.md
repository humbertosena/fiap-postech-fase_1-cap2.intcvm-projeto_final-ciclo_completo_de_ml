# Etapa 1 - Design, Estrutura, Definicoes Implementadas, Desenho Tecnico e ADRs

## Objetivo deste documento

Registrar o estado real da etapa 1 com base no código atual do repositório. Este documento descreve o que está implementado hoje, quais contratos existem, como os módulos se relacionam e quais decisões arquiteturais já foram materializadas.

## Escopo analisado

- código em `src/`
- testes em `tests/`
- configuração do projeto em `pyproject.toml`, `.env.example` e `.github/workflows/ci.yml`
- documentação complementar em `docs/`
- artefatos já gerados em `data/processed/`, `artifacts/` e `mlruns/`

## Resumo executivo

A etapa 1 entrega um bootstrap corporativo de um projeto de ML para triagem cardíaca. O que está realmente operacional hoje e:

- configuração centralizada por ambiente
- parser versionado do dataset legado `cleve.mod`
- geração de dataset processado em CSV
- geração de relatorio de ingestão em JSON com hash do arquivo bruto
- rastreabilidade minima em `MLflow`
- testes unitários para configuração e ingestão
- CI inicial com `uv`, `ruff`, `pytest` e validação da ingestão
- scaffolding para feature engineering, treino, avaliação e serving

O que ainda não está implementado como funcionalidade de negócio:

- treino de modelo real
- métricas reais de avaliação
- serializacao e versionamento de modelo treinado
- inferência real na API
- fairness por região
- baseline oficial do MVP
- SLO/meta de latência

## Estrutura implementada

```text
.github/workflows/
  ci.yml                     -> pipeline de qualidade e validacao da ingestao
artifacts/
  data_ingestion_report.json -> relatorio gerado pelo parser
data/raw/heart+disease/
  cleve.mod                  -> fonte principal da etapa 1
  heart-disease.names        -> referencia de dicionario original
data/processed/
  heart_disease_cleveland.csv -> dataset processado canonico da etapa 1
docs/
  architecture.md
  data-dictionary.md
  mlflow-tracking.md
  decisions/
    *.md                     -> decisoes e pendencias arquiteturais
models/                      -> reservado para artefatos de modelo
mlruns/                      -> backend local de tracking do MLflow
plan/
  fase1.md                   -> este documento
src/
  config.py                  -> configuracao centralizada
  tracking.py                -> bootstrap de tracking
  data/
    ingest_mod.py            -> parser + exportacao + relatorio
    schema.py                -> contrato de colunas e tipos
    dictionary.py            -> serializacao do dicionario de dados
  features/
    build_features.py        -> placeholder de engenharia de atributos
  models/
    train.py                 -> placeholder de treino
  evaluation/
    evaluate.py              -> placeholder de avaliacao
  serving/
    app.py                   -> API Flask scaffold
    schemas.py               -> contratos de request/response
tests/
  unit/
    test_config.py
    test_ingest_mod.py
```

## Design implementado

### 1. Arquitetura logica

O projeto foi organizado em camadas simples, com separacao por responsabilidade:

- `config`: resolve paths, parâmetros de ambiente e metadados fixos do projeto
- `data`: define esquema do dado, parser oficial e materializacao do dataset processado
- `tracking`: registra a execução bootstrap no `MLflow`
- `features`: ponto de extensão para transformacoes futuras
- `models`: ponto de entrada de treino, hoje apenas lendo o dataset processado
- `evaluation`: ponto de entrada de avaliação, hoje em placeholder
- `serving`: scaffold de API para a etapa de inferência

### 2. Principios tecnicos observados no código

- todo código executável fica em `src/`
- `pathlib` e usado para todos os caminhos
- configurações externas entram por variaveis de ambiente via `.env`
- o parser oficial é a única forma prevista de transformar o dado bruto em dado processado
- o dataset processado da etapa 1 é um CSV versionavel por arquivo
- a rastreabilidade minima depende de hash do dado bruto + versão do parser + tags no `MLflow`
- treino, avaliação e serving já possuem contrato de modulo, mas ainda não implementam regra de negócio final

## Definicoes implementadas

### 1. Configuracao centralizada

Arquivo: `src/config.py`

Objeto principal:

- `ProjectSettings` como `@dataclass(frozen=True)`

Campos implementados:

- `project_root`
- `raw_data_path`
- `data_dictionary_path`
- `processed_data_path`
- `ingestion_report_path`
- `model_artifact_dir`
- `mlflow_tracking_uri`
- `parser_version`
- `target_definition`

Defaults atuais vindos de `.env.example` e do código:

- `RAW_DATA_PATH=./data/raw/heart+disease/cleve.mod`
- `DATA_DICTIONARY_PATH=./data/raw/heart+disease/heart-disease.names`
- `PROCESSED_DATA_PATH=./data/processed/heart_disease_cleveland.csv`
- `INGESTION_REPORT_PATH=./artifacts/data_ingestion_report.json`
- `MODEL_ARTIFACT_DIR=./models`
- `MLFLOW_TRACKING_URI=file:./mlruns`
- `parser_version=0.1.0`
- `target_definition=buff=0,sick=1`

Comportamento importante:

- se a variavel de ambiente vier relativa, ela e resolvida a partir do `PROJECT_ROOT`
- todos os paths são normalizados para absolutos
- o objeto `settings` e importavel por todo o projeto como fonte única de configuração

### 2. Contrato do dado bruto e processado

Arquivo: `src/data/schema.py`

Definicoes principais:

- `EXPECTED_TOKEN_COUNT = 15`
- `TARGET_NEGATIVE_LABEL = "buff"`
- `TARGET_POSITIVE_LABEL = "sick"`

Colunas brutas (`RAW_COLUMNS`):

1. `age`
2. `sex`
3. `chest_pain_type`
4. `resting_blood_pressure`
5. `cholesterol`
6. `fasting_blood_sugar_gt_120`
7. `rest_ecg`
8. `max_heart_rate`
9. `exercise_induced_angina`
10. `oldpeak`
11. `slope`
12. `num_vessels`
13. `thal`
14. `diagnosis_label`
15. `diagnosis_code`

Colunas numericas:

- `age`
- `resting_blood_pressure`
- `cholesterol`
- `max_heart_rate`
- `oldpeak`
- `num_vessels`

Colunas categoricas:

- `sex`
- `chest_pain_type`
- `fasting_blood_sugar_gt_120`
- `rest_ecg`
- `exercise_induced_angina`
- `slope`
- `thal`
- `diagnosis_label`
- `diagnosis_code`

Coluna derivada:

- `target`

Colunas processadas finais (`PROCESSED_COLUMNS`):

- todas as colunas brutas
- `target`

Metadados de dicionário:

- `COLUMN_DEFINITIONS` lista nome, tipo, descricao e nulabilidade
- `src/data/dictionary.py` serializa essas definicoes em lista de dicionarios

### 3. Regras implementadas no parser

Arquivo: `src/data/ingest_mod.py`

Regras de leitura:

- o parser le o arquivo bruto como texto
- linhas vazias são descartadas
- linhas iniciadas por `%` são tratadas como comentario e ignoradas
- cada linha valida deve ter exatamente 15 tokens
- token `?` vira `None`
- todos os demais tokens são normalizados com `strip()` e `lower()`

Regras de tipagem:

- colunas numericas são convertidas com `pandas.to_numeric(..., errors="coerce")`
- colunas categoricas são convertidas para `string`
- `target` e derivado de `diagnosis_label`
- `buff -> 0`
- `sick -> 1`
- qualquer label fora desse mapeamento gera erro

Saídas geradas:

- CSV processado em `data/processed/heart_disease_cleveland.csv`
- relatorio JSON em `artifacts/data_ingestion_report.json`

Evidencias validadas pelos testes e artefatos atuais:

- 303 registros processados
- 16 colunas no dataset final
- `num_vessels` possui 5 nulos
- `thal` possui 2 nulos
- hash SHA-256 do `cleve.mod` e registrado no relatorio

### 4. Relatorio de ingestão

Estrutura atual do JSON gerado:

```json
{
  "source_path": "path absoluto do arquivo bruto",
  "file_hash_sha256": "hash do arquivo de entrada",
  "record_count": 303,
  "column_count": 16,
  "missing_values_by_column": {
    "age": 0
  },
  "parser_version": "0.1.0",
  "target_definition": "buff=0,sick=1"
}
```

Objetivo do relatorio:

- fixar a linhagem minima do dado
- expor volume e completude do dataset processado
- funcionar como artefato de auditoria simples da etapa 1

### 5. Tracking com MLflow

Arquivo: `src/tracking.py`

Comportamento implementado:

- define `tracking_uri` a partir de `settings.mlflow_tracking_uri`
- usa o experimento `phase-1-bootstrap`
- abre uma run `phase-1-bootstrap`
- registra tags minimas
- registra parâmetros basicos
- registra metrica `bootstrap_success = 1.0`
- publica o relatorio de ingestão como artefato, se existir

Tags implementadas:

- `dataset_source`
- `parser_version`
- `target_definition`
- `python_version`
- `dataset_hash` quando o relatorio existe

Parâmetros implementados:

- `processed_data_path`
- `tracking_uri`

Backend atual:

- local filesystem em `mlruns/`

### 6. Feature engineering, treino e avaliação

Arquivos:

- `src/features/build_features.py`
- `src/models/train.py`
- `src/evaluation/evaluate.py`

Estado atual:

- `build_features()` retorna uma copia do dataframe sem transformacoes
- `train_placeholder()` carrega o CSV processado, chama `build_features()` e retorna um resumo estrutural
- `evaluate_placeholder()` retorna dicionário estatico com métricas nulas

Contrato atual de `train_placeholder()`:

- `status = "placeholder"`
- `records = quantidade de linhas`
- `features = todas as colunas exceto target`
- `target_column = "target"`

Contrato atual de `evaluate_placeholder()`:

- `status = "placeholder"`
- `metrics.accuracy = null`
- `metrics.recall = null`
- `metrics.precision = null`
- `metrics.f1_score = null`

Interpretacao arquitetural:

- a etapa 1 fixa as interfaces de modulo para evolucao futura
- ainda não ha pipeline de treinamento nem avaliação estatística real

### 7. Serving

Arquivos:

- `src/serving/app.py`
- `src/serving/schemas.py`

API atual:

- `GET /health`
- `POST /predict`

Comportamento real:

- `GET /health` responde `200` com `{"status": "ok", "phase": "bootstrap"}`
- `POST /predict` aceita o JSON recebido, encapsula em `PredictionRequest`, e responde `501`

Contrato de `POST /predict` hoje:

- request e armazenado como `payload: dict[str, Any]`
- response traz:
  - `message`
  - `prediction`
  - `model_version`

Limitacao atual:

- não existe modelo carregado
- não existe validação de schema clinico
- não existe inferência real

### 8. Qualidade e automacao

Arquivos:

- `pyproject.toml`
- `.github/workflows/ci.yml`
- `tests/unit/test_config.py`
- `tests/unit/test_ingest_mod.py`

Ferramentas adotadas:

- Python `>=3.13,<3.14`
- `uv` para ambiente e dependencias
- `ruff` para lint
- `pytest` para testes
- `mypy` configurado, mas não executado no workflow atual

CI atual:

1. checkout do repositório
2. setup do Python 3.13
3. instalacao do `uv`
4. `uv sync --dev`
5. `uv run ruff check .`
6. `uv run pytest`
7. `uv run python -m src.data.ingest_mod`

Cobertura de testes atual:

- existencia dos paths fundamentais de configuração
- shape do dataset processado
- regra do target binario
- presença de valores faltantes esperados
- geração de CSV e relatorio de ingestão

## Desenho técnico

### 1. Visão de componentes

```text
                +----------------------+
                |   .env / settings    |
                |  src/config.py       |
                +----------+-----------+
                           |
                           v
+----------------+   +-----+------------------+   +----------------------+
| data/raw/...   |-->| src/data/ingest_mod.py |-->| data/processed/*.csv |
| cleve.mod      |   | parser + typing + I/O  |   +----------------------+
+----------------+   +-----+------------------+   +----------------------+
                           |                      | artifacts/*.json     |
                           +--------------------->| ingestion report     |
                                                  +----------+-----------+
                                                             |
                                                             v
                                                  +----------+-----------+
                                                  | src/tracking.py      |
                                                  | MLflow bootstrap     |
                                                  +----------+-----------+
                                                             |
                                                             v
                                                  +----------------------+
                                                  | mlruns/              |
                                                  | local experiment log |
                                                  +----------------------+

+---------------------------+   +----------------------+   +----------------------+
| src/features/             |   | src/models/train.py  |   | src/evaluation/      |
| build_features.py         |-->| placeholder          |   | evaluate.py          |
| no-op                     |   | structural contract  |   | placeholder metrics  |
+---------------------------+   +----------------------+   +----------------------+

+---------------------------+
| src/serving/app.py        |
| Flask scaffold            |
| /health ok, /predict 501  |
+---------------------------+
```

### 2. Fluxo técnico da ingestão bootstrap

```text
CLI/CI
  |
  v
python -m src.data.ingest_mod
  |
  +--> resolve settings e paths
  |
  +--> le data/raw/heart+disease/cleve.mod
  |
  +--> remove comentarios (%) e linhas vazias
  |
  +--> faz parse de 15 tokens por linha
  |
  +--> converte tipos numericos e categoricos
  |
  +--> deriva target binario
  |
  +--> grava data/processed/heart_disease_cleveland.csv
  |
  +--> calcula hash SHA-256 do bruto
  |
  +--> grava artifacts/data_ingestion_report.json
  |
  +--> opcionalmente src/tracking.py registra a run no MLflow
```

### 3. Fluxo do serving atual

```text
Cliente HTTP
  |
  +--> GET /health
  |      |
  |      +--> resposta 200 {"status":"ok","phase":"bootstrap"}
  |
  +--> POST /predict
         |
         +--> request.get_json(silent=True) ou {}
         +--> encapsula em PredictionRequest
         +--> monta PredictionResponse placeholder
         +--> resposta 501 sem inferencia real
```

## ADRs implementados

As decisões abaixo já estao efetivamente refletidas no código, nos testes ou na automacao do repositório.

### ADR-001 - Estrutura fonte em `src/` e separacao por domínio

Status: implementado

Decisão:

- centralizar código executável em `src/`
- separar responsabilidades em `data`, `features`, `models`, `evaluation`, `serving` e `tracking`

Motivacao:

- reduzir acoplamento
- facilitar evolucao incremental por etapa
- manter o repositório preparado para CI/CD e packaging Python

Evidencia:

- organizacao de pastas em `src/`
- `pyproject.toml` com `tool.setuptools.packages.find include = ["src*"]`

### ADR-002 - Configuracao única via `.env` + `pathlib` + dataclass imutavel

Status: implementado

Decisão:

- ler variaveis de ambiente com `python-dotenv`
- materializar a configuração em `ProjectSettings`
- usar `pathlib.Path` para todos os caminhos

Motivacao:

- portabilidade entre ambientes
- previsibilidade dos caminhos
- reducao de strings espalhadas no código

Evidencia:

- `src/config.py`
- `.env.example`

### ADR-003 - Parser oficial do dataset legado como fonte canonica do dado processado

Status: implementado

Decisão:

- tratar `data/raw/heart+disease/cleve.mod` como fonte primaria da etapa 1
- impedir leitura ad hoc do bruto fora do parser principal
- produzir um CSV processado canonico

Motivacao:

- garantir repetibilidade
- padronizar tipagem e tratamento de ausentes
- criar um ponto único de manutenção para regras de parsing

Evidencia:

- `src/data/ingest_mod.py`
- `docs/contributing.md`
- `tests/unit/test_ingest_mod.py`

### ADR-004 - Definicao binaria de target com preservacao do código clinico resumido

Status: implementado

Decisão:

- usar `buff -> 0` e `sick -> 1` como target oficial da etapa 1
- manter `diagnosis_code` separado de `diagnosis_label`

Motivacao:

- simplificar a primeira versão do problema para classificação binaria
- preservar informação clinica resumida para análise futura

Evidencia:

- `src/data/schema.py`
- `src/data/ingest_mod.py`
- `docs/decisions/target-definition.md`

### ADR-005 - Rastreabilidade minima com `MLflow` local e hash do dado bruto

Status: implementado

Decisão:

- usar `MLflow` como camada única de tracking da etapa 1
- registrar hash do bruto, origem do dado, versão do parser e definicao do target
- persistir tracking em filesystem local

Motivacao:

- criar auditabilidade minima sem introduzir stack mais pesada nesta etapa
- ligar dado bruto, artefato de ingestão e execução do bootstrap

Evidencia:

- `src/tracking.py`
- `docs/mlflow-tracking.md`
- pasta `mlruns/`

### ADR-006 - Quality gate mínimo com `uv`, `ruff`, `pytest` e GitHub Actions

Status: implementado

Decisão:

- padronizar ambiente com `uv`
- validar lint e testes em CI
- validar que a ingestão roda no workflow

Motivacao:

- detectar regressao cedo
- garantir que o bootstrap continue executável
- dar base para etapas seguintes sem retrabalho estrutural

Evidencia:

- `pyproject.toml`
- `.github/workflows/ci.yml`

### ADR-007 - API Flask entregue como scaffold, sem contrato de inferência definitivo

Status: implementado

Decisão:

- reservar a camada de serving desde a etapa 1
- expor endpoint de saúde real
- manter endpoint de predicao explicitamente não pronto com retorno `501`

Motivacao:

- firmar a interface de entrada/saída cedo
- evitar promessa falsa de inferência em uma etapa ainda sem modelo treinado

Evidencia:

- `src/serving/app.py`
- `src/serving/schemas.py`

## Pendencias arquiteturais já identificadas no repositório

Estas decisões aparecem documentadas, mas ainda não foram implementadas:

- fairness por região: bloqueado pela ausência do atributo no dataset principal
- baseline oficial do MVP: pendente para etapa com treino real
- meta de latência: pendente antes do serving produtivo

## Limites da etapa 1

Para evitar leitura equivocada do estado atual, estes pontos ainda não existem no código:

- pipeline de treinamento com `scikit-learn`
- serializacao de modelo em `models/`
- avaliação com métricas calculadas sobre conjunto de teste
- tracking automatico do treino e da avaliação
- validação forte de schema de entrada na API
- inferência clinica em tempo real
- orchestracao de pipeline
- containerizacao e deploy

## Conclusao

A etapa 1 já materializa a fundacao técnica do projeto: configuração centralizada, parser oficial, dataset processado canonico, artefato de ingestão, rastreabilidade minima em `MLflow`, quality gate inicial e contratos estruturais para as proximas camadas. O design atual privilegia reproducibilidade, auditabilidade basica e evolucao incremental, deixando explicitamente para as etapas seguintes a entrega do modelo, da inferência real e dos requisitos operacionais mais avancados.
