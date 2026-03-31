# Etapa 1 - Backlog Executavel

Este backlog converte o plano da etapa 1 em tarefas técnicas executaveis, com ordem de implementacao, arquivos esperados, validacoes e bloqueios explicitos.

## Escopo Deste Backlog

Este backlog cobre apenas a etapa 1:

- estrutura corporativa do repositório
- ambiente Python 3.13
- ingestão formal do dataset `.MOD`
- qualidade minima de código
- rastreabilidade com `MLflow`
- CI inicial
- scaffolding do domínio de ML

Ficam fora deste backlog:

- treinamento completo do modelo
- fairness operacional implementada
- API `Flask` funcional
- Docker
- monitoramento e drift

## Premissas de Execucao

As tarefas abaixo assumem:

1. Python `3.13`
2. `uv` como ferramenta de ambiente e dependencias
3. `pyproject.toml` como fonte principal das dependencias
4. `MLflow` como única ferramenta de rastreabilidade
5. notebooks apenas para demonstracao
6. compatibilidade com Windows, Linux e macOS

## Bloqueios que Precisam Ser Resolvidos no Inicio

Estes itens não impedem o bootstrap do repositório, mas precisam ser fechados cedo para aderencia estrita ao PDF:

1. Fairness por região
   - o arquivo `data-raw/heart+disease/cleve.mod` não possui atributo de região
   - decisão necessária:
     - enriquecer o dataset com região
     - ou ampliar a base para multiplas origens e usar origem como proxy
2. Regra oficial da variavel alvo
   - o dado bruto usa `buff` e `sick` com subtipos
   - a binarizacao oficial precisa ser registrada antes do treino
3. Baseline do MVP
   - o PDF exige gate técnico baseado em baseline
   - o valor oficial do baseline precisa ser definido
4. Meta inicial de latência
   - a etapa 5 exigira baixa latência
   - a meta precisa existir para orientar desenho do pipeline e da inferência

## Ordem de Execucao Recomendada

1. BP-00 Fechar bloqueios de definicao
2. BP-01 Bootstrap do repositório
3. BP-02 Ambiente Python e dependencias
4. BP-03 Configuracao e paths
5. BP-04 Ingestao do dataset `.MOD`
6. BP-05 Qualidade de código
7. BP-06 Rastreabilidade com `MLflow`
8. BP-07 Documentação e decisões arquiteturais
9. BP-08 CI inicial no GitHub Actions
10. BP-09 Scaffolding do domínio de ML

---

## BP-00 Fechar bloqueios de definicao

Objetivo: eliminar ambiguidades que afetam a aderencia ao PDF é as etapas seguintes.

Tarefas:

- definir se fairness por região será atendida por enriquecimento do dataset ou por ampliacao para multiplas bases UCI
- definir a regra de target binario
- definir o baseline inicial do MVP
- definir a meta de latência de referência

Saídas esperadas:

- `docs/decisions/fairness-region.md`
- `docs/decisions/target-definition.md`
- `docs/decisions/mvp-baseline.md`
- `docs/decisions/latency-target.md`

Critério de pronto:

- todas as decisões acima documentadas e sem conflito com o PDF

Dependencias:

- nenhuma

---

## BP-01 Bootstrap do repositório

Objetivo: criar a estrutura corporativa minima é o mapa do projeto.

Arquivos e diretorios a criar:

- `.gitignore`
- `README.md`
- `docs/`
- `docs/decisions/`
- `data/`
- `data/raw/`
- `data/processed/`
- `models/`
- `notebooks/`
- `src/`
- `src/data/`
- `src/features/`
- `src/models/`
- `src/evaluation/`
- `src/serving/`
- `tests/`
- `tests/unit/`
- `tests/integration/`
- `.github/workflows/`
- `artifacts/`

Tarefas:

- criar a árvore de diretorios do projeto
- mover ou copiar a referência do dataset bruto para o caminho canonico definido no projeto, sem perder o original se ele for mantido como fonte externa
- definir a política do `.gitignore` para:
  - ambientes virtuais
  - caches Python
  - artefatos locais
  - datasets processados
  - artefatos do `MLflow`
- escrever o `README.md` inicial com:
  - objetivo do projeto
  - contexto de negócio
  - estrutura de pastas
  - setup rápido

Validacao:

- a estrutura de pastas existe sem ambiguidade
- o `README.md` consegue orientar o bootstrap

Comandos de verificação:

```powershell
Get-ChildItem -Force
Get-ChildItem -Recurse -Depth 2
```

---

## BP-02 Ambiente Python e dependencias

Objetivo: permitir bootstrap reproduzivel em Windows, Linux e macOS.

Arquivos a criar:

- `pyproject.toml`
- `uv.lock`
- `.python-version`

Dependencias de runtime iniciais:

- `pandas`
- `numpy`
- `scikit-learn`
- `mlflow`
- `python-dotenv`

Dependencias de desenvolvimento:

- `pytest`
- `ruff`
- `mypy`

Tarefas:

- inicializar o projeto Python com `pyproject.toml`
- fixar `requires-python = ">=3.13,<3.14"`
- separar dependencias de runtime e dev
- registrar comandos padrão de bootstrap para PowerShell e shell POSIX
- definir um comando padrão para sincronizacao do ambiente com `uv`

Validacao:

- uma máquina limpa consegue instalar dependencias sem ajustes manuais fora da documentação

Comandos de verificação:

```powershell
uv python pin 3.13
uv sync --dev
uv run python --version
uv run pytest
uv run ruff check .
```

---

## BP-03 Configuracao e paths

Objetivo: centralizar parâmetros e remover dependencia de paths hardcoded.

Arquivos a criar:

- `.env.example`
- `src/config.py`
- opcionalmente `config/base.yaml`

Tarefas:

- definir variaveis minimas:
  - `MLFLOW_TRACKING_URI`
  - `RAW_DATA_PATH`
  - `PROCESSED_DATA_PATH`
  - `MODEL_ARTIFACT_DIR`
- implementar leitura de configuração usando `pathlib`
- garantir comportamento identico em Windows, Linux e macOS
- registrar a convencao de segredos e variaveis locais não versionadas

Validacao:

- o projeto consegue resolver seus caminhos principais sem `os.chdir` e sem separadores de path fixos

Comandos de verificação:

```powershell
uv run python -c "from src.config import settings; print(settings)"
```

---

## BP-04 Ingestao do dataset `.MOD`

Objetivo: encapsular a leitura do dado bruto legado em código versionado e testavel.

Arquivos a criar:

- `src/data/__init__.py`
- `src/data/schema.py`
- `src/data/ingest_mod.py`
- `src/data/dictionary.py`
- `tests/unit/test_ingest_mod.py`
- `docs/data-dictionary.md`

Tarefas:

- registrar o dataset canonico como `data-raw/heart+disease/cleve.mod` ou padronizar copia controlada para `data/raw/cleve.mod`
- implementar parser para:
  - ignorar comentarios iniciados por `%`
  - tokenizar linhas validas
  - normalizar tipos numéricos e simbolicos
  - converter `?` em valor faltante consistente
- definir as colunas do dataset processado
- formalizar a regra de target binario
- exportar dataset tratado para `data/processed/heart_disease_cleveland.csv`
- calcular metadados de linhagem:
  - hash SHA-256
  - numero de registros
  - numero de colunas
  - total de missing values
  - versão do parser
- gerar um manifesto simples da ingestão, por exemplo:
  - `artifacts/data_ingestion_report.json`

Validacao:

- a ingestão produz o mesmo resultado em duas execucoes consecutivas
- o schema final e coerente com o dicionário de dados

Comandos de verificação:

```powershell
uv run python -m src.data.ingest_mod
uv run pytest tests/unit/test_ingest_mod.py
```

Observacao:

- o arquivo `cleve.mod` informa 8 atributos simbolicos e 6 numéricos
- o arquivo `heart-disease.names` documenta a base completa e deve ser usado como complemento do dicionário de dados

---

## BP-05 Qualidade de código

Objetivo: criar gates minimos antes da etapa de treino.

Arquivos a criar:

- `ruff.toml` ou configuração equivalente no `pyproject.toml`
- `tests/conftest.py`
- `pytest.ini` ou configuração equivalente no `pyproject.toml`

Tarefas:

- configurar `ruff`
- configurar `pytest`
- adicionar teste do parser cobrindo:
  - comentarios
  - valores faltantes
  - numero de colunas
  - binarizacao do target
- adicionar ao menos um teste de configuração de paths
- opcionalmente configurar `mypy`

Validacao:

- toda alteracao relevante na ingestão quebra o CI se alterar o contrato sem ajuste de teste

Comandos de verificação:

```powershell
uv run ruff check .
uv run pytest
uv run mypy src
```

---

## BP-06 Rastreabilidade com `MLflow`

Objetivo: preparar a linhagem de experimentos, modelos e metadados de dados.

Arquivos a criar:

- `src/tracking.py`
- `docs/mlflow-tracking.md`

Tarefas:

- definir o `MLFLOW_TRACKING_URI` default para desenvolvimento local
- criar função utilitaria para registrar:
  - parâmetros
  - métricas
  - tags
  - artefatos
- definir tags obrigatorias por run:
  - `dataset_hash`
  - `dataset_source`
  - `parser_version`
  - `target_definition`
  - `python_version`
- preparar a interface para receber `git_commit` quando o repositório estiver inicializado em Git
- registrar o manifesto de ingestão como artefato

Validacao:

- uma execução simples de teste consegue abrir um run do `MLflow` e registrar tags e artefatos minimos

Comandos de verificação:

```powershell
uv run python -c "import mlflow; print(mlflow.__version__)"
uv run python -m src.tracking
```

---

## BP-07 Documentação e decisões arquiteturais

Objetivo: transformar as decisões do projeto em referência operavel para o time.

Arquivos a criar:

- `docs/contributing.md`
- `docs/architecture.md`
- `docs/decisions/README.md`

Tarefas:

- consolidar no `README.md` as decisões da etapa 1
- documentar o motivo do uso exclusivo de `MLflow`
- documentar a estratégia multi-OS
- documentar a política de notebooks apenas para demonstracao
- documentar o contrato de ingestão do `cleve.mod`
- documentar as pendencias do PDF ainda abertas

Validacao:

- um integrante novo consegue iniciar o projeto e entender o que está decidido é o que ainda depende de definicao

---

## BP-08 CI inicial no GitHub Actions

Objetivo: automatizar validacoes minimas a cada `push` e `pull_request`.

Arquivos a criar:

- `.github/workflows/ci.yml`

Tarefas:

- criar job de checkout
- instalar Python 3.13
- instalar `uv`
- sincronizar dependencias
- executar:
  - `uv run ruff check .`
  - `uv run pytest`
- adicionar passo para executar a ingestão do `.MOD`
- falhar o pipeline se o parser quebrar

Validacao:

- qualquer alteracao no parser ou na configuração basica passa por validação automatica

Comandos de verificação local:

```powershell
uv run ruff check .
uv run pytest
uv run python -m src.data.ingest_mod
```

---

## BP-09 Scaffolding do domínio de ML

Objetivo: deixar a etapa 2 pronta para comecar sem refatoracao estrutural.

Arquivos a criar:

- `src/features/build_features.py`
- `src/models/train.py`
- `src/evaluation/evaluate.py`
- `src/serving/app.py`
- `src/serving/schemas.py`

Tarefas:

- criar placeholders com assinaturas minimas
- separar claramente:
  - ingestão
  - features
  - treino
  - avaliação
  - servindo
- deixar `src/serving/app.py` apenas como esqueleto `Flask`, sem entrega funcional completa
- preparar contratos para a etapa 2:
  - entrada de treino
  - saída de treino
  - entrada de avaliação
  - contrato inicial de inferência

Validacao:

- os módulos existem e estao organizados sem misturar responsabilidades

---

## Checklist de Conclusao da Etapa 1

Antes de encerrar a etapa 1, confirme:

- bootstrap do projeto documentado
- ambiente Python 3.13 reproduzivel
- parser do `cleve.mod` implementado e testado
- dataset processado gerado de forma deterministica
- rastreabilidade minima com `MLflow` pronta
- CI validando lint, testes e ingestão
- scaffolding da etapa 2 criado
- pendencias do PDF registradas formalmente

## Sequencia Sugerida de Execucao em Lotes

Lote 1:

- BP-00
- BP-01
- BP-02

Lote 2:

- BP-03
- BP-04
- BP-05

Lote 3:

- BP-06
- BP-07
- BP-08
- BP-09

## Proximo Passo Depois Deste Backlog

Executar o Lote 1 no repositório e criar a estrutura fisica inicial do projeto.
