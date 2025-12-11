#!/usr/bin/env python3
"""
Poll real-time gemaal/pomp data elke 10 minuten
Dit script kan worden aangepast zodra er toegang is tot een real-time API
"""

import requests
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict
import os

# Configuratie
OUTPUT_DIR = Path("realtime_gemaal_data")
LOG_DIR = "logs"
POLL_INTERVAL = 10 * 60  # 10 minuten in seconden
MAX_RETRIES = 3

# Mogelijke API endpoints (moeten worden aangepast zodra beschikbaar)
API_ENDPOINTS = {
    # Voorbeeld endpoints - moeten worden aangepast
    'rijnland_scada': 'https://api.rijnland.nl/scada/gemalen/realtime',  # Niet beschikbaar
    'rijkswaterstaat': 'https://api.rijkswaterstaat.nl/waterdata/v1/waterstanden',  # Mogelijk beschikbaar
}

# Setup logging
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, f"realtime_gemaal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealtimeGemaalPoller:
    """Klasse voor het pollen van real-time gemaal data"""
    
    def __init__(self, output_dir: Path, interval: int = 600):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
        self.interval = interval
        self.stats = {
            'polls': 0,
            'success': 0,
            'failed': 0,
            'last_poll': None
        }
    
    def fetch_rijkswaterstaat_data(self, lat: float = 52.1, lon: float = 4.6, radius: int = 50000) -> Optional[Dict]:
        """
        Haal waterstand data op van Rijkswaterstaat
        Dit is een alternatief tot directe gemaal data
        """
        try:
            # Let op: Dit is een voorbeeld URL - check de actuele Rijkswaterstaat API documentatie
            url = "https://api.rijkswaterstaat.nl/waterdata/v1/waterstanden"
            params = {
                'lat': lat,
                'lon': lon,
                'radius': radius
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Rijkswaterstaat API fout: {e}")
            return None
        except Exception as e:
            logger.error(f"Onverwachte fout bij Rijkswaterstaat API: {e}")
            return None
    
    def fetch_rijnland_scada(self, gemaal_codes: list = None) -> Optional[Dict]:
        """
        Haal real-time gemaal data op van Rijnland SCADA systeem
        Deze functie moet worden aangepast zodra API toegang beschikbaar is
        """
        # TODO: Implementeer zodra API beschikbaar is
        logger.warning("Rijnland SCADA API nog niet beschikbaar - contact opnemen met Rijnland")
        return None
    
    def save_data(self, data: Dict, source: str, timestamp: datetime):
        """Sla real-time data op met timestamp"""
        filename = self.output_dir / f"{source}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        
        save_data = {
            'timestamp': timestamp.isoformat(),
            'source': source,
            'data': data
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data opgeslagen: {filename.name}")
            return True
        except Exception as e:
            logger.error(f"Fout bij opslaan data: {e}")
            return False
    
    def poll_once(self, source: str = 'rijkswaterstaat'):
        """Voer één poll uit"""
        timestamp = datetime.now()
        logger.info(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] Polling {source}...")
        
        self.stats['polls'] += 1
        
        # Kies data bron
        if source == 'rijkswaterstaat':
            data = self.fetch_rijkswaterstaat_data()
        elif source == 'rijnland_scada':
            data = self.fetch_rijnland_scada()
        else:
            logger.error(f"Onbekende bron: {source}")
            self.stats['failed'] += 1
            return False
        
        if data:
            if self.save_data(data, source, timestamp):
                self.stats['success'] += 1
                self.stats['last_poll'] = timestamp
                return True
            else:
                self.stats['failed'] += 1
                return False
        else:
            self.stats['failed'] += 1
            return False
    
    def run_continuous(self, source: str = 'rijkswaterstaat'):
        """Poll continu elke X minuten"""
        logger.info("=" * 70)
        logger.info("Real-time Gemaal Data Poller")
        logger.info("=" * 70)
        logger.info(f"Bron: {source}")
        logger.info(f"Interval: {self.interval/60} minuten")
        logger.info(f"Output directory: {self.output_dir.absolute()}")
        logger.info(f"Log file: {log_file}")
        logger.info("")
        logger.info("Stop met Ctrl+C")
        logger.info("")
        
        try:
            while True:
                self.poll_once(source)
                
                # Print statistieken
                logger.info(f"Statistieken: {self.stats['success']}/{self.stats['polls']} succesvol")
                
                # Wacht tot volgende poll
                wait_minutes = self.interval / 60
                next_poll = datetime.now().timestamp() + self.interval
                logger.info(f"Wachten {wait_minutes:.1f} minuten tot volgende poll (om {datetime.fromtimestamp(next_poll).strftime('%H:%M:%S')})...")
                logger.info("")
                
                time.sleep(self.interval)
        
        except KeyboardInterrupt:
            logger.info("\n\nPolling gestopt door gebruiker")
            self.print_summary()
    
    def print_summary(self):
        """Print samenvatting"""
        logger.info("=" * 70)
        logger.info("SAMENVATTING")
        logger.info("=" * 70)
        logger.info(f"Totaal polls: {self.stats['polls']}")
        logger.info(f"Succesvol: {self.stats['success']}")
        logger.info(f"Gefaald: {self.stats['failed']}")
        if self.stats['last_poll']:
            logger.info(f"Laatste poll: {self.stats['last_poll'].strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Data opgeslagen in: {self.output_dir.absolute()}")
        logger.info("=" * 70)

def main():
    """Hoofdfunctie"""
    import sys
    
    # Parse command line arguments
    source = 'rijkswaterstaat'  # Default
    if len(sys.argv) > 1:
        source = sys.argv[1]
    
    poller = RealtimeGemaalPoller(OUTPUT_DIR, interval=POLL_INTERVAL)
    
    try:
        poller.run_continuous(source)
    except Exception as e:
        logger.error(f"Onverwachte fout: {e}", exc_info=True)

if __name__ == "__main__":
    main()



