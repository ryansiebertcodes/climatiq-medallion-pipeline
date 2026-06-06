-- Run against climatiq_pipeline: psql -U ryansiebert -d climatiq_pipeline
-- Creates the silver schema with typed columns extracted from bronze JSONB.

CREATE SCHEMA IF NOT EXISTS gold;

--Dimensions
CREATE TABLE IF NOT EXISTS gold.region_dim (
    region_dim_id      SERIAL PRIMARY KEY,
    region_code        TEXT UNIQUE,
    country_name       TEXT,
    source_system_key  TEXT,
    source_system_code TEXT,
    created            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    modified           TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS gold.sector_dim (
    sector_dim_id      SERIAL PRIMARY KEY,
    sector_name        TEXT UNIQUE,
    source_system_key  TEXT,
    source_system_code TEXT,
    created            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    modified           TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS gold.year_dim (
    year_dim_id        SERIAL PRIMARY KEY,
    year               INTEGER UNIQUE,
    source_system_key  TEXT,
    source_system_code TEXT,
    created            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    modified           TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);


--Facts
CREATE TABLE IF NOT EXISTS gold.emission_factors_fact (
    emission_factors_fact_id   SERIAL PRIMARY KEY,
    region_dim_id              INTEGER REFERENCES gold.region_dim(region_dim_id),
    sector_dim_id              INTEGER REFERENCES gold.sector_dim(sector_dim_id),
    year_dim_id                INTEGER REFERENCES gold.year_dim(year_dim_id),
    emission_factor_name       TEXT,
    co2e                       NUMERIC(36, 18),
    co2e_unit                  TEXT,
    activity_value             NUMERIC(36, 18),
    activity_unit              TEXT,
    source_system_key          TEXT UNIQUE,
    source_system_code         TEXT,
    created                    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    modified                   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
