# Etapa 2 - Backlog Executavel

Este backlog converte o objetivo da etapa 2 em tarefas técnicas executaveis, considerando o plano mestre do projeto é o estado real entregue pela etapa 1.

## Objetivo da Etapa 2

Transformar o bootstrap da etapa 1 em um pipeline de treinamento reproduzivel, rastreavel e testavel, com pré-processamento consistente, treino automatizado, avaliação objetiva e registro completo no `MLflow`.

Ao final da etapa 2, o projeto deve sair do estado atual de placeholders em `src/features/build_features.py`, `src/models/train.py` e `src/evaluation/evaluate.py` para um fluxo real que:

- consome o dataset processado gerado pelo parser oficial
- separa treino e avaliação de forma reproduzivel
- aplica pré-processamento versionado e consistente
- treina ao menos um baseline oficial
- calcula métricas relevantes para o contexto clinico
- registra parâmetros, métricas, artefatos e metadados no `MLflow`
- persiste o modelo treinado para uso nas etapas seguintes

## Base Real Herdada da Etapa 1

A etapa 2 parte das seguintes entregas já implementadas:

- configuração centralizada em `src/config.py`
- parser oficial do dado bruto em `src/data/ingest_mod.py`
- schema canonico em `src/data/schema.py`
- dataset processado em `data/processed/heart_disease_cleveland.csv`
- relatorio de ingestão em `artifacts/data_ingestion_report.json`
- bootstrap de tracking em `src/tracking.py`
- scaffolding de features, treino e avaliação em `src/features/`, `src/models/` e `src/evaluation/`
- testes unitários da configuração e da ingestão
- CI inicial com `uv`, `ruff`, `pytest` e validação da ingestão

## Escopo Deste Backlog

Este backlog cobre apenas a etapa 2:

- definicao do contrato do dataset de treino
- split reproduzivel de treino e teste
- pré-processamento consistente para treino e inferência futura
- baseline oficial de modelagem
- fluxo de treino real
- avaliação com métricas e artefatos
- rastreabilidade ampliada no `MLflow`
- persistencia do pipeline treinado
- testes do pipeline de treinamento
- documentação operacional da etapa 2

Ficam fora deste backlog:

- fairness operacional e gates de vies da etapa 3
- automacao completa em CI/CD da etapa 4
- API funcional de inferência da etapa 5
- conteinerização com Docker
- monitoramento, drift e retreinamento automatico da etapa 6

## Premissas de Execucao

As tarefas abaixo assumem:

1. Python `3.13`
2. `uv` como ferramenta de ambiente e dependencias
3. `MLflow` como camada única de rastreabilidade
4. consumo exclusivo do dataset processado gerado pelo parser oficial
5. target binario já fixado como `buff=0` e `sick=1`
6. compatibilidade com Windows, Linux e macOS

## Riscos e Pendencias Que Impactam a Etapa 2

Estes itens não impedem o treino do baseline, mas devem ser explicitamente acomodados no desenho técnico:

1. o requisito de fairness por região ainda permanece em aberto e não pode ser resolvido na etapa 2 com o dado atual
2. o baseline do MVP precisa ser formalizado como critério de comparacao, mesmo que o gate oficial fique para etapa posterior
3. a prioridade clinica tende a favorecer `recall`, entao a avaliação não pode se limitar a `accuracy`
4. o projeto ainda não possui contrato de serializacao do modelo treinado
5. a API futura exigira pré-processamento identico ao do treino, entao o pipeline precisa encapsular transformacoes e modelo no mesmo artefato

## Ordem de Execucao Recomendada

1. BP2-00 Fechar definicoes operacionais da etapa 2
2. BP2-01 Formalizar o contrato de treino e avaliação
3. BP2-02 Implementar pré-processamento versionado
4. BP2-03 Implementar baseline oficial de modelagem
5. BP2-04 Implementar avaliação e artefatos de validação
6. BP2-05 Ampliar tracking e registro no `MLflow`
7. BP2-06 Persistir pipeline treinado para reuso
8. BP2-07 Cobrir o pipeline com testes
9. BP2-08 Atualizar documentação operacional
10. BP2-09 Preparar o terreno para CI da etapa 4

## Status Atual

- `BP2-00` concluído
- `BP2-01` concluído
- `BP2-02` concluído
- `BP2-03` concluído
- `BP2-04` concluído
- `BP2-05` concluído
- `BP2-06` concluído
- `BP2-07` concluído
- `BP2-08` concluído
- `BP2-09` concluído
- decisões aprovadas:
  - baseline oficial: `LogisticRegression`
  - metrica principal: `recall`
  - política de threshold: maximizar `recall` com `precision >= 0.70`
  - threshold operacional aprovado: `0.35`
- validação executada:
  - `uv run ruff check .`
  - `uv run pytest -q`
  - `uv run python -m src.models.train`

---

## BP2-00 Fechar definicoes operacionais da etapa 2

Status: concluído.

Objetivo: remover ambiguidades que inviabilizam comparacao de runs e consistencia do treino.

Arquivos criados ou atualizados:

- `docs/decisions/mvp-baseline.md`
- `docs/decisions/threshold-policy.md`
- `docs/architecture.md`
- `README.md`

Decisões registradas:

- metrica principal da etapa 2: `recall`
- métricas obrigatorias por execução:
  - `recall`
  - `precision`
  - `f1`
  - `roc_auc`, quando aplicavel
  - `accuracy` como metrica secundaria
- estratégia de split: hold-out fixo com `random_state=42` e estratificacao por `target`
- baseline oficial inicial: `LogisticRegression`
- política de threshold: maximizar `recall` com `precision >= 0.70`
- threshold operacional aprovado: `0.35`

Critério de pronto:

- existe uma regra documentada e objetiva para comparar duas execucoes de treino
- existe uma decisão arquitetural explicita para o threshold de classificação

Dependencias:

- nenhuma

---

## BP2-01 Formalizar o contrato de treino e avaliação

Status: concluído.

Objetivo: transformar o dataset processado da etapa 1 em entrada oficial do pipeline de modelagem.

Arquivos a criar ou atualizar:

- `src/data/dataset.py`
- `src/data/schema.py`
- `src/config.py`
- `tests/unit/test_dataset.py`

Tarefas:

- criar funcoes para carregar o dataset processado como fonte oficial de treino
- separar explicitamente:
  - colunas de entrada
  - coluna alvo
  - colunas numericas
  - colunas categoricas
- remover do fluxo de treino colunas que representem vazamento de alvo, se aplicavel
- formalizar uma função de split reproduzivel com suporte a `test_size`, `random_state` e estratificacao
- registrar no código o contrato mínimo esperado do dataset para treino
- adicionar validacoes para:
  - coluna `target` obrigatoria
  - tipos esperados
  - ausência de colunas desconhecidas criticas

Saídas esperadas:

- API explicita para carregar e particionar o dataset
- contrato reutilizavel por treino, avaliação e inferência futura

Validacao:

- duas execucoes com o mesmo `random_state` geram o mesmo split
- mudanças indevidas no schema quebram teste automatizado

Comandos de verificação:

```bash
uv run pytest tests/unit/test_dataset.py
```

Dependencias:

- BP2-00

---

## BP2-02 Implementar pré-processamento versionado

Status: concluído.

Objetivo: garantir que o tratamento das features seja identico entre treino e inferência futura.

Arquivos a criar ou atualizar:

- `src/features/build_features.py`
- `src/features/preprocessing.py`
- `src/config.py`
- `tests/unit/test_build_features.py`

Tarefas:

- substituir o placeholder atual por um pipeline real de pré-processamento
- implementar transformacoes com `scikit-learn` usando `Pipeline` e `ColumnTransformer`
- tratar valores faltantes por tipo de coluna
- codificar variaveis categoricas de forma deterministica
- padronizar variaveis numericas apenas se o algoritmo escolhido exigir
- encapsular pré-processamento e modelo no mesmo fluxo treinavel
- registrar uma versão do pré-processamento para tracking

Saídas esperadas:

- função ou factory que monta o pipeline de features
- lista oficial de features esperadas no treino
- pré-processamento serializavel junto com o modelo

Validacao:

- o pipeline aceita o dataset atual sem erro
- a transformacao preserva o alinhamento entre features e target
- a execução não depende de notebook nem de manipulacao manual de dataframe fora do pipeline

Comandos de verificação:

```bash
uv run pytest tests/unit/test_build_features.py
```

Dependencias:

- BP2-01

---

## BP2-03 Implementar baseline oficial de modelagem

Status: concluído.

Objetivo: sair do `train_placeholder()` para um treino real, reproduzivel e comparavel.

Arquivos a criar ou atualizar:

- `src/models/train.py`
- `src/models/baseline.py`
- `src/config.py`
- opcionalmente `src/models/registry.py`
- `tests/unit/test_train.py`

Tarefas:

- definir pelo menos um baseline oficial simples e defensavel:
  - recomendação pragmatica: `LogisticRegression`
- opcionalmente comparar com um segundo baseline tabular:
  - `RandomForestClassifier`
  - ou `HistGradientBoostingClassifier`
- implementar função de treino parametrizavel
- separar nitidamente:
  - leitura do dado
  - split
  - montagem do pipeline
  - ajuste do modelo
  - retorno de artefatos e métricas
- registrar hiperparametros default no código e na documentação
- substituir o `main()` placeholder por execução real de treino

Saídas esperadas:

- pipeline treinado em memoria
- resumo estruturado da execução
- interface pronta para ser chamada por CI na etapa 4

Validacao:

- `uv run python -m src.models.train` executa de ponta a ponta
- a execução produz métricas reais em vez de `None`

Comandos de verificação:

```bash
uv run python -m src.models.train
uv run pytest tests/unit/test_train.py
```

Dependencias:

- BP2-02

---

## BP2-04 Implementar avaliação e artefatos de validação

Status: concluído.

Objetivo: transformar `evaluate_placeholder()` em avaliação util para decisão técnica e auditoria futura.

Arquivos a criar ou atualizar:

- `src/evaluation/evaluate.py`
- `src/evaluation/metrics.py`
- `src/evaluation/reports.py`
- `artifacts/` como destino de saídas locais
- `tests/unit/test_evaluate.py`

Tarefas:

- calcular métricas de classificação no conjunto de teste
- incluir pelo menos:
  - matriz de confusao
  - classification report em JSON
  - tabela de métricas resumidas
- registrar threshold usado para classificação, se houver ajuste explicito
- gerar artefatos locais versionaveis por run:
  - `metrics.json`
  - `classification_report.json`
  - `confusion_matrix.csv` ou equivalente
- preparar estrutura para comparacao futura de modelos

Saídas esperadas:

- avaliação reproduzivel e desacoplada do treino placeholder
- artefatos suficientes para sustentar comparacao de runs no `MLflow`

Validacao:

- os artefatos são gerados em execução local
- as métricas retornadas pelo modulo batem com os artefatos persistidos

Comandos de verificação:

```bash
uv run python -m src.evaluation.evaluate
uv run pytest tests/unit/test_evaluate.py
```

Dependencias:

- BP2-03

---

## BP2-05 Ampliar tracking e registro no `MLflow`

Status: concluído.

Objetivo: sair do tracking bootstrap da etapa 1 para rastreabilidade completa do pipeline de treinamento.

Arquivos a criar ou atualizar:

- `src/tracking.py`
- `docs/mlflow-tracking.md`
- `src/models/train.py`
- `src/evaluation/evaluate.py`
- opcionalmente `tests/unit/test_tracking.py`

Tarefas:

- manter os metadados de linhagem da etapa 1:
  - `dataset_hash`
  - `dataset_source`
  - `parser_version`
  - `target_definition`
  - `python_version`
- adicionar parâmetros obrigatorios da etapa 2:
  - algoritmo
  - `random_state`
  - `test_size`
  - lista de features
  - versão do pré-processamento
  - hiperparametros do modelo
- adicionar métricas obrigatorias:
  - `recall`
  - `precision`
  - `f1`
  - `accuracy`
  - `roc_auc`, se calculada
- registrar artefatos obrigatorios:
  - relatorio de ingestão
  - métricas em JSON
  - classification report
  - matriz de confusao
  - assinatura do modelo ou metadados equivalentes
- padronizar nome de experimento da etapa 2
- garantir que um run permita responder:
  - qual dado foi usado
  - qual pré-processamento foi aplicado
  - qual algoritmo e hiperparametros foram usados
  - quais métricas foram obtidas
  - onde está o modelo treinado

Critério de pronto:

- uma única execução no `MLflow` reconstrui a linhagem completa entre dado processado, treino, avaliação e modelo

Dependencias:

- BP2-04

---

## BP2-06 Persistir pipeline treinado para reuso

Status: concluído.

Objetivo: preparar o artefato de modelo para inferência futura sem duplicar pré-processamento fora do objeto serializado.

Arquivos a criar ou atualizar:

- `src/models/train.py`
- `src/models/io.py`
- `models/`
- `tests/unit/test_model_io.py`

Tarefas:

- serializar o pipeline completo de treino + pré-processamento
- definir convencao de nome para artefatos locais de modelo
- persistir metadados minimos junto ao artefato:
  - timestamp da execução
  - `run_id` do `MLflow`
  - algoritmo
  - hash do dataset
- preferir persistencia compativel com `mlflow.sklearn` ou `joblib`, mantendo simplicidade operacional
- validar carregamento do artefato serializado

Saídas esperadas:

- modelo local reutilizavel pela etapa 5
- contrato de carga e leitura do artefato

Validacao:

- um artefato salvo pode ser carregado e usado para predicao no mesmo schema de entrada

Comandos de verificação:

```bash
uv run pytest tests/unit/test_model_io.py
```

Dependencias:

- BP2-05

---

## BP2-07 Cobrir o pipeline com testes

Status: concluído.

Objetivo: impedir regressao funcional conforme o código de ML deixar de ser scaffold.

Arquivos a criar ou atualizar:

- `tests/unit/test_dataset.py`
- `tests/unit/test_build_features.py`
- `tests/unit/test_train.py`
- `tests/unit/test_evaluate.py`
- `tests/unit/test_model_io.py`
- opcionalmente `tests/integration/test_training_pipeline.py`

Tarefas:

- adicionar testes de split reproduzivel
- adicionar testes de montagem do pipeline de pré-processamento
- adicionar testes de treino com dataset reduzido ou fixture controlada
- adicionar testes de avaliação com as métricas esperadas
- adicionar teste de round-trip de serializacao do modelo
- opcionalmente adicionar teste de integração executando ingestão + treino + avaliação

Critério de pronto:

- regressao no pipeline quebra testes automaticamente

Comandos de verificação:

```bash
uv run pytest
uv run ruff check .
```

Dependencias:

- BP2-06

---

## BP2-08 Atualizar documentação operacional

Status: concluído.

Objetivo: permitir que qualquer integrante reproduza o treino oficial da etapa 2 sem conhecimento tacito.

Arquivos a criar ou atualizar:

- `README.md`
- `docs/architecture.md`
- `docs/mlflow-tracking.md`
- opcionalmente `docs/training-runbook.md`

Tarefas:

- documentar o fluxo oficial da etapa 2
- explicar como executar:
  - ingestão
  - treino
  - avaliação
  - tracking no `MLflow`
- documentar parâmetros principais do treino
- documentar a localizacao dos artefatos gerados
- registrar limitações conhecidas da etapa 2
- explicitar o que continua pendente para etapas 3 a 6

Critério de pronto:

- um colaborador novo consegue reproduzir a execução oficial da etapa 2 apenas com a documentação

Dependencias:

- BP2-07

---

## BP2-09 Preparar o terreno para CI da etapa 4

Status: concluído.

Objetivo: deixar o pipeline de treino pronto para automacao posterior sem acoplamento manual.

Arquivos a criar ou atualizar:

- `.github/workflows/ci.yml`
- opcionalmente novo workflow específico para treino controlado

Tarefas:

- revisar se o CI atual continua valido com os novos testes
- garantir que o treino local tenha um comando único e não interativo
- preparar, sem obrigar execução completa em todo PR, um caminho claro para:
  - validar o pipeline
  - executar treino controlado
  - publicar artefatos em etapas seguintes
- manter o custo do CI sob controle, separando checks rápidos de execucoes mais pesadas

Critério de pronto:

- o código da etapa 2 pode ser automatizado sem refatoracao estrutural adicional relevante

Dependencias:

- BP2-08

---

## Entregaveis Consolidados da Etapa 2

- contrato oficial do dataset de treino e split reproduzivel
- pipeline de pré-processamento versionado
- baseline oficial treinavel por código
- modulo de avaliação com métricas reais
- tracking ampliado no `MLflow`
- artefato serializado do pipeline treinado
- testes cobrindo o fluxo principal
- documentação operacional da etapa 2

## Definicao de Pronto da Etapa 2

A etapa 2 será considerada concluída quando:

1. `uv run python -m src.models.train` executar de ponta a ponta sem placeholders
2. o pipeline usar exclusivamente o dataset processado oficial da etapa 1
3. o pré-processamento estiver encapsulado e serializado junto com o modelo
4. as métricas de avaliação forem reais, reproduziveis e registradas no `MLflow`
5. um run do `MLflow` permitir reconstruir linhagem de dado, parâmetros, artefatos e modelo
6. os artefatos locais do treino puderem ser carregados novamente para inferência futura
7. a suite de testes cobrir dataset, pré-processamento, treino, avaliação e serializacao
8. a documentação permitir reproducao por outro integrante sem suporte verbal

## Comando-Alvo da Etapa 2

Ao final da execução deste backlog, o projeto deve suportar um comando único equivalente a:

```bash
uv run python -m src.models.train
```

Resultado esperado desse comando:

- carrega o dataset processado oficial
- monta o split reproduzivel
- aplica pré-processamento
- treina o baseline oficial
- avalia em conjunto de teste
- persiste artefatos locais
- registra a execução no `MLflow`
- devolve um resumo estruturado com métricas e localizacao dos artefatos

## Dependencias Herdadas para Etapas Seguintes

A etapa 2 deve terminar deixando prontas as bases para:

- etapa 3: fairness, auditoria de vies e relatórios de risco
- etapa 4: automacao de treino e validação em GitHub Actions
- etapa 5: carga do pipeline serializado em serviço `Flask`
- etapa 6: comparacao entre runs e retreinamento orientado por degradação
