import requests
import json
import os
from pathlib import Path

# Configuration
SERVICE_URL = "https://rijnland.enl-mcs.nl/arcgis/rest/services/Peilgebied_vigerend_besluit/MapServer/0"
OUTPUT_DIR = Path("rijnland_kaartlagen/Peilgebied")
OUTPUT_FILE = OUTPUT_DIR / "Peilgebied_layer0.geojson"

def download_layer():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading Peilgebied layer from {SERVICE_URL}...")
    
    # Query parameters for GeoJSON
    params = {
        "where": "1=1",
        "outFields": "*",
        "f": "geojson",
        "returnGeometry": "true"
    }
    
    try:
        response = requests.get(f"{SERVICE_URL}/query", params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if "features" in data:
            count = len(data["features"])
            print(f"Downloaded {count} features.")
            
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"Saved to {OUTPUT_FILE}")
            
            # Check coordinates of first feature
            if count > 0:
                geom = data["features"][0].get("geometry", {})
                print("First feature geometry type:", geom.get("type"))
                coords = geom.get("coordinates", [])
                print("First coordinate sample:", coords[0][0][0] if coords and len(coords)>0 else "Empty")
                
        else:
            print("No features found in response.")
            print(data)
            
    except Exception as e:
        print(f"Error downloading layer: {e}")

if __name__ == "__main__":
    download_layer()
