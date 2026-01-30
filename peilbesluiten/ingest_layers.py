#!/usr/bin/env python3
"""
Ingest gedownloade GeoJSON kaartlagen in DuckDB.
"""

import duckdb
import os
import logging
from pathlib import Path
import time

# Configuratie
DB_PATH = Path("db/rijnland.db")
LAYERS_DIR = Path("rijnland_kaartlagen")
LOG_DIR = Path("logs")

# Setup logging
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

import json

def setup_database(con):
    """Installeer en laad benodigde extensies."""
    logger.info("Setting up database extensions...")
    con.execute("INSTALL spatial;")
    con.execute("LOAD spatial;")
    logger.info("Spatial extension loaded.")

def ensure_valid_geojson(file_path):
    """
    Check of GeoJSON valid is voor DuckDB/GDAL.
    ArcGIS export gebruikt soms 'attributes' ipv 'properties' en mist 'type': 'Feature'.
    Geeft pad naar (eventueel tijdelijk) valid bestand terug.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if 'features' not in data:
            return False, file_path
            
        features = data['features']
        if not features:
            return True, file_path
            
        # Check eerste feature
        first_feature = features[0]
        needs_fix = False
        
        if 'attributes' in first_feature and 'properties' not in first_feature:
            needs_fix = True
        if 'type' not in first_feature:
            needs_fix = True
            
        if needs_fix:
            logger.info(f"  - Fixing ArcGIS JSON format for {file_path.name}...")
            new_features = []
            for feat in features:
                # Fix Geometry
                raw_geom = feat.get('geometry', {})
                new_geom = raw_geom
                
                if raw_geom:
                    if 'x' in raw_geom and 'y' in raw_geom:
                        new_geom = {'type': 'Point', 'coordinates': [raw_geom['x'], raw_geom['y']]}
                    elif 'paths' in raw_geom:
                        new_geom = {'type': 'MultiLineString', 'coordinates': raw_geom['paths']}
                    elif 'rings' in raw_geom:
                        # Naive conversion: treat all rings as one Polygon
                        # This works for simple polygons (1 ring) and polygons with holes
                        # Might fall short for MultiPolygons (multiple outer rings), but often sufficient
                        new_geom = {'type': 'Polygon', 'coordinates': raw_geom['rings']}
                
                new_feat = {
                    'type': 'Feature',
                    'geometry': new_geom,
                    'properties': feat.get('attributes', feat.get('properties', {}))
                }
                new_features.append(new_feat)
            
            data['features'] = new_features
            
            # Save to temp file in same dir
            temp_path = file_path.with_suffix('.temp.geojson')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
            return True, temp_path
            
        return True, file_path
        
    except Exception as e:
        logger.error(f"Error checking GeoJSON {file_path}: {e}")
        return False, file_path

def get_table_name(filename):
    """Bepaal tabelnaam op basis van bestandsnaam."""
    # Voorbeeld: Gemaal_layer0.geojson -> Gemaal
    # Voorbeeld: Afsluitmiddel_layer0.geojson -> Afsluitmiddel
    stem = filename.stem
    if "_layer" in stem:
        return stem.split("_layer")[0]
    return stem

def ingest_layers():
    """Zoek en importeer alle GeoJSON bestanden."""
    if not LAYERS_DIR.exists():
        logger.error(f"Layers directory not found: {LAYERS_DIR}")
        return

    # Maak DB directory
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(DB_PATH))
    try:
        setup_database(con)

        geojson_files = list(LAYERS_DIR.rglob("*.geojson"))
        logger.info(f"Found {len(geojson_files)} GeoJSON files to ingest.")

        for file_path in geojson_files:
            file_path_str = str(file_path)
            table_name = get_table_name(file_path)
            
            logger.info(f"Ingesting {file_path.name} into table '{table_name}'...")
            
            # Check and repair GeoJSON if needed (ArcGIS format vs Standard GeoJSON)
            is_valid, fixed_path = ensure_valid_geojson(file_path)
            if not is_valid:
                logger.warning(f"  ⚠ Skipping {file_path.name}: Invalid format")
                continue
                
            try:
                # Use fixed path for ingestion
                file_path_str = str(fixed_path)
                
                # Gebruik ST_Read om GeoJSON te lezen
                query = f"""
                CREATE OR REPLACE TABLE '{table_name}' AS 
                SELECT * FROM ST_Read('{file_path_str}');
                """
                con.execute(query)
                
                # Count rows
                count = con.execute(f"SELECT count(*) FROM '{table_name}'").fetchone()[0]
                logger.info(f"  ✓ Loaded {count} rows into '{table_name}'")
                
                # Cleanup temp file if created
                if fixed_path != file_path:
                    fixed_path.unlink()
                
            except Exception as e:
                logger.error(f"  ✗ Failed to ingest {file_path.name}: {e}")

        # Summary
        tables = con.execute("SHOW TABLES").fetchall()
        logger.info(f"\nTotal tables in database: {len(tables)}")
        for table in tables:
            t_name = table[0]
            count = con.execute(f"SELECT count(*) FROM '{t_name}'").fetchone()[0]
            logger.info(f"  - {t_name}: {count} rows")

    finally:
        con.close()
        logger.info("Database connection closed.")

if __name__ == "__main__":
    ingest_layers()
