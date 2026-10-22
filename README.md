# chikungunya_ml_project

Pipeline de aprendizado de máquina supervisionado para **predição de óbito em casos
internados por chikungunya**, a partir de dados do SINAN (Sistema de Informação de
Agravos de Notificação), cobrindo o período de 2020 a 2025.

O objetivo é a **avaliação comparativa da capacidade preditiva** de cinco algoritmos que
cobrem o espectro interpretabilidade-complexidade: Regressão Logística, Árvore de Decisão
(CART), Random Forest, XGBoost e LightGBM.

## Estrutura do projeto

```
chikungunya_ml_project/
├── main.py                     # Orquestra o pipeline de dados completo
├── utils/                      # Pipeline de dados (download → tratamento → split)
│   ├── download_data.py        # Baixa os dados brutos do SINAN (2020-2025) em chunks
│   ├── clean_data.py           # Filtra internados com desfecho conhecido (todos os anos)
│   ├── treat_data.py           # Feature engineering + construção do alvo (dataset único)
│   ├── split_data.py           # Split temporal: treino 2020-2023 / teste 2024 / validação 2025
│   └── preprocessing.py        # Funções compartilhadas pelos notebooks de modelagem
└── notebooks/
    ├── 01_diagnostics/          # Qualidade de datas e padrão de preenchimento das fichas
    ├── 02_models/                # Treino e avaliação dos 5 algoritmos num único fluxo comparável
    ├── 03_evaluation/            # Comparação, bootstrap (IC 95%), calibração, validação 2025
    ├── 04_interpretation/        # Importância das variáveis (5 modelos)
    └── 05_fairness/              # Análise de equidade estratificada
```

## Pipeline de dados

Todos os anos de **2020 a 2025** são consolidados num **único dataset tratado**. A coluna
`year` é preservada e usada como parâmetro de split temporal (treino 2020-2023, teste 2024,
validação externa 2025).

Execute o pipeline completo a partir da raiz do projeto:

```bash
python main.py
```

Etapas (também executáveis individualmente):

1. `utils/download_data.py` → `data/raw/chik_{ano}.parquet`
2. `utils/clean_data.py` → `data/raw/chik_hospitalized.parquet`
3. `utils/treat_data.py` → `data/processed/chik_treated.parquet`
4. `utils/split_data.py` → `data/features/baseline/{X,y}_{train,test,val2025}.parquet`

> Os diretórios `data/` e `output/` não são versionados; são regenerados pela execução
> do pipeline e dos notebooks.

## Notebooks

- **01_diagnostics/** - qualidade e consistência das datas, diagnóstico de ausência de
  dados por campo e por desfecho, e padrão de preenchimento por bloco da ficha.
- **02_models/** - um único notebook treina e avalia os 5 algoritmos (Regressão Logística,
  Árvore de Decisão, Random Forest, XGBoost, LightGBM) lado a lado: pré-processamento,
  validação temporal (*expanding window*), otimização de hiperparâmetros (GridSearchCV),
  treino final e avaliação.
- **03_evaluation/** - um notebook por tipo de análise, cobrindo os 5 modelos: comparação e
  bootstrap para intervalos de confiança 95%, calibração (Brier Score/BSS), e validação
  externa no ano de 2025.
- **04_interpretation/** - importância das variáveis dos cinco modelos: MDI/ganho para os
  modelos de árvore e coeficientes/razões de chances para a Regressão Logística.
- **05_fairness/** - análise de equidade estratificada por sexo, raça/cor e faixa etária,
  com intervalo de confiança bootstrap (IC 95%) sobre o ΔAUPRC/ΔROC-AUC de cada subgrupo,
  para distinguir disparidade real de ruído amostral.

## Principais resultados

Coorte final: 14.390 internados com chikungunya confirmada e desfecho conhecido
(2020-2025), 515 óbitos (prevalência global de 3,58%, variando de 1,11% a 5,23% por ano).

**Desempenho no teste 2024** (28 preditores, após excluir variáveis com risco de
vazamento de informação ou de inflação por alta cardinalidade):

| Algoritmo | AUPRC | ROC-AUC | BSS (pós-calibração) |
|---|---|---|---|
| Regressão Logística | 0,207 | 0,811 | 0,073 |
| XGBoost | 0,196 | 0,766 | 0,061 |
| Random Forest | 0,187 | 0,805 | 0,070 |
| LightGBM | 0,168 | 0,746 | 0,049 |
| Árvore de Decisão | 0,120 | 0,715 | 0,043 |

Nenhum dos cinco algoritmos degrada de forma acentuada na validação externa de 2025.

**Importância de variáveis:** idade é o preditor dominante e unânime entre os modelos,
seguida por escolaridade e pela presença de vômito.
Comorbidades crônicas não aparecem entre os preditores mais importantes em nenhum modelo.

**Equidade:** depois de contabilizar incerteza amostral via bootstrap, não há evidência
estatística robusta de capacidade discriminativa (ROC-AUC) diferente por sexo, raça/cor ou
faixa etária.

## Ambiente

Projeto gerenciado com [uv](https://github.com/astral-sh/uv):

```bash
uv sync
```

Requer Python ≥ 3.12.
