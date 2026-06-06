# Climatiq Medallion ETL Pipeline

A production-style data engineering pipeline implementing the **Bronze → Silver → Gold** medallion architecture, ingesting carbon emission factor data from the [Climatiq API](https://www.climatiq.io/) into PostgreSQL.

## Architecture

```
Climatiq API
     │
     ▼
Bronze Layer  →  Raw API responses stored as JSONB (truncate-reload)
     │
     ▼
Silver Layer  →  Typed columns extracted from JSONB, duplicates removed
     │
     ▼
Gold Layer    →  Aggregations and metrics (in progress)
     │
     ▼
Streamlit Dashboard  (planned)
```

## Tech Stack

- **Python 3.12** — extraction, transformation, loading
- **PostgreSQL 18** (Postgres.app) — data warehouse
- **Climatiq API** — emission factor data source

## Project Structure

```
src/
├── extraction.py       # Bronze: fetch from Climatiq API
├── transformation.py   # Silver: extract JSONB into typed columns
├── loading.py          # Bronze: insert raw data into PostgreSQL
└── db.py               # Shared database connection
sql/
├── 001_create_database.sql
├── 002_bronze_schema.sql
├── 003_silver_schema.sql
├── 999_reset_bronze.sql
└── 999_reset_silver.sql
docs/
└── Climatiq.postman_collection.json
```

## Setup

**Prerequisites:** Python 3.12, Postgres.app running locally

```bash
# Install dependencies
make install

# Create database and schemas
make db-setup
make db-migrate-silver
```

Create a `.env` file in the project root:
```
CLIMATIQ_API_KEY=your_key_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=climatiq_pipeline
DB_USER=your_os_username
DB_PASS=
```

## Running the Pipeline

```bash
# Full Bronze extraction (fetches from Climatiq API, loads into PostgreSQL)
make run

# Silver transformation (promotes JSONB to typed columns)
make transform
```

## Data Quality Notes

- **Bronze** is a truncate-reload layer — raw data is replaced on each run, preserving source fidelity in JSONB
- **Silver** deduplicates on `emission_factor.id` — records without a valid ID or with duplicate IDs are excluded via `ON CONFLICT (id) DO NOTHING`
- In testing, 100 Bronze estimate records reduced to 98 in Silver due to 3 records sharing the same `emission_factor.id` (API duplicate) and 2 records with null IDs
- **Region enrichment** uses `pycountry` to map ISO alpha-2 codes to full country names. Sub-national codes (e.g. `CA-BC`) fall back to the parent country (`Canada`). Climatiq-specific regional aggregations (`ROW_WF`, `ROW_WE`, `ROW_WM`) represent "Rest of World" groupings with no ISO equivalent and are stored as `"Unknown"`

## PostgreSQL Schema

Each medallion layer lives in its own schema:

| Schema | Table | Description |
|--------|-------|-------------|
| `bronze` | `emission_factors` | Raw emission factor JSON from `/data/v1/search` |
| `bronze` | `estimates` | Raw CO2e estimate JSON from `/data/v1/estimate/batch` |
| `silver` | `emission_factors` | Typed, deduplicated emission factors |
| `silver` | `estimates` | Typed, deduplicated CO2e estimates |
