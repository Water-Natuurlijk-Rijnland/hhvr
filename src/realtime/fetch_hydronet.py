#!/usr/bin/env python3
"""
Fetch real-time gemaal data van Hydronet Water Control Room API
Gebaseerd op de ontdekte API: https://watercontrolroom.hydronet.com/service/efsserviceprovider/api/chart/
"""

import requests
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import time

# Configuratie
HYDRONET_BASE_URL = "https://watercontrolroom.hydronet.com/service/efsserviceprovider/api"
CHART_ID = "e743fb87-2a02-4f3e-ac6c-03d03401aab8"  # Rijnland chart ID
OUTPUT_DIR = Path("realtime_gemaal_data")
LOG_DIR = "logs"

# Setup logging
Path(LOG_DIR).mkdir(exist_ok=True)
log_file = Path(LOG_DIR) / f"hydronet_gemaal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HydronetGemaalDataFetcher:
    """Klasse voor het ophalen van real-time gemaal data via Hydronet API"""
    
    def __init__(self, chart_id: str, output_dir: Path):
        self.chart_id = chart_id
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
        self.base_url = f"{HYDRONET_BASE_URL}/chart/{chart_id}"
    
    def fetch_gemaal_data(self, feature_identifier: str) -> Optional[Dict]:
        """
        Haal real-time data op voor een specifiek gemaal
        
        Args:
            feature_identifier: Gemaal code (bijv. '176-036-00021')
        
        Returns:
            Dict met gemaal data of None bij fout
        """
        url = self.base_url
        params = {
            'featureIdentifier': feature_identifier
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://rijnland.maps.arcgis.com/'
        }
        
        try:
            logger.info(f"Ophalen data voor gemaal {feature_identifier}...")
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Probeer JSON te parsen
            try:
                data = response.json()
                logger.info(f"✓ JSON data ontvangen")
                return data
            except json.JSONDecodeError:
                # Als het geen JSON is, parse Highcharts configuratie uit HTML
                logger.info(f"Parsen Highcharts configuratie uit HTML...")
                return self.parse_highcharts_config(response.text, feature_identifier)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request fout: {e}")
            return None
        except Exception as e:
            logger.error(f"Onverwachte fout: {e}")
            return None
    
    def fetch_all_gemalen(self, gemaal_codes: List[str]) -> Dict[str, Dict]:
        """
        Haal data op voor meerdere gemalen
        
        Args:
            gemaal_codes: Lijst van gemaal codes
        
        Returns:
            Dict met gemaal_code als key en data als value
        """
        results = {}
        
        for code in gemaal_codes:
            data = self.fetch_gemaal_data(code)
            if data:
                results[code] = data
            
            # Korte pauze tussen requests
            time.sleep(0.5)
        
        return results
    
    def save_data(self, data: Dict, feature_identifier: str, timestamp: datetime):
        """Sla gemaal data op"""
        filename = self.output_dir / f"gemaal_{feature_identifier}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        
        save_data = {
            'timestamp': timestamp.isoformat(),
            'feature_identifier': feature_identifier,
            'chart_id': self.chart_id,
            'data': data
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data opgeslagen: {filename.name}")
            return True
        except Exception as e:
            logger.error(f"Fout bij opslaan: {e}")
            return False
    
    def parse_highcharts_config(self, html_content: str, feature_identifier: str) -> Optional[Dict]:
        """
        Parse Highcharts configuratie uit HTML response
        
        De API geeft HTML terug met een Highcharts.chart() configuratie
        die de tijdreeks data bevat
        """
        try:
            # Zoek naar Highcharts.chart('container', { ... })
            pattern = r'Highcharts\.chart\([\'"]container[\'"],\s*(\{.*?\})\);'
            match = re.search(pattern, html_content, re.DOTALL)
            
            if not match:
                logger.warning("Kon Highcharts configuratie niet vinden in HTML")
                # Sla raw response op voor analyse
                raw_file = self.output_dir / f"raw_{feature_identifier}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(raw_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"Raw response opgeslagen in {raw_file}")
                return None
            
            config_json = match.group(1)
            # Parse de JSON configuratie
            config = json.loads(config_json)
            
            # Extraheer relevante data
            parsed_data = {
                'feature_identifier': feature_identifier,
                'timestamp': datetime.now().isoformat(),
                'time_range': {
                    'min': config.get('xAxis', [{}])[0].get('min'),
                    'max': config.get('xAxis', [{}])[0].get('max')
                },
                'yAxis': [],
                'series': []
            }
            
            # Parse yAxis informatie
            for yaxis in config.get('yAxis', []):
                parsed_data['yAxis'].append({
                    'title': yaxis.get('title', {}).get('text', ''),
                    'min': yaxis.get('min'),
                    'max': yaxis.get('max'),
                    'id': yaxis.get('id', '')
                })
            
            # Parse series data (tijdreeksen)
            for series in config.get('series', []):
                series_data = {
                    'name': series.get('name', ''),
                    'type': series.get('type', 'line'),
                    'color': series.get('color', ''),
                    'data': []
                }
                
                # Converteer data punten
                for point in series.get('data', []):
                    timestamp_ms = point.get('x', 0)
                    value = point.get('y', 0)
                    
                    # Converteer timestamp naar datetime
                    timestamp_dt = datetime.fromtimestamp(timestamp_ms / 1000)
                    
                    series_data['data'].append({
                        'timestamp': timestamp_dt.isoformat(),
                        'timestamp_ms': timestamp_ms,
                        'value': value,
                        'status': 'aan' if value > 0.001 else 'uit'  # Bepaal status op basis van debiet
                    })
                
                parsed_data['series'].append(series_data)
            
            logger.info(f"✓ {len(parsed_data['series'])} series geparsed met {sum(len(s['data']) for s in parsed_data['series'])} data punten")
            
            return parsed_data
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse fout: {e}")
            return None
        except Exception as e:
            logger.error(f"Fout bij parsen Highcharts config: {e}")
            return None
    
    def load_gemaal_codes_from_geojson(self, geojson_file: str) -> List[str]:
        """Laad gemaal codes uit gedownloade GeoJSON"""
        try:
            with open(geojson_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            codes = []
            for feature in data.get('features', []):
                code = feature.get('attributes', {}).get('CODE')
                if code:
                    codes.append(code)
            
            logger.info(f"{len(codes)} gemaal codes geladen uit {geojson_file}")
            return codes
        except Exception as e:
            logger.error(f"Fout bij laden gemaal codes: {e}")
            return []

def main():
    """Hoofdfunctie"""
    import sys
    
    fetcher = HydronetGemaalDataFetcher(CHART_ID, OUTPUT_DIR)
    
    # Test met het gevonden gemaal
    test_code = "176-036-00021"  # Gemaal Zwetterpolder
    default_geojson = "rijnland_kaartlagen/Gemaal/Gemaal_layer0.geojson"
    
    if len(sys.argv) > 1 and sys.argv[1] != '--all':
        # Specifiek gemaal code opgegeven
        gemaal_code = sys.argv[1]
        logger.info(f"Ophalen data voor gemaal: {gemaal_code}")
        
        timestamp = datetime.now()
        data = fetcher.fetch_gemaal_data(gemaal_code)
        
        if data:
            fetcher.save_data(data, gemaal_code, timestamp)
            logger.info("\n" + "=" * 70)
            logger.info("DATA OPGESLAGEN")
            logger.info("=" * 70)
            logger.info(f"Gemaal: {gemaal_code}")
            logger.info(f"Timestamp: {timestamp.isoformat()}")
            logger.info(f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
        else:
            logger.error("Geen data ontvangen")
    
    elif len(sys.argv) > 1 and sys.argv[1] == '--all':
        # Alle gemalen uit GeoJSON
        geojson_file = sys.argv[2] if len(sys.argv) > 2 else default_geojson
        
        logger.info("=" * 70)
        logger.info("Ophalen real-time data voor ALLE gemalen")
        logger.info("=" * 70)
        logger.info(f"GeoJSON bestand: {geojson_file}")
        logger.info("")
        
        codes = fetcher.load_gemaal_codes_from_geojson(geojson_file)
        
        if not codes:
            logger.error("Geen gemaal codes gevonden")
            return
        
        logger.info(f"Start ophalen data voor {len(codes)} gemalen...")
        logger.info("")
        
        start_time = time.time()
        results = {}
        failed = []
        
        for i, code in enumerate(codes, 1):
            logger.info(f"[{i}/{len(codes)}] Verwerken: {code}")
            
            timestamp = datetime.now()
            data = fetcher.fetch_gemaal_data(code)
            
            if data and 'series' in data and len(data.get('series', [])) > 0:
                # Alleen opslaan als er daadwerkelijk data is
                if fetcher.save_data(data, code, timestamp):
                    results[code] = {
                        'success': True,
                        'data_points': sum(len(s.get('data', [])) for s in data.get('series', []))
                    }
                    logger.info(f"  ✓ Opgeslagen ({results[code]['data_points']} data punten)")
                else:
                    failed.append(code)
                    logger.warning(f"  ✗ Opslaan gefaald")
            else:
                failed.append(code)
                logger.warning(f"  ✗ Geen data beschikbaar")
            
            # Korte pauze tussen requests
            if i < len(codes):
                time.sleep(1)  # 1 seconde tussen requests om server niet te overbelasten
        
        elapsed_time = time.time() - start_time
        
        # Samenvatting
        logger.info("\n" + "=" * 70)
        logger.info("SAMENVATTING")
        logger.info("=" * 70)
        logger.info(f"Totaal gemalen: {len(codes)}")
        logger.info(f"Succesvol: {len(results)}")
        logger.info(f"Gefaald: {len(failed)}")
        logger.info(f"Tijd: {elapsed_time:.1f} seconden ({elapsed_time/60:.1f} minuten)")
        
        if results:
            total_points = sum(r['data_points'] for r in results.values())
            logger.info(f"Totaal data punten: {total_points:,}")
        
        if failed:
            logger.warning(f"\nGefaalde gemalen ({len(failed)}):")
            for code in failed[:10]:  # Toon eerste 10
                logger.warning(f"  - {code}")
            if len(failed) > 10:
                logger.warning(f"  ... en {len(failed) - 10} meer")
        
        logger.info(f"\nOutput directory: {fetcher.output_dir.absolute()}")
        logger.info("=" * 70)
    
    else:
        # Test met voorbeeld gemaal
        logger.info("Gebruik:")
        logger.info("  python fetch_hydronet_gemaal_data.py <gemaal_code>")
        logger.info(f"  python fetch_hydronet_gemaal_data.py {test_code}")
        logger.info("")
        logger.info("  python fetch_hydronet_gemaal_data.py --all [geojson_file]")
        logger.info(f"  python fetch_hydronet_gemaal_data.py --all {default_geojson}")
        logger.info("")
        
        # Test met voorbeeld
        logger.info("Test modus - ophalen voorbeeld gemaal...")
        timestamp = datetime.now()
        data = fetcher.fetch_gemaal_data(test_code)
        
        if data:
            fetcher.save_data(data, test_code, timestamp)
            logger.info("\n" + "=" * 70)
            logger.info("TEST DATA OPGESLAGEN")
            logger.info("=" * 70)
            logger.info(f"Gemaal: {test_code} (Gemaal Zwetterpolder)")
            logger.info(f"Timestamp: {timestamp.isoformat()}")
            logger.info(f"Output: {fetcher.output_dir.absolute()}")

if __name__ == "__main__":
    main()

