import os
import psycopg2
from datetime import datetime, timezone
import json
from db import get_connection
import pycountry


# Region is country id in this dataset
def get_enriched_country_name(region):
    country = pycountry.countries.get(alpha_2=region)
    if country:
        return country.name
    parent_code = region.split("-")[0]
    parent = pycountry.countries.get(alpha_2=parent_code)
    return parent.name if parent else "Unknown"
    
# Normalized region lookup enriched with full country names via pycountry.                                                                          
# Placed in Silver (not Gold) because it is a stable reference dataset used                                                                         
# by multiple Silver tables, and enrichment is a Silver-layer responsibility.  
def transform_regions(conn):
      # Populate silver.regions by pulling distinct region codes from bronze
      # and enriching with full country names via pycountry.
      # We call pycountry once per unique code rather than once per row —
      # avoids redundant lookups across thousands of emission factor records.
      cur = conn.cursor()
      cur.execute("""
          SELECT DISTINCT raw_data->>'region'
          FROM bronze.emission_factors
          WHERE raw_data->>'region' IS NOT NULL;
      """)
      regions = cur.fetchall()

      for (region_code,) in regions:
          country_name = get_enriched_country_name(region_code)
          cur.execute(
              """INSERT INTO silver.regions (region_code, country_name)
                 VALUES (%s, %s)
                 ON CONFLICT (region_code) DO NOTHING;""",
              (region_code, country_name),
          )

      conn.commit()
      cur.close()


def transform_emission_factors(conn):
    sql = """
        INSERT INTO silver.emission_factors (
            id,
            activity_id,
            name,
            sector,
            category,
            source,
            region,
            year,
            unit_type,
            unit,
            factor
        )
        SELECT
            raw_data->>'id',
            raw_data->>'activity_id',
            raw_data->>'name',
            raw_data->>'sector',
            raw_data->>'category',
            raw_data->>'source',
            raw_data->>'region',
            (raw_data->>'year')::INTEGER,
            raw_data->>'unit_type',
            raw_data->>'unit',
            (raw_data->>'factor')::NUMERIC
        FROM bronze.emission_factors
        ON CONFLICT (id) DO NOTHING;
    """
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()

def transform_estimates(conn):
    sql = """
        INSERT INTO silver.estimates (
            id,
            activity_id,
            emission_factor_name,
            region,
            year,
            source,
            co2e,
            co2e_unit,
            activity_value,
            activity_unit
        )
        SELECT
            raw_data->'emission_factor'->>'id',
            raw_data->'emission_factor'->>'activity_id',
            raw_data->'emission_factor'->>'name',
            raw_data->'emission_factor'->>'region',
            (raw_data->'emission_factor'->>'year')::INTEGER,
            raw_data->'emission_factor'->>'source',
            (raw_data->>'co2e')::NUMERIC,
            raw_data->>'co2e_unit',
            (raw_data->'activity_data'->>'activity_value')::NUMERIC,
            raw_data->'activity_data'->>'activity_unit'
        FROM bronze.estimates
        ON CONFLICT (id) DO NOTHING;
    """
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()

if __name__ == "__main__":
    conn = get_connection()
    transform_regions(conn)
    transform_emission_factors(conn)
    transform_estimates(conn)
    conn.close()
