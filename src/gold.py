import os
import psycopg2
from datetime import datetime, timezone
import json
from db import get_connection
import pycountry

SOURCE_SYSTEM_CODE = "climatiq"


 # 1. load_sector_dim(conn) — SELECT DISTINCT sector FROM silver.emission_factors
 # 2. load_region_dim(conn) — SELECT region_code, country_name FROM silver.regions
  #3. load_year_dim(conn) — SELECT DISTINCT year FROM silver.emission_factors
  #3. load_year_dim(conn) — SELECT DISTINCT year FROM silver.emission_factors
  #4. load_emissions_fact(conn) — the main aggregation joining all three dims
    
 
def load_sector_dim(conn):
    sql = """
        INSERT INTO gold.sector_dim (
            sector_name,
            source_system_key,
            source_system_code
        )
        SELECT DISTINCT
            sector,
            CONCAT(%s, '.', sector),
            %s
        FROM silver.emission_factors
        ON CONFLICT (sector_name) DO NOTHING;
    """
    cur = conn.cursor()
    cur.execute(sql, (SOURCE_SYSTEM_CODE, SOURCE_SYSTEM_CODE))
    conn.commit()
    cur.close()

def load_year_dim(conn):
    sql = """
        INSERT INTO gold.year_dim (
            year,
            source_system_key,
            source_system_code
        )
        SELECT DISTINCT
            year,
            CONCAT(%s, '.', year::TEXT),
            %s
        FROM silver.emission_factors
        WHERE year IS NOT NULL
        ON CONFLICT (year) DO NOTHING;
    """
    cur = conn.cursor()
    cur.execute(sql, (SOURCE_SYSTEM_CODE, SOURCE_SYSTEM_CODE))
    conn.commit()
    cur.close()


def load_region_dim(conn):
    sql = """
        INSERT INTO gold.region_dim (
            region_code,
            country_name,
            source_system_key,
            source_system_code
        )
        SELECT
            region_code,
            country_name,
            CONCAT(%s, '.', region_code),
            %s
        FROM silver.regions
        ON CONFLICT (region_code) DO NOTHING;
    """
    cur = conn.cursor()
    cur.execute(sql, (SOURCE_SYSTEM_CODE, SOURCE_SYSTEM_CODE))
    conn.commit()
    cur.close()


def load_emissions_fact(conn):
    sql = """
        INSERT INTO gold.emission_factors_fact (
            region_dim_id,
            sector_dim_id,
            year_dim_id,
            emission_factor_name,
            co2e,
            co2e_unit,
            activity_value,
            activity_unit,
            source_system_key,
            source_system_code
        )
        SELECT
            r.region_dim_id,
            s.sector_dim_id,
            y.year_dim_id,
            ef.name,
            e.co2e,
            e.co2e_unit,
            e.activity_value,
            e.activity_unit,
            CONCAT(%s, '.', e.id),
            %s
        FROM silver.estimates e
        JOIN silver.emission_factors ef ON e.id = ef.id
        JOIN gold.region_dim r  ON e.region  = r.region_code
        JOIN gold.sector_dim s  ON ef.sector = s.sector_name
        JOIN gold.year_dim y    ON e.year    = y.year
        ON CONFLICT (source_system_key) DO NOTHING;
    """
    cur = conn.cursor()
    cur.execute(sql, (SOURCE_SYSTEM_CODE, SOURCE_SYSTEM_CODE))
    conn.commit()
    cur.close()


if __name__ == "__main__":
    conn = get_connection()
    load_region_dim(conn)
    load_year_dim(conn)
    load_sector_dim(conn)
    load_emissions_fact(conn)
    conn.close()
