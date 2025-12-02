#!/usr/bin/env python3
"""
Import Rijnland peilgebieden GeoJSON data into PostgreSQL database
"""

import json
import psycopg2
from psycopg2.extras import execute_values
import sys
import os

# Database connection parameters
DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'peilbeheer'),
    'user': os.getenv('POSTGRES_USER', os.getenv('USER', 'postgres')),
    'password': os.getenv('POSTGRES_PASSWORD', ''),
    'host': os.getenv('POSTGRES_HOST', '127.0.0.1'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

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
            props.get('ORACLE_OBJECTID'),
            props.get('CODE'),
            props.get('NAAM'),
            props.get('STATUSOBJECT'),
            props.get('SOORTPEILGEBIED'),
            props.get('SOORTAFWATERING'),
            props.get('PEILBEHERENDEINSTANTIE'),
            props.get('PEILINDEXERING'),
            props.get('JAARTALHUIDIGPEIL'),
            props.get('JAARTALVOLGENDEWIJZIGING'),
            props.get('EINDZOMERPEIL'),
            props.get('EINDWINTERPEIL'),
            props.get('VORIGZOMERPEIL'),
            props.get('VORIGWINTERPEIL'),
            props.get('OPPERVLAKTE'),
            props.get('OMTREK'),
            props.get('OPMERKING'),
            props.get('HYPERLINK'),
            props.get('SOORTPEILBEHEER'),
            props.get('VASTPEIL'),
            props.get('ZOMERPEIL'),
            props.get('WINTERPEIL'),
            props.get('FLEXZOMERPEILONDERGRENS'),
            props.get('FLEXZOMERPEILBOVENGRENS'),
            props.get('FLEXWINTERPEILONDERGRENS'),
            props.get('FLEXWINTERPEILBOVENGRENS'),
            props.get('ZOMERPEILTEKST'),
            props.get('WINTERPEILTEKST'),
            props.get('VERLENGDTOT'),
            geom_json
        ))

    # Batch insert with ON CONFLICT to handle duplicates
    insert_query = """
        INSERT INTO peilbesluiten.peilgebieden_rijnland
        (oracle_objectid, code, naam, statusobject, soortpeilgebied, soortafwatering,
         peilbeherendeinstantie, peilindexering, jaartalhuidigpeil, jaartalvolgendewijziging,
         eindzomerpeil, eindwinterpeil, vorigzomerpeil, vorigwinterpeil, oppervlakte,
         omtrek, opmerking, hyperlink, soortpeilbeheer, vastpeil, zomerpeil, winterpeil,
         flexzomerpeilondergrens, flexzomerpeilbovengrens, flexwinterpeilondergrens,
         flexwinterpeilbovengrens, zomerpeiltekst, winterpeiltekst, verlengdtot, geometry)
        VALUES %s
        ON CONFLICT (code)
        DO UPDATE SET
            naam = EXCLUDED.naam,
            statusobject = EXCLUDED.statusobject,
            soortpeilgebied = EXCLUDED.soortpeilgebied,
            soortafwatering = EXCLUDED.soortafwatering,
            zomerpeil = EXCLUDED.zomerpeil,
            winterpeil = EXCLUDED.winterpeil,
            oppervlakte = EXCLUDED.oppervlakte,
            hyperlink = EXCLUDED.hyperlink,
            geometry = EXCLUDED.geometry,
            updated_at = CURRENT_TIMESTAMP
    """

    template = """(
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s,
        ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
    )"""

    execute_values(cursor, insert_query, values, template=template, page_size=100)

    conn.commit()
    print(f"Successfully imported {len(values)} peilgebieden")

    # Show statistics
    cursor.execute("SELECT COUNT(*) FROM peilbesluiten.peilgebieden_rijnland")
    total = cursor.fetchone()[0]
    print(f"Total peilgebieden in database: {total}")

    cursor.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: python import_rijnland.py <geojson_file>")
        print("Example: python import_rijnland.py data/peilgebieden_rijnland.geojson")
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
