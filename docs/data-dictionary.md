# Dicionario de Dados do Dataset Cleveland MOD

## Origem

- arquivo bruto: `data/raw/heart+disease/cleve.mod`
- documento complementar: `data/raw/heart+disease/heart-disease.names`

## Colunas Processadas

| Coluna | Tipo | Descricao |
| --- | --- | --- |
| `age` | numérico | idade em anos |
| `sex` | categórico | sexo biologico informado no dataset (`male`, `fem`) |
| `chest_pain_type` | categórico | tipo de dor toracica |
| `resting_blood_pressure` | numérico | pressao arterial em repouso |
| `cholesterol` | numérico | colesterol serico |
| `fasting_blood_sugar_gt_120` | categórico | glicemia em jejum acima de 120 |
| `rest_ecg` | categórico | resultado do ECG em repouso |
| `max_heart_rate` | numérico | frequência cardíaca maxima |
| `exercise_induced_angina` | categórico | angina induzida por exercício |
| `oldpeak` | numérico | depressao ST |
| `slope` | categórico | inclinacao do segmento ST |
| `num_vessels` | numérico | numero de vasos coloridos |
| `thal` | categórico | tipo de thal |
| `diagnosis_label` | categórico | `buff` ou `sick` |
| `diagnosis_code` | categórico | código clinico resumido (`H`, `S1`...`S4`) |
| `target` | binario | 0 para `buff`, 1 para `sick` |

## Regras de Conversao

- comentarios iniciados por `%` são ignorados
- `?` vira valor faltante
- valores numéricos são convertidos para `float`
- target binario:
  - `buff` -> `0`
  - `sick` -> `1`
