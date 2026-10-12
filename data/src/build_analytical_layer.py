
from pathlib import Path

import pandas as pd

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from data.src.column_mapping import COLUMN_MAPPING

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CURATED_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "atlasdigital"
    / "atlas_disasters.parquet"
)

ANALYTICAL_DIR = PROJECT_ROOT / "data" / "processed" / "analytical"


def build_dim_municipality(df: pd.DataFrame) -> pd.DataFrame:
    """Build the municipality dimension from curated disaster records."""
    source_columns = [
        "Cod_IBGE_Mun",
        "Nome_Municipio",
        "Sigla_UF",
        "regiao",
    ]

    dim_municipality = df[source_columns].drop_duplicates().copy()

    dim_municipality = dim_municipality.rename(
        columns={
            column: COLUMN_MAPPING[column]
            for column in source_columns
        }
    )

    if dim_municipality["municipality_code"].duplicated().any():
        raise ValueError(
            "A municipality code is associated with conflicting attributes."
        )

    return dim_municipality.sort_values("municipality_code").reset_index(
        drop=True
    )


def build_dim_disaster_type(df: pd.DataFrame) -> pd.DataFrame:
    """Build the disaster type dimension from curated disaster records."""
    source_columns = [
        "Cod_Cobrade",
        "grupo_de_desastre",
        "tipologia",
        "descricao_tipologia",
    ]

    dim_disaster_type = df[source_columns].drop_duplicates().copy()

    dim_disaster_type = dim_disaster_type.rename(
        columns={
            column: COLUMN_MAPPING[column]
            for column in source_columns
        }
    )

    if dim_disaster_type["cobrade_code"].duplicated().any():
        raise ValueError(
            "A COBRADE code is associated with conflicting attributes."
        )

    return dim_disaster_type.sort_values("cobrade_code").reset_index(
        drop=True
    )

def build_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    """Build a calendar dimension covering both disaster dates."""
    date_columns = ["Data_Evento", "Data_Registro"]

    all_dates = pd.concat(
        [pd.to_datetime(df[column], errors="coerce") for column in date_columns],
        ignore_index=True,
    ).dropna()

    if all_dates.empty:
        raise ValueError("No valid dates were found in the source data.")

    date_range = pd.date_range(
        start=all_dates.min().normalize(),
        end=all_dates.max().normalize(),
        freq="D",
    )

    dim_date = pd.DataFrame({"date": date_range})

    dim_date["date_key"] = (
        dim_date["date"].dt.strftime("%Y%m%d").astype("int32")
    )
    dim_date["day"] = dim_date["date"].dt.day
    dim_date["month"] = dim_date["date"].dt.month
    dim_date["month_name"] = dim_date["date"].dt.month_name()
    dim_date["quarter"] = dim_date["date"].dt.quarter
    dim_date["year"] = dim_date["date"].dt.year

    return dim_date[
        [
            "date_key",
            "date",
            "day",
            "month",
            "month_name",
            "quarter",
            "year",
        ]
    ]


def build_fact_disasters(df: pd.DataFrame) -> pd.DataFrame:
    """Build the disaster fact table."""
    excluded_columns = {
        "Nome_Municipio_raw",
        "Status",
        "Setores Censitários",
        "DH_Descricao",
        "DM_Descricao",
        "DA_Descricao",
        "PEPL_Descricao",
        "PEPR_Descricao",
        "municipality_match",
    }

    source_columns = [
        column
        for column in COLUMN_MAPPING
        if column in df.columns and column not in excluded_columns
    ]

    fact_disasters = df[source_columns].rename(
        columns=COLUMN_MAPPING
    ).copy()

    fact_disasters["event_date_key"] = (
        pd.to_datetime(fact_disasters["event_date"], errors="coerce")
        .dt.strftime("%Y%m%d")
        .astype("Int64")
    )

    fact_disasters["registration_date_key"] = (
        pd.to_datetime(fact_disasters["registration_date"], errors="coerce")
        .dt.strftime("%Y%m%d")
        .astype("Int64")
    )

    if fact_disasters["disaster_id"].isna().any():
        raise ValueError("Disaster IDs cannot be null.")

    if fact_disasters["disaster_id"].duplicated().any():
        raise ValueError("Disaster IDs must be unique.")

    return fact_disasters.sort_values("disaster_id").reset_index(
        drop=True
    )


def validate_analytical_layer(
    fact: pd.DataFrame,
    dim_municipality: pd.DataFrame,
    dim_disaster_type: pd.DataFrame,
    dim_date: pd.DataFrame,
    expected_rows: int,
) -> None:
    """Validate primary keys, foreign keys, dates, and row counts."""

    primary_keys = {
        "disaster_id": fact["disaster_id"],
        "municipality_code": dim_municipality["municipality_code"],
        "cobrade_code": dim_disaster_type["cobrade_code"],
        "date_key": dim_date["date_key"],
    }

    for column, values in primary_keys.items():
        if values.isna().any():
            raise ValueError(f"Primary key contains nulls: {column}")

        if values.duplicated().any():
            raise ValueError(f"Primary key contains duplicates: {column}")

    foreign_keys = {
        "municipality_code": (
            fact["municipality_code"],
            dim_municipality["municipality_code"],
        ),
        "cobrade_code": (
            fact["cobrade_code"],
            dim_disaster_type["cobrade_code"],
        ),
        "event_date_key": (
            fact["event_date_key"],
            dim_date["date_key"],
        ),
        "registration_date_key": (
            fact["registration_date_key"],
            dim_date["date_key"],
        ),
    }

    for column, (fact_keys, dimension_keys) in foreign_keys.items():
        missing = set(fact_keys.dropna()) - set(dimension_keys.dropna())

        if missing:
            raise ValueError(
                f"Foreign key {column} has {len(missing)} "
                "values without a matching dimension."
            )

    date_columns = {
        "event_date": "event_date_key",
        "registration_date": "registration_date_key",
    }

    for date_column, key_column in date_columns.items():
        expected_keys = (
            pd.to_datetime(fact[date_column], errors="coerce")
            .dt.strftime("%Y%m%d")
            .astype("Int64")
        )

        if not expected_keys.equals(fact[key_column].astype("Int64")):
            raise ValueError(
                f"Date key mismatch between {date_column} and {key_column}."
            )

    if len(fact) != expected_rows:
        raise ValueError(
            f"Unexpected fact row count: {len(fact)}; "
            f"expected {expected_rows}."
        )

    print("All analytical layer validations passed.")


def main() -> None:
    df = pd.read_parquet(CURATED_PATH)

    dim_municipality = build_dim_municipality(df)
    dim_disaster_type = build_dim_disaster_type(df)
    dim_date = build_dim_date(df)
    fact_disasters = build_fact_disasters(df)

    validate_analytical_layer(
        fact=fact_disasters,
        dim_municipality=dim_municipality,
        dim_disaster_type=dim_disaster_type,
        dim_date=dim_date,
        expected_rows=len(df),
    )

    ANALYTICAL_DIR.mkdir(parents=True, exist_ok=True)

    tables = {
        "dim_municipality": dim_municipality,
        "dim_disaster_type": dim_disaster_type,
        "dim_date": dim_date,
        "fact_disasters": fact_disasters,
    }

    for table_name, table_df in tables.items():
        output_path = ANALYTICAL_DIR / f"{table_name}.parquet"
        table_df.to_parquet(output_path, index=False)

        print(f"{table_name}: {len(table_df):,} rows")
        print(f"Output: {output_path}")

if __name__ == "__main__":
    main()
