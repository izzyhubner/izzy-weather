
from pathlib import Path

import pandas as pd

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data.src.column_mapping import COLUMN_MAPPING


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "atlasdigital"
    / "atlas_disasters.parquet"
)

EXCLUDED_COLUMNS = {
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


def main():
    df = pd.read_parquet(INPUT_PATH)

    expected_columns = set(df.columns) - EXCLUDED_COLUMNS
    mapped_columns = set(COLUMN_MAPPING)

    missing_mappings = expected_columns - mapped_columns
    unknown_source_columns = mapped_columns - set(df.columns)

    destination_names = list(COLUMN_MAPPING.values())
    duplicate_destinations = sorted(
        {
            name
            for name in destination_names
            if destination_names.count(name) > 1
        }
    )

    print(f"Expected columns: {len(expected_columns)}")
    print(f"Mapped columns: {len(mapped_columns)}")
    print(f"Missing mappings: {sorted(missing_mappings)}")
    print(f"Unknown source columns: {sorted(unknown_source_columns)}")
    print(f"Duplicate destination names: {duplicate_destinations}")


if __name__ == "__main__":
    main()
