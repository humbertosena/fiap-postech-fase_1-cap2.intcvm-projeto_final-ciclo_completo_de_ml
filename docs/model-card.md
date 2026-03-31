# Model Card

## Identificação

- modelo atual: `LogisticRegression`
- tarefa: classificação binaria para triagem cardíaca
- estado atual: modelo aprovado com serving ativo e monitoramento local na etapa 6

## Dados de entrada

- dataset processado oficial derivado de `data/raw/heart+disease/cleve.mod`
- features numericas e categoricas com pré-processamento via `ColumnTransformer`
- colunas de diagnóstico bruto fora do treino para evitar leakage
- payload HTTP alinhado ao contrato de features do pipeline promovido
- aliases amigaveis normalizados para o vocabulario canônico do treino

## Politica de decisão

- metrica principal: `recall`
- threshold operacional aprovado: `0.35`
- critério de threshold: maximizar `recall` com `precision >= 0.70`

## Auditoria de fairness vigente

- grupos auditados: `age_group` e `sex`
- métricas auditadas: `precision`, `recall`, `f1`, `false_negative_rate`, `false_positive_rate`
- alerta inicial: gap absoluto maior que `0.15`
- dimensao indisponivel: região

## Politica de release vigente

- bloqueio de promocao quando `recall < 0.80`
- bloqueio de promocao quando `precision < 0.70`
- bloqueio de promocao quando o threshold aprovado `0.35` não for respeitado
- alertas de fairness não bloqueiam promocao nesta etapa

## Politica de serving vigente

- a API serve apenas o último modelo aprovado no registro local
- a resposta inclui probabilidade positiva, threshold e identificadores do modelo
- a API retorna degradação controlada quando não houver modelo aprovado disponivel
- a API emite telemetria estruturada e persiste eventos locais de inferência

## Politica de monitoramento vigente

- monitoramento local por eventos de API e inferência
- relatórios batch de qualidade de dados e drift
- recomendação de retreinamento quando os gatilhos configurados forem atingidos
- sem troca automatica de modelo em produção

## Restrições de uso

- não usar como diagnóstico autonomo
- requer interpretacao humana e contexto clinico
- fairness regional permanece não demonstrada
- implantação atual e local e não substitui ambiente produtivo monitorado
