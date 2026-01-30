#!/usr/bin/env python3
"""
Haal historische data (laatste 24u+) op voor gemalen en sla op in DuckDB.
"""

import duckdb
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Import fetcher
from fetch_hydronet_gemaal_data import HydronetGemaalDataFetcher, CHART_ID

# Config
DB_FILE = Path("db/rijnland.db")
LOG_DIR = Path("logs")
# Correct path for frontend proxy data
# script is in peilbesluiten/, web is in ../web/
# vite config looks in ../data/realtime relative to web/ -> peilbeheer/data/realtime
# so from here it is ../data/realtime
EXPORT_DIR = Path("../data/realtime")

# Setup logging
LOG_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def init_db(con):
    """Maak metingen tabel aan."""
    con.execute("""
    CREATE TABLE IF NOT EXISTS Gemaal_Metingen (
        gemaal_code VARCHAR,
        timestamp TIMESTAMP,
        waarde DOUBLE,
        status VARCHAR,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (gemaal_code, timestamp)
    );
    """)

def get_codes(con):
    """Haal alle gemaal codes op."""
    # Check if table exists
    tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]
    if 'Gemaal' not in tables:
        logger.error("Gemaal table not found in DuckDB!")
        return []
        
    return [r[0] for r in con.execute("SELECT CODE FROM Gemaal WHERE CODE IS NOT NULL").fetchall()]

def main():
    if not DB_FILE.exists():
        logger.error(f"Database {DB_FILE} not found")
        sys.exit(1)
        
    con = duckdb.connect(str(DB_FILE))
    init_db(con)
    
    codes = get_codes(con)
    if not codes:
        logger.error("No pumping stations found")
        sys.exit(1)
        
    logger.info(f"Found {len(codes)} pumping stations")
    
    # Initialize fetcher with export dir
    fetcher = HydronetGemaalDataFetcher(CHART_ID, EXPORT_DIR)
    
    # Calculate cutoff time (24 hours ago)
    cutoff_time = datetime.now() - timedelta(hours=24)
    logger.info(f"Filtering DB insert since {cutoff_time.isoformat()}")
    
    total_inserted = 0
    
    for i, code in enumerate(codes, 1):
        try:
            logger.info(f"[{i}/{len(codes)}] Fetching {code}...")
            data = fetcher.fetch_gemaal_data(code)
            
            if not data or 'series' not in data:
                logger.warning(f"  No data for {code}")
                continue

            # Save JSON for frontend proxy (Real-time update)
            # This allows the charts to show the data immediately
            fetcher.save_data(data, code, datetime.now())
                
            # Prepare rows for DB
            rows = []
            for series in data.get('series', []):
                for point in series.get('data', []):
                    # Parse timestamp from ISO string or timestamp_ms
                    ts_str = point.get('timestamp')
                    ts = datetime.fromisoformat(ts_str)
                    
                    # Filter last 24h
                    if ts >= cutoff_time:
                        val = point.get('value', 0.0)
                        status = point.get('status', 'uit')
                        rows.append((code, ts, val, status))
            
            if rows:
                # Bulk insert
                # DuckDB python execute writes many rows efficiently
                con.executemany(
                    "INSERT OR IGNORE INTO Gemaal_Metingen (gemaal_code, timestamp, waarde, status) VALUES (?, ?, ?, ?)",
                    rows
                )
                count = len(rows)
                total_inserted += count
                logger.info(f"  ✓ Inserted {count} rows")
            
        except Exception as e:
            logger.error(f"Error processing {code}: {e}")
            
    logger.info("=" * 50)
    logger.info(f"Total rows inserted: {total_inserted}")
    
    # Verification
    count = con.execute("SELECT count(*) FROM Gemaal_Metingen").fetchone()[0]
    logger.info(f"Total count in Gemaal_Metingen: {count}")
    
    con.close()

if __name__ == "__main__":
    main()
