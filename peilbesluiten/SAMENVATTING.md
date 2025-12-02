# Peilbesluiten Database - Samenvatting

## Wat is er gemaakt?

Een complete PostgreSQL database setup met peilbesluiten data van twee waterschappen:

### 1. Database Structuur
- **Database**: `peilbeheer` (lokale PostgreSQL)
- **Schema**: `peilbesluiten`
- **PostGIS extensie**: Geïnstalleerd voor spatial queries

### 2. Data van HDSR (48 peilbesluiten)
- **Tabel**: `peilbesluiten.peilbesluiten`
- **Bron**: Hoogheemraadschap De Stichtse Rijnlanden
- **Velden**: naam, gebiedsplan, besluit URL, goedkeuringsdatum, geometrie
- **GeoJSON**: `data/peilbesluiten_hdsr.geojson` (1.9 MB)

### 3. Data van Rijnland (780 peilgebieden)
- **Tabel**: `peilbesluiten.peilgebieden_rijnland`
- **Bron**: Hoogheemraadschap van Rijnland
- **Velden**: code, naam, zomer/winterpeil, oppervlakte, soort peilbeheer, geometrie
- **GeoJSON**: `data/peilgebieden_rijnland.geojson` (17 MB)

## Hoe te gebruiken

### Database queries

```sql
-- Totaal aantal per waterschap
SELECT 
    'HDSR' as waterschap, COUNT(*) as aantal 
FROM peilbesluiten.peilbesluiten
UNION ALL
SELECT 
    'Rijnland' as waterschap, COUNT(*) as aantal 
FROM peilbesluiten.peilgebieden_rijnland;

-- Rijnland peilgebieden met zomerpeil
SELECT naam, zomerpeil, winterpeil, oppervlakte
FROM peilbesluiten.peilgebieden_rijnland
WHERE zomerpeil IS NOT NULL
ORDER BY oppervlakte DESC
LIMIT 10;

-- HDSR peilbesluiten
SELECT ws_pbnaam, ws_info, ws_dtm_goed
FROM peilbesluiten.peilbesluiten
ORDER BY ws_pbnaam;
```

### Data updaten

**HDSR:**
```bash
curl -s "https://geoservices.hdsr.nl/arcgis/rest/services/Extern/PeilbesluitenExtern_damo24/FeatureServer/3/query?where=1%3D1&outFields=*&f=geojson" \
  -o data/peilbesluiten_hdsr.geojson

python db/import.py data/peilbesluiten_hdsr.geojson
```

**Rijnland:**
```bash
curl -s "https://rijnland.enl-mcs.nl/arcgis/rest/services/Peilgebied_vigerend_besluit/MapServer/0/query?where=1%3D1&outFields=*&f=geojson" \
  -o data/peilgebieden_rijnland.geojson

python db/import_rijnland.py data/peilgebieden_rijnland.geojson
```

## Spatial Queries

```sql
-- Vind peilgebieden binnen bounding box (Utrecht e.o.)
SELECT naam, zomerpeil
FROM peilbesluiten.peilgebieden_rijnland
WHERE ST_Intersects(
    geometry,
    ST_MakeEnvelope(5.0, 52.0, 5.2, 52.2, 4326)
);

-- Vind peilbesluit bij specifieke coördinaat
SELECT naam, zomerpeil, winterpeil
FROM peilbesluiten.peilgebieden_rijnland
WHERE ST_Contains(
    geometry,
    ST_SetSRID(ST_MakePoint(5.1, 52.1), 4326)
);

-- Oppervlakte statistieken
SELECT 
    COUNT(*) as aantal_gebieden,
    SUM(ST_Area(geometry::geography) / 10000) as totaal_ha,
    AVG(ST_Area(geometry::geography) / 10000) as gemiddeld_ha
FROM peilbesluiten.peilgebieden_rijnland;
```

## Database Schema

### HDSR Tabel
```sql
peilbesluiten.peilbesluiten (
    id SERIAL PRIMARY KEY,
    objectid INTEGER UNIQUE,
    ws_pbnaam VARCHAR(255),      -- Naam peilbesluit
    ws_gpnaam VARCHAR(255),       -- Gebiedsplan naam
    ws_info TEXT,                 -- URL naar besluit
    ws_dtm_goed TIMESTAMP,        -- Goedkeuringsdatum
    globalid UUID,
    geometry GEOMETRY(MultiPolygon, 4326)
)
```

### Rijnland Tabel
```sql
peilbesluiten.peilgebieden_rijnland (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE,     -- Unieke code (bijv. PBS_GH-110.00)
    naam VARCHAR(255),            -- Naam peilgebied
    zomerpeil DOUBLE PRECISION,   -- Zomerpeil in m NAP
    winterpeil DOUBLE PRECISION,  -- Winterpeil in m NAP
    oppervlakte DOUBLE PRECISION, -- Oppervlakte in m²
    soortpeilbeheer VARCHAR(100), -- Type peilbeheer
    hyperlink TEXT,               -- URL naar besluit
    geometry GEOMETRY(MultiPolygon, 4326)
)
```

## Views voor eenvoudige queries

```sql
-- HDSR view
SELECT * FROM peilbesluiten.peilbesluiten_view;

-- Rijnland view
SELECT * FROM peilbesluiten.peilgebieden_rijnland_view;
```

## Connectie Details

**Lokale PostgreSQL:**
- Host: 127.0.0.1 (localhost)
- Port: 5432
- Database: peilbeheer
- Schema: peilbesluiten

**Connect via psql:**
```bash
psql -d peilbeheer
```

**Connect via Python:**
```python
import psycopg2
conn = psycopg2.connect(
    dbname="peilbeheer",
    user="your_username",
    host="127.0.0.1",
    port="5432"
)
```
