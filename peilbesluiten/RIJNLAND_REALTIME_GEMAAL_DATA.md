# Real-time Gemaal/Pomp Data Rijnland (10 minuten interval)

Dit document beschrijft de beschikbaarheid van real-time gemaal- en pompdata met een update frequentie van elke 10 minuten.

## Huidige Situatie

### ArcGIS Services (Statische/Locatie Data)

De ArcGIS server van Rijnland bevat **geen real-time operationele data** van gemalen. De beschikbare gemaal data bevat alleen:

- **Locatie informatie**: Coördinaten, adres, gemeente
- **Statische eigenschappen**: 
  - Capaciteit (MAXIMALECAPACITEIT)
  - Aantal pompen (AANTALPOMPEN)
  - Functie (FUNCTIEGEMAAL)
  - Soort gemaal (SOORTGEMAAL)
  - Status (STATUSOBJECT)
- **Laatste update**: LAST_EDITED_DATE (meestal maanden geleden)

**Services beschikbaar:**
- `Gemaal/MapServer` - Locaties van alle gemalen
- `Gemaal_opgrootte/MapServer` - Gemalen gegroepeerd op capaciteit
- `Effluentgemaal/MapServer` - Effluent gemalen
- `Rioolgemaal_influent/MapServer` - Rioolgemalen

**Beperking**: Deze services bevatten **geen** real-time operationele data zoals:
- Actuele pompsnelheid
- Debiet (m³/s)
- Draaiuren
- Energieverbruik
- Status (aan/uit)
- Waterstanden

## Real-time Data Bronnen

### 1. SCADA Systemen (Intern)

Rijnland gebruikt waarschijnlijk SCADA (Supervisory Control and Data Acquisition) systemen voor real-time monitoring van gemalen. Deze data is meestal:

- **Niet publiek beschikbaar** via ArcGIS
- **Intern systeem** voor operationeel beheer
- **Update frequentie**: Elke 10 minuten of vaker
- **Toegang**: Vereist authenticatie en mogelijk speciale toegang

**Mogelijke SCADA systemen:**
- Historische data systemen
- Real-time monitoring dashboards
- API's voor operationele data

### 2. Rijkswaterstaat Data (10-minuten interval)

Rijkswaterstaat biedt wel real-time waterdata met 10-minuten interval:

**Bron**: https://rijkswaterstaatdata.nl/waterdata/

**Beschikbare data:**
- Waterstanden (elke 10 minuten)
- Debieten
- Waterkwaliteit
- Neerslag

**API**: Rijkswaterstaat Data API
- Update frequentie: Elke 10 minuten
- Gebied: Landelijk (inclusief delen van Rijnland gebied)
- Toegang: Publiek beschikbaar

**Let op**: Dit is niet specifiek gemaal data, maar waterstand/debiet data die mogelijk relevant is voor gemaal operaties.

### 3. Meetlocaties Waterkwantiteit

Rijnland heeft meetlocaties voor waterkwantiteit:

**Service**: `Meetlocatie_waterkwantiteit/MapServer`

**Mogelijke data**:
- Locaties van meetpunten
- Mogelijk koppeling met real-time sensoren
- Waterstanden, debieten

**Status**: Service beschikbaar, maar real-time data mogelijk niet via ArcGIS API

## Aanbevelingen voor Real-time Gemaal Data

### Optie 1: Contact Rijnland

Voor toegang tot real-time gemaal data (elke 10 minuten):

1. **Contact opnemen met Rijnland**:
   - Website: https://www.rijnland.net
   - Email: Via contactformulier op website
   - Telefoon: 071 - 306 30 63

2. **Vraag naar**:
   - SCADA API toegang
   - Real-time gemaal monitoring data
   - Historische gemaal data
   - API documentatie voor operationele data

### Optie 2: Rijkswaterstaat Data API

Voor waterstand/debiet data in het gebied:

```python
# Voorbeeld: Rijkswaterstaat Data API
import requests

# Waterstanden (10-minuten interval)
url = "https://api.rijkswaterstaat.nl/waterdata/v1/waterstanden"
params = {
    'lat': 52.1,  # Rijnland gebied
    'lon': 4.6,
    'radius': 50000  # 50 km radius
}

response = requests.get(url, params=params)
data = response.json()
```

**Documentatie**: https://rijkswaterstaatdata.nl/waterdata/

### Optie 3: Historische Data Analyse

Als real-time data niet beschikbaar is, kun je:

1. **Gebruik maken van historische patronen**:
   - Analyseer wanneer gemalen actief zijn
   - Correlatie met neerslag/waterstanden
   - Schattingen op basis van capaciteit en waterstanden

2. **Combineer beschikbare data**:
   - Gemaal locaties (ArcGIS)
   - Waterstanden (Rijkswaterstaat)
   - Neerslagdata
   - Peilgebied data

## Script voor Real-time Data Polling

Als je toegang krijgt tot een real-time API, gebruik dit script:

```python
#!/usr/bin/env python3
"""
Poll real-time gemaal data elke 10 minuten
"""

import requests
import time
import json
from datetime import datetime
from pathlib import Path

API_URL = "https://api.rijnland.nl/gemalen/realtime"  # Voorbeeld URL
OUTPUT_DIR = Path("realtime_gemaal_data")
OUTPUT_DIR.mkdir(exist_ok=True)

def fetch_gemaal_data():
    """Haal real-time gemaal data op"""
    try:
        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Fout bij ophalen data: {e}")
        return None

def save_data(data, timestamp):
    """Sla data op met timestamp"""
    filename = OUTPUT_DIR / f"gemaal_data_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump({
            'timestamp': timestamp.isoformat(),
            'data': data
        }, f, indent=2)
    print(f"Data opgeslagen: {filename}")

def main():
    """Poll elke 10 minuten"""
    interval = 10 * 60  # 10 minuten in seconden
    
    print(f"Start polling gemaal data elke 10 minuten...")
    print(f"Stop met Ctrl+C")
    
    while True:
        timestamp = datetime.now()
        print(f"\n[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] Ophalen data...")
        
        data = fetch_gemaal_data()
        if data:
            save_data(data, timestamp)
        
        print(f"Wachten {interval/60} minuten tot volgende update...")
        time.sleep(interval)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPolling gestopt")
```

## Database Schema voor Real-time Data

Als je real-time data gaat opslaan:

```sql
CREATE TABLE peilbesluiten.gemaal_realtime (
    id SERIAL PRIMARY KEY,
    gemaal_code VARCHAR(50) NOT NULL,
    gemaal_naam VARCHAR(255),
    timestamp TIMESTAMP NOT NULL,
    status VARCHAR(50),  -- aan/uit/onderhoud
    debiet_m3s DOUBLE PRECISION,
    pompsnelheid_rpm DOUBLE PRECISION,
    energieverbruik_kwh DOUBLE PRECISION,
    waterstand_beneden DOUBLE PRECISION,
    waterstand_boven DOUBLE PRECISION,
    draaiuren DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(gemaal_code, timestamp)
);

CREATE INDEX idx_gemaal_realtime_code_time 
    ON peilbesluiten.gemaal_realtime(gemaal_code, timestamp DESC);
```

## Hydronet Water Control Room API (Gevonden!)

**Belangrijke ontdekking**: Via de Rijnland ArcGIS Instant App kan je real-time gemaal data ophalen via de Hydronet Water Control Room API!

### API Details

**Basis URL**: `https://watercontrolroom.hydronet.com/service/efsserviceprovider/api/chart/`

**Chart ID**: `e743fb87-2a02-4f3e-ac6c-03d03401aab8` (Rijnland)

**Endpoint**: 
```
https://watercontrolroom.hydronet.com/service/efsserviceprovider/api/chart/e743fb87-2a02-4f3e-ac6c-03d03401aab8?featureIdentifier=<GEMAAL_CODE>
```

**Voorbeeld**:
```
https://watercontrolroom.hydronet.com/service/efsserviceprovider/api/chart/e743fb87-2a02-4f3e-ac6c-03d03401aab8?featureIdentifier=176-036-00021
```

### Data Format

De API geeft HTML terug met een Highcharts configuratie die bevat:
- **Tijdreeks data**: Timestamps met debietwaarden (m³/s)
- **Update frequentie**: Variabel (meestal 10-30 minuten)
- **Data periode**: Meestal laatste 14 dagen
- **Status**: Aan/uit gebaseerd op debiet (>0.001 m³/s = aan)

### Gebruik

**Script**: `fetch_hydronet_gemaal_data.py`

```bash
# Haal data op voor een specifiek gemaal
python fetch_hydronet_gemaal_data.py 176-036-00021

# Haal data op voor alle gemalen uit GeoJSON
python fetch_hydronet_gemaal_data.py --all rijnland_kaartlagen/Gemaal/Gemaal_layer0.geojson
```

**Output**: JSON bestanden met geparsed tijdreeks data in `realtime_gemaal_data/`

### Data Structuur

```json
{
  "feature_identifier": "176-036-00021",
  "timestamp": "2025-12-02T20:47:32",
  "time_range": {
    "min": 1763495252000,
    "max": 1764704912000
  },
  "yAxis": [{
    "title": "WNS2367.Gemaal - m3/s",
    "min": -0.04,
    "max": 0.44
  }],
  "series": [{
    "name": "WNS2367.Gemaal - Gemaal Zwetterpolder",
    "type": "line",
    "data": [{
      "timestamp": "2025-11-18T21:18:32",
      "timestamp_ms": 1763497112000,
      "value": 0.0,
      "status": "uit"
    }]
  }]
}
```

### Toegang

1. **Via ArcGIS Instant App**: 
   - Ga naar: https://rijnland.maps.arcgis.com/apps/instant/portfolio/index.html?appid=04473876a9fa44e4a80acb78f883ee61
   - Klik op een gemaal
   - Klik op "weergeven" link
   - URL bevat `featureIdentifier` parameter

2. **Direct via API**: 
   - Gebruik gemaal code uit ArcGIS data (`CODE` veld)
   - Vervang `featureIdentifier` parameter in URL

## Conclusie

**Huidige status:**
- ✅ **Real-time gemaal data gevonden via Hydronet API!**
- ✅ Tijdreeks data met debietwaarden (m³/s)
- ✅ Update frequentie: 10-30 minuten (variabel per gemaal)
- ✅ Data periode: Meestal laatste 14 dagen
- ✅ Script beschikbaar om data op te halen
- ✅ Locatie data beschikbaar via ArcGIS
- ✅ Rijkswaterstaat heeft 10-minuten waterstand data

**Volgende stappen:**
1. Contact opnemen met Rijnland voor SCADA/real-time API toegang
2. Gebruik Rijkswaterstaat data voor waterstanden/debieten
3. Combineer beschikbare data voor schattingen
4. Implementeer polling script zodra API beschikbaar is

## Contact Informatie

**Hoogheemraadschap van Rijnland**
- Website: https://www.rijnland.net
- Contact: Via website contactformulier
- Telefoon: 071 - 306 30 63
- Adres: Archimedesweg 1, 2333 CM Leiden

**Vraag specifiek naar:**
- Real-time gemaal monitoring data
- SCADA API toegang
- Historische gemaal operationele data
- API documentatie

