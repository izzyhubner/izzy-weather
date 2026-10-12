# Data Quality and Cleaning Rules

## 1. Sources

### Disaster dataset
- Dataset: Atlas Digital de Desastres, Brazil
- Raw file: `BD_Atlas_1991_2025_v1.1_2026.08.06_Consolidado.csv`
- S3 location: `s3://izzy-weather/raw/atlasdigital/`

### Municipality reference dataset
- Source: Brazilian Institute of Geography and Statistics (IBGE)
- Raw file: `RELATORIO_DTB_BRASIL_MUNICIPIO.xls`
- Local directory: `data/raw/ibge/`
- S3 location: `s3://izzy-weather/raw/ibge/`
- Purpose: provide official municipality codes and names for standardizing municipality information.

The raw source files must remain unchanged.

## 2. Approved transformations

### 2.1 Municipality names

Use the IBGE municipality reference table to standardize municipality names.

- Join the disaster dataset to the IBGE reference table using `Cod_IBGE_Mun` and the corresponding IBGE municipality code.
- Preserve the original disaster-source municipality name in `Nome_Municipio_raw`.
- Populate `Nome_Municipio` using the official name from the IBGE reference table.
- Use the current reference-table names consistently throughout the curated dataset.
- Normalize `Sigla_UF` to uppercase (e.g., `pa` → `PA`).
- Do not manually correct municipality names using string replacements when an authoritative reference is available.
- Do not infer a municipality name from its spelling or from another column.

#### Municipality matching and validation
- Confirm that municipality codes are compatible in type and format before joining.
- Ensure that the IBGE reference table has no duplicate municipality codes that would multiply disaster records during the join.
- Identify disaster records whose municipality codes do not match the reference table.
- Preserve unmatched records and flag them for investigation; do not silently delete them or guess their municipality names.
- Validate that the join does not unexpectedly change the number of disaster records.
- Record the IBGE reference-table edition or publication year used.

Note: official municipality names can change over time. This project uses the selected IBGE reference edition consistently; it does not attempt to reconstruct historical municipality names for each disaster date.

### 2.2 State abbreviations
- Convert `Sigla_UF` values to uppercase.
- Example: `pa` → `PA`.

### 2.3 Description fields
Convert whitespace-only values to null in:
- `DH_Descricao`
- `DM_Descricao`
- `DA_Descricao`
- `PEPL_Descricao`
- `PEPR_Descricao`

Preserve meaningful descriptions exactly as recorded, including their capitalization and surrounding whitespace.

### 2.4 Dates
- Parse `Data_Evento` and `Data_Registro` as dates.
- Preserve the original date values in the raw source.
- Do not delete records solely because `Data_Evento` is later than `Data_Registro`.
- Do not replace either date using the date embedded in `Protocolo_S2iD`.
- Keep unresolved date anomalies for investigation.

## 3. Record preservation
- Do not delete records solely because they contain data quality anomalies.
- Do not remove duplicates until their meaning and appropriate handling are established.
- Do not replace missing numeric values with zero without a documented justification.
- Preserve the raw source data for traceability.

## 4. Validation
Validate the curated output for:
- Expected schema and data types.
- Unexpected nulls and invalid dates.
- Correct application of approved transformations.
- Municipality-code matching rates.
- Duplicate municipality codes in the reference table.
- Unexpected increases or decreases in record counts after the municipality join.
- Unmatched municipality codes and other unresolved anomalies.

## 5. Output
- Format: Parquet.
- S3 destination: `s3://izzy-weather/curated/atlasdigital/`
- The curated dataset must be reproducible from the raw sources using the documented rules.
- The reference-table edition and unresolved data quality issues must be documented.