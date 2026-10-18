"""Baixa os dados brutos de notificação de chikungunya do SINAN (anos 2020 a 2025).

Usa a biblioteca `pysus` para localizar e baixar os arquivos da ficha de notificação
de chikungunya (`disease="CHIK"`) junto ao FTP do DATASUS. Cada ano é baixado e lido em
chunks de partições parquet, para manter o uso de memória sob controle, e consolidado
num único parquet por ano em `data/raw/chik_{ano}.parquet`.
"""

from pathlib import Path

import pandas as pd
from pysus.online_data.SINAN import SINAN

ANOS = [2020, 2021, 2022, 2023, 2024, 2025]
DOENCA = "CHIK"
DIRETORIO_SAIDA = Path("data/raw")


def baixar_ano(sinan: SINAN, ano: int) -> pd.DataFrame:
    arquivos = sinan.get_files(DOENCA, ano)
    if not arquivos:
        print(f"[{ano}] nenhum arquivo encontrado no FTP do DATASUS, pulando")
        return pd.DataFrame()

    conjunto_parquet = sinan.download(arquivos)
    partes = sorted(Path(conjunto_parquet.path).glob("*.parquet"))
    print(f"[{ano}] {len(partes)} partições encontradas em {conjunto_parquet.path}")

    chunks = []
    for parte in partes:
        chunk = pd.read_parquet(parte)
        chunks.append(chunk)
        print(f"[{ano}] partição {parte.name}: {len(chunk)} registros")

    df_ano = pd.concat(chunks, ignore_index=True)
    print(f"[{ano}] total consolidado: {len(df_ano)} registros")
    return df_ano


def main() -> None:
    DIRETORIO_SAIDA.mkdir(parents=True, exist_ok=True)
    sinan = SINAN().load()

    for ano in ANOS:
        caminho_saida = DIRETORIO_SAIDA / f"chik_{ano}.parquet"
        if caminho_saida.exists():
            print(f"[{ano}] arquivo já existe em {caminho_saida}, pulando download")
            continue

        df_ano = baixar_ano(sinan, ano)
        if df_ano.empty:
            continue

        df_ano.to_parquet(caminho_saida, index=False)
        print(f"[{ano}] salvo em {caminho_saida}")

    print("Download concluído para os anos:", ANOS)


if __name__ == "__main__":
    main()
