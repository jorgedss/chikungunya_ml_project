"""Feature engineering e construção do alvo binário para o dataset de chikungunya.

A partir de `data/raw/chik_hospitalized.parquet`, decodifica a idade (`NU_IDADE_N`) e a
semana epidemiológica de início de sintomas (`SEM_PRI`) para formatos numéricos
utilizáveis por modelos, deriva o tempo entre início de sintomas e notificação, e
constrói o alvo binário `obito` (`EVOLUCAO == "2"`). O dataset tratado único, com a
coluna `year` preservada, é salvo em `data/processed/chik_treated.parquet`.
"""

from pathlib import Path

import pandas as pd

CAMINHO_ENTRADA = Path("data/raw/chik_hospitalized.parquet")
DIRETORIO_SAIDA = Path("data/processed")
CAMINHO_SAIDA = DIRETORIO_SAIDA / "chik_treated.parquet"

UNIDADES_IDADE = {
    "2": 1 / 365,
    "3": 1 / 12,
    "4": 1.0,
}


IDADE_MAXIMA_PLAUSIVEL = 110


def decodificar_idade(serie_idade: pd.Series) -> pd.Series:
    serie_idade = serie_idade.astype(str).str.strip()
    unidade = serie_idade.str[0]
    valor = pd.to_numeric(serie_idade.str[1:], errors="coerce")
    fator = unidade.map(UNIDADES_IDADE)
    idade_anos = valor * fator
    idade_anos = idade_anos.where(idade_anos <= IDADE_MAXIMA_PLAUSIVEL, pd.NA)
    return idade_anos


def decodificar_semana_epidemiologica(serie_sem_pri: pd.Series) -> pd.Series:
    serie_sem_pri = serie_sem_pri.astype(str).str.strip()
    semana = pd.to_numeric(serie_sem_pri.str[-2:], errors="coerce")
    return semana


def calcular_tempo_sintoma_notificacao(df: pd.DataFrame) -> pd.Series:
    dt_sin_pri = pd.to_datetime(df["DT_SIN_PRI"], format="%Y%m%d", errors="coerce")
    dt_notific = pd.to_datetime(df["DT_NOTIFIC"], format="%Y%m%d", errors="coerce")
    tempo_dias = (dt_notific - dt_sin_pri).dt.days
    return tempo_dias


def normalizar_ausentes(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    for coluna in colunas:
        df[coluna] = df[coluna].replace("", pd.NA)
    return df


def main() -> None:
    df = pd.read_parquet(CAMINHO_ENTRADA)
    print(f"Registros carregados de {CAMINHO_ENTRADA}: {len(df)}")

    df["IDADE_ANOS"] = decodificar_idade(df["NU_IDADE_N"])
    registros_idade_invalida = df["IDADE_ANOS"].isna().sum()
    print(f"Registros com idade implausível (> {IDADE_MAXIMA_PLAUSIVEL} anos) marcados como ausentes: {registros_idade_invalida}")
    df["SEMANA_EPI_SIN_PRI"] = decodificar_semana_epidemiologica(df["SEM_PRI"])
    df["TEMPO_SINTOMA_NOTIFICACAO"] = calcular_tempo_sintoma_notificacao(df)
    df = df.drop(columns=["NU_IDADE_N", "SEM_PRI"])

    colunas_categoricas = [
        "CS_SEXO",
        "CS_GESTANT",
        "CS_RACA",
        "CS_ESCOL_N",
        "SG_UF",
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
        "DIABETES",
        "HEMATOLOG",
        "HEPATOPAT",
        "RENAL",
        "HIPERTENSA",
        "ACIDO_PEPT",
        "AUTO_IMUNE",
    ]
    df = normalizar_ausentes(df, colunas_categoricas)

    print("Valores ausentes por coluna categórica (após normalização):")
    print(df[colunas_categoricas].isna().sum())

    print("Estatísticas de IDADE_ANOS:")
    print(df["IDADE_ANOS"].describe())
    print("Estatísticas de TEMPO_SINTOMA_NOTIFICACAO (dias):")
    print(df["TEMPO_SINTOMA_NOTIFICACAO"].describe())

    df["obito"] = (df["EVOLUCAO"] == "2").astype(int)

    print("\nDistribuição do alvo (obito):")
    print(df["obito"].value_counts())
    print("Proporção de óbito por ano:")
    print(df.groupby("year")["obito"].mean())

    DIRETORIO_SAIDA.mkdir(parents=True, exist_ok=True)
    df.to_parquet(CAMINHO_SAIDA, index=False)
    print(f"\nSalvo em {CAMINHO_SAIDA}")


if __name__ == "__main__":
    main()
