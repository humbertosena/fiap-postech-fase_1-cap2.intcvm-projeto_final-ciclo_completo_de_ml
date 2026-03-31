# FIAP HealthCare Plus MLOps

- FIAP - Curso de Pós Tech Machine Learning Engineering
- Turma: 9MLET
- Aluno: Humberto Sena Santos (rm370472)

> **Aviso importante**
>
> Este repositório é um exercício acadêmico. Os dados utilizados são públicos.
> O fluxo de treinamento e inferência aqui descrito não possui validação clínica
> e não deve ser utilizado para decisão médica real.

Este repositório implementa um ciclo completo de MLOps local e reproduzível
para triagem cardíaca, cobrindo ingestão, treino, avaliação, governança,
release, serving e monitoramento.

## Acesso Rápido

Se você quer validar o projeto sem ler o documento inteiro, siga esta ordem:

```bash
uv sync --dev
cp .env.example .env
uv run ruff check .
uv run pytest -q
uv run python -m src.models.release
uv run mlflow ui --backend-store-uri ./mlruns --host 127.0.0.1 --port 5000
uv run python -m src.serving.app
```

Depois abra:

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- MLflow: `http://127.0.0.1:5000`

## O Que Você Vai Encontrar

- pipeline de treino supervisionado com `scikit-learn`
- rastreabilidade com `MLflow`
- release automatizado do último modelo aprovado
- API `Flask` de inferência real
- documentação OpenAPI e Swagger UI
- monitoramento local com eventos, drift e gatilhos de retreinamento

## Público-Alvo

O projeto foi estruturado para que desenvolvedores plenos e entusiastas de
tecnologia consigam:

- reproduzir o ambiente local
- executar qualidade e testes
- treinar e promover um modelo
- subir a API
- consultar o `MLflow`
- navegar na API via Swagger

## Pré-Requisitos

Instale estes itens antes de começar:

1. `Python 3.13`
2. `uv`
3. `git`

Verificações rápidas:

```bash
python --version
uv --version
git --version
```

Se o seu ambiente usa `python3` em vez de `python`, ajuste os comandos conforme necessário.

## Ordem Recomendada de Leitura

Para avaliação técnica ou banca, a leitura mais eficiente é:

1. `README.md`
2. `docs/entrega-final.md`
3. `docs/api.md`
4. `docs/mlflow-tracking.md`
5. `plan/projeto-final-summary-executivo.md`

## Estrutura Relevante

```text
artifacts/            relatorios de treino, release e monitoramento
data/                 dados brutos e processados
docs/                 documentacao funcional e operacional
models/               pipelines serializados e registro local do aprovado
src/data/             ingestao, schema e contrato do dado
src/features/         preprocessamento e pipeline de features
src/models/           treino, release e registro
src/evaluation/       metricas, fairness, risco e gates
src/serving/          API Flask, OpenAPI, Swagger UI e telemetria
src/monitoring/       persistencia de eventos, drift e gatilhos
tests/                testes unitarios e de integracao
plan/                 plano, backlog e summaries por etapa
```

## Passo a Passo Para Reproduzir o Desenvolvimento

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd postech-fase_1-2.intcvm-projeto_final-ciclo_completo_de_ml
```

### 2. Instalar dependências

```bash
uv sync --dev
```

Esse comando cria o ambiente virtual do projeto e instala dependências de
execução e desenvolvimento.

### 3. Criar o arquivo `.env`

#### Shell POSIX

```bash
cp .env.example .env
```

#### PowerShell

```powershell
Copy-Item .env.example .env
```

O projeto funciona com os valores padrão do `.env.example`. Ajustes adicionais são opcionais.

### 4. Validar qualidade e testes

```bash
uv run ruff check .
uv run pytest -q
```

Se isso falhar, não avance para treino ou serving. Corrija o ambiente primeiro.

### 5. Treinar o modelo

```bash
uv run python -m src.models.train
```

Esse comando gera:

- métricas de treino e avaliação em `artifacts/training/<run_label>/`
- pipeline serializado em `models/<run_label>/`
- novo run no `MLflow`

### 6. Avaliar explicitamente o pipeline

```bash
uv run python -m src.evaluation.evaluate
```

Esse passo é útil para inspeção local das métricas e artefatos sem depender do release.

### 7. Promover o modelo aprovado

```bash
uv run python -m src.models.release
```

Esse comando:

- aplica os gates definidos no projeto
- registra a decisão de release
- atualiza `models/registry/latest_approved_model.json`

Sem esse passo, a API pode subir sem modelo aprovado disponível.

## Como Acessar o MLflow

### 1. Subir a interface do MLflow

```bash
uv run mlflow ui --backend-store-uri ./mlruns --host 127.0.0.1 --port 5000
```

### 2. Abrir no navegador

```text
http://127.0.0.1:5000
```

### 3. O que você verá

No `MLflow`, você consegue inspecionar:

- runs de treino
- parâmetros
- métricas
- artefatos
- runs de release
- runs de monitoramento

## Como Subir a Aplicação

Antes de subir a API, garanta que já exista um modelo aprovado:

```bash
uv run python -m src.models.release
```

Agora suba a aplicação:

```bash
uv run python -m src.serving.app
```

A API sobe por padrão em:

```text
http://127.0.0.1:8000
```

## Endpoints Principais

- `GET /health`
- `POST /predict`
- `GET /openapi.json`
- `GET /docs`

## Como Acessar o Swagger

Com a aplicação rodando:

1. abra o navegador em `http://127.0.0.1:8000/docs`
2. consulte a especificação OpenAPI em `http://127.0.0.1:8000/openapi.json`
3. execute chamadas de teste diretamente pela Swagger UI

Observação:

- a Swagger UI carrega os assets visuais por CDN
- a especificação OpenAPI continua disponível localmente em `/openapi.json`

## Exemplo de Chamada da API

### Health check

```bash
curl http://127.0.0.1:8000/health
```

### Predição

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "age": 63,
      "sex": "male",
      "chest_pain_type": "typical",
      "resting_blood_pressure": 145,
      "cholesterol": 233,
      "fasting_blood_sugar_gt_120": "yes",
      "rest_ecg": "normal",
      "max_heart_rate": 150,
      "exercise_induced_angina": "no",
      "oldpeak": 2.3,
      "slope": "flat",
      "num_vessels": 0,
      "thal": "normal"
    }
  }'
```

## Como Rodar o Monitoramento Batch

Depois de gerar tráfego na API:

```bash
uv run python -m src.monitoring.run_monitoring
```

Os artefatos ficam em `artifacts/monitoring/<run_label>/`.

## Fluxo Completo Recomendado

Se você quiser reproduzir o fluxo principal do projeto do zero:

```bash
uv sync --dev
cp .env.example .env
uv run ruff check .
uv run pytest -q
uv run python -m src.models.train
uv run python -m src.evaluation.evaluate
uv run python -m src.models.release
uv run mlflow ui --backend-store-uri ./mlruns --host 127.0.0.1 --port 5000
uv run python -m src.serving.app
```

## Documentos Principais

- `docs/README.md`
- `docs/entrega-final.md`
- `docs/api.md`
- `docs/monitoring.md`
- `docs/mlflow-tracking.md`
- `plan/projeto-final-summary-executivo.md`

## Limitações Conhecidas

- fairness por região: o "fairness por região" solicitado no documento de requisito inicial trata-se de um erro material, pois o atributo "região" não está contemplado na solicitação
- o baseline atual ainda não foi comparado sistematicamente com uma família maior de candidatos
- sem labels de produção, drift não prova sozinho degradação clínica
- a API ainda não possui autenticação nem endurecimento operacional de produção
