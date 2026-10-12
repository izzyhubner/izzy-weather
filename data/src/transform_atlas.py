from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "atlasdigital"
    / "BD_Atlas_1991_2025_v1.1_2026.08.06_Consolidado.csv"
)

IBGE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ibge"
    / "municipality_reference.parquet"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "atlasdigital"
    / "atlas_disasters.parquet"
)


def main():
    df = pd.read_csv(
        INPUT_PATH,
        sep=";",
        encoding="latin1",
        dtype={"Cod_IBGE_Mun": "string"},
    )

    municipality_reference = pd.read_parquet(IBGE_PATH)

    # Standardize municipality codes
    df["Cod_IBGE_Mun"] = df["Cod_IBGE_Mun"].str.strip()

    municipality_reference["Código Município Completo"] = (
        municipality_reference["Código Município Completo"].str.strip()
    )

    # Preserve the original municipality name
    df = df.rename(columns={"Nome_Municipio": "Nome_Municipio_raw"})

    # Normalize state abbreviations
    df["Sigla_UF"] = df["Sigla_UF"].str.strip().str.upper()

    # Convert whitespace-only descriptions to null
    description_columns = [
        column
        for column in df.columns
        if column.endswith("_Descricao")
    ]

    for column in description_columns:
        df[column] = df[column].replace(r"^\s*$", pd.NA, regex=True)

    # Prepare the IBGE reference for enrichment
    municipality_reference = municipality_reference.rename(
        columns={
            "Código Município Completo": "Cod_IBGE_Mun",
            "Nome_Município": "Nome_Municipio_ibge",
        }
    )

    # Enrich Atlas with official municipality names
    df = df.merge(
        municipality_reference,
        on="Cod_IBGE_Mun",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    df["municipality_match"] = df["_merge"].eq("both")

    df["Nome_Municipio"] = df["Nome_Municipio_ibge"]

    df = df.drop(columns=["Nome_Municipio_ibge", "_merge"])

    # Preserve date values and report temporal anomalies
    df["Data_Evento"] = pd.to_datetime(
        df["Data_Evento"], errors="coerce", dayfirst=True
    )
    df["Data_Registro"] = pd.to_datetime(
        df["Data_Registro"], errors="coerce", dayfirst=True
    )

    invalid_event_dates = df["Data_Evento"].isna().sum()
    invalid_registration_dates = df["Data_Registro"].isna().sum()
    temporal_anomalies = (
        df["Data_Evento"].notna()
        & df["Data_Registro"].notna()
        & (df["Data_Evento"] > df["Data_Registro"])
    ).sum()

    # Create the output directory and save the curated dataset
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_PATH, index=False)

    print("\nNull counts in key columns:")
    for column in [
        "Cod_IBGE_Mun",
        "Sigla_UF",
        "Data_Evento",
        "Data_Registro",
        "Nome_Municipio",
    ]:
        print(f"{column}: {df[column].isna().sum()}")

    print("\nWhitespace-only values remaining in descriptions:")
    for column in description_columns:
        whitespace_count = (
            df[column]
            .astype("string")
            .str.fullmatch(r"\s*", na=False)
            .sum()
        )
        print(f"{column}: {whitespace_count}")

if __name__ == "__main__":
    main()
