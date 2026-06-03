# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a data engineering portfolio project implementing a **Medallion Architecture ETL pipeline** (Bronze → Silver → Gold layers). The goal is to demonstrate production-ready data engineering skills including pipeline design, data quality checks, and a live dashboard.

**Tech stack:** Python, PostgreSQL, Streamlit
**Data source:** Public dataset (e.g., Kaggle: stock prices, NYC taxi, or Amazon reviews)

## Intended Architecture

```
Bronze layer  →  Raw data ingestion (as-is from source API/file)
Silver layer  →  Cleaning, deduplication, type casting
Gold layer    →  Business-ready aggregations and metrics
Dashboard     →  Streamlit app reading from Gold layer in PostgreSQL
```

## Planned Directory Structure

```
src/
├── extraction.py       # Bronze: ingest from source
├── transformation.py   # Silver + Gold: cleaning and aggregations
└── loading.py          # Load layers into PostgreSQL
data/
└── sample_data.csv     # Local sample for development/testing
notebooks/
└── exploratory_analysis.ipynb
tests/
└── test_transformations.py
architecture_diagram.png
```

## Data Quality Requirements

Every pipeline stage must include:
- Validation checks (null checks, type enforcement, range checks)
- Error logging with counts of rejected/accepted records
- Handling strategy for bad data (quarantine or skip with logging)

## PostgreSQL Schema Convention

Each medallion layer should live in its own schema: `bronze`, `silver`, `gold`. Tables are named `<schema>.<dataset_name>`.
