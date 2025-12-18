#!/usr/bin/env python3
"""
Update dynamische waterdata van Rijnland
Download en update alleen datasets die regelmatig worden bijgewerkt (peilen, meetlocaties, etc.)
"""

import json
import requests
import os
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
import hashlib

# Configuratie
ARCGIS_BASE_URL = "https://rijnland.enl-mcs.nl/arcgis/rest/services"
OUTPUT_DIR = "rijnland_kaartlagen"
LOG_DIR = "logs"
REQUEST_DELAY = 0.5
MAX_RETRIES = 3
TIMEOUT = 60

# Dynamische datasets (worden regelmatig bijgewerkt)
DYNAMISCHE_DATASETS = [
    {
        'name': 'Peilenkaart_praktijk',
        'service': 'Peilenkaart_praktijk/MapServer',
        'layer_id': 0,
        'description': 'Actuele peilen in de praktijk',
        'update_frequency': 'daily'  # Geschat: dagelijks
    },
    {
        'name': 'Peilafwijking_praktijk',
        'service': 'Peilafwijking_praktijk/MapServer',
        'layer_id': 0,
        'description': 'Afwijkingen van vastgestelde peilen',
        'update_frequency': 'daily'
    },
    {
        'name': 'Peilgebied_praktijk_soort_gebied',
        'service': 'Peilgebied_praktijk_soort_gebied/MapServer',
        'layer_id': 0,
        'description': 'Peilgebieden volgens praktijksituatie',
        'update_frequency': 'weekly'
    },
    {
        'name': 'Meetlocatie_waterkwantiteit',
        'service': 'Meetlocatie_waterkwantiteit/MapServer',
        'layer_id': 0,
        'description': 'Locaties waar waterkwantiteit wordt gemeten',
        'update_frequency': 'daily'
    },
    {
        'name': 'Meetlocatie_waterkwaliteit',
        'service': 'Meetlocatie_waterkwaltiteit/MapServer',
        'layer_id': 0,
        'description': 'Locaties waar waterkwaliteit wordt gemeten',
        'update_frequency': 'weekly'
    },
    {
        'name': 'TransportleidingMeetpunt',
        'service': 'TransportleidingMeetpunt/MapServer',
        'layer_id': 0,
        'description': 'Meetpunten op transportleidingen',
        'update_frequency': 'daily'
    }
]

# Setup logging
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, f"update_dynamische_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DynamicDataUpdater:
    """Klasse voor het updaten van dynamische waterdata"""
    
    def __init__(self, base_url: str, output_dir: str):
        self.base_url = base_url.rstrip('/') + '/'
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.stats = {
            'datasets_checked': 0,
            'datasets_updated': 0,
            'datasets_unchanged': 0,
            'datasets_failed': 0,
            'total_features_downloaded': 0
        }
    
    def sanitize_filename(self, name: str) -> str:
        """Maak een veilige bestandsnaam"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        return name.strip(' .')
    
    def make_request(self, url: str, params: Dict = None, retries: int = MAX_RETRIES) -> Optional[Dict]:
        """Maak HTTP request met retry mechanisme"""
        if params is None:
            params = {}
        
        params['f'] = 'json'
        
        for attempt in range(retries):
            try:
                response = requests.get(url, params=params, timeout=TIMEOUT)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request fout bij {url}: {e} (poging {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode fout bij {url}: {e}")
                return None
        
        return None
    
    def get_data_hash(self, data: Dict) -> str:
        """Genereer hash van data om te checken of er wijzigingen zijn"""
        # Gebruik LAST_EDITED_DATE en feature count voor snelle vergelijking
        features = data.get('features', [])
        if not features:
            return ""
        
        # Haal laatste edit datum op uit eerste feature
        last_edit = None
        if features:
            attrs = features[0].get('attributes', {})
            last_edit = attrs.get('LAST_EDITED_DATE') or attrs.get('DATUMINWINNING')
        
        hash_data = {
            'count': len(features),
            'last_edit': last_edit,
            'sample_id': features[0].get('attributes', {}).get('OBJECTID') if features else None
        }
        
        return hashlib.md5(json.dumps(hash_data, sort_keys=True).encode()).hexdigest()
    
    def get_existing_hash(self, file_path: Path) -> Optional[str]:
        """Haal hash op van bestaand bestand"""
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            features = data.get('features', [])
            if not features:
                return ""
            
            # Haal laatste edit datum op
            last_edit = None
            if features:
                attrs = features[0].get('attributes', {})
                last_edit = attrs.get('LAST_EDITED_DATE') or attrs.get('DATUMINWINNING')
            
            hash_data = {
                'count': len(features),
                'last_edit': last_edit,
                'sample_id': features[0].get('attributes', {}).get('OBJECTID') if features else None
            }
            
            return hashlib.md5(json.dumps(hash_data, sort_keys=True).encode()).hexdigest()
        except Exception as e:
            logger.warning(f"Kon hash niet lezen van {file_path}: {e}")
            return None
    
    def download_features(self, service_path: str, layer_id: int, max_features: int = None) -> Optional[Dict]:
        """Download alle features van een layer"""
        query_url = f"{self.base_url}{service_path}/{layer_id}/query"
        
        all_features = []
        offset = 0
        has_more = True
        MAX_FEATURES_PER_QUERY = 1000
        
        while has_more:
            params = {
                'where': '1=1',
                'outFields': '*',
                'f': 'geojson',
                'returnGeometry': 'true',
                'resultOffset': offset,
                'resultRecordCount': MAX_FEATURES_PER_QUERY
            }
            
            data = self.make_request(query_url, params)
            
            if not data:
                return None
            
            if 'features' in data:
                features = data['features']
                all_features.extend(features)
                
                # Stop als we max_features hebben bereikt (voor testen)
                if max_features and len(all_features) >= max_features:
                    all_features = all_features[:max_features]
                    has_more = False
                elif len(features) < MAX_FEATURES_PER_QUERY:
                    has_more = False
                else:
                    offset += len(features)
                    logger.debug(f"    {len(all_features)} features gedownload...")
                    time.sleep(REQUEST_DELAY)
            elif 'error' in data:
                logger.error(f"    ArcGIS fout: {data['error']}")
                return None
            else:
                has_more = False
        
        return {
            'type': 'FeatureCollection',
            'features': all_features
        }
    
    def update_dataset(self, dataset: Dict) -> bool:
        """Update een dynamische dataset"""
        service_name = self.sanitize_filename(dataset['name'])
        service_path = dataset['service']
        layer_id = dataset['layer_id']
        description = dataset.get('description', '')
        
        logger.info(f"\n[{dataset.get('update_frequency', 'unknown')}] {service_name}")
        logger.info(f"  {description}")
        
        # Bepaal output bestand
        layer_info = self.make_request(f"{self.base_url}{service_path}")
        if not layer_info or 'layers' not in layer_info:
            logger.error(f"  Kon layer info niet ophalen")
            return False
        
        layer_name = None
        for layer in layer_info.get('layers', []):
            if layer['id'] == layer_id:
                layer_name = layer.get('name', f"Layer_{layer_id}")
                break
        
        if not layer_name:
            logger.error(f"  Layer {layer_id} niet gevonden")
            return False
        
        layer_name_safe = self.sanitize_filename(layer_name)
        output_file = self.output_dir / service_name / f"{layer_name_safe}_layer{layer_id}.geojson"
        
        # Download nieuwe data
        logger.info(f"  Downloaden...")
        new_data = self.download_features(service_path, layer_id)
        
        if not new_data or not new_data.get('features'):
            logger.warning(f"  Geen data gevonden")
            self.stats['datasets_failed'] += 1
            return False
        
        # Check of data is veranderd
        new_hash = self.get_data_hash(new_data)
        existing_hash = self.get_existing_hash(output_file)
        
        if new_hash == existing_hash and existing_hash is not None:
            logger.info(f"  ✓ Geen wijzigingen (hash: {new_hash[:8]}...)")
            self.stats['datasets_unchanged'] += 1
            return False
        
        # Data is veranderd, sla op
        logger.info(f"  ⚡ Data bijgewerkt! ({len(new_data['features'])} features)")
        logger.info(f"  Oude hash: {existing_hash[:8] if existing_hash else 'geen'}...")
        logger.info(f"  Nieuwe hash: {new_hash[:8]}...")
        
        # Voeg metadata toe
        geojson = {
            'type': 'FeatureCollection',
            'features': new_data['features'],
            'metadata': {
                'service': service_path,
                'layer_id': layer_id,
                'layer_name': layer_name,
                'feature_count': len(new_data['features']),
                'update_date': datetime.now().isoformat(),
                'source': self.base_url,
                'description': description,
                'update_frequency': dataset.get('update_frequency', 'unknown'),
                'data_hash': new_hash
            }
        }
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, ensure_ascii=False, indent=2)
        
        self.stats['datasets_updated'] += 1
        self.stats['total_features_downloaded'] += len(new_data['features'])
        
        return True
    
    def run(self, datasets: List[Dict] = None):
        """Voer update uit voor alle dynamische datasets"""
        if datasets is None:
            datasets = DYNAMISCHE_DATASETS
        
        logger.info("=" * 70)
        logger.info("Rijnland Dynamische Data Updater")
        logger.info("=" * 70)
        logger.info(f"Output directory: {self.output_dir.absolute()}")
        logger.info(f"Log file: {log_file}")
        logger.info(f"Aantal datasets: {len(datasets)}")
        logger.info("")
        
        start_time = time.time()
        
        for dataset in datasets:
            self.stats['datasets_checked'] += 1
            try:
                self.update_dataset(dataset)
            except Exception as e:
                logger.error(f"Fout bij updaten {dataset['name']}: {e}")
                self.stats['datasets_failed'] += 1
            
            time.sleep(REQUEST_DELAY)
        
        elapsed_time = time.time() - start_time
        
        # Print samenvatting
        self.print_summary(elapsed_time)
    
    def print_summary(self, elapsed_time: float):
        """Print samenvatting van de update"""
        logger.info("\n" + "=" * 70)
        logger.info("SAMENVATTING")
        logger.info("=" * 70)
        logger.info(f"Datasets gecontroleerd: {self.stats['datasets_checked']}")
        logger.info(f"Datasets bijgewerkt: {self.stats['datasets_updated']}")
        logger.info(f"Datasets ongewijzigd: {self.stats['datasets_unchanged']}")
        logger.info(f"Datasets gefaald: {self.stats['datasets_failed']}")
        logger.info(f"Totaal features gedownload: {self.stats['total_features_downloaded']:,}")
        logger.info(f"Tijd: {elapsed_time:.1f} seconden ({elapsed_time/60:.1f} minuten)")
        logger.info("=" * 70)

def main():
    """Hoofdfunctie"""
    import sys
    
    # Optionele command line argumenten
    dataset_filter = None
    if len(sys.argv) > 1:
        dataset_filter = sys.argv[1]
        logger.info(f"Filter: alleen '{dataset_filter}' updaten")
    
    updater = DynamicDataUpdater(
        base_url=ARCGIS_BASE_URL,
        output_dir=OUTPUT_DIR
    )
    
    datasets_to_update = DYNAMISCHE_DATASETS
    if dataset_filter:
        datasets_to_update = [d for d in DYNAMISCHE_DATASETS if dataset_filter.lower() in d['name'].lower()]
        if not datasets_to_update:
            logger.error(f"Geen datasets gevonden met filter '{dataset_filter}'")
            return
    
    try:
        updater.run(datasets_to_update)
    except KeyboardInterrupt:
        logger.warning("\n\nUpdate onderbroken door gebruiker")
        updater.print_summary(0)
    except Exception as e:
        logger.error(f"Onverwachte fout: {e}", exc_info=True)

if __name__ == "__main__":
    main()





