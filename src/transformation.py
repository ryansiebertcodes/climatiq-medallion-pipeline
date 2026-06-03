import os
import psycopg2
from datetime import datetime, timezone
import json
from db import get_connection


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
    transform_emission_factors(conn)
    transform_estimates(conn)
    conn.close()
