#!/usr/bin/env python3
"""
Download alleen de Gemaal kaartlaag van de Rijnland ArcGIS Server.
"""

import json
import requests
import os
import time
import logging
from pathlib import Path
from datetime import datetime

# Configuratie
ARCGIS_BASE_URL = "https://rijnland.enl-mcs.nl/arcgis/rest/services"
OUTPUT_DIR = "rijnland_kaartlagen"
MAX_FEATURES_PER_QUERY = 1000
TIMEOUT = 60

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_layer():
    service_path = "Gemaal/MapServer"
    layer_id = 0
    layer_name = "Gemaal"
    
    # URL construction
    base = ARCGIS_BASE_URL.rstrip('/') + '/'
    query_url = f"{base}{service_path}/{layer_id}/query"
    
    logger.info(f"Downloaden Gemaal layer van: {query_url}")
    
    all_features = []
    offset = 0
    has_more = True
    
    while has_more:
        params = {
            'where': '1=1',
            'outFields': '*',
            'f': 'geojson',
            'returnGeometry': 'true',
            'resultOffset': offset,
            'resultRecordCount': MAX_FEATURES_PER_QUERY
        }
        
        try:
            response = requests.get(query_url, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            if 'features' in data:
                features = data['features']
                all_features.extend(features)
                
                if len(features) < MAX_FEATURES_PER_QUERY:
                    has_more = False
                else:
                    offset += len(features)
                    logger.info(f"  {len(all_features)} features gedownload...")
                    time.sleep(0.5)
            elif 'error' in data:
                logger.error(f"  ArcGIS fout: {data['error']}")
                return False
            else:
                has_more = False
                
        except Exception as e:
            logger.error(f"Error requesting data: {e}")
            return False

    # Save to file
    output_path = Path(OUTPUT_DIR) / "Gemaal" / "Gemaal_layer0.geojson"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    geojson = {
        'type': 'FeatureCollection',
        'features': all_features,
        'metadata': {
            'service': service_path,
            'layer_id': layer_id,
            'layer_name': layer_name,
            'feature_count': len(all_features),
            'download_date': datetime.now().isoformat()
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2)
        
    logger.info(f"✓ {len(all_features)} gemalen opgeslagen in {output_path}")
    return True

if __name__ == "__main__":
    download_layer()
