# Arquitetura do Projeto

> **AVISO IMPORTANTE**
>
> Este repositório é um **exercício de aula** desenvolvido para fins exclusivamente acadêmicos no contexto do curso de pós-graduação da FIAP. Os dados utilizados são **públicos**. O processo de treinamento descrito é de **mera experimentação** e não passou por nenhuma validação de especialista da area cardíaca. Qualquer referência à empresa, produto ou serviço (como "FIAP HealthCare Plus") é uma **simulacao fictícia** criada para fins didáticos. **Não utilize nenhuma informação deste repositório para fins clínicos, médicos ou de diagnóstico.**

## Objetivo

Estabelecer uma base corporativa reproduzivel para ingestão, treino, avaliação, rastreabilidade, auditoria, gates de promocao, inferência, monitoramento e evolucao do modelo de triagem cardíaca.

## Decisões Estruturais

- código executável concentrado em `src/`
- dados brutos preservados em `data/raw/`
- dados processados gerados em `data/processed/`
- relatórios de ingestão gerados em `artifacts/`
- artefatos de treino, fairness, risco e release gerados em `artifacts/training/`
- artefatos de monitoramento gerados em `artifacts/monitoring/`
- artefatos de modelo locais em `models/`
- registro local de candidato e aprovado em `models/registry/`
- inferência operacional servida em `Flask` a partir do modelo aprovado
- notebooks fora do fluxo principal de execução

## Módulos Principais

- `src/config.py`: configuração centralizada e resolucao de paths
- `src/data/ingest_mod.py`: parser e exportação do dataset processado
- `src/data/dataset.py`: contrato oficial de treino, split reproduzivel e grupos de auditoria
- `src/features/preprocessing.py`: pré-processamento versionado
- `src/models/train.py`: treino, threshold tuning, fairness, risco, referência de monitoramento e persistencia
- `src/evaluation/gates.py`: checks bloqueantes e alertas de promocao
- `src/models/release.py`: pipeline de release com gates e decisão operacional
- `src/models/registry.py`: registro local do último candidato e do último aprovado
- `src/serving/model_store.py`: carregamento do último modelo aprovado
- `src/serving/schemas.py`: contrato HTTP da API
- `src/serving/monitoring.py`: telemetria estruturada do serving
- `src/serving/app.py`: API `Flask` com `/health` e `/predict`
- `src/monitoring/store.py`: persistencia local dos eventos de monitoramento
- `src/monitoring/data_quality.py`: checks batch de qualidade de dados
- `src/monitoring/drift.py`: checks batch de drift
- `src/monitoring/triggers.py`: política executável de alertas e retreinamento
- `src/monitoring/run_monitoring.py`: consolidação oficial do monitoramento
- `src/tracking.py`: tracking com `MLflow`

## Decisões de Modelagem Vigentes

- baseline oficial: `LogisticRegression`
- metrica principal de comparacao: `recall`
- threshold operacional aprovado: `0.35`
- política de decisão: maximizar `recall` com `precision >= 0.70`
- política de fairness: auditar `age_group` e `sex`, com alerta para gaps acima de `0.15`
- política de release: bloquear promocao quando `recall < 0.80`, `precision < 0.70` ou o threshold aprovado não for respeitado
- a API deve servir apenas o último modelo aprovado no registro local
- a política de monitoramento deve abrir investigacao e recomendação de retreinamento, não atualizar o modelo automaticamente

## Diretrizes de Governança

- fairness e risco são artefatos formais do run, não comentarios externos
- grupos pequenos devem ser tratados como evidencia de baixa confiança
- ausência de região precisa aparecer explicitamente como limitacao do dado
- a inferência online não recalcula fairness
- a promocao local do modelo depende do resultado dos gates automatizados
- drift e data quality em produção local devem gerar artefatos auditaveis por execução

## Diretrizes Multi-OS

- usar `pathlib` para todos os caminhos
- evitar scripts dependentes de shell específico dentro do código Python
- documentar exemplos tanto para PowerShell quanto para shell POSIX

## Restrições Herdadas do PDF

- a arquitetura final precisa suportar fairness, CI/CD, deployment e monitoramento
- a falta do atributo de região no `cleve.mod` deve ser tratada como dependencia de negócio e dado
