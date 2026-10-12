# Brazil Disaster Data Engineering Pipeline

An end-to-end data engineering portfolio project built using Brazil's Atlas Digital de Desastres dataset.

## Project Overview

This project processes disaster records from Brazil's Atlas Digital de Desastres to build a curated dataset and an analytical data model. It focuses on data quality, reliable transformations, dimensional modeling, and automated validation.

## Architecture

The pipeline is organized into the following layers:

- **Raw:** Original source files.
- **Curated:** Cleaned and standardized disaster records, enriched with official municipality names from IBGE.
- **Analytical:** Dimensional model designed for analysis and reporting.

### Analytical Model

The analytical layer follows a star schema:

- `fact_disasters`: Disaster records and impact measures.
- `dim_municipality`: Municipality attributes and geographic information.
- `dim_disaster_type`: Disaster classification based on COBRADE codes.
- `dim_date`: Calendar attributes for event and registration dates.

## Technologies

- Python
- Pandas
- Parquet
- Pytest
- Git and GitHub
- Amazon S3

## Data Quality and Validation

The pipeline includes checks for:

- Unique and non-null primary keys.
- Foreign key consistency between facts and dimensions.
- Preservation of source record counts.
- Date-key consistency.
- Municipality reference matching against IBGE data.

Automated tests are implemented with Pytest.

## Project Structure

```text
data/
  src/          # Data transformation and analytical modeling
docs/           # Data quality documentation
exploration/    # Data profiling and validation scripts
scripts/        # Data upload scripts
tests/          # Automated tests
```

Raw and processed datasets are excluded from version control.

## Current Status

- [x] Curated dataset built and validated.
- [x] Analytical dimensional model implemented.
- [x] Automated tests created.
- [x] Project published on GitHub.
- [ ] Continuous integration with GitHub Actions.
- [ ] Analytical dashboard.

## Goals

Demonstrate practical data engineering skills through reproducible transformations, data quality controls, dimensional modeling, testing, and cloud storage integration.