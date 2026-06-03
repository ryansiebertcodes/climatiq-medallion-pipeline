-- Run against climatiq_pipeline: psql -U ryansiebert -d climatiq_pipeline
-- Creates the bronze schema for raw API responses.

CREATE SCHEMA IF NOT EXISTS bronze;

-- Raw emission factor records from /data/v1/search, one row per factor
CREATE TABLE IF NOT EXISTS bronze.emission_factors (
    id          SERIAL PRIMARY KEY,
    sector      TEXT,
    raw_data    JSONB        NOT NULL,
    fetched_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Raw batch estimate results from /data/v1/estimate/batch, one row per estimate
CREATE TABLE IF NOT EXISTS bronze.estimates (
    id          SERIAL PRIMARY KEY,
    activity_id TEXT,
    raw_data    JSONB        NOT NULL,
    fetched_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
