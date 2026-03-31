# Etapa 6 - Summary Tecnico, Comparacao com a Etapa 5, Estado Atual do Código e Evidencias

## Objetivo deste documento

Registrar o estado real da etapa 6 com base no código atual do repositório, comparando explicitamente o que existia ao final da etapa 5 com o que foi implementado na etapa 6.

Este documento descreve:

- o que mudou da etapa 5 para a etapa 6
- quais módulos passaram a cobrir monitoramento, drift e gatilhos de retreinamento
- quais decisões arquiteturais foram formalizadas nesta etapa
- quais evidencias de validação existem hoje
- quais limitações e riscos continuam abertos para o fechamento do projeto

## Escopo analisado

- código em `src/`
- testes em `tests/`
- configuração do projeto em `pyproject.toml` e `.env.example`
- documentação complementar em `docs/`
- workflow em `.github/workflows/ci.yml`
- artefatos gerados em `artifacts/training/`, `artifacts/monitoring/`, `models/` e `mlruns/`
- backlog executável em `plan/etapa-6-backlog-executável.md`
- summary da etapa 5 em `plan/etapa-5-summary.md`

## Resumo executivo

Na etapa 5, o projeto entregava treino, release e serving real do modelo aprovado. A etapa 6 manteve esse fluxo sem regressao e adicionou o ciclo pos-deploy: telemetria estruturada da API, persistencia local de eventos de inferência, referência de monitoramento gerada no treino, relatórios batch de qualidade e drift, gatilhos rastreaveis de retreinamento e tracking desse monitoramento no `MLflow`.

O que está operacional hoje na etapa 6:

- eventos estruturados da API em `artifacts/monitoring/events/api_events.jsonl`
- eventos de inferência em `artifacts/monitoring/events/inference_events.jsonl`
- referência de monitoramento por run em `artifacts/training/<run_label>/monitoring_reference.json`
- rotina oficial `src.monitoring.run_monitoring` para consolidação batch
- relatórios de qualidade de dados, drift e gatilhos por execução de monitoramento
- tracking do monitoramento no `MLflow`
- CI validando não apenas treino, release e API, mas também a consolidação batch de monitoramento
- backlog da etapa 6 refletindo o estado implementado

O que continua não implementado como funcionalidade final:

- labels de produção para confirmar degradação real do modelo em uso
- monitoramento em plataforma externa gerenciada
- scheduler operacional dedicado para rodar o monitoramento de forma periodica fora do CI e do uso manual
- retreinamento automatico governado ponta a ponta
- fairness por região com dado real ou proxy aprovado
- autenticação e protecoes operacionais mais fortes na API

## Comparacao Objetiva: Etapa 5 vs Etapa 6

### 1. Estado do serving e operação

Na etapa 5:

- a API `Flask` já respondia `GET /health` e `POST /predict`
- o modelo aprovado era carregado corretamente do registro local
- a inferência real estava operacional, mas sem trilha persistida de eventos

Na etapa 6:

- `src/serving/app.py` passou a emitir telemetria por request
- requests bem sucedidos e falhos ficam registrados de forma estruturada
- inferencias reais deixam rastro local para análise posterior
- o serving passou a participar formalmente do ciclo de observabilidade do projeto

### 2. Estado do treinamento e dos artefatos

Na etapa 5:

- o treino gerava métricas, fairness, risco, modelo serializado e artefatos de release
- não existia snapshot oficial para comparar inferência com referência de treino

Na etapa 6:

- `src/models/train.py` passou a gerar `monitoring_reference.json`
- o manifesto aprovado passou a carregar o path da referência de monitoramento
- o modelo aprovado agora entrega não apenas o pipeline, mas também a base estatística para drift e qualidade

### 3. Estado do contrato da API

Na etapa 5:

- o contrato HTTP existia e era validado, mas a etapa ainda não tinha confrontado esse contrato contra a referência de treino em produção

Na etapa 6:

- o monitoramento revelou um problema real: a API aceitava aliases amigaveis que não batiam com o vocabulario canônico do treino
- `src/serving/schemas.py` foi corrigido para normalizar aliases como `typical -> angina`, `yes -> true`, `normal -> norm`, `no -> fal`
- isso alinhou inferência online e monitoramento com o mesmo contrato categórico do dataset treinado

### 4. Estado da observabilidade

Na etapa 5:

- havia apenas smoke test de latência local
- não havia relatorio consolidado de operação, qualidade e drift

Na etapa 6:

- `src/monitoring/store.py` passou a persistir eventos locais
- `src/monitoring/data_quality.py` calcula qualidade e conformidade de inferência
- `src/monitoring/drift.py` compara inferência com referência de treino
- `src/monitoring/triggers.py` transforma sinais em recomendação rastreavel
- `src/monitoring/run_monitoring.py` consolida tudo em uma execução única

### 5. Estado do tracking e governança

Na etapa 5:

- o `MLflow` rastreava treino e release
- não existia experimento dedicado ao monitoramento

Na etapa 6:

- `src/tracking.py` passou a registrar runs de monitoramento
- o projeto ganhou experimento dedicado `phase-6-monitoring`
- a recomendação de retreinamento passou a ser artefato formal, não comentario externo

### 6. Estado do CI/CD

Na etapa 5:

- o CI validava qualidade, avaliação, API, packaging e release
- não havia passo oficial de observabilidade batch

Na etapa 6:

- o workflow ganhou etapa para gerar trafego sintetico local
- o workflow passou a rodar `src.monitoring.run_monitoring`
- os artefatos de monitoramento passam a ser enviados junto dos demais artefatos do pipeline

### 7. Estado da documentação

Na etapa 5:

- o projeto tinha API, deployment local, latência, baseline, threshold, fairness, risco e release documentados
- faltava documentar o ciclo pos-deploy

Na etapa 6:

- foram adicionados `docs/monitoring.md` e `docs/decisions/retraining-trigger-policy.md`
- `README.md`, `docs/api.md`, `docs/deployment.md`, `docs/architecture.md` e `docs/model-risk.md` foram atualizados
- a documentação agora representa o ciclo completo: treino, release, serving, monitoramento e investigacao de retreinamento

## Estrutura implementada na etapa 6

```text
src/
  monitoring/
    contracts.py                     -> contratos dos eventos monitorados
    store.py                         -> persistencia local em jsonl
    reference.py                     -> referencia estatistica do treino aprovado
    data_quality.py                  -> checks de qualidade de inferencia
    drift.py                         -> checks de drift offline
    triggers.py                      -> gatilhos de alerta e retreinamento
    reporting.py                     -> agregacoes operacionais
    run_monitoring.py                -> rotina batch oficial da etapa 6
  serving/
    app.py                           -> API com telemetria e persistencia de eventos
    monitoring.py                    -> helpers de request_id, timestamp e escrita
    schemas.py                       -> normalizacao do contrato categórico da API
docs/
  monitoring.md                      -> contrato e operacao do monitoramento
  decisions/
    retraining-trigger-policy.md     -> politica aprovada para gatilhos
artifacts/
  monitoring/
    events/                          -> eventos persistidos da API e da inferencia
```

## Design implementado na etapa 6

### 1. Arquitetura logica atual

A arquitetura continua organizada em camadas, mas agora o serving deixa de ser fim do fluxo e passa a alimentar a camada de observabilidade:

- `models`: treinam, liberam e registram o modelo aprovado junto com a referência de monitoramento
- `serving`: carrega o aprovado, atende requests e persiste eventos operacionais é de inferência
- `monitoring`: consolida eventos em relatórios de qualidade, drift e gatilhos
- `tracking`: registra treino, release e monitoramento no `MLflow`

### 2. Principios tecnicos observados no código atual

- o monitoramento continua local e reproduzivel, sem dependencia de plataforma externa
- a referência estatística usada em drift nasce do treino aprovado, não de fonte paralela
- o serving não persiste payload bruto arbitrario; ele persiste o payload já normalizado para o contrato do treino
- recomendação de retreinamento abre processo auditavel, não promocao automatica
- o CI usa trafego sintetico para validar o ciclo mínimo de monitoramento fim a fim

## Definicoes implementadas na etapa 6

### 1. Telemetria e persistencia local

Arquivos: `src/serving/app.py`, `src/serving/monitoring.py`, `src/monitoring/contracts.py` e `src/monitoring/store.py`

Capacidades implementadas:

- geração de `request_id` por chamada
- latência por request
- eventos `request_received`, `prediction_completed`, `prediction_failed`, `model_unavailable` e `health_checked`
- escrita em `jsonl` para eventos de API e inferência

### 2. Referencia estatística do treino aprovado

Arquivos: `src/models/train.py`, `src/monitoring/reference.py`, `src/models/registry.py` e `src/serving/model_store.py`

Capacidades implementadas:

- geração de bins e proporções de referência por feature numerica
- distribuição de categorias de referência
- distribuição de score e taxa positiva prevista
- propagacao da referência para o manifesto aprovado

### 3. Qualidade de dados, drift e gatilhos

Arquivos: `src/monitoring/data_quality.py`, `src/monitoring/drift.py`, `src/monitoring/triggers.py` e `src/monitoring/reporting.py`

Capacidades implementadas:

- taxa de missing por feature
- taxa de valores fora de faixa numerica
- taxa de categorias desconhecidas
- PSI para features numericas e score
- diferenca absoluta maxima para features categoricas
- diferenca da taxa de positivos previstos
- decisão final `healthy`, `insufficient_data` ou `retraining_recommended`

### 4. Contrato categórico da API

Arquivo: `src/serving/schemas.py`

Capacidades implementadas:

- aliases amigaveis aceitos no payload HTTP
- normalizacao para o vocabulario canonico do dataset treinado
- rejeicao explicita de categorias fora do contrato conhecido

## Evidencias de validação da etapa 6

Validacoes executadas com sucesso:

- `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check .`
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q`
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m src.models.release`
- smoke real da API com `Flask` test client usando o manifesto aprovado atualizado
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m src.monitoring.run_monitoring`
- validação isolada do monitoramento em diretorio temporario após a correção do contrato categórico

Resultado da suite:

- `36 passed`
- `2 warnings` vindos de dependencias do `mlflow` e `pydantic`, sem bloqueio funcional

## Resultado operacional validado

Release renovado no `MLflow`:

- experimento de treino/release: `phase-4-release`
- `run_id = c4b7428206b94411b86cffd511e6bbb2`
- status de release: `approved_with_alerts`
- promocao elegivel: `true`
- promovido no registro local: `true`

Artefatos principais gerados no release validado:

- `artifacts/training/20260329T130143Z/metrics.json`
- `artifacts/training/20260329T130143Z/monitoring_reference.json`
- `models/registry/latest_approved_model.json`

Monitoramento registrado no `MLflow`:

- experimento: `phase-6-monitoring`
- `monitoring_run_id = 8635bfe0c896401582e60c373afb63aa`
- artefatos em `artifacts/monitoring/20260329T130318Z/`

## Leitura critica dos resultados

A primeira execução real do monitoramento sobre o workspace acumulado trouxe sinais fortes de drift e qualidade, mas esse resultado precisa ser interpretado corretamente:

- o histórico local continha eventos de sessões anteriores
- parte desses eventos vinha de payloads gerados antes da correção do contrato categórico do serving
- por isso, esse run funciona como evidencia de que a observabilidade estava ativa, mas não como fotografia limpa do estado final após a correção

Para validar o comportamento final da etapa 6 sem contaminacao por histórico anterior, foi executado um monitoramento isolado em diretorio temporario com trafego sintetico novo. Nesse cenário:

- `prediction_count = 2`
- `error_rate = 0.0`
- `unknown_category_rate = 0.0` em todos os campos categóricos
- `trigger_status = healthy`

Essa segunda validação confirma que o problema exposto pelo monitoramento era real, foi corrigido no contrato da API é o pipeline pos-fix passou a gerar eventos coerentes com a referência do treino.

## Estado atual do backlog da etapa 6

O backlog executável da etapa 6 foi atualizado para refletir implementacao concluída:

- `BP6-00` a `BP6-08`: `concluído`
- status geral do backlog: `implementado`

## Riscos e limitações residuais após a etapa 6

Mesmo com a etapa 6 implementada, permanecem riscos importantes:

- sem labels de produção, drift continua sendo evidencia indireta e não prova clinica de degradação
- monitoramento continua local ao projeto e não distribuido em plataforma operacional externa
- thresholds de gatilho ainda são heuristicas iniciais e devem ser recalibrados com uso real
- fairness por região continua indisponivel pela ausência do atributo no dado
- a API ainda não tem autenticação, rate limiting ou protecoes mais fortes de produção

## Conclusao

A transição principal da etapa 5 para a etapa 6 foi concluída:

- etapa 5: treino + release + serving real
- etapa 6: treino + release + serving real + monitoramento operacional + drift + gatilhos rastreaveis de retreinamento

Com isso, o projeto deixa de terminar no deploy e passa a operar com um ciclo fechado mínimo de MLOps dentro do escopo local do repositório.
