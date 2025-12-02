#!/usr/bin/env python3
"""
Import peilbesluiten GeoJSON data into PostgreSQL database
"""

import json
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import sys
import os

# Database connection parameters
DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'peilbeheer'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

def convert_timestamp(timestamp_ms):
    """Convert milliseconds timestamp to datetime"""
    if timestamp_ms:
        return datetime.fromtimestamp(timestamp_ms / 1000)
    return None

def import_geojson(geojson_file, conn):
    """Import GeoJSON data into PostgreSQL"""

    with open(geojson_file, 'r') as f:
        data = json.load(f)

    features = data.get('features', [])
    print(f"Found {len(features)} features to import")

    cursor = conn.cursor()

    # Prepare data for batch insert
    values = []
    for feature in features:
        props = feature['properties']
        geom = feature['geometry']

        # Convert geometry to WKT for PostGIS
        geom_json = json.dumps(geom)

        values.append((
            props.get('OBJECTID'),
            props.get('WS_PBNAAM'),
            props.get('WS_GPNAAM'),
            props.get('WS_INFO'),
            convert_timestamp(props.get('WS_DTM_GOED')),
            props.get('GLOBALID'),
            geom_json
        ))

    # Batch insert with ON CONFLICT to handle duplicates
    insert_query = """
        INSERT INTO peilbesluiten.peilbesluiten
        (objectid, ws_pbnaam, ws_gpnaam, ws_info, ws_dtm_goed, globalid, geometry)
        VALUES %s
        ON CONFLICT (objectid)
        DO UPDATE SET
            ws_pbnaam = EXCLUDED.ws_pbnaam,
            ws_gpnaam = EXCLUDED.ws_gpnaam,
            ws_info = EXCLUDED.ws_info,
            ws_dtm_goed = EXCLUDED.ws_dtm_goed,
            globalid = EXCLUDED.globalid,
            geometry = EXCLUDED.geometry,
            updated_at = CURRENT_TIMESTAMP
    """

    template = """(
        %s, %s, %s, %s, %s, %s,
        ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
    )"""

    execute_values(cursor, insert_query, values, template=template, page_size=100)

    conn.commit()
    print(f"Successfully imported {len(values)} peilbesluiten")

    # Show statistics
    cursor.execute("SELECT COUNT(*) FROM peilbesluiten.peilbesluiten")
    total = cursor.fetchone()[0]
    print(f"Total peilbesluiten in database: {total}")

    cursor.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: python import.py <geojson_file>")
        print("Example: python import.py data/peilbesluiten_hdsr.geojson")
        sys.exit(1)

    geojson_file = sys.argv[1]

    if not os.path.exists(geojson_file):
        print(f"Error: File {geojson_file} not found")
        sys.exit(1)

    print(f"Connecting to PostgreSQL database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("Connected successfully")

        import_geojson(geojson_file, conn)

        conn.close()
        print("Import completed successfully")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
