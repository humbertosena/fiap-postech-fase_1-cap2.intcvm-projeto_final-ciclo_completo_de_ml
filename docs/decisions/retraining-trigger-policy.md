# Retraining Trigger Policy

## Status

Aprovado para a etapa 6.

## Contexto

A etapa 5 encerrou a implantação inicial com API ativa, mas o projeto ainda não possuia regra objetiva para transformar sinais operacionais e estatisticos em investigacao estruturada.

## Decisão

O projeto passa a usar gatilhos batch locais e rastreaveis para recomendar retreinamento quando houver evidencia suficiente em produção local.

Regras iniciais:

- erro operacional acima do limite configurado gera alerta critico
- requests invalidos acima do limite configurado geram alerta de qualidade
- missing rate acima do limite configurado gera alerta de qualidade
- drift numérico é de score acima do limite configurado pode recomendar retreinamento
- drift categórico e mudança relevante da taxa prevista positiva podem recomendar retreinamento
- volume abaixo da janela minima impede recomendação automatica de retreinamento

## Impacto Tecnico

- retreinamento continua governado e não automatico
- a rotina oficial de monitoramento passa a produzir `trigger_report.json`
- thresholds de monitoramento ficam centralizados em configuração
- a equipe passa a ter um critério único para abrir nova investigacao de modelo

## Limitações

- sem labels de produção, drift não prova sozinho degradação clinica
- thresholds atuais são pragmáticos e devem ser recalibrados com uso real
