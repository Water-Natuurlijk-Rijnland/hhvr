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

# Import the fetcher class
from fetch_hydronet_gemaal_data import HydronetGemaalDataFetcher, CHART_ID

# Configuration
OUTPUT_FILE = Path("../simulatie-peilbeheer/public/data/gemaal_status_latest.json")
GEOJSON_FILE = Path("rijnland_kaartlagen/Gemaal/Gemaal_layer0.geojson")
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

def main():
    logger.info("Starting Digital Twin Data Generation...")
    
    # Initialize fetcher
    # We use a temp directory for the individual files, we only care about the summary
    temp_dir = Path("temp_data")
    temp_dir.mkdir(exist_ok=True)
    fetcher = HydronetGemaalDataFetcher(CHART_ID, temp_dir)
    
    # 1. Load all gemalen from GeoJSON
    if not GEOJSON_FILE.exists():
        logger.error(f"GeoJSON file not found: {GEOJSON_FILE}")
        sys.exit(1)
        
    codes = fetcher.load_gemaal_codes_from_geojson(str(GEOJSON_FILE))
    logger.info(f"Found {len(codes)} pumping stations in GeoJSON")
    
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
                # Get the latest data point
                series = data['series'][0]
                if 'data' in series and len(series['data']) > 0:
                    last_point = series['data'][-1]
                    
                    debiet = last_point.get('value', 0)
                    status = last_point.get('status', 'uit')
                    
                    # Update summary stats
                    if status == 'aan':
                        active_count += 1
                        total_debiet += debiet
                    
                    summary_data["stations"][code] = {
                        "status": status,
                        "debiet": round(debiet, 3),
                        "timestamp": last_point.get('timestamp'),
                        "last_update": datetime.fromtimestamp(last_point.get('timestamp_ms', 0)/1000).isoformat()
                    }
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
        
    logger.info("="*50)
    logger.info(f"Digital Twin Status Generated")
    logger.info(f"Active Stations: {active_count}/{len(codes)}")
    logger.info(f"Total Flow: {total_debiet:.3f} m3/s")
    logger.info(f"Saved to: {OUTPUT_FILE}")
    logger.info("="*50)

if __name__ == "__main__":
    main()
