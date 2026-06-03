import os
import psycopg2
from datetime import datetime, timezone
import json


def get_connection():
    try:
        conn = psycopg2.connect(
            database=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASS"],
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
        )
        print("Connection established successfully!")
        return conn

    except Exception as e:
        print("Connection failed! Error=", {e})
        return None


def load_emission_factors(conn, factors):
    insert_query = "INSERT INTO bronze.emission_factors ( sector, raw_data, fetched_at ) VALUES ( %s, %s, %s ) ON CONFLICT (id) DO NOTHING;"
    for f in factors:
        try:
            cur = conn.cursor()
            cur.execute(
                insert_query,
                (
                    f.get("sector"),
                    json.dumps(f),
                    datetime.now(timezone.utc),
                ),
            )
            print("Loading emission factors successful!")

        except Exception as e:
            print("Loading emission factors failed: ", {e})
            conn.rollback()

    conn.commit()
    cur.close()

    return None


def load_estimates(conn, factors):
    insert_query = "INSERT INTO bronze.estimates (  activity_id, raw_data, fetched_at ) VALUES ( %s, %s, %s ) ON CONFLICT (id) DO NOTHING;"
    for f in factors:
        try:
            cur = conn.cursor()
            cur.execute(
                insert_query,
                (
                    f.get("emission_factor", {}).get("activity_id"), 
                    json.dumps(f), 
                    datetime.now(timezone.utc)),
            )
            print("Loading estimates successful!")

        except Exception as e:
            print("Loading estimates failed: ", {e})
            conn.rollback()

    conn.commit()
    cur.close()

    return None
