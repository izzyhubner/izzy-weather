
from pathlib import Path
import sys

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from data.src.build_analytical_layer import (
    build_dim_date,
    build_dim_disaster_type,
    build_dim_municipality,
    build_fact_disasters,
    validate_analytical_layer,
)


@pytest.fixture
def sample_source_data():
    """Create a small dataset for automated tests."""
    return pd.DataFrame(
        {
            "Protocolo_S2iD": ["TEST-001", "TEST-002"],
            "Cod_IBGE_Mun": ["430001", "430001"],
            "Nome_Municipio": ["Test Municipality", "Test Municipality"],
            "Sigla_UF": ["RS", "RS"],
            "regiao": ["Sul", "Sul"],
            "Cod_Cobrade": ["1.1.1.1.0", "1.1.1.1.0"],
            "grupo_de_desastre": ["Test Group", "Test Group"],
            "tipologia": ["Test Type", "Test Type"],
            "descricao_tipologia": ["Test Description", "Test Description"],
            "Data_Evento": pd.to_datetime(
                ["2025-01-01", "2025-01-03"]
            ),
            "Data_Registro": pd.to_datetime(
                ["2025-01-02", "2025-01-04"]
            ),
        }
    )


@pytest.fixture
def analytical_tables(sample_source_data):
    """Build analytical tables from the sample dataset."""
    source = sample_source_data

    dim_municipality = build_dim_municipality(source)
    dim_disaster_type = build_dim_disaster_type(source)
    dim_date = build_dim_date(source)
    fact = build_fact_disasters(source)

    return fact, dim_municipality, dim_disaster_type, dim_date


def test_primary_keys_are_unique_and_not_null(analytical_tables):
    fact, dim_municipality, dim_disaster_type, dim_date = analytical_tables

    primary_keys = {
        "municipality_code": dim_municipality["municipality_code"],
        "cobrade_code": dim_disaster_type["cobrade_code"],
        "date_key": dim_date["date_key"],
        "disaster_id": fact["disaster_id"],
    }

    for column, values in primary_keys.items():
        assert values.notna().all(), f"{column} contains null values"
        assert values.is_unique, f"{column} contains duplicates"


def test_fact_foreign_keys_exist_in_dimensions(analytical_tables):
    fact, dim_municipality, dim_disaster_type, dim_date = analytical_tables

    relationships = [
        ("municipality_code", dim_municipality["municipality_code"]),
        ("cobrade_code", dim_disaster_type["cobrade_code"]),
        ("event_date_key", dim_date["date_key"]),
        ("registration_date_key", dim_date["date_key"]),
    ]

    for fact_column, dimension_keys in relationships:
        fact_keys = set(fact[fact_column].dropna())
        valid_keys = set(dimension_keys.dropna())

        assert fact_keys.issubset(valid_keys), (
            f"{fact_column} contains keys missing from its dimension"
        )


def test_fact_preserves_source_record_count(
    sample_source_data, analytical_tables
):
    fact, _, _, _ = analytical_tables

    assert len(fact) == len(sample_source_data)
    assert fact["disaster_id"].nunique() == len(sample_source_data)


def test_pipeline_validation_rejects_duplicate_primary_keys():
    fact = pd.DataFrame(
        {
            "disaster_id": ["A", "A"],
            "municipality_code": ["M1", "M1"],
            "cobrade_code": ["C1", "C1"],
            "event_date": pd.to_datetime(
                ["2025-01-01", "2025-01-01"]
            ),
            "event_date_key": pd.Series(
                [20250101, 20250101], dtype="Int64"
            ),
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
