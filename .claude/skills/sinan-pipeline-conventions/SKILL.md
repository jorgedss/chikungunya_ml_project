---
name: sinan-pipeline-conventions
description: Convenções para os scripts de pipeline de dados deste projeto (chikungunya_ml_project), em utils/. Use ao criar ou editar download_data.py, clean_data.py, treat_data.py, split_data.py ou main.py.
---

# Convenções do pipeline de dados (chikungunya_ml_project)

## Estrutura do pipeline

Quatro etapas sequenciais, cada uma em um módulo próprio dentro de `utils/`, orquestradas
por `main.py` na raiz do projeto:

1. `download_data.py` - baixa os dados brutos do SINAN (2020-2025) via `pysus`, em chunks,
   um parquet por ano em `data/raw/`.
2. `clean_data.py` - filtra a coorte de interesse (internados com desfecho conhecido) e
   consolida todos os anos num único parquet em `data/raw/`.
3. `treat_data.py` - feature engineering e construção do alvo, gera o dataset tratado único
   em `data/processed/`, preservando a coluna `year`.
4. `split_data.py` - split temporal (treino/teste/validação externa por ano), grava
   `X`/`y` por partição em `data/features/`.

Cada módulo expõe uma função `main()` e é executável isoladamente
(`python -m utils.clean_data`) ou via `python main.py`.

## Features vs. metadados

A lista de preditores (`FEATURES`) é definida em `clean_data.py` a partir do dicionário de
dados do SINAN para chikungunya e da revisão bibliográfica do projeto, nunca copiada de
outro estudo sem verificação.

Colunas de data e o campo de classificação final do caso (`CLASSI_FIN` ou equivalente) são
metadados: viajam junto com a coorte para auditoria e diagnóstico, mas nunca entram em `X`.
A exclusão explícita acontece em `split_data.py`, que importa a lista de metadados do módulo
que a define.

## Estilo de código

- Docstring de módulo no topo do arquivo explicando o que o script faz, sem comentários
  inline no corpo do código.
- Nomes de variáveis em português ou inglês consistentes com o restante do módulo que está
  sendo editado, nunca misturados na mesma função.
- Toda função que processa um ano ou uma etapa imprime um resumo (contagens, distribuição do
  desfecho) para permitir auditoria manual da execução.
