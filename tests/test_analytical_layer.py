
from pathlib import Path

import pandas as pd

import pytest

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT_ROOT))

from data.src.build_analytical_layer import validate_analytical_layer

ANALYTICAL_DIR = PROJECT_ROOT / "data" / "processed" / "analytical"


def test_primary_keys_are_unique_and_not_null():
    dim_municipality = pd.read_parquet(
        ANALYTICAL_DIR / "dim_municipality.parquet"
    )
    dim_disaster_type = pd.read_parquet(
        ANALYTICAL_DIR / "dim_disaster_type.parquet"
    )
    dim_date = pd.read_parquet(
        ANALYTICAL_DIR / "dim_date.parquet"
    )
    fact = pd.read_parquet(
        ANALYTICAL_DIR / "fact_disasters.parquet"
    )

    primary_keys = {
        "municipality_code": dim_municipality["municipality_code"],
        "cobrade_code": dim_disaster_type["cobrade_code"],
        "date_key": dim_date["date_key"],
        "disaster_id": fact["disaster_id"],
    }

    for column, values in primary_keys.items():
        assert values.notna().all(), f"{column} contains null values"
        assert values.is_unique, f"{column} contains duplicates"


def test_fact_foreign_keys_exist_in_dimensions():
    fact = pd.read_parquet(
        ANALYTICAL_DIR / "fact_disasters.parquet"
    )
    dim_municipality = pd.read_parquet(
        ANALYTICAL_DIR / "dim_municipality.parquet"
    )
    dim_disaster_type = pd.read_parquet(
        ANALYTICAL_DIR / "dim_disaster_type.parquet"
    )
    dim_date = pd.read_parquet(
        ANALYTICAL_DIR / "dim_date.parquet"
    )

    relationships = [
        (
            "municipality_code",
            dim_municipality["municipality_code"],
        ),
        (
            "cobrade_code",
            dim_disaster_type["cobrade_code"],
        ),
        (
            "event_date_key",
            dim_date["date_key"],
        ),
        (
            "registration_date_key",
            dim_date["date_key"],
        ),
    ]

    for fact_column, dimension_keys in relationships:
        fact_keys = set(fact[fact_column].dropna())
        valid_keys = set(dimension_keys.dropna())

        assert fact_keys.issubset(valid_keys), (
            f"{fact_column} contains keys missing from its dimension"
        )


def test_fact_preserves_curated_record_count():
    curated = pd.read_parquet(
        PROJECT_ROOT
        / "data"
        / "processed"
        / "atlasdigital"
        / "atlas_disasters.parquet"
    )
    fact = pd.read_parquet(
        ANALYTICAL_DIR / "fact_disasters.parquet"
    )

    assert len(fact) == len(curated)
    assert fact["disaster_id"].nunique() == len(curated)



def test_pipeline_validation_rejects_duplicate_primary_keys():
    fact = pd.DataFrame(
        {
            "disaster_id": ["A", "A"],
            "municipality_code": ["M1", "M1"],
            "cobrade_code": ["C1", "C1"],
            "event_date": pd.to_datetime(["2025-01-01", "2025-01-01"]),
            "event_date_key": pd.Series([20250101, 20250101], dtype="Int64"),
            "registration_date": pd.to_datetime(
                ["2025-01-02", "2025-01-02"]
            ),
            "registration_date_key": pd.Series(
                [20250102, 20250102], dtype="Int64"
            ),
        }
    )

    dim_municipality = pd.DataFrame(
        {"municipality_code": ["M1"]}
    )
    dim_disaster_type = pd.DataFrame(
        {"cobrade_code": ["C1"]}
    )
    dim_date = pd.DataFrame(
        {"date_key": [20250101, 20250102]}
    )

    with pytest.raises(ValueError, match="disaster_id"):
        validate_analytical_layer(
            fact=fact,
            dim_municipality=dim_municipality,
            dim_disaster_type=dim_disaster_type,
            dim_date=dim_date,
            expected_rows=2,
        )

