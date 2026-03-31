# Guia de Execucao: Projeto Final MLOps (FIAP HealthCare Plus)

Este documento organiza a implementacao do projeto de MLOps para deteccao de doencas cardiacas, saindo de um experimento local para uma solução reproduzivel, auditavel e pronta para evolucao em Azure com GitHub e MLflow.

## Premissas Obrigatorias Fechadas

As decisões abaixo foram fixadas para este projeto e já orientam a implementacao da etapa 1:

1. Estrutura com padrão corporativo desde o início.
2. Rastreabilidade com `MLflow` somente.
3. Dataset bruto principal em `data-raw/heart+disease/cleve.mod`.
4. Compatibilidade com Windows, Linux e macOS.
5. Notebooks permitidos apenas para demonstracao.
6. Servico futuro de inferência em `Flask`.
7. Padrao de execução em Python `3.13`.
8. Docker apenas na etapa 5.

## Aderencia Obrigatoria ao PDF da Disciplina

O documento `plan/FIAP-MLEng-Fase-1-cap2-projeto-final.pdf` introduz exigencias que devem refletir no planejamento desde a etapa 1:

1. O projeto deve abandonar o notebook monolitico e adotar código modular em `src/`.
2. A estrutura base obrigatoria inclui `src/`, `data/`, `models/`, `tests/` e `.github/workflows/`.
3. O projeto precisa garantir rastreabilidade de código, dados e modelos.
4. A arquitetura deve ser preparada para governança, fairness, CI/CD, deployment e monitoramento, mesmo que essas entregas completas ocorram em etapas posteriores.
5. O pipeline final deve atender requisitos de negócio da FIAP HealthCare Plus: baixa latência, auditabilidade, retreinamento orientado por degradação e controle de vies.

## Visão Geral das Etapas

### Etapa 1: Estruturacao e Versionamento
Construir a base técnica do projeto: estrutura do repositório, padrão de código, configuração do ambiente, contrato de ingestão do dataset, rastreabilidade com MLflow e bootstrap do pipeline de qualidade.

### Etapa 2: Pipeline de Treinamento e Rastreabilidade
Transformar o treinamento em um fluxo automatizado, com pré-processamento consistente, rastreabilidade de métricas, hiperparametros e artefatos.

### Etapa 3: Governança e Auditoria de Vies
Adicionar fairness, verificacoes de risco e documentação técnica do comportamento e limitações do modelo.

### Etapa 4: Automacao via CI/CD
Executar validacoes, treinamento, avaliação e registro de modelo de forma automatizada via GitHub Actions.

### Etapa 5: Implantação
Publicar o modelo como serviço conteinerizado com API REST e validacoes de integração.

### Etapa 6: Monitoramento e Fechamento do Ciclo
Monitorar operação, drift e gatilhos de retreinamento para manter valor de negócio ao longo do tempo.

---

## Plano Detalhado da Etapa 1

### Objetivo da Etapa 1
Criar uma fundacao corporativa que permita ao time desenvolver, treinar, testar e versionar o projeto de forma consistente desde o início. Ao final da etapa, qualquer integrante deve conseguir clonar o repositório, preparar o ambiente em Windows, Linux ou macOS, entender a organizacao dos arquivos, carregar o dataset bruto `.MOD` com contrato conhecido e executar o fluxo mínimo de qualidade sem ambiguidade.

### Resultado Esperado
Ao concluir a etapa 1, o projeto deve ter:

1. Estrutura de diretorios definida e documentada.
2. Ambiente Python padronizado e reproduzivel.
3. Contrato de ingestão do dataset `cleve.mod` definido e documentado.
4. Convencoes de desenvolvimento registradas.
5. Estratégia de rastreabilidade com MLflow escolhida e justificada.
6. Pipeline inicial de qualidade preparado para evoluir nas proximas etapas.
7. Esqueleto do projeto pronto para receber treino, inferência, testes e automacao.

### Escopo da Etapa 1

Inclui:

- organizacao do repositório
- configuração de dependencias
- formalizacao da ingestão do arquivo bruto `.MOD`
- configuração basica de testes e lint
- definicao da estratégia de rastreabilidade de dados e experimentos com `MLflow`
- documentação inicial
- bootstrap do CI

Não inclui:

- treinamento completo do modelo
- deploy da API em `Flask`
- monitoramento em produção
- gates de fairness operacionais
- conteinerização com Docker

---

## Backlog de Implementacao da Etapa 1

### Etapa 1: Definir padrões arquiteturais do repositório

Objetivo: estabelecer a espinha dorsal do projeto antes de escrever código de negócio.

Tarefas:

1. Definir o nome técnico do projeto é o pacote Python principal.
2. Escolher o padrão de organizacao base:
   - preferencia recomendada: inspiracao em Cookiecutter Data Science
3. Definir a estrutura inicial de pastas:
   - `.github/workflows/`
   - `data/raw/`
   - `data/processed/`
   - `docs/`
   - `models/`
   - `notebooks/`
   - `src/`
   - `src/data/`
   - `src/features/`
   - `src/models/`
   - `src/evaluation/`
   - `src/serving/`
   - `tests/unit/`
   - `tests/integration/`
   - `artifacts/` ou pasta equivalente para saídas locais ignoradas do Git
4. Definir quais diretorios entram em versionamento e quais entram no `.gitignore`.
5. Garantir que notebooks fiquem fora do caminho principal de execução e sejam usados apenas para demonstracao.

Entregaveis:

- árvore inicial do projeto
- `.gitignore`
- `README.md` com mapa da estrutura
- decisão documentada de que o código executável vive em `src/`

Critério de aceite:

- um novo membro do time entende onde cada tipo de arquivo deve ficar sem depender de explicação verbal

### Etapa 2: Padronizar ambiente e dependencias

Objetivo: garantir reproducibilidade local e futura integração com CI/CD.

Tarefas:

1. Escolher o gerenciador de ambiente e dependencias com suporte consistente para Windows, Linux e macOS:
   - opções validas: `venv` + `pip-tools`, `Poetry`, `uv`
   - recomendação pragmatica: `uv`, por simplicidade operacional e boa portabilidade cross-platform
2. Criar arquivo de dependencias principal.
3. Separar dependencias de runtime e desenvolvimento.
4. Fixar Python `3.13` como versão padrão.
5. Criar instruções de setup local no `README.md`.
6. Garantir que o comando de instalacao seja único e replicavel.

Dependencias iniciais sugeridas:

- `pandas`
- `numpy`
- `scikit-learn`
- `mlflow`
- `pytest`
- `ruff`
- `mypy` opcional
- `python-dotenv`
- `flask` apenas como dependencia futura do serviço, sem ativar deployment nesta etapa

Entregaveis:

- `requirements.txt` e `requirements-dev.txt`, ou equivalentes
- `.python-version` opcional
- instruções de setup local
- instruções equivalentes para PowerShell e shell POSIX

Critério de aceite:

- ambiente sobe do zero em uma máquina limpa com passos documentados

### Etapa 3: Definir configuração e gerenciamento de parâmetros

Objetivo: evitar configurações espalhadas e preparar o projeto para multiplos ambientes.

Tarefas:

1. Decidir como as configurações serao armazenadas:
   - `.env`
   - YAML
   - combinacao de ambos
2. Separar:
   - configuração de ambiente
   - caminhos de dados
   - hiperparametros default
   - limiares de avaliação
3. Criar convencao para segredos e variaveis não versionadas.
4. Documentar quais parâmetros serao obrigatorios na etapa 2.
5. Garantir que o carregamento de configuração use `pathlib` e não dependa de separador de path do sistema operacional.

Entregaveis:

- `.env.example`
- pasta ou arquivo de configuração
- convencao documentada de leitura de parâmetros

Critério de aceite:

- o projeto consegue mudar paths e parâmetros sem editar código-fonte espalhado

### Etapa 4: Formalizar ingestão do dataset bruto `.MOD`

Objetivo: transformar o arquivo legado `data-raw/heart+disease/cleve.mod` em uma entrada controlada e reproduzivel do pipeline.

Tarefas:

1. Registrar a origem oficial do dataset é o caminho canonico do arquivo bruto.
2. Criar um parser dedicado para o formato `.MOD`, tratando:
   - linhas de comentario iniciadas por `%`
   - valores faltantes representados por `?`
   - colunas simbolicas e numericas
   - rotulo alvo em formato consistente para classificação binaria
3. Extrair e consolidar o dicionário de dados a partir do cabecalho do arquivo e do arquivo `heart-disease.names`.
4. Definir o schema canonico do dataset processado:
   - nomes de colunas
   - tipos esperados
   - regras de conversao
   - política de dados faltantes
5. Gerar um artefato intermediario reproduzivel, preferencialmente `CSV` ou `Parquet`, em `data/processed/`.
6. Calcular e registrar metadados de linhagem do dado bruto:
   - hash do arquivo
   - tamanho do arquivo
   - quantidade de linhas validas
   - versão do parser
7. Garantir que todo consumo de dados nas etapas seguintes parta do parser versionado, e não de leitura ad hoc em notebook.

Entregaveis:

- modulo de ingestão em `src/data/`
- documento de schema do dataset
- primeiro dataset processado reproduzivel
- convencao de hash e metadados do arquivo bruto

Critério de aceite:

- duas execucoes independentes sobre o mesmo `cleve.mod` geram o mesmo dataset processado é os mesmos metadados de linhagem

### Etapa 5: Estruturar qualidade de código

Objetivo: impedir que a base cresca desorganizada.

Tarefas:

1. Configurar linting com `ruff`.
2. Configurar testes com `pytest`.
3. Definir estrutura minima de testes unitários.
4. Adicionar pelo menos um teste inicial para validar o bootstrap da suite.
5. Opcionalmente configurar verificação de tipos com `mypy`.
6. Definir convencao de nomenclatura de módulos, funcoes e scripts.

Entregaveis:

- arquivo de configuração do linter
- arquivo de configuração do pytest
- teste placeholder ou teste real do primeiro modulo utilitario

Critério de aceite:

- comandos de qualidade executam localmente sem erro:
  - `pytest`
  - `ruff check .`

### Etapa 6: Definir estratégia de rastreabilidade de dados e experimentos com MLflow

Objetivo: garantir rastreabilidade entre dataset, experimento e modelo usando apenas `MLflow`, conforme decisão do projeto.

Tarefas:

1. Definir o servidor de tracking do `MLflow` para desenvolvimento local e futura promocao para ambiente compartilhado.
2. Estabelecer o identificador de linhagem de dados por execução, registrando no `MLflow`:
   - hash SHA-256 do arquivo bruto `cleve.mod`
   - caminho logico do arquivo
   - versão do parser
   - schema utilizado
   - quantidade de registros validos
3. Definir como datasets processados serao armazenados e referenciados:
   - artefato do run
   - arquivo local fora do Git
   - storage externo em etapas posteriores
4. Padronizar tags e parâmetros minimos de experimento:
   - `dataset_hash`
   - `dataset_source`
   - `parser_version`
   - `target_definition`
   - `python_version`
   - `git_commit`, quando o repositório Git estiver inicializado
5. Documentar fluxo de atualização do dado é de reproducao de uma execução.

Recomendacao:

- como a decisão foi usar apenas `MLflow`, a rastreabilidade do dado precisa ser compensada por metadados obrigatorios e imutabilidade do dado bruto em `data/raw/`

Entregaveis:

- decisão arquitetural registrada
- fluxo documentado de ingestão e rastreabilidade
- convencao de tags e artefatos do `MLflow`
- estrutura de pastas de dados consistente com a decisão

Critério de aceite:

- o time consegue responder qual versão do dado gerou determinado modelo

### Etapa 7: Criar documentação base do projeto

Objetivo: reduzir dependencia de conhecimento tacito.

Tarefas:

1. Escrever `README.md` principal com:
   - objetivo do projeto
   - contexto de negócio
   - requisitos do cenário FIAP HealthCare Plus
   - restrições de fairness, latência e auditabilidade vindas do PDF
   - stack técnica
   - como subir ambiente
   - como rodar validacoes
   - estrutura de diretorios
2. Criar documento curto de convencoes de contribuicao.
3. Registrar backlog técnico das etapas seguintes.
4. Criar uma secao de decisões arquiteturais com:
   - motivo para uso exclusivo de `MLflow`
   - motivo para Python 3.13
   - estratégia multi-OS
   - política de notebooks apenas para demonstracao
5. Explicar claramente o escopo da etapa 1 é o que ainda não foi implementado.
6. Registrar desde já os requisitos de negócio que virarao gates tecnicos nas etapas seguintes:
   - prioridade de recall no contexto clinico
   - fairness por idade e, quando viavel, por região
   - necessidade de baixa latência
   - necessidade de rastreabilidade completa

Entregaveis:

- `README.md`
- `docs/contributing.md` ou equivalente
- roadmap resumido

Critério de aceite:

- um colaborador novo consegue iniciar no projeto apenas com a documentação

### Etapa 8: Preparar CI inicial no GitHub Actions

Objetivo: criar a base de automacao sem ainda treinar o modelo completo.

Tarefas:

1. Criar workflow inicial com gatilhos em `push` e `pull_request`.
2. Executar instalacao de dependencias.
3. Executar lint.
4. Executar testes unitários.
5. Validar o parser do dataset `.MOD`.
6. Opcionalmente publicar relatorio simples de status.
7. Garantir que o workflow use comandos compativeis com projeto multi-OS, ainda que a execução inicial do CI rode em Linux.

Entregaveis:

- `.github/workflows/ci.yml`

Critério de aceite:

- qualquer PR novo passa por validação automatica minima

### Etapa 9: Preparar esqueleto do domínio de ML

Objetivo: evitar que a etapa 2 comece sem contratos minimos de código.

Tarefas:

1. Criar módulos vazios ou scaffolds para:
   - ingestão
   - pré-processamento
   - treino
   - avaliação
   - inferência
   - servindo em `Flask` apenas como esqueleto de pacote, sem entregar a API completa
2. Definir interfaces minimas esperadas de cada etapa.
3. Criar um script placeholder de treino com logging básico.
4. Garantir que o esqueleto separe claramente:
   - código de treino
   - código de inferência
   - código de servindo

Entregaveis:

- esqueleto de módulos em `src/`
- script inicial `train.py` ou equivalente

Critério de aceite:

- existe um caminho claro para encaixar a etapa 2 sem refatoracao estrutural grande

---

## Ordem Recomendada de Execucao

1. Estrutura de diretorios e pacote Python
2. Ambiente e dependencias
3. Configuracao e parâmetros
4. Formalizacao da ingestão do dataset `.MOD`
5. Qualidade de código
6. Rastreabilidade com `MLflow`
7. Documentação base
8. CI inicial
9. Esqueleto dos módulos de ML

---

## Entregaveis Consolidados da Etapa 1

- estrutura inicial do repositório
- `README.md`
- `.gitignore`
- arquivos de dependencia
- parser do dataset `.MOD`
- schema do dataset e dicionário de dados
- arquivos de configuração de lint e teste
- `.env.example`
- decisão documentada sobre rastreabilidade com `MLflow`
- workflow inicial de CI
- scaffolding do código-fonte

---

## Definicao de Pronto da Etapa 1

A etapa 1 será considerada concluída quando:

1. O repositório estiver estruturado e documentado.
2. O ambiente local puder ser recriado sem improviso.
3. O arquivo `cleve.mod` puder ser convertido de forma reproduzivel para um formato consumivel pelo pipeline.
4. O fluxo de qualidade minima estiver automatizado.
5. A estratégia de rastreabilidade com `MLflow` estiver definida.
6. O projeto estiver pronto para iniciar a implementacao do pipeline de treinamento.

---

## Riscos se a Etapa 1 for Mal Executada

- retrabalho estrutural nas etapas 2 e 4
- baixa reprodutibilidade de experimentos
- acoplamento excessivo entre notebooks e código produtivo
- dificuldade de onboard de novos integrantes
- rastreabilidade incompleta entre dados, experimento e modelo
- parser inconsistente do dataset legado `.MOD`
- incompatibilidades entre Windows, Linux e macOS

---

## Pendencias Criticas Identificadas a Partir do PDF

As decisões gerais foram fechadas, mas o PDF introduz dependencias que ainda precisam ser resolvidas para manter aderencia estrita:

1. Fairness por região: o cenário da disciplina exige controle de vies por região e idade, mas o arquivo `cleve.mod` não contem atributo de região. Para cumprir esse requisito literalmente, será necessário:
   - enriquecer o dataset com um atributo confiavel de região
   - ou ampliar a base para multiplas origens do UCI e tratar a origem como proxy de região
2. KPI de gatekeeping: o PDF sugere acuracia minima baseada em baseline do MVP, mas esse baseline ainda precisa ser formalizado no projeto.
3. Politica de target: o `.MOD` representa o estado clinico em formato simbolico (`buff` e `sick` com subtipos), entao a regra oficial de binarizacao precisa ser fixada e documentada.
4. Politica de latência: o cenário exige baixa latência, entao a etapa 1 deve registrar um alvo inicial de desempenho para orientar selecao de features e desenho do serviço nas etapas 2 e 5.

---

## Recomendacao Inicial

A abordagem recomendada para comecar a etapa 1, dado o que já foi decidido, e:

- estrutura baseada em `src/` com modularizacao clara
- Python 3.13
- `uv`
- `pytest` + `ruff`
- `MLflow` para rastreabilidade de experimentos, modelos e metadados de dados
- notebooks permitidos apenas para exploracao, com consolidação rápida em código versionado
- parser versionado para o arquivo `cleve.mod`
- GitHub Actions validando lint e testes desde o primeiro commit
- desenho multi-OS desde o primeiro script

---

## Proximos Passos Apos Aprovar Este Plano

1. Fechar as pendencias criticas do PDF que ainda dependem de definicao.
2. Criar a estrutura fisica do repositório.
3. Implementar o parser é o schema do `cleve.mod`.
4. Configurar ambiente, dependencias e ferramentas de qualidade.
5. Registrar a estratégia de rastreabilidade com `MLflow`.
6. Subir o primeiro workflow de CI.

## Backlog Operacional da Etapa 1

O desdobramento técnico executável deste plano foi registrado em:

- `plan/etapa-1-backlog-executável.md`

Esse arquivo quebra a etapa 1 em blocos de implementacao, com:

- ordem de execução
- arquivos a criar
- comandos de verificação
- critérios de pronto
- bloqueios derivados do PDF

---

## Objetivos Finais do Projeto

1. Confiabilidade: modelo auditavel e resiliente a falhas.
2. Escalabilidade: deploy conteinerizado pronto para nuvem.
3. Etica: governança integrada ao código para evitar discriminacao.
4. Valor de negócio: sistema evolutivo com monitoramento e retreinamento.
