#!/usr/bin/env python3
"""
Download alle kaartlagen met objecten van de Rijnland ArcGIS Server
en sla ze op als GeoJSON bestanden in een aparte map.

Features:
- Automatische detectie van alle services en layers
- Paginering voor grote datasets (>1000 features)
- Resume functionaliteit (skip reeds gedownloade bestanden)
- Uitgebreide logging naar bestand
- Progress tracking en statistieken
- Error handling en retry mechanisme
"""

import json
import requests
import os
import time
import logging
from urllib.parse import urljoin
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Configuratie
ARCGIS_BASE_URL = "https://rijnland.enl-mcs.nl/arcgis/rest/services"
OUTPUT_DIR = "rijnland_kaartlagen"
LOG_DIR = "logs"
MAX_FEATURES_PER_QUERY = 1000  # ArcGIS limiet
REQUEST_DELAY = 0.5  # Seconden tussen requests
MAX_RETRIES = 3  # Aantal retries bij fouten
TIMEOUT = 60  # Timeout voor requests in seconden
RESUME = True  # Skip reeds gedownloade bestanden

# Setup logging
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, f"download_rijnland_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ArcGISDownloader:
    """Klasse voor het downloaden van ArcGIS kaartlagen"""
    
    def __init__(self, base_url: str, output_dir: str, resume: bool = True):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.resume = resume
        self.stats = {
            'services_found': 0,
            'services_processed': 0,
            'layers_found': 0,
            'layers_downloaded': 0,
            'layers_skipped': 0,
            'layers_failed': 0,
            'total_features': 0,
            'errors': []
        }
        self.downloaded_files = set()
        
        # Laad lijst van reeds gedownloade bestanden als resume enabled is
        if self.resume:
            self._load_downloaded_files()
    
    def _load_downloaded_files(self):
        """Laad lijst van reeds gedownloade bestanden"""
        if not self.output_dir.exists():
            return
        
        for geojson_file in self.output_dir.rglob("*.geojson"):
            self.downloaded_files.add(str(geojson_file))
        logger.info(f"Resume modus: {len(self.downloaded_files)} bestanden gevonden")
    
    def sanitize_filename(self, name: str) -> str:
        """Maak een veilige bestandsnaam"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        # Verwijder trailing spaces en dots (Windows probleem)
        name = name.strip(' .')
        return name
    
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
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout bij {url} (poging {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request fout bij {url}: {e} (poging {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode fout bij {url}: {e}")
                return None
        
        return None
    
    def get_services(self, folder: Optional[str] = None) -> Tuple[List[Dict], List[str]]:
        """Haal alle services op van de ArcGIS server"""
        base = self.base_url.rstrip('/') + '/'
        if folder:
            path = folder.lstrip('/') + '/'
            url = base + path
        else:
            url = base
        
        data = self.make_request(url)
        if not data:
            return [], []
        
        services = []
        folders = []
        
        # Check voor folders
        if 'folders' in data:
            folders.extend([f for f in data['folders'] if f])
        
        # Check voor services
        if 'services' in data:
            for service in data['services']:
                if service.get('type') in ['MapServer', 'FeatureServer']:
                    service_name = service['name']
                    service_path = service_name
                    if folder:
                        service_path = f"{folder}/{service_name}"
                    services.append({
                        'name': service_name,
                        'type': service['type'],
                        'path': service_path
                    })
        
        return services, folders
    
    def get_all_services(self) -> List[Dict]:
        """Haal recursief alle services op"""
        all_services = []
        folders_to_process = [None]  # Start met root
        
        logger.info("Services ophalen van ArcGIS server...")
        
        while folders_to_process:
            folder = folders_to_process.pop(0)
            services, folders = self.get_services(folder)
            all_services.extend(services)
            
            # Voeg nieuwe folders toe
            for f in folders:
                folder_path = f"{folder}/{f}" if folder else f
                folders_to_process.append(folder_path)
            
            time.sleep(REQUEST_DELAY)
        
        self.stats['services_found'] = len(all_services)
        logger.info(f"{len(all_services)} services gevonden")
        return all_services
    
    def get_layers(self, service_path: str) -> List[Dict]:
        """Haal alle layers op van een service"""
        # Zorg dat base_url eindigt met / en service_path niet begint met /
        base = self.base_url.rstrip('/') + '/'
        path = service_path.lstrip('/')
        url = base + path
        
        data = self.make_request(url)
        if not data:
            return []
        
        layers = []
        if 'layers' in data:
            for layer in data['layers']:
                # Alleen layers met geometrie
                if layer.get('geometryType'):
                    layers.append({
                        'id': layer['id'],
                        'name': layer.get('name', f"Layer_{layer['id']}"),
                        'geometryType': layer.get('geometryType'),
                        'service_path': service_path
                    })
        
        return layers
    
    def download_features(self, service_path: str, layer_id: int, layer_name: str, 
                         output_file: Path) -> int:
        """Download alle features van een layer met paginering"""
        base = self.base_url.rstrip('/') + '/'
        path = service_path.lstrip('/')
        query_url = f"{base}{path}/{layer_id}/query"
        
        all_features = []
        offset = 0
        has_more = True
        
        logger.info(f"  Downloaden layer {layer_id}: {layer_name}...")
        
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
                logger.error(f"    Kon geen data ophalen voor layer {layer_id}")
                break
            
            if 'features' in data:
                features = data['features']
                all_features.extend(features)
                
                # Check of er meer features zijn
                if len(features) < MAX_FEATURES_PER_QUERY:
                    has_more = False
                else:
                    offset += len(features)
                    logger.info(f"    {len(all_features)} features gedownload...")
                    time.sleep(REQUEST_DELAY)
            elif 'error' in data:
                logger.error(f"    ArcGIS fout: {data['error']}")
                has_more = False
            else:
                has_more = False
        
        # Sla op als GeoJSON
        if all_features:
            geojson = {
                'type': 'FeatureCollection',
                'features': all_features,
                'metadata': {
                    'service': service_path,
                    'layer_id': layer_id,
                    'layer_name': layer_name,
                    'feature_count': len(all_features),
                    'download_date': datetime.now().isoformat(),
                    'source': self.base_url
                }
            }
            
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(geojson, f, ensure_ascii=False, indent=2)
            
            logger.info(f"    ✓ {len(all_features)} features opgeslagen in {output_file.name}")
            return len(all_features)
        else:
            logger.warning(f"    ⚠ Geen features gevonden")
            return 0
    
    def process_service(self, service: Dict) -> int:
        """Verwerk een service en download alle layers"""
        service_name = self.sanitize_filename(service['name'])
        service_type = service['type']
        service_path = service['path']
        
        logger.info(f"\n[{service_type}] {service_name}")
        
        # Voeg service type toe aan path (MapServer of FeatureServer)
        service_url_path = f"{service_path}/{service_type}"
        
        # Haal layers op
        layers = self.get_layers(service_url_path)
        
        if not layers:
            logger.warning(f"  Geen layers gevonden")
            return 0
        
        self.stats['layers_found'] += len(layers)
        total_features = 0
        
        for layer in layers:
            layer_name = self.sanitize_filename(layer['name'])
            output_file = self.output_dir / service_name / f"{layer_name}_layer{layer['id']}.geojson"
            
            # Check of bestand al bestaat (resume modus)
            if self.resume and str(output_file) in self.downloaded_files:
                logger.info(f"  ⏭ Skipping {layer_name} (reeds gedownload)")
                self.stats['layers_skipped'] += 1
                continue
            
            try:
                features_count = self.download_features(
                    service_url_path,
                    layer['id'],
                    layer['name'],
                    output_file
                )
                
                if features_count > 0:
                    total_features += features_count
                    self.stats['layers_downloaded'] += 1
                    self.downloaded_files.add(str(output_file))
                else:
                    self.stats['layers_failed'] += 1
                
            except Exception as e:
                logger.error(f"  Fout bij downloaden layer {layer_name}: {e}")
                self.stats['layers_failed'] += 1
                self.stats['errors'].append({
                    'service': service_name,
                    'layer': layer_name,
                    'error': str(e)
                })
            
            time.sleep(REQUEST_DELAY)
        
        if total_features > 0:
            self.stats['services_processed'] += 1
        
        return total_features
    
    def run(self):
        """Hoofdfunctie - download alle kaartlagen"""
        logger.info("=" * 70)
        logger.info("Rijnland ArcGIS Server - Download alle kaartlagen")
        logger.info("=" * 70)
        logger.info(f"Output directory: {self.output_dir.absolute()}")
        logger.info(f"Log file: {log_file}")
        logger.info(f"Resume modus: {'AAN' if self.resume else 'UIT'}")
        logger.info("")
        
        # Maak output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Haal alle services op
        all_services = self.get_all_services()
        
        if not all_services:
            logger.error("Geen services gevonden!")
            return
        
        logger.info(f"\n{len(all_services)} services gevonden\n")
        
        # Verwerk elke service
        start_time = time.time()
        
        for i, service in enumerate(all_services, 1):
            try:
                features_count = self.process_service(service)
                self.stats['total_features'] += features_count
            except Exception as e:
                logger.error(f"Fout bij verwerken service {service['name']}: {e}")
                self.stats['errors'].append({
                    'service': service['name'],
                    'error': str(e)
                })
            
            logger.info(f"\nVoortgang: {i}/{len(all_services)} services verwerkt")
        
        elapsed_time = time.time() - start_time
        
        # Print samenvatting
        self.print_summary(elapsed_time)
    
    def print_summary(self, elapsed_time: float):
        """Print samenvatting van de download"""
        logger.info("\n" + "=" * 70)
        logger.info("SAMENVATTING")
        logger.info("=" * 70)
        logger.info(f"Services gevonden: {self.stats['services_found']}")
        logger.info(f"Services verwerkt: {self.stats['services_processed']}")
        logger.info(f"Layers gevonden: {self.stats['layers_found']}")
        logger.info(f"Layers gedownload: {self.stats['layers_downloaded']}")
        logger.info(f"Layers overgeslagen: {self.stats['layers_skipped']}")
        logger.info(f"Layers gefaald: {self.stats['layers_failed']}")
        logger.info(f"Totaal features: {self.stats['total_features']:,}")
        logger.info(f"Tijd: {elapsed_time:.1f} seconden ({elapsed_time/60:.1f} minuten)")
        logger.info(f"Output directory: {self.output_dir.absolute()}")
        
        if self.stats['errors']:
            logger.warning(f"\n{len(self.stats['errors'])} fouten opgetreden:")
            for error in self.stats['errors'][:10]:  # Toon eerste 10 fouten
                logger.warning(f"  - {error.get('service', 'Unknown')}: {error.get('error', 'Unknown error')}")
            if len(self.stats['errors']) > 10:
                logger.warning(f"  ... en {len(self.stats['errors']) - 10} meer (zie log bestand)")
        
        logger.info("=" * 70)

def main():
    """Hoofdfunctie"""
    downloader = ArcGISDownloader(
        base_url=ARCGIS_BASE_URL,
        output_dir=OUTPUT_DIR,
        resume=RESUME
    )
    
    try:
        downloader.run()
    except KeyboardInterrupt:
        logger.warning("\n\nDownload onderbroken door gebruiker")
        downloader.print_summary(0)
    except Exception as e:
        logger.error(f"Onverwachte fout: {e}", exc_info=True)

if __name__ == "__main__":
    main()

