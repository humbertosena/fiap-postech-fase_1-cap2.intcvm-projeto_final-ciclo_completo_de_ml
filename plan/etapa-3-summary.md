# Etapa 3 - Summary Tecnico, Comparacao com a Etapa 2, Estado Atual do Código e Evidencias

## Objetivo deste documento

Registrar o estado real da etapa 3 com base no código atual do repositório, comparando explicitamente o que existia ao final da etapa 2 com o que foi implementado na etapa 3.

Este documento descreve:

- o que mudou da etapa 2 para a etapa 3
- quais módulos passaram a cobrir governança, auditoria e risco
- quais decisões arquiteturais foram formalizadas nesta etapa
- quais evidencias de validação existem hoje
- quais limitações e riscos continuam abertos para as etapas seguintes

## Escopo analisado

- código em `src/`
- testes em `tests/`
- configuração do projeto em `pyproject.toml` e `.env.example`
- documentação complementar em `docs/`
- artefatos gerados em `artifacts/training/`, `models/` e `mlruns/`
- backlog executável em `plan/etapa-3-backlog-executável.md`
- summary da etapa 2 em `plan/etapa-2-summary.md`

## Resumo executivo

Na etapa 2, o projeto entregava um pipeline reproduzivel de treinamento supervisionado com threshold tuning, serializacao do pipeline e tracking ampliado no `MLflow`. A etapa 3 mantem esse fluxo funcional e adiciona uma camada explicita de governança: auditoria segmentada por grupos sensiveis observaveis, relatórios de fairness por execução, relatórios de risco, model card inicial e ampliacao do tracking para evidencias de auditoria.

O que está operacional hoje na etapa 3:

- derivacao explicita de grupos de auditoria por `age_group` e `sex`
- separacao formal entre atributos usados no treino e atributos usados apenas para auditoria
- avaliação segmentada por grupo sobre o conjunto de teste do pipeline oficial
- calculo de `precision`, `recall`, `f1`, `false_negative_rate` e `false_positive_rate` por grupo
- calculo de gaps maximos entre grupos com política de alerta configuravel
- geração de `fairness_report.json` e `fairness_summary.txt` por run
- geração de `risk_summary.json` e `model_card.json` por run
- registro de métricas agregadas de fairness no `MLflow`
- documentação formal da política de fairness e do bloqueio de fairness por região
- testes automatizados cobrindo a nova camada de fairness
- validação fim a fim executada com sucesso

O que continua não implementado como funcionalidade final:

- fairness por região com dado real ou proxy aprovado
- gates bloqueantes automatizados em CI/CD
- comparacao sistematica entre multiplos modelos candidatos
- validação cruzada para estabilidade de threshold e fairness
- uso da API `Flask` como interface real de inferência
- monitoramento em produção por segmento

## Comparacao Objetiva: Etapa 2 vs Etapa 3

### 1. Estado do treino

Na etapa 2:

- `src/models/train.py` treinava, avaliava, serializava e registrava o baseline
- o resultado principal era desempenho global e artefatos de classificação
- não havia camada formal de auditoria por grupo

Na etapa 3:

- `src/models/train.py` continua treinando o baseline sem regressao funcional
- o mesmo fluxo agora executa auditoria segmentada no conjunto de teste
- o treino gera artefatos adicionais de fairness e risco no mesmo run
- o resumo retornado pelo comando de treino inclui métricas globais e auditoria de fairness

### 2. Estado da avaliação

Na etapa 2:

- a avaliação era global, centrada em `accuracy`, `precision`, `recall`, `f1` e `roc_auc`
- existiam matriz de confusao e classification report
- o threshold operacional `0.35` já era refletido no pipeline

Na etapa 3:

- a avaliação continua calculando as métricas globais da etapa 2
- foi adicionada avaliação por `age_group` e `sex`
- a auditoria calcula tamanhos de grupo, contagens de classe e taxas de erro por grupo
- gaps absolutos entre grupos passaram a ser computados e classificados como alertas
- `src/evaluation/evaluate.py` agora devolve também o bloco de fairness

### 3. Estado da governança e fairness

Na etapa 2:

- fairness existia apenas como pendencia de backlog e documentação futura
- não havia política técnica implementada para auditoria de vies

Na etapa 3:

- fairness virou parte formal do contrato do pipeline
- foi criada uma política operacional de fairness baseada em grupos observaveis no dado atual
- o projeto audita `age_group` e `sex`
- a etapa 3 registra explicitamente que região permanece indisponivel no dataset atual
- a documentação distingue evidencia observacional de conclusão normativa

### 4. Estado do tracking

Na etapa 2:

- o `MLflow` registrava dado, pré-processamento, parâmetros, métricas globais e artefatos de modelo e avaliação

Na etapa 3:

- o `MLflow` continua cobrindo toda a linhagem da etapa 2
- o run passou a registrar política de fairness e grupos auditados como parâmetros e tags
- gaps agregados de fairness passaram a ser logados como métricas
- relatórios de fairness, risco e model card passaram a ser publicados como artefatos do mesmo run

### 5. Estado da documentação

Na etapa 2:

- o projeto já tinha baseline, threshold e arquitetura documentados
- não havia documentação operacional de fairness ou risco do modelo

Na etapa 3:

- foi criada a ADR de política de fairness
- a decisão de fairness por região foi formalizada como bloqueio por dado indisponivel
- foram adicionados `docs/model-risk.md` e `docs/model-card.md`
- `README.md`, `docs/architecture.md` e `docs/mlflow-tracking.md` foram atualizados para refletir a etapa 3

### 6. Estado dos testes

Na etapa 2:

- os testes cobriam config, ingestão, dataset, features, treino, avaliação e serializacao
- não havia teste de auditoria por subgrupo

Na etapa 3:

- foi criado `tests/unit/test_fairness.py`
- a suite agora valida:
  - derivacao de grupos de auditoria
  - métricas segmentadas por grupo
  - calculo de gaps
  - estrutura do fairness report
  - exposicao do bloco de fairness em treino e avaliação

## Estrutura implementada na etapa 3

```text
artifacts/
  training/
    <run_label>/
      metrics.json                 -> metricas globais do run
      classification_report.json   -> relatorio detalhado por classe
      confusion_matrix.csv         -> matriz de confusao global
      threshold_selection.json     -> comparacao de thresholds e threshold escolhido
      fairness_report.json         -> auditoria segmentada por grupo
      fairness_summary.txt         -> resumo executivo da auditoria
      risk_summary.json            -> resumo de risco do modelo no run
      model_card.json              -> model card inicial do run
models/
  <run_label>/
    training_pipeline.joblib       -> pipeline completo serializado
    model_metadata.json            -> metadados do modelo, threshold e fairness
    dataset_lineage.json           -> linhagem do dataset do run
src/
  config.py                        -> configuracao ampliada para fairness e governanca
  tracking.py                      -> tracking com artefatos e metricas de auditoria
  data/
    dataset.py                     -> contrato de treino e grupos de auditoria
    schema.py                      -> schema ampliado com colunas e faixas de auditoria
  evaluation/
    fairness.py                    -> avaliacao segmentada e gaps por grupo
    risk.py                        -> relatorio de risco e model card
    metrics.py                     -> metricas globais e taxas de erro
    reports.py                     -> persistencia de JSON, CSV e TXT
    evaluate.py                    -> avaliacao executavel com bloco de fairness
  models/
    train.py                       -> treino fim a fim com fairness e risco
tests/
  unit/
    test_fairness.py               -> testes da camada de auditoria
```

## Design implementado na etapa 3

### 1. Arquitetura logica atual

A arquitetura continua organizada em camadas, mas a camada de ML deixou de ser apenas performance + rastreabilidade e passou a incorporar governança:

- `config`: centraliza parâmetros de treino, threshold, fairness e tracking
- `data`: define parser, schema, contrato de treino e derivacao dos grupos de auditoria
- `features`: preserva pré-processamento consistente entre treino e inferência futura
- `models`: seleciona baseline, treina, serializa e gera artefatos tecnicos é de governança
- `evaluation`: calcula métricas globais, métricas segmentadas, gaps, risco e relatórios
- `tracking`: registra desempenho e auditoria no `MLflow`
- `serving`: permanece como scaffold para etapas posteriores

### 2. Principios tecnicos observados no código atual

- o parser oficial da etapa 1 continua sendo a única entrada valida do dado processado
- o treino continua consumindo apenas o dataset processado oficial
- colunas de diagnóstico bruto continuam fora das features para evitar leakage
- fairness não interfere na selecao do threshold nem no treino; ela audita o resultado do pipeline aprovado
- grupos sensiveis são derivados de atributos observaveis e explicitamente separados do conjunto de modelagem
- ausencias do dado, como região, são tratadas como limitacao formal e não como suposicao implicita

## Definicoes implementadas na etapa 3

### 1. Configuracao centralizada ampliada

Arquivo: `src/config.py`

Novos campos relevantes adicionados na etapa 3:

- `fairness_policy_name`
- `fairness_alert_threshold`
- `fairness_min_group_size`

Defaults atuais relevantes:

- `MLFLOW_EXPERIMENT_NAME=phase-3-training`
- `FAIRNESS_POLICY_NAME=max_gap_alert_0.15`
- `FAIRNESS_ALERT_THRESHOLD=0.15`
- `FAIRNESS_MIN_GROUP_SIZE=10`

### 2. Contrato de auditoria por grupos

Arquivos: `src/data/schema.py` e `src/data/dataset.py`

Definicoes materializadas:

- `AUDIT_SOURCE_COLUMNS`
- `AUDIT_GROUP_COLUMNS`
- `AGE_GROUP_COLUMN`
- `AGE_GROUP_BINS`
- `AGE_GROUP_LABELS`
- `build_audit_frame()`

Faixas etarias atuais:

- `lt_45`
- `45_54`
- `55_64`
- `65_plus`

### 3. Camada de fairness

Arquivo: `src/evaluation/fairness.py`

Capacidades implementadas:

- derivacao e normalizacao de grupos de auditoria
- métricas por grupo
- calculo de gaps maximos por metrica
- emissao de alertas quando gaps excedem o limite configurado
- exposicao de métricas agregadas para `MLflow`
- geração de resumo executivo legivel

Métricas auditadas por grupo:

- `precision`
- `recall`
- `f1`
- `false_negative_rate`
- `false_positive_rate`

### 4. Camada de risco

Arquivo: `src/evaluation/risk.py`

Artefatos e contratos implementados:

- `build_risk_summary()`
- `build_model_card()`

Conteúdo coberto:

- uso pretendido e não pretendido
- limitações do dado
- limitações do modelo
- política operacional vigente
- riscos atuais do baseline
- proximos passos recomendados

### 5. Tracking ampliado

Arquivo: `src/tracking.py`

Mudanças relevantes:

- `fairness_policy_name` passou a ser tag do run
- o nome do experimento default passou a ser `phase-3-training`
- o tracking passou a receber métricas agregadas de fairness e artefatos adicionais de auditoria

## Resultado validado da etapa 3

### 1. Validacao executada

Comandos executados com sucesso:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check .
UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q
UV_CACHE_DIR=/tmp/uv-cache uv run python -m src.models.train
UV_CACHE_DIR=/tmp/uv-cache uv run python -m src.evaluation.evaluate
```

Resultado dos testes:

- `17 passed`
- `2 warnings` vindos de dependencias do `mlflow` e `pydantic`, sem falha funcional

### 2. Resultado do treino validado

Run registrado no `MLflow`:

- `run_id = 962243cd11964a3880e189cc1c39f6f5`
- experimento: `phase-3-training`

Métricas globais:

- `accuracy = 0.7704918032786885`
- `precision = 0.7058823529411765`
- `recall = 0.8571428571428571`
- `f1 = 0.7741935483870968`
- `roc_auc = 0.8766233766233767`
- `decision_threshold = 0.35`

Resumo de fairness do run:

- `fairness_alert_count = 10`
- grupos auditados: `age_group`, `sex`
- dimensao indisponivel: `region`

Interpretacao objetiva:

- o baseline continua funcional e reproduzivel
- a auditoria detectou gaps relevantes acima do limite inicial de `0.15`
- o projeto agora produz evidencia explicita dessas diferencas, em vez de deixar fairness como lacuna tacita

## Principais artefatos da etapa 3

Run de treino validado:

- `artifacts/training/20260324T213143Z/metrics.json`
- `artifacts/training/20260324T213143Z/classification_report.json`
- `artifacts/training/20260324T213143Z/confusion_matrix.csv`
- `artifacts/training/20260324T213143Z/threshold_selection.json`
- `artifacts/training/20260324T213143Z/fairness_report.json`
- `artifacts/training/20260324T213143Z/fairness_summary.txt`
- `artifacts/training/20260324T213143Z/risk_summary.json`
- `artifacts/training/20260324T213143Z/model_card.json`
- `models/20260324T213143Z/training_pipeline.joblib`
- `models/20260324T213143Z/model_metadata.json`
- `models/20260324T213143Z/dataset_lineage.json`

## Limitações e riscos residuais após a etapa 3

### 1. Fairness por região segue bloqueada

O projeto continua sem dado real ou proxy aprovado de região. Portanto:

- não é possivel afirmar fairness regional
- a ausência dessa dimensao foi corretamente documentada, mas não resolvida

### 2. Gaps de fairness foram detectados, não mitigados

A etapa 3 mede e registra o problema, mas não aplica técnica de mitigacao. Isso e coerente com o backlog, mas implica que:

- o baseline ainda pode apresentar comportamento desigual entre grupos
- a etapa 4 deve decidir como transformar esses achados em alertas ou gates

### 3. Threshold segue validado por hold-out único

O threshold `0.35` continua tecnicamente rastreado e coerente com o objetivo de maximizar `recall`, mas ainda:

- não foi submetido a validação cruzada
- não teve estabilidade por grupo verificada em multiplos folds

### 4. Dataset pequeno aumenta variancia da auditoria

Mesmo sem grupos abaixo do mínimo configurado neste run validado, a base continua pequena. Portanto:

- os gaps observados precisam ser interpretados com cautela
- pequenas mudanças na amostragem podem alterar métricas segmentadas de forma relevante

## Conclusao

A etapa 3 foi implementada com sucesso e elevou o projeto de um pipeline reproduzivel de treino para um pipeline reproduzivel com governança técnica minima. O sistema agora não responde apenas como o modelo performa globalmente, mas também como essa performance se distribui entre grupos auditaveis, quais riscos continuam abertos e quais limitações impedem afirmacoes mais fortes.

Em termos praticos, a transição principal foi:

- Etapa 2: treino, threshold tuning, avaliação global, persistencia e tracking
- Etapa 3: treino + auditoria de fairness + relatórios de risco + governança rastreavel no mesmo run

## Proximo passo natural para a Etapa 4

A etapa 4 deve partir do estado real deixado pela etapa 3 e transformar parte dessa governança em critério operacional automatizavel, especialmente:

- alertas e possiveis gates para gaps de fairness
- limites minimos de desempenho global
- critério formal para promocao ou bloqueio de modelos
