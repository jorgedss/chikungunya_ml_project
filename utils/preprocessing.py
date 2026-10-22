"""Funções compartilhadas pelos notebooks de modelagem (Fase 5) do projeto chikungunya_ml_project.

Reúne a construção dos folds de validação temporal expanding window, os dois
pré-processadores usados pelos algoritmos (codificação one hot e codificação
categórica nativa), e as funções de avaliação e de salvamento padronizado de
artefatos, para evitar duplicação entre os cinco notebooks de modelagem.
"""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

COLUNA_ALVO = "obito"
COLUNAS_NUMERICAS = ["IDADE_ANOS", "SEMANA_EPI_SIN_PRI"]
ANOS_TREINO = [2020, 2021, 2022, 2023]
ANOS_VALIDACAO_EXPANDING_WINDOW = [2021, 2022, 2023]


def obter_colunas_categoricas(X: pd.DataFrame) -> list[str]:
    return [coluna for coluna in X.columns if coluna not in COLUNAS_NUMERICAS]


def construir_folds_expanding_window(project_root: Path, tamanho_treino: int) -> list[tuple]:
    caminho_dados_tratados = Path(project_root) / "data" / "processed" / "chik_treated.parquet"
    dados_tratados = pd.read_parquet(caminho_dados_tratados, columns=["year"])
    anos_do_treino = dados_tratados[dados_tratados["year"].isin(ANOS_TREINO)].reset_index(drop=True)["year"]

    if len(anos_do_treino) != tamanho_treino:
        raise ValueError(
            "Numero de registros reconstruidos a partir de chik_treated.parquet "
            f"({len(anos_do_treino)}) difere do tamanho esperado do treino ({tamanho_treino})."
        )

    folds = []
    for ano_validacao in ANOS_VALIDACAO_EXPANDING_WINDOW:
        indices_treino = anos_do_treino[anos_do_treino < ano_validacao].index.to_numpy()
        indices_validacao = anos_do_treino[anos_do_treino == ano_validacao].index.to_numpy()
        folds.append((indices_treino, indices_validacao))

    return folds


def construir_preprocessador_one_hot(
    colunas_numericas: list[str], colunas_categoricas: list[str], escalonar_numericas: bool = False
) -> ColumnTransformer:
    etapas_numericas = [("imputador", SimpleImputer(strategy="median"))]
    if escalonar_numericas:
        etapas_numericas.append(("escalonador", StandardScaler()))

    transformador_numerico = Pipeline(steps=etapas_numericas)
    transformador_categorico = Pipeline(
        steps=[
            ("imputador", SimpleImputer(strategy="constant", fill_value="ausente")),
            ("codificador", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numericas", transformador_numerico, colunas_numericas),
            ("categoricas", transformador_categorico, colunas_categoricas),
        ]
    )


class ImputadorCategoricoNativo(BaseEstimator, TransformerMixin):
    """Imputa ausentes e expõe as categóricas como dtype category, para uso nativo em XGBoost e LightGBM."""

    def __init__(self, colunas_numericas: list[str], colunas_categoricas: list[str]):
        self.colunas_numericas = colunas_numericas
        self.colunas_categoricas = colunas_categoricas

    def fit(self, X: pd.DataFrame, y=None) -> "ImputadorCategoricoNativo":
        self.medianas_ = X[self.colunas_numericas].median()
        self.categorias_por_coluna_ = {
            coluna: sorted(X[coluna].fillna("ausente").astype(str).unique())
            for coluna in self.colunas_categoricas
        }
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X_transformado = X[self.colunas_numericas + self.colunas_categoricas].copy()
        X_transformado[self.colunas_numericas] = X_transformado[self.colunas_numericas].fillna(self.medianas_)

        for coluna in self.colunas_categoricas:
            valores_preenchidos = X_transformado[coluna].fillna("ausente").astype(str)
            X_transformado[coluna] = pd.Categorical(
                valores_preenchidos, categories=self.categorias_por_coluna_[coluna]
            )

        return X_transformado


def obter_scale_pos_weight(y: pd.Series) -> float:
    numero_negativos = (y == 0).sum()
    numero_positivos = (y == 1).sum()
    return numero_negativos / numero_positivos


def avaliar_predicoes(y_verdadeiro: pd.Series, probabilidade_predita) -> dict:
    return {
        "auprc": average_precision_score(y_verdadeiro, probabilidade_predita),
        "roc_auc": roc_auc_score(y_verdadeiro, probabilidade_predita),
        "brier_score": brier_score_loss(y_verdadeiro, probabilidade_predita),
    }


def salvar_predicoes(caminho: Path, probabilidade_predita, y_verdadeiro: pd.Series) -> None:
    tabela_predicoes = pd.DataFrame(
        {
            "probabilidade_predita": probabilidade_predita,
            COLUNA_ALVO: pd.Series(y_verdadeiro).reset_index(drop=True),
        }
    )
    tabela_predicoes.to_parquet(caminho, index=False)


def salvar_modelo(caminho: Path, modelo_ajustado) -> None:
    joblib.dump(modelo_ajustado, caminho)


def salvar_resultados_grid_search(grid_search, caminho: Path) -> pd.DataFrame:
    resultados = pd.DataFrame(grid_search.cv_results_).sort_values("rank_test_score").reset_index(drop=True)
    resultados.to_csv(caminho, index=False)
    return resultados
