"""Orquestra o pipeline de dados completo do projeto chikungunya_ml_project.

Executa, em sequência, as quatro etapas que transformam os dados brutos de
notificação de chikungunya do SINAN num conjunto de treino/teste/validação externa
pronto para modelagem: download (`utils/download_data.py`), limpeza e filtro da coorte
(`utils/clean_data.py`), feature engineering e construção do alvo
(`utils/treat_data.py`) e split temporal (`utils/split_data.py`).
"""

from utils import clean_data, download_data, split_data, treat_data


def main() -> None:
    print("=" * 60)
    print("Etapa 1/4: download dos dados brutos do SINAN")
    print("=" * 60)
    download_data.main()

    print("\n" + "=" * 60)
    print("Etapa 2/4: limpeza e filtro da coorte")
    print("=" * 60)
    clean_data.main()

    print("\n" + "=" * 60)
    print("Etapa 3/4: feature engineering e construção do alvo")
    print("=" * 60)
    treat_data.main()

    print("\n" + "=" * 60)
    print("Etapa 4/4: split temporal treino/teste/validação externa")
    print("=" * 60)
    split_data.main()

    print("\n" + "=" * 60)
    print("Pipeline de dados concluído")
    print("=" * 60)


if __name__ == "__main__":
    main()
