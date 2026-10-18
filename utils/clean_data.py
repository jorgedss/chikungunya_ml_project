"""Filtra a coorte de interesse e consolida os anos de dados de chikungunya.

A partir dos parquets anuais gerados por `download_data.py`, aplica os filtros que
definem a coorte do estudo (casos internados, com desfecho conhecido e confirmação
laboratorial/clínica de chikungunya) e consolida todos os anos num único parquet em
`data/raw/chik_hospitalized.parquet`.

`FEATURES` é a lista de preditores usada a partir daqui em todo o pipeline, definida com
base no dicionário de dados real da ficha de notificação de chikungunya do SINAN e na
revisão bibliográfica do projeto (`docs/revisao_bibliografica_features.md`). `DATE_COLS`
e `METADATA_COLS` acompanham a coorte para auditoria, mas nunca entram em `X`.
"""

from pathlib import Path

import pandas as pd

ANOS = [2020, 2021, 2022, 2023, 2024, 2025]
DIRETORIO_RAW = Path("data/raw")
CAMINHO_SAIDA = DIRETORIO_RAW / "chik_hospitalized.parquet"

FEATURES_DEMOGRAFIA = [
    "CS_SEXO",
    "CS_GESTANT",
    "CS_RACA",
    "CS_ESCOL_N",
    "SG_UF",
    "SEM_PRI",
    "NU_IDADE_N",
]

FEATURES_SINTOMAS = [
    "FEBRE",
    "MIALGIA",
    "CEFALEIA",
    "EXANTEMA",
    "VOMITO",
    "NAUSEA",
    "DOR_COSTAS",
    "CONJUNTVIT",
    "ARTRITE",
    "ARTRALGIA",
    "PETEQUIA_N",
    "LEUCOPENIA",
    "LACO",
    "DOR_RETRO",
]

FEATURES_COMORBIDADES = [
    "DIABETES",
    "HEMATOLOG",
    "HEPATOPAT",
    "RENAL",
    "HIPERTENSA",
    "ACIDO_PEPT",
    "AUTO_IMUNE",
]

FEATURES = FEATURES_DEMOGRAFIA + FEATURES_SINTOMAS + FEATURES_COMORBIDADES

DATE_COLS = [
    "DT_NOTIFIC",
    "DT_SIN_PRI",
    "DT_INVEST",
    "DT_ENCERRA",
    "DT_OBITO",
    "DT_INTERNA",
    "DT_DIGITA",
]

METADATA_COLS = DATE_COLS + ["CLASSI_FIN", "CLINC_CHIK"]

COLUNAS_NECESSARIAS = FEATURES + METADATA_COLS + ["HOSPITALIZ", "EVOLUCAO"]


def limpar_colunas_texto(df: pd.DataFrame) -> pd.DataFrame:
    colunas_texto = df.select_dtypes(include="object").columns
    df[colunas_texto] = df[colunas_texto].apply(lambda col: col.str.strip())
    return df


def filtrar_ano(df: pd.DataFrame, ano: int) -> pd.DataFrame:
    total_inicial = len(df)
    df = limpar_colunas_texto(df)

    df = df[df["HOSPITALIZ"] == "1"]
    print(f"[{ano}] após HOSPITALIZ == 1: {len(df)} de {total_inicial} registros")

    df = df[df["EVOLUCAO"].isin(["1", "2"])]
    print(f"[{ano}] após EVOLUCAO em (cura, óbito): {len(df)} registros")

    df = df[df["CLASSI_FIN"] == "13"]
    print(f"[{ano}] após CLASSI_FIN == 13 (chikungunya confirmada): {len(df)} registros")

    distribuicao = df["EVOLUCAO"].value_counts()
    print(f"[{ano}] distribuição do desfecho (EVOLUCAO): {distribuicao.to_dict()}")

    return df


def main() -> None:
    partes = []
    for ano in ANOS:
        caminho_entrada = DIRETORIO_RAW / f"chik_{ano}.parquet"
        if not caminho_entrada.exists():
            print(f"[{ano}] arquivo {caminho_entrada} não encontrado, pulando")
            continue

        df_ano = pd.read_parquet(caminho_entrada, columns=None)
        colunas_presentes = [c for c in COLUNAS_NECESSARIAS if c in df_ano.columns]
        df_ano = df_ano[colunas_presentes + ["NU_ANO"]].copy()
        df_ano["year"] = ano

        df_ano = filtrar_ano(df_ano, ano)
        partes.append(df_ano)

    if not partes:
        print("Nenhum ano disponível para consolidar, abortando")
        return

    df_consolidado = pd.concat(partes, ignore_index=True)

    print("\nResumo consolidado:")
    print(f"Total de registros: {len(df_consolidado)}")
    print("Registros por ano:")
    print(df_consolidado["year"].value_counts().sort_index())
    print("Distribuição do desfecho (EVOLUCAO) consolidada:")
    print(df_consolidado["EVOLUCAO"].value_counts())

    DIRETORIO_RAW.mkdir(parents=True, exist_ok=True)
    df_consolidado.to_parquet(CAMINHO_SAIDA, index=False)
    print(f"\nSalvo em {CAMINHO_SAIDA}")


if __name__ == "__main__":
    main()
