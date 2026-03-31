# Entrega Final

> **AVISO IMPORTANTE**
>
> Este repositório é um **exercício de aula** desenvolvido para fins exclusivamente acadêmicos no contexto do curso de pós-graduação da FIAP. Os dados utilizados são **públicos**. O processo de treinamento descrito é de **mera experimentação** e não passou por nenhuma validação de especialista da area cardíaca. Qualquer referência à empresa, produto ou serviço (como "FIAP HealthCare Plus") é uma **simulacao fictícia** criada para fins didáticos. **Não utilize nenhuma informação deste repositório para fins clínicos, médicos ou de diagnóstico.**

## O que o projeto entrega

O repositório entrega um ciclo completo de MLOps local e reproduzivel para triagem cardíaca, cobrindo:

- ingestão controlada do dataset legado
- treinamento supervisionado com pré-processamento versionado
- auditoria de fairness e risco
- gates automatizados de promocao
- release rastreavel com registro local do modelo aprovado
- inferência real via API `Flask`
- conteinerização inicial
- monitoramento local com drift e gatilhos de retreinamento

## Registro de assistencia ao desenvolvimento

O desenvolvimento deste projeto foi assistido pela OpenAI Codex, utilizada como apoio técnico na implementacao, organizacao documental e consolidação dos artefatos finais.

## Baseline e contrato atual

- baseline oficial: `LogisticRegression`
- threshold operacional aprovado: `0.35`
- metrica principal: `recall`
- grupos auditados em fairness: `age_group` e `sex`
- modelo servido: sempre o último aprovado em `models/registry/latest_approved_model.json`

## Artefatos principais gerados pelo projeto

### Treino e release

- `artifacts/training/<run_label>/metrics.json`
- `artifacts/training/<run_label>/classification_report.json`
- `artifacts/training/<run_label>/confusion_matrix.csv`
- `artifacts/training/<run_label>/fairness_report.json`
- `artifacts/training/<run_label>/risk_summary.json`
- `artifacts/training/<run_label>/model_card.json`
- `artifacts/training/<run_label>/monitoring_reference.json`
- `models/<run_label>/training_pipeline.joblib`
- `models/registry/latest_approved_model.json`

### Monitoramento

- `artifacts/monitoring/events/api_events.jsonl`
- `artifacts/monitoring/events/inference_events.jsonl`
- `artifacts/monitoring/<run_label>/monitoring_report.json`
- `artifacts/monitoring/<run_label>/data_quality_report.json`
- `artifacts/monitoring/<run_label>/drift_report.json`
- `artifacts/monitoring/<run_label>/trigger_report.json`

## Comandos finais de demonstracao

### 1. Validar qualidade e testes

```bash
uv run ruff check .
uv run pytest -q
```

### 2. Gerar release do modelo aprovado

```bash
uv run python -m src.models.release
```

### 3. Subir a API

```bash
uv run python -m src.serving.app
```

### 4. Rodar monitoramento batch

```bash
uv run python -m src.monitoring.run_monitoring
```

## Riscos residuais assumidos na entrega

- fairness por região não é demonstravel com o dataset atual
- drift sem labels de produção não mede sozinho degradação clinica
- monitoramento e retreinamento continuam locais e governados manualmente
- a API ainda não possui autenticação e endurecimento operacional de produção
- a comparacao entre multiplos modelos candidatos ainda não foi expandida além do baseline atual

## Documentos mais importantes da entrega

- `README.md`
- `docs/README.md`
- `plan/projeto-final-summary-executivo.md`
- `docs/architecture.md`
- `docs/model-risk.md`
- `docs/api.md`
- `docs/monitoring.md`
