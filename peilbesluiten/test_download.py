#!/usr/bin/env python3
"""
Kleine test versie om te controleren of de ArcGIS API bereikbaar is
en of we services kunnen ophalen.
"""

import json
import sys

try:
    import requests
except ImportError:
    print("ERROR: requests module niet gevonden!")
    print("Installeer met: pip install requests")
    print("Of gebruik: python3 -m pip install --user requests")
    sys.exit(1)

ARCGIS_BASE_URL = "https://rijnland.enl-mcs.nl/arcgis/rest/services"

def test_connection():
    """Test of we verbinding kunnen maken met de ArcGIS server"""
    print("Testen verbinding met Rijnland ArcGIS server...")
    print(f"URL: {ARCGIS_BASE_URL}\n")
    
    try:
        response = requests.get(ARCGIS_BASE_URL, params={'f': 'json'}, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print("✓ Verbinding succesvol!\n")
        
        # Toon aantal services
        if 'services' in data:
            services = data['services']
            print(f"Services gevonden: {len(services)}")
            
            # Toon eerste 5 services
            print("\nEerste 5 services:")
            for i, service in enumerate(services[:5], 1):
                print(f"  {i}. {service.get('name', 'Unknown')} ({service.get('type', 'Unknown')})")
            
            if len(services) > 5:
                print(f"  ... en {len(services) - 5} meer")
        
        # Toon folders
        if 'folders' in data and data['folders']:
            print(f"\nFolders gevonden: {len(data['folders'])}")
            print("Folders:", ", ".join(data['folders'][:5]))
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Fout bij verbinden: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ Fout bij parsen JSON: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)



