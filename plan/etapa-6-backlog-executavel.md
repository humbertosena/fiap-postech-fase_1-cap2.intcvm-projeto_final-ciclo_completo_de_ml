# Etapa 6 - Backlog Executavel

## Objetivo

Fechar o ciclo de MLOps após a implantação, adicionando monitoramento operacional, verificacoes de qualidade e drift em inferência e gatilhos rastreaveis de retreinamento para sustentar o valor de negócio do serviço ao longo do tempo.

## Status Atual

Status geral da etapa 6: `implementado`

A etapa 6 parte de um estado em que treino, release e serving já estao ativos, mas o projeto ainda não observa o comportamento do modelo depois da implantação.

Lacunas abertas neste momento:

- a API não registra telemetria operacional persistida de forma estruturada
- não existe trilha local de eventos de inferência para análise posterior
- não existe rotina oficial de data quality em produção
- não existe rotina oficial de drift de entrada, predicao ou score
- não existe política codificada de gatilhos para retreinamento
- a meta de latência existe apenas como smoke local e ainda não se conecta a uma rotina de monitoramento continuo

## Ponto de Partida Real

Ao início da etapa 6, o projeto já possui:

- pipeline oficial de treino, avaliação, fairness, risco e release
- gates automatizados de promocao com registro local do último aprovado
- API `Flask` ativa com `GET /health` e `POST /predict`
- carregamento do modelo promovido a partir de `models/registry/latest_approved_model.json`
- artefatos por run em `artifacts/training/`
- validação de integração da API e smoke test de latência local
- conteinerização inicial e job de packaging no CI

O que ainda falta para fechar o ciclo de operação:

- observar disponibilidade, volume, erro e latência da API de forma persistente
- registrar amostras de inferência sem depender apenas de logs ad hoc
- avaliar degradação da qualidade dos dados de entrada
- detectar drift comparando referência de treino e distribuição de inferência
- definir quando um desvio observado deve abrir retreinamento ou investigacao humana
- consolidar relatarios operacionais reproduziveis para auditoria

## Fora de Escopo da Etapa 6

Não incluir nesta etapa:

- observabilidade em plataforma externa gerenciada como Azure Monitor, Datadog ou Prometheus remoto
- retreinamento totalmente automatico em produção sem aprovação humana
- aprendizado online ou atualização continua do modelo em tempo real
- coleta de labels de produção em tempo real com feedback clinico integrado
- fairness por região sem novo atributo aprovado na base
- mecanismos avancados de autenticação, rate limiting ou multi-tenant

## Decisões Herdadas que a Etapa 6 Deve Respeitar

1. o serviço continua usando apenas o último modelo aprovado
2. o threshold operacional aprovado permanece `0.35`
3. o baseline oficial atual continua sendo `LogisticRegression`
4. fairness oficial permanece offline, por `sex` e `age_group`, com limitacao explicita para região
5. a meta de latência atual `p95 < 100 ms` segue valida apenas como referência local até reavaliacao em ambiente implantado
6. qualquer gatilho de retreinamento nesta etapa deve abrir processo rastreavel, não trocar o modelo automaticamente sem governança

## Estratégia Recomendada

A etapa 6 deve evitar duas armadilhas comuns:

- adicionar observabilidade sofisticada demais sem dado suficiente para sustentar a operação
- chamar qualquer oscilacao estatística de drift critico e disparar retreinamento indevido

A ordem pragmatica da etapa 6 e:

1. definir contrato mínimo de observabilidade da API
2. persistir eventos de inferência e métricas operacionais localmente
3. medir data quality e schema compliance em dados de inferência
4. medir drift offline contra a referência de treino
5. codificar regras claras de alerta é de abertura de retreinamento
6. gerar relatórios reproduziveis e atualizar a documentação operacional

## Blocos Executaveis

### BP6-00 Fechar o contrato de monitoramento operacional

Status: `concluído`

Objetivo: formalizar quais sinais o sistema precisa produzir após a implantação para permitir operação e auditoria minima.

Arquivos a criar ou atualizar:

- novo `docs/monitoring.md`
- `README.md`
- `docs/architecture.md`
- opcionalmente novo `docs/decisions/monitoring-policy.md`

Tarefas:

- definir os eventos operacionais minimos da API:
  - `request_received`
  - `prediction_completed`
  - `prediction_failed`
  - `model_unavailable`
- definir o payload mínimo de observabilidade para cada evento:
  - `timestamp_utc`
  - `event_type`
  - `request_id`
  - `model_run_id`
  - `model_run_label`
  - `latency_ms`
  - `status_code`
- definir quais campos de entrada podem ser persistidos e quais devem ser omitidos para evitar exposicao indevida
- separar claramente métricas operacionais de análise offline de drift
- definir onde os artefatos de monitoramento ficarao salvos no projeto

Critério de pronto:

- existe um contrato escrito e rastreavel do que a API deve emitir e do que os jobs de monitoramento devem consumir

### BP6-01 Instrumentar telemetria estruturada da API

Status: `concluído`

Objetivo: fazer a API produzir eventos estruturados suficientes para medir disponibilidade, latência, volume e falhas.

Arquivos a criar ou atualizar:

- `src/serving/app.py`
- novo `src/serving/monitoring.py`
- opcionalmente novo `src/serving/logging.py`
- `tests/integration/test_serving_api.py`

Tarefas:

- gerar `request_id` por chamada
- medir latência fim a fim por request
- emitir logs estruturados em JSON ou linha delimitada com schema estavel
- registrar eventos de sucesso e falha sem quebrar o caminho critico de inferência
- garantir que `/health` e `/predict` exponham sinais operacionais coerentes
- evitar acoplamento com serviço externo nesta etapa

Critério de pronto:

- cada chamada principal da API gera telemetria minima reproduzivel e utilizavel em análise posterior

### BP6-02 Persistir eventos de inferência e snapshots de monitoramento

Status: `concluído`

Objetivo: criar uma trilha local auditavel para analisar comportamento do modelo após o serving.

Arquivos a criar ou atualizar:

- novo `src/monitoring/store.py`
- novo `src/monitoring/contracts.py`
- `src/serving/app.py`
- `.gitignore`
- `README.md`

Tarefas:

- definir um diretorio canonico para eventos de monitoramento, por exemplo `artifacts/monitoring/`
- persistir eventos de inferência em formato simples e reproduzivel, como `jsonl` ou `csv`
- armazenar campos minimos para auditoria:
  - `timestamp_utc`
  - `request_id`
  - `model_run_id`
  - `prediction`
  - `prediction_score`
  - `decision_threshold`
  - resumo sanitizado das features monitoraveis
- separar eventos brutos de agregados periodicos
- garantir que o manifesto aprovado continue sendo a fonte oficial do identificador do modelo servido

Critério de pronto:

- inferencias reais deixam rastro local suficiente para consolidação e análise sem depender de memoria operacional do time

### BP6-03 Monitorar data quality e conformidade do schema em inferência

Status: `concluído`

Objetivo: detectar rapidamente problemas de payload e degradação basica dos dados de entrada antes mesmo de falar em drift.

Arquivos a criar ou atualizar:

- novo `src/monitoring/data_quality.py`
- `src/serving/schemas.py`
- novo `tests/unit/test_data_quality.py`
- opcionalmente `docs/model-risk.md`

Tarefas:

- calcular completude por campo nas amostras de inferência persistidas
- medir taxa de valores ausentes, invalidos e fora de faixa por variavel numerica relevante
- medir frequência de categorias desconhecidas em campos categóricos
- detectar violacao de schema ou aumento anormal de erro de validação no endpoint
- produzir um relatorio local periodico de qualidade de dados

Critério de pronto:

- o projeto passa a diferenciar claramente erro operacional de payload, problema de qualidade e drift estatistico

### BP6-04 Implementar monitoramento offline de drift

Status: `concluído`

Objetivo: comparar dados de inferência com a referência do treino aprovado para detectar mudança relevante de distribuição.

Arquivos a criar ou atualizar:

- novo `src/monitoring/drift.py`
- novo `src/monitoring/reference.py`
- `src/models/train.py`
- `src/models/release.py`
- novo `tests/unit/test_drift.py`

Tarefas:

- definir o snapshot de referência a partir do dataset usado no modelo aprovado
- persistir estatisticas de referência no momento do treino ou release:
  - distribuicoes por feature
  - taxas de missing
  - distribuição de score prevista
- implementar checks simples e defensaveis para drift, por exemplo:
  - PSI para variaveis numericas discretizadas
  - diferenca absoluta de proporcao para categoricas
  - comparacao da distribuição de scores ou da taxa prevista positiva
- gerar relatorio batch de drift sobre eventos de inferência acumulados
- evitar técnicas mais complexas que o volume atual de dados não sustenta

Critério de pronto:

- existe uma rotina reproduzivel que compara referência e inferência e produz um relatorio objetivo de drift

### BP6-05 Definir gatilhos de alerta e retreinamento

Status: `concluído`

Objetivo: transformar sinais operacionais e estatisticos em regra de negócio rastreavel.

Arquivos a criar ou atualizar:

- novo `src/monitoring/triggers.py`
- novo `docs/decisions/retraining-trigger-policy.md`
- `docs/model-risk.md`
- opcionalmente `README.md`

Tarefas:

- definir diferenca entre:
  - alerta operacional
  - alerta de qualidade de dados
  - alerta de drift
  - gatilho para abrir retreinamento
- codificar limiares iniciais simples, por exemplo:
  - aumento sustentado da taxa de erro HTTP
  - violacao recorrente do schema
  - drift acima de limite acordado em features-chave
  - mudança relevante na taxa de positivos previstos
- exigir janela minima de observação para evitar falso alarme em volume baixo
- fazer o gatilho abrir estado ou relatorio de investigacao, não promover modelo novo automaticamente

Critério de pronto:

- o projeto tem uma política executável que indica quando investigar e quando abrir retreinamento

### BP6-06 Gerar relatórios consolidados de monitoramento

Status: `concluído`

Objetivo: fechar a etapa com artefatos auditaveis, e não apenas funcoes isoladas.

Arquivos a criar ou atualizar:

- novo `src/monitoring/reporting.py`
- novo `src/monitoring/run_monitoring.py`
- `docs/monitoring.md`
- novo `tests/integration/test_monitoring_pipeline.py`

Tarefas:

- agregar eventos de inferência em relatorio operacional contendo:
  - volume por período
  - taxa de erro
  - latência agregada
  - distribuição de predicoes
- agregar relatorio de data quality
- agregar relatorio de drift
- agregar avaliação final dos gatilhos de retreinamento
- salvar artefatos em caminho versionado por execução, por exemplo `artifacts/monitoring/<run_label>/`

Critério de pronto:

- uma execução única do monitoramento gera um pacote completo de evidencias operacionais é de drift

### BP6-07 Integrar monitoramento ao ciclo do projeto

Status: `concluído`

Objetivo: conectar a observabilidade recem-criada ao fluxo já existente de release e operação.

Arquivos a criar ou atualizar:

- `.github/workflows/ci.yml`
- opcionalmente novo workflow dedicado de monitoramento offline
- `src/tracking.py`
- `README.md`

Tarefas:

- adicionar validação de lint e testes da nova camada de monitoramento
- definir comando oficial para executar consolidação de monitoramento
- opcionalmente registrar artefatos de monitoramento no `MLflow` quando a rotina batch rodar
- documentar como a equipe operacional deve rodar o monitoramento localmente ou via agendamento futuro
- manter a etapa sem dependencia de scheduler externo obrigatorio

Critério de pronto:

- o monitoramento vira parte oficial do projeto e não um script solto fora do fluxo principal

### BP6-08 Atualizar documentação de risco, arquitetura e operação

Status: `concluído`

Objetivo: refletir no desenho do projeto como o ciclo passa a ser fechado após a implantação.

Arquivos a criar ou atualizar:

- `README.md`
- `docs/architecture.md`
- `docs/model-risk.md`
- `docs/model-card.md`
- `docs/deployment.md`
- `docs/decisions/README.md`

Tarefas:

- registrar a trilha operacional da API é os relatórios batch de monitoramento
- documentar limitações da análise de drift sem labels de produção
- documentar que fairness continua offline e não é recalculada no caminho online
- explicitar que gatilho de retreinamento abre processo governado e não atualização automatica do modelo em produção
- atualizar mapa do ciclo completo para incluir serving, observabilidade e nova rodada de treino

Critério de pronto:

- a documentação do repositório passa a representar o ciclo completo real do projeto após a implantação

## Critérios de Aceite da Etapa 6

A etapa 6 podera ser considerada concluída quando os itens abaixo estiverem atendidos:

1. a API emitir telemetria estruturada minima por request
2. eventos de inferência ficarem persistidos em trilha local auditavel
3. existir relatorio de data quality para inferência
4. existir relatorio de drift comparando referência de treino e eventos de inferência
5. existir política codificada de alertas e gatilhos de retreinamento
6. existir comando oficial para consolidar monitoramento e gerar artefatos reproduziveis
7. a documentação refletir o ciclo fechado entre serving, monitoramento e nova investigacao de modelo

## Sequencia de Execucao Recomendada

1. `BP6-00` e `BP6-01`
2. `BP6-02`
3. `BP6-03`
4. `BP6-04`
5. `BP6-05`
6. `BP6-06`
7. `BP6-07` e `BP6-08`

## Riscos e Cuidados da Etapa 6

- monitoramento sem sanitizacao pode vazar dado sensivel em artefatos locais
- drift estatistico sem labels não prova sozinho degradação clinica do modelo
- volume baixo de inferência pode gerar falso positivo de alerta
- thresholds de retreinamento muito agressivos podem criar ruido operacional desnecessario
- fairness por região continua indisponivel enquanto o atributo não existir de forma governada no dataset

## Resultado Esperado ao Final da Etapa 6

Ao concluir a etapa 6, o projeto deve operar com um ciclo minimamente fechado:

- modelo aprovado servido pela API
- telemetria operacional persistida
- análise periodica de qualidade e drift
- relatorio consolidado de monitoramento
- regra objetiva para abrir investigacao e retreinamento
- documentação coerente com um fluxo de MLOps que não termina no deploy
