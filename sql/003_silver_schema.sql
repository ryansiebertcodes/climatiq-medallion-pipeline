-- Run against climatiq_pipeline: psql -U ryansiebert -d climatiq_pipeline
-- Creates the silver schema with typed columns extracted from bronze JSONB.

CREATE SCHEMA IF NOT EXISTS silver;

/* Normalized region lookup enriched with full country names.
   Placed in Silver (not Gold) because it is a stable reference dataset
   shared across multiple Silver tables; enrichment is a Silver-layer
   responsibility. */
CREATE TABLE IF NOT EXISTS silver.regions (
    region_code  TEXT PRIMARY KEY,
    country_name TEXT
);

CREATE TABLE IF NOT EXISTS silver.emission_factors (
    id          TEXT PRIMARY KEY,
    activity_id TEXT,
    name        TEXT,
    sector      TEXT,
    category    TEXT,
    source      TEXT,
    region      TEXT,
    year        INTEGER,
    unit_type   TEXT,
    unit        TEXT,
    factor      NUMERIC(36, 18),
    created     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    modified    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS silver.estimates (
    id                   TEXT PRIMARY KEY,  -- from emission_factor.id
    activity_id          TEXT,              -- from emission_factor.activity_id
    emission_factor_name TEXT,              -- from emission_factor.name
    region               TEXT,              -- from emission_factor.region
    year                 INTEGER,           -- from emission_factor.year
    source               TEXT,              -- from emission_factor.source
    co2e                 NUMERIC(36, 18),   -- from co2e
    co2e_unit            TEXT,              -- from co2e_unit
    activity_value       NUMERIC(36, 18),   -- from activity_data.activity_value
    activity_unit        TEXT,              -- from activity_data.activity_unit
    created     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),    
    modified    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
