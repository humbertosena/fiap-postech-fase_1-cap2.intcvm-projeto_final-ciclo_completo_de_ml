# Etapa 5 - Backlog Executavel

## Objetivo

Publicar o modelo aprovado pela etapa 4 como serviço conteinerizado com API REST em `Flask`, usando o registro local atual como fonte oficial do artefato promovido e adicionando validacoes de integração suficientes para sustentar a implantação.

## Status Atual

Status geral da etapa 5: `implementado com ressalva`

Implementado nesta etapa:

- API `Flask` ativa com `/health` e `/predict`
- carregamento do último modelo aprovado via manifesto local
- contrato HTTP formalizado e validado por testes
- testes de integração e smoke test de latência
- meta inicial de latência documentada
- `Dockerfile`, `.dockerignore` e job de packaging no CI
- documentação operacional da implantação

Ressalva atual:

- o `docker build` local foi preparado e enviado ao CI, mas a validação manual completa do build no ambiente atual depende do daemon Docker fora do sandbox

## Ponto de Partida Real

Ao início da etapa 5, o projeto já possui:

- pipeline oficial de treino, avaliação, fairness, risco e release
- gates automatizados de promocao
- registro local do último candidato e do último aprovado
- artefatos completos por run em `artifacts/training/`
- pipeline serializado em `models/<run_label>/training_pipeline.joblib`
- scaffold de API em `src/serving/app.py`, ainda retornando `501`
- `Flask` já presente nas dependencias
- CI/CD cobrindo qualidade, avaliação e release

O que ainda falta para cumprir o objetivo de implantação:

- carregar o último modelo aprovado no runtime da API
- definir e validar contrato de entrada e saída da predicao
- transformar o endpoint `/predict` em inferência real
- adicionar testes de integração da API
- definir meta inicial de latência e medi-la
- conteinerizar a aplicação com Docker

## Fora de Escopo da Etapa 5

Não incluir nesta etapa:

- monitoramento em produção e drift
- retreinamento automatico
- fairness por região com novo dado
- registry compartilhado multiambiente
- orquestracao em nuvem gerenciada

## Decisões Herdadas que a Etapa 5 Deve Respeitar

1. baseline oficial atual: `LogisticRegression`
2. threshold operacional aprovado: `0.35`
3. o serviço deve consumir o último modelo aprovado, não o último candidato arbitrario
4. fairness continua evidencial e não deve ser recalculada em tempo de inferência
5. a API de inferência futura do projeto deve ser `Flask`
6. Docker só entra a partir desta etapa

## Estratégia Recomendada

A implementacao deve evoluir o scaffold atual de `src/serving/` sem criar um segundo caminho paralelo de inferência.

A ordem pragmatica da etapa 5 e:

1. ativar o carregamento do modelo aprovado
2. definir schemas HTTP e validação de payload
3. implementar predicao real no `/predict`
4. cobrir com testes de integração
5. medir latência local e formalizar um alvo inicial
6. empacotar tudo em Docker

## Blocos Executaveis

### BP5-00 Fechar o contrato operacional da API

Status: `concluído`

Objetivo: transformar o scaffold de `Flask` em uma interface com contrato técnico claro antes de conectar o modelo.

Arquivos a criar ou atualizar:

- `src/serving/schemas.py`
- `src/serving/app.py`
- `README.md`
- opcionalmente `docs/api.md`

Tarefas:

- definir payload oficial esperado pelo endpoint `/predict`
- mapear nomes de campos para o contrato do pipeline de features
- definir resposta minima da API contendo:
  - classe prevista
  - score ou probabilidade
  - threshold usado
  - versão ou identificador do modelo aprovado
- definir comportamento para payload invalido
- garantir que o contrato use tipos coerentes com o dataset processado e com o pré-processamento atual

Critério de pronto:

- a API passa a ter request/response contract explicito e documentado

### BP5-01 Carregar o último modelo aprovado

Status: `concluído`

Objetivo: usar o registro local da etapa 4 como única fonte oficial do artefato servido.

Arquivos a criar ou atualizar:

- novo `src/serving/model_store.py`
- `src/models/io.py`
- `src/models/registry.py`
- `src/serving/app.py`

Tarefas:

- implementar função para localizar `models/registry/latest_approved_model.json`
- validar existencia do manifesto e do `training_pipeline.joblib` referenciado
- carregar o pipeline aprovado com `joblib`
- expor metadados minimos do modelo carregado:
  - `run_id`
  - `run_label`
  - `decision_threshold`
  - `model_name`
- definir comportamento quando não houver modelo aprovado disponivel

Critério de pronto:

- a API consegue iniciar consumindo o último modelo oficialmente aprovado

### BP5-02 Implementar inferência real no endpoint `/predict`

Status: `concluído`

Objetivo: substituir o retorno `501` por predicao real, reusando o pipeline serializado da etapa 4.

Arquivos a criar ou atualizar:

- `src/serving/app.py`
- `src/serving/schemas.py`
- opcionalmente novo `src/serving/predict.py`

Tarefas:

- converter o payload HTTP para `DataFrame` compatível com o pipeline treinado
- chamar `predict_proba` ou `predict` no pipeline carregado
- retornar probabilidade da classe positiva quando disponivel
- aplicar o threshold aprovado somente como contrato de resposta, sem divergencia do modelo promovido
- garantir resposta `200` para payload valido e mensagens claras para erro de validação
- manter o endpoint `/health` com informações uteis para operação minima

Critério de pronto:

- o endpoint `/predict` passa a responder com inferência real sobre o modelo aprovado

### BP5-03 Cobrir API com testes de integração

Status: `concluído`

Objetivo: garantir que o serviço não dependa apenas de teste unitario do pipeline.

Arquivos a criar ou atualizar:

- novo `tests/integration/test_serving_api.py`
- novo `tests/integration/conftest.py`, se necessário
- opcionalmente `tests/unit/test_serving_schemas.py`

Tarefas:

- testar `/health`
- testar `/predict` com payload valido
- testar `/predict` com payload invalido
- testar comportamento sem modelo aprovado
- validar que a resposta inclui metadados operacionais esperados
- evitar depender de rede externa ou servicos compartilhados

Critério de pronto:

- o fluxo HTTP principal fica coberto por testes automatizados reproduziveis

### BP5-04 Fechar meta inicial de latência

Status: `concluído`

Objetivo: transformar a pendencia de latência em alvo técnico mensuravel antes da conteinerização final.

Arquivos a criar ou atualizar:

- `docs/decisions/latency-target.md`
- novo `tests/integration/test_latency_smoke.py` ou script equivalente
- `README.md`

Tarefas:

- definir um alvo inicial simples de latência, por exemplo percentil e ambiente local de referência
- medir latência da API ou da predicao no processo local
- registrar metodologia minima da medicao
- evitar metas irreais ou sem contexto de hardware

Critério de pronto:

- existe uma meta inicial de latência documentada é uma verificação minima reproduzivel

### BP5-05 Conteinerizar a aplicação

Status: `parcial`

Objetivo: empacotar API e runtime do modelo em imagem Docker reproduzivel.

Arquivos a criar ou atualizar:

- novo `Dockerfile`
- opcionalmente `.dockerignore`
- `README.md`
- opcionalmente `compose.yaml` para execução local

Tarefas:

- definir imagem base compatível com Python `3.13`
- instalar dependencias com estratégia simples e reproduzivel
- copiar somente arquivos necessários para runtime
- expor porta do serviço `Flask`
- garantir inicializacao do app apontando para o modelo aprovado
- documentar build e run local da imagem

Critério de pronto:

- a API sobe localmente em container e responde aos endpoints principais

### BP5-06 Integrar container e API ao CI

Status: `concluído`

Objetivo: impedir regressao do serviço e da empacotacao depois da implantação inicial.

Arquivos a criar ou atualizar:

- `.github/workflows/ci.yml`
- opcionalmente novo workflow dedicado a imagem

Tarefas:

- adicionar job para validar build do `Dockerfile`
- executar testes de integração da API no pipeline
- manter custo de execução controlado
- publicar artefatos ou logs relevantes em caso de falha

Critério de pronto:

- o CI passa a validar não só treino e release, mas também a camada de serviço

### BP5-07 Atualizar documentação operacional da implantação

Status: `concluído`

Objetivo: documentar o fluxo oficial de subida do serviço é os limites conhecidos da implantação.

Arquivos a criar ou atualizar:

- `README.md`
- novo `docs/deployment.md`
- `docs/architecture.md`
- `docs/model-card.md`
- `docs/model-risk.md`

Tarefas:

- documentar como iniciar a API localmente
- documentar como rodar a imagem Docker
- registrar dependencia do modelo aprovado e do manifesto local
- deixar claro o que ainda não é monitorado nesta etapa
- registrar riscos operacionais da implantação inicial

Critério de pronto:

- um integrante novo consegue subir e validar a API sem depender de explicação verbal

## Dependencias Entre Blocos

- `BP5-00` antes de `BP5-02`
- `BP5-01` antes de `BP5-02`
- `BP5-02` antes de `BP5-03`
- `BP5-04` pode andar em paralelo depois de `BP5-02`
- `BP5-05` depois de `BP5-02`
- `BP5-06` depois de `BP5-03` e `BP5-05`
- `BP5-07` ao final, consolidando o fluxo real implementado

## Critérios de Aceite da Etapa 5

A etapa 5 pode ser considerada concluída quando:

1. a API `Flask` responder `200` em `/health`
2. o endpoint `/predict` executar inferência real com o modelo aprovado
3. o serviço consumir o manifesto `latest_approved_model.json` como fonte oficial
4. existirem testes de integração cobrindo sucesso e falha principal da API
5. a imagem Docker buildar e subir localmente
6. a documentação de execução local e container estiver atualizada
7. existir uma meta inicial de latência documentada

## Riscos e Cuidados da Etapa 5

- não acoplar a API ao último candidato; o contrato e com o último aprovado
- não duplicar pré-processamento manual fora do pipeline serializado
- não embutir fairness online no endpoint de predicao
- não usar o Docker para mascarar falhas de contrato que deveriam ser resolvidas no código Python
- manter o custo de CI controlado para não degradar o fluxo criado na etapa 4

## Resultado Esperado ao Final da Etapa 5

Ao concluir a etapa 5, o projeto deve sair de um pipeline com release automatizado para um serviço real de inferência localmente implantavel, conteinerizado e coerente com o registro do modelo aprovado.
