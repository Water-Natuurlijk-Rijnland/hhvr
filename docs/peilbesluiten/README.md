# Peilbesluiten Database

Deze directory bevat de peilbesluiten (waterpeil besluiten) data van meerdere waterschappen in een PostgreSQL database met PostGIS.

## Data Bronnen

### HDSR (Hoogheemraadschap De Stichtse Rijnlanden)
- **Service**: `https://geoservices.hdsr.nl/arcgis/rest/services/Extern/PeilbesluitenExtern_damo24/FeatureServer`
- **Layer**: Layer 3 - "Gebied peilbesluit"
- **Features**: 48 peilbesluiten
- **Tabel**: `peilbesluiten.peilbesluiten`

### Rijnland (Hoogheemraadschap van Rijnland)
- **Service**: `https://rijnland.enl-mcs.nl/arcgis/rest/services/Peilgebied_vigerend_besluit/MapServer`
- **Layer**: Layer 0 - "PeilgebiedVigerend"
- **Features**: 780 peilgebieden
- **Tabel**: `peilbesluiten.peilgebieden_rijnland`

## Structuur

```
peilbesluiten/
├── data/                               # GeoJSON data bestanden
│   ├── peilbesluiten_hdsr.geojson     # HDSR peilbesluiten (48 gebieden, 1.9 MB)
│   └── peilgebieden_rijnland.geojson  # Rijnland peilgebieden (780 gebieden, 17 MB)
├── rijnland_kaartlagen/                # Alle Rijnland kaartlagen (zie download script)
├── db/                                 # Database scripts
│   ├── schema.sql                      # PostgreSQL schema HDSR
│   ├── schema_rijnland.sql             # PostgreSQL schema Rijnland
│   ├── import.py                       # Python import script HDSR
│   └── import_rijnland.py              # Python import script Rijnland
├── logs/                                # Log bestanden van downloads
├── download_rijnland_layers.py         # Script om alle Rijnland kaartlagen te downloaden
├── requirements.txt                    # Python dependencies
├── docker-compose.yml                  # PostgreSQL + pgAdmin setup (optioneel)
└── README.md                           # Deze documentatie
```

### Data Velden

- `OBJECTID`: Uniek object ID
- `WS_PBNAAM`: Naam van het peilbesluit
- `WS_GPNAAM`: Naam van het gebiedsplan
- `WS_INFO`: URL naar besluit op lokaleregelgeving.overheid.nl
- `WS_DTM_GOED`: Datum goedkeuring
- `GLOBALID`: Globaal uniek ID
- `geometry`: Polygoon geometrie (GeoJSON)

## Database Setup

### 1. Start PostgreSQL met PostGIS

```bash
cd peilbesluiten
docker-compose up -d
```

Dit start:
- PostgreSQL 16 met PostGIS 3.4 op poort 5432
- pgAdmin op http://localhost:5050 (admin@peilbeheer.nl / admin)

Het database schema wordt automatisch aangemaakt bij eerste start.

### 2. Data Importeren

#### Optie A: Met Python script

```bash
# Installeer dependencies
pip install psycopg2-binary

# Importeer data
python db/import.py data/peilbesluiten_hdsr.geojson
```

#### Optie B: Met PostgreSQL tools

```bash
# Connect to database
docker exec -it peilbeheer-postgres psql -U postgres -d peilbeheer

# Import GeoJSON (vereist ogr2ogr)
ogr2ogr -f "PostgreSQL" \
  PG:"host=localhost dbname=peilbeheer user=postgres password=postgres" \
  data/peilbesluiten_hdsr.geojson \
  -nln peilbesluiten.peilbesluiten \
  -lco GEOMETRY_NAME=geometry \
  -lco FID=objectid
```

## Database Schema

### Tabel: `peilbesluiten.peilbesluiten`

```sql
CREATE TABLE peilbesluiten.peilbesluiten (
    id SERIAL PRIMARY KEY,
    objectid INTEGER UNIQUE NOT NULL,
    ws_pbnaam VARCHAR(255) NOT NULL,
    ws_gpnaam VARCHAR(255),
    ws_info TEXT,
    ws_dtm_goed TIMESTAMP,
    globalid UUID UNIQUE,
    geometry GEOMETRY(MultiPolygon, 4326) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### View: `peilbesluiten.peilbesluiten_view`

Gemakkelijke query met GeoJSON output en oppervlakte in hectare:

```sql
SELECT * FROM peilbesluiten.peilbesluiten_view;
```

## Voorbeeld Queries

### Alle peilbesluiten ophalen

```sql
SELECT 
    id,
    ws_pbnaam as naam,
    ws_gpnaam as gebiedsplan,
    ws_dtm_goed as goedkeuringsdatum,
    ST_Area(geometry::geography) / 10000 as oppervlakte_ha
FROM peilbesluiten.peilbesluiten
ORDER BY ws_pbnaam;
```

### Peilbesluiten binnen bounding box

```sql
SELECT 
    ws_pbnaam,
    ST_AsGeoJSON(geometry) as geojson
FROM peilbesluiten.peilbesluiten
WHERE ST_Intersects(
    geometry,
    ST_MakeEnvelope(5.0, 52.0, 5.5, 52.5, 4326)
);
```

### Zoek peilbesluit bij coordinaat

```sql
SELECT 
    ws_pbnaam,
    ws_info as besluit_url
FROM peilbesluiten.peilbesluiten
WHERE ST_Contains(
    geometry,
    ST_SetSRID(ST_MakePoint(5.173, 52.178), 4326)
);
```

### Export naar GeoJSON

```sql
SELECT json_build_object(
    'type', 'FeatureCollection',
    'features', json_agg(ST_AsGeoJSON(t.*)::json)
)
FROM (
    SELECT 
        id,
        ws_pbnaam,
        ws_gpnaam,
        ws_info,
        ws_dtm_goed,
        geometry
    FROM peilbesluiten.peilbesluiten
) t;
```

## pgAdmin Connectie

1. Open http://localhost:5050
2. Login: admin@peilbeheer.nl / admin
3. Add Server:
   - Name: Peilbeheer Local
   - Host: postgres (of host.docker.internal op Mac)
   - Port: 5432
   - Database: peilbeheer
   - Username: postgres
   - Password: postgres

## Data Updaten

### HDSR Data

Om de data te vernieuwen van HDSR:

```bash
# Download nieuwe data
curl -s "https://geoservices.hdsr.nl/arcgis/rest/services/Extern/PeilbesluitenExtern_damo24/FeatureServer/3/query?where=1%3D1&outFields=*&f=geojson" \
  -o data/peilbesluiten_hdsr.geojson

# Importeer opnieuw (update bestaande records)
python db/import.py data/peilbesluiten_hdsr.geojson
```

### Rijnland - Download Alle Kaartlagen

Het script `download_rijnland_layers.py` download automatisch alle kaartlagen (90+ services) van de Rijnland ArcGIS server:

```bash
# Installeer dependencies
pip install -r requirements.txt

# Download alle kaartlagen
python download_rijnland_layers.py
```

Het script:
- Detecteert automatisch alle services en layers
- Download alle features met paginering (>1000 features)
- Slaat data op als GeoJSON in `rijnland_kaartlagen/`
- Ondersteunt resume modus (skip reeds gedownloade bestanden)
- Logt alle activiteit naar `logs/`

**Configuratie** (aanpasbaar in script):
- `OUTPUT_DIR`: Waar bestanden worden opgeslagen (default: `rijnland_kaartlagen`)
- `REQUEST_DELAY`: Tijd tussen requests in seconden (default: 0.5)
- `RESUME`: Resume modus aan/uit (default: True)
- `MAX_RETRIES`: Aantal retries bij fouten (default: 3)

**Output structuur:**
```
rijnland_kaartlagen/
├── Gemaal/
│   └── Gemaal_layer0.geojson
├── Stuw/
│   └── Stuw_layer0.geojson
├── Watergang_vlak/
│   └── Watergang_vlak_layer0.geojson
└── ...
```

Zie `RIJNLAND_DATA.md` voor een overzicht van alle beschikbare datasets.

### Rijnland - Update Dynamische Data

Het script `update_dynamische_data.py` update alleen de dynamische datasets die regelmatig worden bijgewerkt (peilen, meetlocaties, etc.):

```bash
# Update alle dynamische datasets
python update_dynamische_data.py

# Update alleen een specifieke dataset
python update_dynamische_data.py Peilenkaart_praktijk
```

Het script:
- Download alleen datasets die zijn veranderd (hash vergelijking)
- Controleert `LAST_EDITED_DATE` om wijzigingen te detecteren
- Update alleen als er nieuwe data is
- Logt alle activiteit naar `logs/`

**Dynamische datasets:**
- `Peilenkaart_praktijk` - Actuele peilen (dagelijks)
- `Peilafwijking_praktijk` - Peilafwijkingen (dagelijks)
- `Peilgebied_praktijk_soort_gebied` - Praktijk peilgebieden (wekelijks)
- `Meetlocatie_waterkwantiteit` - Waterkwantiteit meetpunten (dagelijks)
- `Meetlocatie_waterkwaliteit` - Waterkwaliteit meetpunten (wekelijks)
- `TransportleidingMeetpunt` - Transportleiding meetpunten (dagelijks)

**Automatisch updaten met cron:**

```bash
# Voeg toe aan crontab (crontab -e)
# Update elke dag om 6:00 uur
0 6 * * * cd /path/to/peilbesluiten && ./venv/bin/python3 update_dynamische_data.py >> logs/cron.log 2>&1

# Of meerdere keren per dag (bijv. om 6:00, 12:00, 18:00)
0 6,12,18 * * * cd /path/to/peilbesluiten && ./venv/bin/python3 update_dynamische_data.py >> logs/cron.log 2>&1
```

Zie `RIJNLAND_DYNAMISCHE_DATA.md` voor meer informatie over dynamische data.

## Environment Variables

Voor productie gebruik, zet deze environment variables:

```bash
export POSTGRES_DB=peilbeheer
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=your_secure_password
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
```

## Andere Waterschappen

Om data van andere waterschappen toe te voegen, zoek naar hun open data portalen:
- **Rijnland**: https://rijnland.maps.arcgis.com/ (vereist authenticatie)
- **HDSR**: https://data-hdsr.opendata.arcgis.com/ (publiek)
- **Waternet**: https://maps.waternet.nl/
