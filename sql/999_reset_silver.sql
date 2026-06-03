-- Run as superuser: psql -U postgres
-- Drops all the tables in the silver schema

DROP TABLE IF EXISTS silver.emission_factors CASCADE;
DROP TABLE IF EXISTS silver.estimates CASCADE;
