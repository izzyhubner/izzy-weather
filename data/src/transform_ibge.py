
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "ibge"
    / "RELATORIO_DTB_BRASIL_MUNICIPIO.xls"
)
OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ibge"
    / "municipality_reference.parquet"
)

CODE_COLUMN = "Código Município Completo"
NAME_COLUMN = "Nome_Município"


def main():
    df = pd.read_excel(
    INPUT_PATH,
    header=6,
    usecols=[CODE_COLUMN, NAME_COLUMN ],
    dtype={CODE_COLUMN: "string"},
    )

    df = df.drop_duplicates(subset=[CODE_COLUMN, NAME_COLUMN])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_PATH, index=False)

    print(f"Rows saved: {len(df)}")
    print(f"Output: {OUTPUT_PATH}")

    print(f"Unique municipality codes: {df[CODE_COLUMN].nunique()}")
    print(f"Duplicate codes: {df.duplicated(subset=[CODE_COLUMN]).sum()}")
    print(f"Null codes: {df[CODE_COLUMN].isna().sum()}")
    print(f"Null names: {df[NAME_COLUMN].isna().sum()}")


if __name__ == "__main__":
    main()
