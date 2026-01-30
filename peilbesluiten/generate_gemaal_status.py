#!/usr/bin/env python3
"""
Generate Gemaal Status Summary
==============================

This script fetches real-time data for all pumping stations (gemalen)
and generates a summary JSON file for the frontend Digital Twin visualization.

It uses the Hydronet Water Control Room API.

API Update Frequentie:
---------------------
De Hydronet Water Control Room API levert data met 30-minuten intervallen.
Nieuwe datapunten verschijnen op :19 en :49 minuten van elk uur.

Aanbevolen cron schedule:
    # Elke 15 minuten (optimaal)
    */15 * * * * cd /path/to/peilbesluiten && python3 generate_gemaal_status.py

    # Of elke 30 minuten (minimaal)
    */30 * * * * cd /path/to/peilbesluiten && python3 generate_gemaal_status.py

Vaker pollen dan elke 15 minuten is niet zinvol omdat de brondata niet vaker update.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
import sys

import duckdb

# Import the fetcher class
from fetch_hydronet_gemaal_data import HydronetGemaalDataFetcher, CHART_ID
from sliding_window_processor import process_gemaal_series

# Configuration
OUTPUT_FILE = Path("../web/public/data/gemaal_status_latest.json")
GEOJSON_FILE = Path("rijnland_kaartlagen/Gemaal/Gemaal_layer0.geojson")
DB_FILE = Path("db/rijnland.db")
LOG_DIR = Path("logs")

# Setup logging
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def validate_gemaal_data(gemaal_code: str, debiet: float, timestamp_ms: int) -> tuple[bool, str]:
    """
    Valideer dat gemaaldata realistisch is (CCG richtlijn - data kwaliteit).
    
    Returns:
        (bool, str): (is_valide, foutmelding)
    """
    # Check 1: Realistic range
    if debiet < 0:
        return False, f"Negatief debiet: {debiet}"
    if debiet > 1000:  # Onrealistisch hoog voor dit type gemaal
        return False, f"Debiet te hoog: {debiet} m³/s"
    
    # Check 2: Timestamp freshness
    if timestamp_ms > 0:
        timestamp = datetime.fromtimestamp(timestamp_ms / 1000)
        age = datetime.now() - timestamp
        
        # We zijn nu coulant met de leeftijd (24 uur i.p.v. 2 uur) 
        # omdat sommige stations minder vaak updaten maar de status 'aan' nog wel klopt.
        if age.total_seconds() > 3600 * 24:  
            return False, f"Data te oud: {age.total_seconds()/3600:.1f} uur"
        
        if age.total_seconds() < -3600: # Meer dan een uur in de toekomst
            return False, f"Data in de toekomst: {age.total_seconds()/3600:.1f} uur"
            
    return True, ""

def get_gemaal_codes(fetcher):
    """
    Haal lijst met gemaalcodes op.
    Probeert eerst DuckDB, valt terug op GeoJSON.
    """
    # 1. Probeer DuckDB
    if DB_FILE.exists():
        try:
            logger.info(f"Connecting to DuckDB: {DB_FILE}")
            con = duckdb.connect(str(DB_FILE))
            
            # Check if Gemaal table exists
            tables = con.execute("SHOW TABLES").fetchall()
            table_names = [t[0] for t in tables]
            
            if 'Gemaal' in table_names:
                result = con.execute("SELECT CODE FROM Gemaal WHERE CODE IS NOT NULL").fetchall()
                codes = [r[0] for r in result if r[0]]
                logger.info(f"Loaded {len(codes)} pumping stations from DuckDB")
                con.close()
                return codes
            else:
                logger.warning("Table 'Gemaal' not found in DuckDB")
                con.close()
        except Exception as e:
            logger.error(f"Error reading from DuckDB: {e}")
    
    # 2. Fallback naar GeoJSON
    if GEOJSON_FILE.exists():
        logger.info(f"Falling back to GeoJSON: {GEOJSON_FILE}")
        return fetcher.load_gemaal_codes_from_geojson(str(GEOJSON_FILE))
    else:
        logger.error(f"GeoJSON file not found: {GEOJSON_FILE}")
        return []

def main():
    logger.info("Starting Digital Twin Data Generation...")
    
    # Initialize fetcher
    # We use a temp directory for the individual files, we only care about the summary
    temp_dir = Path("temp_data")
    temp_dir.mkdir(exist_ok=True)
    fetcher = HydronetGemaalDataFetcher(CHART_ID, temp_dir)
    
    # 1. Load all gemalen codes
    codes = get_gemaal_codes(fetcher)
    
    if not codes:
        logger.error("No pumping station codes found!")
        sys.exit(1)
        
    logger.info(f"Found {len(codes)} pumping stations to process")
    
    # 2. Fetch data for all gemalen
    timestamp = datetime.now()
    summary_data = {
        "generated_at": timestamp.isoformat(),
        "total_stations": len(codes),
        "active_stations": 0,
        "total_debiet_m3s": 0.0,
        "stations": {}
    }
    
    active_count = 0
    total_debiet = 0.0
    
    # Limit for testing/dev to avoid spamming the API too much if needed
    # codes = codes[:5] 
    
    for i, code in enumerate(codes, 1):
        print(f"[{i}/{len(codes)}] Fetching {code}...", end="\r")
        
        try:
            data = fetcher.fetch_gemaal_data(code)
            
            if data and 'series' in data and len(data['series']) > 0:
                # Get the series data for sliding window processing
                series = data['series'][0]
                if 'data' in series and len(series['data']) > 0:
                    series_data = series['data']
                    last_point = series_data[-1]
                    
                    debiet = last_point.get('value', 0)
                    status = last_point.get('status', 'uit')
                    
                    # Data validatie (CCG richtlijn)
                    is_valide, fout = validate_gemaal_data(code, debiet, last_point.get('timestamp_ms', 0))
                    if not is_valide:
                        logger.warning(f"Validatie gefaald voor {code}: {fout}")
                        summary_data["stations"][code] = {"status": "error", "error": fout}
                        continue
                    
                    # Process with sliding windows (30 min, 1 hour, 3 hours)
                    windowed_data = process_gemaal_series(
                        code, 
                        series_data, 
                        windows_minutes=[30, 60, 180]
                    )
                    
                    # Update summary stats
                    if status == 'aan':
                        active_count += 1
                        total_debiet += debiet
                    
                    # Build station data with sliding window metrics
                    station_data = {
                        "status": status,
                        "debiet": round(debiet, 3),
                        "timestamp": last_point.get('timestamp'),
                        "last_update": datetime.fromtimestamp(last_point.get('timestamp_ms', 0)/1000).isoformat(),
                        # Sliding window metrics
                        "trends": {
                            "30_min": windowed_data['windows'].get('30_min', {}).get('trend'),
                            "60_min": windowed_data['windows'].get('60_min', {}).get('trend'),
                            "180_min": windowed_data['windows'].get('180_min', {}).get('trend')
                        },
                        "window_stats": {
                            "30_min": windowed_data['windows'].get('30_min', {}).get('stats'),
                            "60_min": windowed_data['windows'].get('60_min', {}).get('stats'),
                            "180_min": windowed_data['windows'].get('180_min', {}).get('stats')
                        },
                        "summary": windowed_data['summary']
                    }
                    
                    summary_data["stations"][code] = station_data
                else:
                    summary_data["stations"][code] = {"status": "unknown", "error": "No data points"}
            else:
                summary_data["stations"][code] = {"status": "unknown", "error": "No series data"}
                
        except Exception as e:
            logger.error(f"Error fetching {code}: {e}")
            summary_data["stations"][code] = {"status": "error", "error": str(e)}
            
        # Rate limiting
        time.sleep(0.2)
        
    print("") # Newline after progress
    
    # 3. Finalize summary
    summary_data["active_stations"] = active_count
    summary_data["total_debiet_m3s"] = round(total_debiet, 3)
    
    # 4. Save to frontend public folder
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2)
        
    # 5. Calculate aggregate trends
    aggregate_trends = {
        "30_min": {"increasing": 0, "decreasing": 0, "stable": 0},
        "60_min": {"increasing": 0, "decreasing": 0, "stable": 0},
        "180_min": {"increasing": 0, "decreasing": 0, "stable": 0}
    }
    
    for station_data in summary_data["stations"].values():
        if "trends" in station_data:
            for window_key in ["30_min", "60_min", "180_min"]:
                trend = station_data["trends"].get(window_key)
                if trend and "direction" in trend:
                    direction = trend["direction"]
                    if direction in aggregate_trends[window_key]:
                        aggregate_trends[window_key][direction] += 1
    
    summary_data["aggregate_trends"] = aggregate_trends
    
    logger.info("="*50)
    logger.info(f"Digital Twin Status Generated")
    logger.info(f"Active Stations: {active_count}/{len(codes)}")
    logger.info(f"Total Flow: {total_debiet:.3f} m3/s")
    logger.info(f"Saved to: {OUTPUT_FILE}")
    logger.info("")
    logger.info("Aggregate Trends (30 min window):")
    logger.info(f"  Increasing: {aggregate_trends['30_min']['increasing']}")
    logger.info(f"  Decreasing: {aggregate_trends['30_min']['decreasing']}")
    logger.info(f"  Stable: {aggregate_trends['30_min']['stable']}")
    logger.info("="*50)

if __name__ == "__main__":
    main()
