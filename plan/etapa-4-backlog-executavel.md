# Etapa 4 - Backlog Executavel

## Objetivo

Automatizar validação, avaliação, gates de promocao e registro local do modelo via CI/CD, partindo do estado real entregue pela etapa 3.

## Status Atual

Status geral da etapa 4: `concluído`

Implementado nesta etapa:

- workflow de CI com jobs separados para qualidade, validação e release
- gates automatizados de promocao com checks bloqueantes e alertas informativos
- decisão de promocao registrada em artefatos locais e no `MLflow`
- registro local do último candidato e do último modelo aprovado
- documentação formal da política de gates e promocao

## Blocos Executados

### BP4-00 Formalizar política de gates

Status: `concluído`

Entregas:

- `docs/decisions/release-gate-policy.md`
- `src/evaluation/gates.py`

### BP4-01 Automatizar validação em CI

Status: `concluído`

Entregas:

- `.github/workflows/ci.yml`

Checks automatizados:

- `ruff`
- `pytest`
- ingestão oficial
- avaliação oficial

### BP4-02 Implementar decisão de promocao

Status: `concluído`

Entregas:

- `src/models/release.py`
- `src/models/registry.py`
- `artifacts/training/<run_label>/release_gate_report.json`
- `artifacts/training/<run_label>/release_decision.txt`

### BP4-03 Registrar candidato e aprovado

Status: `concluído`

Entregas:

- `models/registry/latest_candidate.json`
- `models/registry/latest_approved_model.json`

### BP4-04 Ampliar tracking do release

Status: `concluído`

Entregas:

- tags `release_status` e `promotion_eligible` no `MLflow`
- métricas `release_blocking_failures` e `release_active_alerts`
- artefatos de release no mesmo run

### BP4-05 Atualizar documentação operacional

Status: `concluído`

Entregas:

- `README.md`
- `docs/architecture.md`
- `docs/mlflow-tracking.md`
- `docs/model-risk.md`
- `docs/model-card.md`
- `docs/decisions/README.md`

## Resultado Esperado Materializado

A etapa 4 deixa o projeto com um fluxo automatizado em que:

1. qualidade basica roda em CI
2. avaliação oficial roda em CI
3. o release executa treino, aplica gates e registra a decisão
4. o último candidato é o último aprovado ficam rastreaveis no registro local
5. o run no `MLflow` passa a refletir o resultado operacional da promocao
