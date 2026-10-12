from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "atlasdigital"
    / "atlas_disasters.parquet"
)


def main():
    df = pd.read_parquet(INPUT_PATH)

    for column in df.columns:
        print(f"{column}: {df[column].dtype}")

    # 1. Validate disaster type dimension
    disaster_type_columns = [
        "Cod_Cobrade",
        "grupo_de_desastre",
        "tipologia",
        "descricao_tipologia",
    ]

    disaster_types = df[disaster_type_columns].drop_duplicates()

    cobrade_counts = (
        disaster_types.groupby("Cod_Cobrade", dropna=False)
        .size()
    )

    conflicting_cobrade = cobrade_counts[cobrade_counts > 1]

    print("=== Disaster Type Dimension ===")
    print(f"Distinct attribute combinations: {len(disaster_types)}")
    print(f"Unique COBRADE codes: {df['Cod_Cobrade'].nunique()}")
    print(f"Null COBRADE codes: {df['Cod_Cobrade'].isna().sum()}")
    print(f"COBRADE codes with conflicting attributes: {len(conflicting_cobrade)}")

    if not conflicting_cobrade.empty:
        print("\nConflicting COBRADE codes:")
        print(
            disaster_types[
                disaster_types["Cod_Cobrade"].isin(conflicting_cobrade.index)
            ].sort_values("Cod_Cobrade").to_string(index=False)
        )

    # 2. Validate municipality dimension
    municipality_columns = [
        "Cod_IBGE_Mun",
        "Nome_Municipio",
        "Sigla_UF",
        "regiao",
    ]

    municipalities = df[municipality_columns].drop_duplicates()

    municipality_counts = (
        municipalities.groupby("Cod_IBGE_Mun", dropna=False)
        .size()
    )

    conflicting_municipalities = municipality_counts[
        municipality_counts > 1
    ]

    print("\n=== Municipality Dimension ===")
    print(f"Distinct attribute combinations: {len(municipalities)}")
    print(f"Unique municipality codes: {df['Cod_IBGE_Mun'].nunique()}")
    print(f"Null municipality codes: {df['Cod_IBGE_Mun'].isna().sum()}")
    print(
        "Municipality codes with conflicting attributes:",
        len(conflicting_municipalities),
    )

    if not conflicting_municipalities.empty:
        print("\nConflicting municipality codes:")
        print(
            municipalities[
                municipalities["Cod_IBGE_Mun"].isin(
                    conflicting_municipalities.index
                )
            ]
            .sort_values("Cod_IBGE_Mun")
            .to_string(index=False)
        )


if __name__ == "__main__":
    main()