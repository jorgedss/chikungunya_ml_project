"""Split temporal do dataset tratado de chikungunya em treino, teste e validação externa.

A partir de `data/processed/chik_treated.parquet`, separa a coorte por ano: treino
(2020-2023), teste (2024) e validação externa (2025). Em cada partição, `X` contém
apenas os preditores (excluindo datas, metadados de classificação do caso e colunas
administrativas usadas só para filtragem/auditoria) e `y` contém o alvo `obito`. Os
arquivos são salvos em `data/features/baseline/`.
"""

from pathlib import Path

import pandas as pd

from utils.clean_data import METADATA_COLS

CAMINHO_ENTRADA = Path("data/processed/chik_treated.parquet")
DIRETORIO_SAIDA = Path("data/features/baseline")

ANOS_TREINO = [2020, 2021, 2022, 2023]
ANO_TESTE = 2024
ANO_VALIDACAO_EXTERNA = 2025

COLUNA_ALVO = "obito"
COLUNAS_NAO_PREDITORAS = METADATA_COLS + [
    "HOSPITALIZ",
    "EVOLUCAO",
    "NU_ANO",
    "year",
    COLUNA_ALVO,
]


def separar_x_y(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    colunas_excluidas = [c for c in COLUNAS_NAO_PREDITORAS if c in df.columns]
    X = df.drop(columns=colunas_excluidas)
    y = df[COLUNA_ALVO]
    return X, y


def salvar_particao(nome: str, df: pd.DataFrame) -> None:
    X, y = separar_x_y(df)
    X.to_parquet(DIRETORIO_SAIDA / f"X_{nome}.parquet", index=False)
    y.to_frame(name=COLUNA_ALVO).to_parquet(DIRETORIO_SAIDA / f"y_{nome}.parquet", index=False)

    print(f"[{nome}] registros: {len(df)}, preditores: {X.shape[1]}")
    print(f"[{nome}] distribuição do alvo: {y.value_counts().to_dict()}")
    print(f"[{nome}] prevalência de óbito: {y.mean():.4f}")


def main() -> None:
    df = pd.read_parquet(CAMINHO_ENTRADA)
    print(f"Registros carregados de {CAMINHO_ENTRADA}: {len(df)}")

    df_treino = df[df["year"].isin(ANOS_TREINO)]
    df_teste = df[df["year"] == ANO_TESTE]
    df_validacao = df[df["year"] == ANO_VALIDACAO_EXTERNA]

    DIRETORIO_SAIDA.mkdir(parents=True, exist_ok=True)

    salvar_particao("train", df_treino)
    salvar_particao("test", df_teste)
    salvar_particao("val2025", df_validacao)

    total_particionado = len(df_treino) + len(df_teste) + len(df_validacao)
    print(f"\nTotal particionado: {total_particionado} de {len(df)} registros")
    if total_particionado != len(df):
        print("Aviso: existem registros fora dos anos de treino/teste/validação definidos")

    print(f"\nArquivos salvos em {DIRETORIO_SAIDA}")


if __name__ == "__main__":
    main()
