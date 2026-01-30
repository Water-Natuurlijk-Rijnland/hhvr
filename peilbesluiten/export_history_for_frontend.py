#!/usr/bin/env python3
"""
Export gemaal data from DuckDB to JSON files compatible with Rijnland Dashboard Proxy.
"""

import duckdb
import json
import logging
from pathlib import Path
from datetime import datetime

# Config
DB_FILE = Path("db/rijnland.db")
OUTPUT_DIR = Path("../data/realtime")  # Vite proxy expects data here (relative to where script runs?)
# Vite config says: resolve(__dirname, '..', 'data', 'realtime')
# If script runs in peilbesluiten, and web is next to it...
# peilbeheer/
#   peilbesluiten/ (cwd)
#   web/ (vite config here)
#   data/ (target)
# 
# Vite config is in web/, so .. is peilbeheer/
# So data/realtime is peilbeheer/data/realtime
# 
# From peilbesluiten/, we want to reach peilbeheer/data/realtime
# so ../data/realtime seems correct.

OUTPUT_DIR = Path("../data/realtime")
CHART_ID = "e743fb87-2a02-4f3e-ac6c-03d03401aab8"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    if not DB_FILE.exists():
        logger.error(f"DB not found at {DB_FILE}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    con = duckdb.connect(str(DB_FILE))
    
    # Check tables
    tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]
    if 'Gemaal_Metingen' not in tables:
        logger.error("Gemaal_Metingen table not found")
        con.close()
        return

    # Get all codes
    codes = [r[0] for r in con.execute("SELECT DISTINCT gemaal_code FROM Gemaal_Metingen").fetchall()]
    logger.info(f"Exporting data for {len(codes)} stations...")
    
    for code in codes:
        # Fetch last 24h data ordered by time
        query = """
        SELECT timestamp, waarde 
        FROM Gemaal_Metingen 
        WHERE gemaal_code = ? 
        ORDER BY timestamp ASC
        """
        rows = con.execute(query, [code]).fetchall()
        
        if not rows:
            continue
            
        # Format for frontend proxy
        # Structure: {"data": {"series": [{"name": "Debiet", "data": [{"x": ms, "y": val}, ...]}]}}
        # But wait, vite config expects:
        # savedData.data.series[0].data[].timestamp (ISO) or timestamp_ms
        # Let's match what fetch_hydronet_gemaal_data.py saves.
        
        # Hydronet fetcher saves:
        # {
        #   'timestamp': ...,
        #   'data': {
        #      'series': [ { 'data': [ {'timestamp': ISO, 'timestamp_ms': ms, 'value': val }, ... ] } ]
        #   }
        # }
        
        series_data = []
        for ts, val in rows:
            # ts is datetime
            ts_ms = int(ts.timestamp() * 1000)
            series_data.append({
                'timestamp': ts.isoformat(),
                'timestamp_ms': ts_ms,
                'value': val,
                'status': 'aan' if val > 0.001 else 'uit'
            })
            
        final_data = {
            'timestamp': datetime.now().isoformat(),
            'feature_identifier': code,
            'chart_id': CHART_ID,
            'data': {
                'feature_identifier': code,
                'series': [{
                    'name': 'Debiet',
                    'type': 'line',
                    'data': series_data
                }]
            }
        }
        
        # Write to file
        # Filename format: gemaal_{code}_{timestamp}.json
        # Timestamp format in proxy match: 
        # But proxy looks for `files = readdirSync...` and `gemaalFiles.sort().reverse()`
        # So we just need a filename that sorts correctly as "newest"
        
        # We should remove old files for this gemaal to avoid clutter?
        # The proxy logic sorts and takes [0].
        
        now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"gemaal_{code}_{now_str}.json"
        
        with open(OUTPUT_DIR / filename, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2)
            
    logger.info("Export complete.")
    con.close()

if __name__ == "__main__":
    main()
