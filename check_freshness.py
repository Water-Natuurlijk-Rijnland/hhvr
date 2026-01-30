#!/usr/bin/env python3
"""
Diagnostic script to check data freshness for all pumping stations.
"""
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.realtime.fetch_hydronet import HydronetGemaalDataFetcher, CHART_ID

# Config
GEOJSON_FILE = Path("data/kaartlagen/Gemaal/Gemaal_layer0.geojson")
OUTPUT_FILE = Path("data_freshness_report.json")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Data Freshness Diagnosis...")
    
    fetcher = HydronetGemaalDataFetcher(CHART_ID, Path("temp_dia"))
    
    if not GEOJSON_FILE.exists():
        logger.error(f"GeoJSON not found: {GEOJSON_FILE}")
        return

    codes = fetcher.load_gemaal_codes_from_geojson(str(GEOJSON_FILE))
    logger.info(f"Found {len(codes)} stations to check.")
    
    # We'll check a sample or all? Let's check first 20 to be fast, or all if user wants deep dive.
    # Let's check 50 for a good representative sample.
    sample_codes = codes # codes[:50] 
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_checked": 0,
        "summary": {
            "fresh_lt_2h": 0,
            "stale_lt_24h": 0,
            "stale_gt_24h": 0,
            "no_data": 0,
            "error": 0
        },
        "details": []
    }
    
    print(f"Checking {len(sample_codes)} stations...")
    
    for i, code in enumerate(sample_codes):
        print(f"[{i+1}/{len(sample_codes)}] Checking {code}...", end="\r")
        
        try:
            data = fetcher.fetch_gemaal_data(code)
            
            status = "no_data"
            age_hours = -1
            
            if data and 'series' in data and len(data['series']) > 0:
                series = data['series'][0]
                if 'data' in series and len(series['data']) > 0:
                    last_point = series['data'][-1]
                    timestamp_ms = last_point.get('timestamp_ms', 0)
                    if timestamp_ms > 0:
                        ts = datetime.fromtimestamp(timestamp_ms / 1000)
                        age = datetime.now() - ts
                        age_hours = age.total_seconds() / 3600
                        
                        if age_hours < 2:
                            status = "fresh_lt_2h"
                        elif age_hours < 24:
                            status = "stale_lt_24h"
                        else:
                            status = "stale_gt_24h"
            
            results["summary"][status] += 1
            results["details"].append({
                "code": code,
                "status": status,
                "age_hours": round(age_hours, 1)
            })
            
        except Exception as e:
            results["summary"]["error"] += 1
        
        time.sleep(0.1)
        
    print("\n\nDiagnosis Complete.")
    print(json.dumps(results["summary"], indent=2))
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Full report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
