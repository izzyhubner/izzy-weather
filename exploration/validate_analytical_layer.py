
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ANALYTICAL_DIR = PROJECT_ROOT / "data" / "processed" / "analytical"

fact = pd.read_parquet(ANALYTICAL_DIR / "fact_disasters.parquet")
dim_municipality = pd.read_parquet(
    ANALYTICAL_DIR / "dim_municipality.parquet"
)
dim_disaster_type = pd.read_parquet(
    ANALYTICAL_DIR / "dim_disaster_type.parquet"
)
dim_date = pd.read_parquet(ANALYTICAL_DIR / "dim_date.parquet")


def check_foreign_key(
    fact_df: pd.DataFrame,
    fact_column: str,
    dimension_df: pd.DataFrame,
    dimension_column: str,
) -> None:
    """Validate that non-null foreign keys exist in the dimension."""
    fact_keys = fact_df[fact_column].dropna().unique()
    dimension_keys = set(dimension_df[dimension_column].dropna())

    missing_keys = set(fact_keys) - dimension_keys

    print(f"\n{fact_column}")
    print(f"Distinct non-null keys: {len(fact_keys):,}")
    print(f"Missing dimension keys: {len(missing_keys):,}")

    if missing_keys:
        print(f"Examples: {list(missing_keys)[:10]}")


check_foreign_key(
    fact,
    "municipality_code",
    dim_municipality,
    "municipality_code",
)

check_foreign_key(
    fact,
    "cobrade_code",
    dim_disaster_type,
    "cobrade_code",
)

check_foreign_key(
    fact,
    "event_date_key",
    dim_date,
    "date_key",
)

check_foreign_key(
    fact,
    "registration_date_key",
    dim_date,
    "date_key",
)


print("\n=== Primary Key Checks ===")

primary_key_checks = {
    "disaster_id": fact["disaster_id"],
    "municipality_code": dim_municipality["municipality_code"],
    "cobrade_code": dim_disaster_type["cobrade_code"],
    "date_key": dim_date["date_key"],
}

for column, values in primary_key_checks.items():
    null_count = values.isna().sum()
    duplicate_count = values.duplicated().sum()

    print(
        f"{column}: "
        f"nulls={null_count:,}, duplicates={duplicate_count:,}"
    )


print("\n=== Date Key Consistency ===")

date_checks = {
    "event_date": "event_date_key",
    "registration_date": "registration_date_key",
}

for date_column, key_column in date_checks.items():
    expected_keys = pd.to_datetime(
        fact[date_column], errors="coerce"
    ).dt.strftime("%Y%m%d")

    expected_keys = expected_keys.astype("Int64")

    mismatch_count = (
        expected_keys.ne(fact[key_column]).fillna(False)
    ).sum()

    print(f"{date_column}: mismatches={mismatch_count:,}")


print("\n=== Record Count ===")

print(f"Fact records: {len(fact):,}")
print(f"Unique disaster IDs: {fact['disaster_id'].nunique():,}")
