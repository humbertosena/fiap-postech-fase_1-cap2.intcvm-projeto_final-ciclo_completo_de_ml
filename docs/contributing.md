# Convencoes de Contribuicao

## Principios

- todo código executável deve viver em `src/`
- notebooks são apenas para demonstracao
- paths devem usar `pathlib`
- nenhuma leitura do dataset bruto deve ser feita ad hoc fora do parser oficial

## Qualidade Minima

- rodar `uv run ruff check .`
- rodar `uv run pytest`
- manter compatibilidade com Python 3.13

## Estratégia de Mudança

- preferir mudanças pequenas e validaveis
- documentar decisões arquiteturais em `docs/decisions/`
- atualizar a documentação quando o contrato de dados mudar
