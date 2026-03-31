# Etapa 3 - Backlog Executavel

Este backlog converte o objetivo da etapa 3 em tarefas técnicas executaveis, considerando o plano mestre do projeto é o estado real entregue pelas etapas 1 e 2.

## Objetivo da Etapa 3

Adicionar governança, auditoria e fairness sobre o pipeline de treinamento já funcional da etapa 2, de modo que o projeto passe a produzir não apenas um modelo reproduzivel, mas também evidencias técnicas sobre comportamento, vies, limitações, critérios de aceitacao e riscos de uso.

Ao final da etapa 3, o projeto deve ser capaz de:

- avaliar o modelo por segmentos sensiveis disponiveis no dado
- registrar diferencas de desempenho entre grupos
- emitir relatórios de fairness e risco por execução
- documentar limitações técnicas é de negócio do baseline atual
- preparar gates objetivos para a etapa 4, ainda que sem automatiza-los por completo

## Base Real Herdada das Etapas 1 e 2

A etapa 3 parte das seguintes entregas já implementadas:

- parser oficial e dataset processado reproduzivel
- contrato explicito do dataset de treino em `src/data/dataset.py`
- split reproduzivel com `random_state=42`
- pré-processamento versionado com `ColumnTransformer`
- baseline oficial com `LogisticRegression`
- threshold tuning orientado por `recall`
- threshold operacional aprovado em `0.35`
- artefatos locais de avaliação e modelo
- tracking ampliado no `MLflow`
- suite de testes cobrindo treino, avaliação e serializacao
- documentação da decisão de baseline e threshold

## Escopo Deste Backlog

Este backlog cobre apenas a etapa 3:

- definicao dos atributos sensiveis observaveis no dado atual
- avaliação segmentada de métricas por grupo
- relatorio de fairness operacional viavel com o dataset atual
- registro explicito da limitacao de fairness por região
- relatorio de risco e limitações do modelo
- critérios de aceitacao tecnicos para fairness e governança
- ampliacao do tracking para artefatos de auditoria
- testes dos calculos de fairness e relatórios
- documentação técnica da etapa 3

Ficam fora deste backlog:

- correção automatica de vies por reamostragem, reweighting ou pos-processamento
- enriquecimento definitivo do dado com região real
- gates operacionais em CI/CD da etapa 4
- deployment da API da etapa 5
- monitoramento em produção da etapa 6

## Premissas de Execucao

As tarefas abaixo assumem:

1. o baseline validado da etapa 2 continua sendo `LogisticRegression`
2. a metrica principal do projeto continua sendo `recall`
3. o threshold operacional aprovado continua sendo `0.35`
4. o dataset atual não contem atributo literal de região
5. qualquer análise de fairness por região dependera de estratégia de proxy ou ampliacao da base
6. compatibilidade com Windows, Linux e macOS deve ser preservada

## Riscos e Pendencias Que Impactam a Etapa 3

Estes itens precisam ser acomodados de forma explicita no desenho da etapa 3:

1. o requisito da disciplina menciona idade e região, mas apenas idade está diretamente operacionalizavel no dado atual
2. o dataset e pequeno, entao métricas por subgrupo podem oscilar e ter alta variancia
3. fairness sem contexto clinico pode gerar conclusoes superficiais ou enganosas
4. a etapa 3 precisa distinguir claramente entre evidencia observada e critério normativo aprovado
5. qualquer proxy de região precisa ser documentado como aproximacao e não como atributo real

## Ordem de Execucao Recomendada

1. BP3-00 Fechar definicoes operacionais de fairness e governança
2. BP3-01 Formalizar atributos sensiveis e grupos de análise
3. BP3-02 Implementar avaliação segmentada por grupo
4. BP3-03 Implementar relatorio de fairness por execução
5. BP3-04 Implementar relatorio de risco e limitações do modelo
6. BP3-05 Ampliar tracking no `MLflow` para auditoria
7. BP3-06 Cobrir fairness e governança com testes
8. BP3-07 Atualizar documentação técnica e ADRs
9. BP3-08 Preparar gates para a etapa 4

## Status Atual

- `BP3-00` a `BP3-08`: `concluído`
- política de fairness vigente: `age_group` e `sex`
- limite de alerta de fairness: `0.15`
- threshold operacional refletido na auditoria: `0.35`
- fairness por região: bloqueado por ausência do atributo no dataset atual
- validação executada:
  - `uv run ruff check .`
  - `uv run pytest -q`
  - `uv run python -m src.models.train`
  - `uv run python -m src.evaluation.evaluate`

---

## BP3-00 Fechar definicoes operacionais de fairness e governança

Status: `concluído`

Objetivo: remover ambiguidades sobre o que será medido, com quais grupos e com qual grau de compromisso técnico nesta etapa.

Arquivos a criar ou atualizar:

- `docs/decisions/fairness-region.md`
- `docs/decisions/fairness-policy.md`
- `docs/architecture.md`
- opcionalmente `docs/decisions/model-risk-policy.md`

Tarefas:

- confirmar que fairness operacional da etapa 3 será implementada com base apenas em atributos observaveis no dado atual e limitações explicitas para região
- definir os grupos iniciais de auditoria recomendados:
  - idade em faixas
  - sexo, se mantido no conjunto de atributos disponiveis para análise
- definir quais métricas por grupo serao calculadas:
  - `recall`
  - `precision`
  - `f1`
  - `false_negative_rate`
  - `false_positive_rate`
- definir o que será tratado como alerta de fairness nesta etapa:
  - recomendação pragmatica: diferenca absoluta entre grupos acima de um limite acordado
- registrar explicitamente que região continua pendente e depende de dados adicionais ou proxy aprovado

Critério de pronto:

- existe uma regra documentada para dizer o que será medido, em quais grupos e com qual interpretacao

Dependencias:

- nenhuma

---

## BP3-01 Formalizar atributos sensiveis e grupos de análise

Status: `concluído`

Objetivo: transformar grupos de auditoria em contrato técnico reutilizavel por avaliação, relatórios e testes.

Arquivos a criar ou atualizar:

- `src/evaluation/fairness.py`
- `src/data/schema.py`
- `src/data/dataset.py`
- `tests/unit/test_fairness.py`

Tarefas:

- definir faixas etarias operacionais para análise de fairness
- formalizar funcoes para derivar grupos a partir do dataset processado
- separar atributos usados para modelagem de atributos usados apenas para auditoria
- garantir que a análise de fairness consuma o mesmo conjunto avaliado pelo modelo da etapa 2
- definir uma representacao padrão de subgrupo para os relatórios

Saídas esperadas:

- API reutilizavel para gerar segmentos de auditoria
- contrato consistente entre dataset, avaliação e relatorio

Validacao:

- o mesmo registro cai sempre no mesmo grupo dado o mesmo contrato
- mudanças nas faixas ou nomes de grupos quebram testes de contrato

Comandos de verificação:

```bash
uv run pytest tests/unit/test_fairness.py
```

Dependencias:

- BP3-00

---

## BP3-02 Implementar avaliação segmentada por grupo

Status: `concluído`

Objetivo: produzir métricas por subgrupo usando o modelo e threshold aprovados na etapa 2.

Arquivos a criar ou atualizar:

- `src/evaluation/fairness.py`
- `src/evaluation/metrics.py`
- `src/models/train.py`
- `tests/unit/test_fairness.py`

Tarefas:

- calcular métricas por grupo sensivel no conjunto de teste
- incluir pelo menos:
  - tamanho do grupo
  - `precision`
  - `recall`
  - `f1`
  - `false_negative_rate`
  - `false_positive_rate`
- calcular gaps entre grupos para as métricas principais
- manter a avaliação alinhada ao threshold operacional `0.35`
- garantir que a análise não altere o fluxo principal de treino, apenas o complemente

Saídas esperadas:

- função de avaliação segmentada por grupo
- estrutura de dados pronta para relatorio e tracking

Validacao:

- a avaliação segmentada roda sobre o baseline atual sem quebrar o treino
- os grupos retornam métricas consistentes com a matriz de confusao global

Comandos de verificação:

```bash
uv run pytest tests/unit/test_fairness.py
uv run python -m src.models.train
```

Dependencias:

- BP3-01

---

## BP3-03 Implementar relatorio de fairness por execução

Status: `concluído`

Objetivo: materializar a auditoria de vies em artefatos persistidos por run.

Arquivos a criar ou atualizar:

- `src/evaluation/reports.py`
- `src/evaluation/fairness.py`
- `src/models/train.py`
- `artifacts/` como destino de saídas locais
- opcionalmente `docs/fairness-report-template.md`

Tarefas:

- gerar um artefato `fairness_report.json` por execução
- incluir no relatorio:
  - grupos analisados
  - métricas por grupo
  - gaps entre grupos
  - threshold usado
  - observações sobre confiança limitada por tamanho amostral
- registrar de forma explicita quando fairness por região não puder ser calculada
- gerar resumo executivo legivel para documentação posterior

Saídas esperadas:

- relatorio de fairness versionado por run
- artefato pronto para uso no `MLflow`

Validacao:

- o relatorio e gerado em execução local
- os dados do relatorio batem com as métricas segmentadas calculadas em memoria

Comandos de verificação:

```bash
uv run python -m src.models.train
```

Dependencias:

- BP3-02

---

## BP3-04 Implementar relatorio de risco e limitações do modelo

Status: `concluído`

Objetivo: registrar tecnicamente o que o modelo faz, o que não faz e em quais condições seu uso e arriscado.

Arquivos a criar ou atualizar:

- `docs/model-risk.md`
- `docs/model-card.md`
- `src/models/train.py`
- opcionalmente `src/evaluation/risk.py`

Tarefas:

- documentar risco de uso do baseline em contexto clinico
- registrar limitações do dado:
  - ausência de região real
  - tamanho da base
  - fonte única principal
  - possivel instabilidade por subgrupo
- registrar limitações do modelo:
  - baseline simples
  - threshold calibrado por hold-out único
  - falta de validação cruzada e comparacao sistematica com outros candidatos
- opcionalmente gerar um `model_card.json` ou `risk_summary.json` por run

Saídas esperadas:

- documento técnico de risco
- model card inicial coerente com o estado real do projeto

Validacao:

- a documentação consegue explicar claramente onde o modelo e defensavel e onde ainda não é

Dependencias:

- BP3-03

---

## BP3-05 Ampliar tracking no `MLflow` para auditoria

Status: `concluído`

Objetivo: conectar fairness e governança ao mesmo run de treinamento da etapa 2.

Arquivos a criar ou atualizar:

- `src/tracking.py`
- `src/models/train.py`
- `docs/mlflow-tracking.md`
- opcionalmente `tests/unit/test_tracking.py`

Tarefas:

- registrar artefatos de fairness no mesmo run de treino
- adicionar parâmetros de auditoria:
  - grupos analisados
  - política de fairness ativa
  - threshold usado
- adicionar métricas agregadas de fairness:
  - gap máximo de `recall`
  - gap máximo de `precision`
  - gap máximo de `false_negative_rate`
- garantir que a auditoria de vies fique rastreavel junto ao modelo treinado

Critério de pronto:

- um run do `MLflow` passa a responder não apenas como o modelo performou, mas também como essa performance se distribuiu entre grupos

Dependencias:

- BP3-04

---

## BP3-06 Cobrir fairness e governança com testes

Status: `concluído`

Objetivo: impedir regressao na camada de auditoria conforme o pipeline evoluir.

Arquivos a criar ou atualizar:

- `tests/unit/test_fairness.py`
- `tests/unit/test_train.py`
- `tests/unit/test_evaluate.py`
- opcionalmente `tests/integration/test_governance_pipeline.py`

Tarefas:

- testar derivacao de grupos de auditoria
- testar métricas por subgrupo em fixture controlada
- testar calculo de gaps
- testar geração de `fairness_report.json`
- opcionalmente testar treino + avaliação + fairness no mesmo fluxo de integração

Critério de pronto:

- mudanças na logica de fairness ou relatorio quebram testes automaticamente

Comandos de verificação:

```bash
uv run pytest
uv run ruff check .
```

Dependencias:

- BP3-05

---

## BP3-07 Atualizar documentação técnica e ADRs

Status: `concluído`

Objetivo: garantir que governança e limitações do modelo não fiquem como conhecimento tacito.

Arquivos a criar ou atualizar:

- `README.md`
- `docs/architecture.md`
- `docs/mlflow-tracking.md`
- `docs/decisions/fairness-region.md`
- `docs/decisions/fairness-policy.md`
- `docs/model-risk.md`
- `docs/model-card.md`

Tarefas:

- documentar a política de fairness vigente da etapa 3
- documentar o que pode é o que não pode ser afirmado sobre vies com o dado atual
- explicar a dependencia ainda aberta de região
- registrar o fluxo oficial de auditoria da etapa 3
- descrever como interpretar gaps entre grupos

Critério de pronto:

- um colaborador novo entende como o projeto mede fairness hoje e quais lacunas ainda existem

Dependencias:

- BP3-06

---

## BP3-08 Preparar gates para a etapa 4

Status: `concluído`

Objetivo: deixar fairness e governança prontas para automacao posterior.

Arquivos a criar ou atualizar:

- `.github/workflows/ci.yml`
- opcionalmente novo workflow de auditoria
- `docs/decisions/fairness-policy.md`

Tarefas:

- definir quais checks de fairness poderao virar gates automatizados
- propor limites iniciais para alertas de fairness
- separar claramente:
  - gate bloqueante futuro
  - alerta informativo imediato
- manter o custo de execução sob controle para futura integração em CI

Critério de pronto:

- fairness e governança ficam tecnicamente prontas para serem promovidas a gates na etapa 4

Dependencias:

- BP3-07

---

## Entregaveis Consolidados da Etapa 3

- contrato de atributos sensiveis e grupos de auditoria
- avaliação segmentada por grupo
- relatorio de fairness por execução
- relatorio de risco e limitações do modelo
- tracking ampliado no `MLflow` para governança
- testes da camada de fairness
- documentação técnica da etapa 3

## Definicao de Pronto da Etapa 3

A etapa 3 será considerada concluída quando:

1. o pipeline da etapa 2 continuar treinando sem regressao funcional
2. o projeto calcular métricas por grupo sobre o conjunto de teste
3. um relatorio de fairness for gerado e persistido por run
4. a limitacao de fairness por região estiver documentada sem ambiguidade
5. o threshold operacional `0.35` estiver refletido nas avaliações de fairness
6. os artefatos de auditoria estiverem rastreados no `MLflow`
7. a documentação técnica explicar claramente riscos, limitações e interpretacao dos resultados

## Comando-Alvo da Etapa 3

Ao final da execução deste backlog, o projeto deve suportar um comando único equivalente a:

```bash
uv run python -m src.models.train
```

Resultado esperado desse comando:

- treina o baseline atual
- avalia o modelo globalmente
- executa auditoria segmentada por grupo
- gera artefatos de fairness e risco
- registra tudo no `MLflow`
- devolve um resumo estruturado com métricas globais é de auditoria

## Dependencias Herdadas para Etapas Seguintes

A etapa 3 deve terminar deixando prontas as bases para:

- etapa 4: gates automatizados de desempenho e fairness em CI/CD
- etapa 5: exposicao do modelo com contrato de inferência e limitações documentadas
- etapa 6: monitoramento por segmento, drift e retreinamento orientado por degradação
