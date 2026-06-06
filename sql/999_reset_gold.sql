-- Run as superuser: psql -U postgres
-- Creates the database and grants ownership to the applicati

DROP TABLE IF EXISTS gold.region_dim CASCADE;
DROP TABLE IF EXISTS gold.sector_dim CASCADE;
DROP TABLE IF EXISTS gold.year_dim CASCADE;
DROP TABLE IF EXISTS gold.emission_factors CASCADE;
