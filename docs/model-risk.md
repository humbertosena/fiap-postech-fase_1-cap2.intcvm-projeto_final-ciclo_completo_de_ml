# Model Risk

> **AVISO IMPORTANTE**
>
> Este repositório é um **exercício de aula** desenvolvido para fins exclusivamente acadêmicos no contexto do curso de pós-graduação da FIAP. Os dados utilizados são **públicos**. O processo de treinamento descrito é de **mera experimentação** e não passou por nenhuma validação de especialista da area cardíaca. Qualquer referência à empresa, produto ou serviço (como "FIAP HealthCare Plus") é uma **simulacao fictícia** criada para fins didáticos. **Não utilize nenhuma informação deste repositório para fins clínicos, médicos ou de diagnóstico.**

## Escopo

Este documento resume os riscos tecnicos e operacionais do baseline atual após a implementacao da etapa 6.

## Uso pretendido

- apoio técnico a triagem cardíaca experimental
- comparacao de desempenho, fairness, release, serving e monitoramento

## Uso não pretendido

- diagnóstico clinico autonomo
- substituicao de avaliação medica humana
- decisão automatica de tratamento

## Principais riscos

- `false_negative_rate` ainda existe e pode ocultar pacientes positivos
- threshold `0.35` privilegia `recall`, aumentando falsos positivos e carga downstream
- fairness por idade e sexo e apenas observacional
- fairness por região não pode ser afirmada
- base pequena é de origem principal única aumenta variancia por subgrupo
- o registro do modelo ainda e local e pode ficar desatualizado se o release não for executado
- monitoramento e retreinamento continuam locais ao workspace, sem orquestracao externa
- drift sem labels de produção não prova sozinho degradação clinica

## Limitações do dado

- ausência de atributo real de região
- uma única base principal no fluxo oficial
- possibilidade de instabilidade estatística em grupos pequenos
- ausência de labels online para confirmar degradação em produção

## Limitações do modelo e serviço

- baseline simples com `LogisticRegression`
- threshold calibrado em hold-out único
- ausência de validação cruzada e comparacao sistematica entre candidatos
- API sem autenticação ou controle de carga
- telemetria e batch de monitoramento ainda não usam plataforma externa

## Controles atuais

- rastreabilidade de dataset, parser, pré-processamento, threshold, fairness e release no `MLflow`
- relatorio de fairness por run
- model card inicial
- gates automatizados de promocao em CI/CD
- registro local do último candidato e do último aprovado
- testes automatizados para pipeline, auditoria, gates, API e monitoramento
- smoke test de latência local
- eventos locais de API e inferência em `jsonl`
- relatórios batch de data quality, drift e gatilhos

## Proximos controles desejados

- validação em container com medicao de latência fora do processo de teste
- mitigacao de fairness quando gaps relevantes persistirem
- avaliação com novos dados e estratégia para região
- labels de produção ou estratégia robusta de feedback para avaliar degradação real
- integração do monitoramento com scheduler e plataforma externa
