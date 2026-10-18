---
name: sinan-notebook-style
description: Convenção de formatação para os notebooks Jupyter deste projeto (chikungunya_ml_project). Use sempre que for criar ou editar qualquer notebook .ipynb do projeto, em qualquer fase (diagnóstico, modelagem, avaliação, interpretação, equidade).
---

# Estilo de notebooks (chikungunya_ml_project)

Convenção obrigatória para todo notebook `.ipynb` deste repositório.

## Regra 1 - célula de texto antes de cada célula de código

Toda célula de código é precedida por uma célula markdown que explica, em 1-3 frases,
o propósito da célula de código seguinte: o que ela calcula, carrega ou produz, e por quê.

A célula markdown descreve o propósito, não o código linha a linha.

Exemplo de sequência correta:

1. Célula markdown: "Carrega o dataset tratado e filtra apenas os registros do período
   de treino (2020-2023), para evitar vazamento de anos futuros na etapa de tuning."
2. Célula de código correspondente.

## Regra 2 - sem comentários no código

As células de código não devem conter comentários inline (`#`).
Nomes de variáveis e funções devem ser autoexplicativos; qualquer explicação de propósito
já está na célula markdown anterior (Regra 1).

## Regra 3 - markdown longo, uma frase por linha

Em células markdown com mais de uma frase, cada frase fica em sua própria linha.
Listas e títulos seguem a estrutura markdown normal.

## Regra 4 - sem travessão

Nunca usar o caractere em dash em texto. Usar o hífen simples no lugar.

## Regra 5 - nenhuma menção a outro projeto

Este projeto não referencia, por nome ou comparação direta, nenhum outro projeto de
pesquisa do usuário. Metodologia e estrutura podem ser similares a trabalhos anteriores,
mas o texto do notebook nunca cita isso.

## Checklist antes de salvar um notebook

- Toda célula de código tem uma célula markdown imediatamente anterior explicando o propósito.
- Nenhum comentário `#` dentro de células de código.
- Markdown com mais de uma frase está formatado uma frase por linha.
- Nenhum travessão "-" usado como pontuação.
- Nenhuma referência a outro projeto.
