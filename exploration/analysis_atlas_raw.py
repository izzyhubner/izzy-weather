import pandas as pd

df = pd.read_csv(
    "data/raw/atlasdigital/BD_Atlas_1991_2025_v1.1_2026.08.06_Consolidado.csv",
    sep=";",
    encoding="latin1"
)

# types/nulls
print(df.dtypes)
print(df.isna().sum().sort_values(ascending=False))

# valid rows
print("Valid protocols:", df["Protocolo_S2iD"].notna().sum())

print(
    "Duplicated protocols:",
    df["Protocolo_S2iD"].dropna().duplicated().sum()
)

print("Duplicated rows:", df.duplicated().sum())

# date types
print(df[["Data_Evento", "Data_Registro"]].dtypes)
print(df[["Data_Evento", "Data_Registro"]].head(10).to_string())

# check interval
for column in ["Data_Evento", "Data_Registro"]:
    datas = pd.to_datetime(
        df[column],
        errors="coerce",
        dayfirst=True
    )

    print(f"\n--- {column} ---")
    print("Initial date:", datas.min())
    print("Final date:", datas.max())

# Check date consistency
event_dates = pd.to_datetime(
    df["Data_Evento"],
    errors="coerce",
    dayfirst=True
)

registration_dates = pd.to_datetime(
    df["Data_Registro"],
    errors="coerce",
    dayfirst=True
)

print("Missing event dates:", df["Data_Evento"].isna().sum())
print("Unparseable event dates:", (
    df["Data_Evento"].notna() & event_dates.isna()
).sum())

print("Missing registration dates:", df["Data_Registro"].isna().sum())
print("Unparseable registration dates:", (
    df["Data_Registro"].notna() & registration_dates.isna()
).sum())

event_after_registration = (
    event_dates.notna()
    & registration_dates.notna()
    & (event_dates > registration_dates)
)

print(
    "Events after registration:",
    event_after_registration.sum()
)

print(
    df.loc[
        event_after_registration,
        [
            "Protocolo_S2iD",
            "Data_Evento",
            "Data_Registro",
            "tipologia",
            "descricao_tipologia",
            "grupo_de_desastre",
            "Nome_Municipio",
            "Sigla_UF",
        ]
    ].sort_values("Data_Registro").to_string(index=False)
)

# Extract the date embedded in the protocol
protocol_dates = pd.to_datetime(
    df.loc[event_after_registration, "Protocolo_S2iD"]
    .str.extract(r"-(\d{8})$")[0],
    format="%Y%m%d",
    errors="coerce"
)

date_comparison = df.loc[
    event_after_registration,
    ["Protocolo_S2iD", "Data_Evento", "Data_Registro"]
].copy()

date_comparison["Protocol_Date"] = protocol_dates

print(date_comparison.to_string(index=False))

# Extract the date embedded in the protocol
protocol_dates = pd.to_datetime(
    df["Protocolo_S2iD"].str.extract(r"-(\d{8})$")[0],
    format="%Y%m%d",
    errors="coerce"
)

# Parse registration dates
registration_dates = pd.to_datetime(
    df["Data_Registro"],
    format="%d/%m/%Y",
    errors="coerce"
)

# Compare the dates
date_mismatch = (
    protocol_dates.notna()
    & registration_dates.notna()
    & (protocol_dates != registration_dates)
)

print("Protocols with extractable dates:", protocol_dates.notna().sum())
print("Registration dates different from protocol dates:", date_mismatch.sum())


event_dates = pd.to_datetime(
    df["Data_Evento"],
    format="%d/%m/%Y",
    errors="coerce"
)

comparable = (
    protocol_dates.notna()
    & registration_dates.notna()
    & event_dates.notna()
)

print(
    "Protocol date matches Data_Evento:",
    (protocol_dates[comparable] == event_dates[comparable]).sum()
)

print(
    "Protocol date matches Data_Registro:",
    (protocol_dates[comparable] == registration_dates[comparable]).sum()
)

print(
    "Protocol date matches neither:",
    (
        (protocol_dates[comparable] != event_dates[comparable])
        & (protocol_dates[comparable] != registration_dates[comparable])
    ).sum()
)

# check subtopics
for prefix in ["DH_", "DM_", "DA_", "PEPL_", "PEPR_"]:
    columns = [c for c in df.columns if c.startswith(prefix)]

    print(f"\n--- {prefix} ({len(columns)} columns) ---")
    print(columns)

# check data availability
groups = ["DH_", "DM_", "DA_", "PEPL_", "PEPR_"]

for group in groups:
    columns = [
        c for c in df.columns
        if c.startswith(group) and not c.endswith("Descricao")
    ]

    has_data = df[columns].notna().any(axis=1)

    print(
        f"{group}: "
        f"{has_data.sum()} protocols with data "
        f"({has_data.mean():.1%})"
    )

# check diff between zero/nulls
column = "DH_MORTOS"

print("Null count:", df[column].isna().sum())
print("Zero count:", (df[column] == 0).sum())
print("Positive count:", (df[column] > 0).sum())
print("Sample values:")
print(df[column].value_counts(dropna=False).head(10))

column = "DA_Polui/cont do solo"

print("Null count:", df[column].isna().sum())
print("Zero count:", (df[column] == 0).sum())
print("Non-zero count:", (df[column].notna() & (df[column] != 0)).sum())
print("Sample values:")
print(df[column].value_counts(dropna=False).head(10))

# checking categoris for environmental columns
environmental_columns = [
    column for column in df.columns
    if column.startswith("DA_")
]

for column in environmental_columns:
    print(f"\n--- {column} ---")
    print("Null count:", df[column].isna().sum())
    print("Distinct values:", df[column].nunique())
    print("Examples:")
    print(df[column].dropna().unique()[:10])

# checking categorical columns and relationship
categorical_columns = [
    "tipologia",
    "descricao_tipologia",
    "grupo_de_desastre",
    "Status"
]

for column in categorical_columns:
    print(f"\n--- {column} ---")
    print(f"Missing values: {df[column].isna().sum()}")
    print(f"Distinct values: {df[column].nunique()}")

    print("\nMost common values:")
    print(df[column].value_counts(dropna=False).head(15))


type_mapping = (
    df.groupby("tipologia")
    .agg(
        description_count=("descricao_tipologia", "nunique"),
        group_count=("grupo_de_desastre", "nunique"),
        descriptions=("descricao_tipologia", "unique"),
        disaster_groups=("grupo_de_desastre", "unique")
    )
)

print(type_mapping.to_string())

classification_counts = (
    df.groupby(
        ["tipologia", "descricao_tipologia", "grupo_de_desastre"]
    )
    .size()
    .reset_index(name="record_count")
    .sort_values(["tipologia", "grupo_de_desastre"])
)

print(
    classification_counts[
        classification_counts["tipologia"].isin([9, 10])
    ].to_string(index=False)
)

# checking municipality relationship
municipality_mapping = (
    df.groupby(["Cod_IBGE_Mun", "Nome_Municipio", "Sigla_UF"])
    .size()
    .reset_index(name="record_count")
)

print(f"Distinct municipality/code/state combinations: {len(municipality_mapping)}")
print(f"Distinct municipality codes: {df['Cod_IBGE_Mun'].nunique()}")
print(f"Missing municipality codes: {df['Cod_IBGE_Mun'].isna().sum()}")

municipality_names_per_code = (
    df.groupby("Cod_IBGE_Mun")["Nome_Municipio"].nunique()
)

print(
    "Municipality codes associated with multiple names:",
    (municipality_names_per_code > 1).sum()
)

# lowercase/uppercase - typos
municipality_mapping = (
    df.groupby("Cod_IBGE_Mun")
    .agg(
        municipality_names=("Nome_Municipio", "unique"),
        states=("Sigla_UF", "unique"),
        name_count=("Nome_Municipio", "nunique"),
        state_count=("Sigla_UF", "nunique"),
        record_count=("Protocolo_S2iD", "size")
    )
)

inconsistent_municipalities = municipality_mapping[
    (municipality_mapping["name_count"] > 1)
    | (municipality_mapping["state_count"] > 1)
]

print(inconsistent_municipalities.to_string())

# Identify numeric columns
numeric_columns = df.select_dtypes(include="number").columns

# Summarize negative values
negative_counts = (
    df[numeric_columns]
    .lt(0)
    .sum()
    .sort_values(ascending=False)
)

print("Columns containing negative values:")
print(negative_counts[negative_counts > 0].to_string())

# Identify categorical/text columns
text_columns = df.select_dtypes(include=["object", "string"]).columns

for column in text_columns:
    values = df[column].dropna().astype(str)

    # Leading/trailing whitespace
    whitespace_count = (
        values != values.str.strip()
    ).sum()

    # Values differing only by capitalization
    case_variants = (
        values.groupby(values.str.strip().str.casefold())
        .nunique()
    )

    case_variant_groups = case_variants[case_variants > 1]

    if whitespace_count > 0 or len(case_variant_groups) > 0:
        print(f"\n--- {column} ---")
        print("Values with surrounding whitespace:", whitespace_count)
        print("Groups differing by capitalization:", len(case_variant_groups))

        if len(case_variant_groups) > 0:
            print("Examples:")
            for normalized_value in case_variant_groups.index[:5]:
                variants = values[
                    values.str.strip().str.casefold() == normalized_value
                ].unique()[:10]
                print(f"  {variants}")


# checking descriptions with white spaces only
description_columns = [
    column for column in df.columns
    if column.endswith("_Descricao")
]

for column in description_columns:
    values = df[column].dropna().astype(str)
    whitespace_only = values.str.strip().eq("")

    print(
        f"{column}: "
        f"{whitespace_only.sum()} whitespace-only values"
    )