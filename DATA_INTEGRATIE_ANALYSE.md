# Data Integratie en Management - Toepassing op Peilbeheer Digital Twin

**Datum**: 2025-12-11  
**Gebaseerd op**: Hoofdstuk 4 "Data integration and management" uit Digital Twins boek  
**Project**: Peilbeheer Digital Twin voor Hoogheemraadschap van Rijnland

---

## 1. Samenvatting Hoofdstuk 4

### 1.1 Kernconcepten

Hoofdstuk 4 behandelt de fundamenten van data integratie en management voor digital twins:

**Belangrijkste principes:**
- **Polyglot persistence**: Verschillende datatypes vereisen verschillende storage technologieën
- **Data lifecycle management**: Data verandert van hot → warm → cold storage naarmate het ouder wordt
- **IT/OT convergentie**: Operational Technology (OT) en Information Technology (IT) systemen moeten veilig geïntegreerd worden
- **Schema-on-read vs schema-on-write**: Flexibiliteit versus performance trade-offs

### 1.2 Data Types

1. **Reference Data** (statisch)
   - Asset metadata, configuraties, organisatiestructuren
   - Verandert zelden (weken/maanden)
   - Voorbeeld: Gemaal specificaties, peilbesluit metadata

2. **Timeseries Data** (operationeel)
   - Continue metingen, sensordata, state changes
   - Hoge frequentie, groot volume
   - Immutable historische records
   - Voorbeeld: Gemaal debiet, waterpeilen, temperatuur

3. **Spatial Data** (geografisch)
   - Coördinaten, geometrieën, GIS data
   - Complexiteit varieert (punten tot 3D meshes)
   - Voorbeeld: Peilgebied polygonen, gemaal locaties

4. **Unstructured Data** (documenten/media)
   - PDFs, afbeeldingen, video's, configuratiebestanden
   - Voorbeeld: Peilbesluit documenten, gemaal foto's

5. **Derived Data** (afgeleid)
   - Features, embeddings, aggregaties
   - Resultaten van berekeningen en ML modellen
   - Voorbeeld: Gemiddelde debieten, trend analyses

### 1.3 Data Sources

**Operational Technology (OT):**
- SCADA systemen, industriële controle systemen
- IoT/IIoT sensoren
- Process historians
- **Uitdaging**: Air-gapped netwerken, proprietary protocollen, real-time vereisten

**Information Technology (IT):**
- ERP systemen (SAP, etc.)
- Business intelligence tools
- Enterprise databases
- **Voordeel**: Flexibele API toegang, gestandaardiseerde protocollen

**External Sources:**
- Publieke APIs
- Partner systemen
- Cloud services
- **Uitdaging**: Rate limiting, beschikbaarheid, data kwaliteit

### 1.4 Data Structures

| Structuur | Gebruik | Voorbeeld |
|-----------|---------|-----------|
| **Relational** | Reference data, complexe queries | PostgreSQL voor peilbesluiten |
| **Columnar** | Timeseries, analytics | InfluxDB, TimescaleDB |
| **Graph** | Relaties, traversals | Memgraph voor asset relaties |
| **Document** | Flexibele schema's | MongoDB voor sensor configs |
| **Key-Value** | Caching, sessies | Redis voor real-time cache |

### 1.5 Data Ingestion Methoden

1. **Batch Ingestion**
   - Scheduled updates (dagelijks, wekelijks)
   - Grote volumes historische data
   - ETL/ELT transformaties
   - Voorbeeld: Maandelijkse peilbesluit updates

2. **Streaming Ingestion**
   - Real-time data streams
   - Sliding window aggregaties
   - Continue updates
   - Voorbeeld: Live gemaal monitoring

3. **API Integration**
   - REST, GraphQL, gRPC, WebSocket
   - On-demand data pull
   - Event-driven patterns
   - Voorbeeld: Hydronet API calls

### 1.6 Storage Solutions

**Timeseries Databases:**
- InfluxDB, TimescaleDB, Amazon Timestream
- Columnar storage, compressie, time-based partitioning
- Automatische aggregaties

**Analytical Storage:**
- Snowflake, Redshift, BigQuery
- Columnar file formats (Parquet)
- Separation of storage and compute

**Data Lakes & Lakehouses:**
- Schema-on-read flexibiliteit
- Delta tables voor ACID transactions
- Object storage (S3) voor ongestructureerde data

**Transactional Storage:**
- PostgreSQL, MySQL voor reference data
- ACID compliance, relational integrity

**Specialized Storage:**
- Object storage (S3) voor media
- Graph databases voor relaties
- Vector databases voor embeddings
- Feature stores voor ML

### 1.7 Data Lifecycle Management

**Hot Data** (recent, operationeel):
- Real-time access (< 100ms)
- Premium storage
- Voorbeeld: Actuele gemaal status

**Warm Data** (weken/maanden oud):
- Snelle access (< 1s)
- Gecomprimeerde storage
- Voorbeeld: Maandelijkse rapporten

**Cold Data** (archief):
- Langzame access (minuten/uren)
- Zeer goedkope storage
- Voorbeeld: Historische peilbesluiten

### 1.8 Data Governance

- **Data classificatie**: Public, Internal, Confidential, Restricted
- **Regulatory compliance**: GDPR, sector-specifieke regels
- **Access control**: RBAC, ABAC, zero-trust
- **Data quality**: Validatie, monitoring, error handling

---

## 2. Huidige Situatie Peilbeheer Project

### 2.1 Data Types in Project

#### ✅ Reference Data
**Huidige implementatie:**
- Peilbesluit metadata (naam, datum, URL) in PostgreSQL
- Gemaal configuraties in GeoJSON bestanden
- **Storage**: PostgreSQL met PostGIS
- **Status**: Goed geïmplementeerd

**Voorbeelden:**
```sql
-- Peilbesluiten tabel
peilbesluiten.peilbesluiten (
    ws_pbnaam VARCHAR(255),      -- Naam
    ws_dtm_goed TIMESTAMP,       -- Goedkeuringsdatum
    ws_info TEXT                 -- URL naar besluit
)
```

#### ✅ Timeseries Data
**Huidige implementatie:**
- Real-time gemaal data (debiet, status) via Hydronet API
- Data wordt opgeslagen in JSON bestand (`gemaal_status_latest.json`)
- **Storage**: Flat JSON file
- **Status**: Basis werkt, maar niet optimaal voor timeseries

**Problemen:**
- Geen historische data opslag
- Geen time-based queries mogelijk
- Geen compressie of aggregatie
- Geen efficiente filtering op tijd

**Voorbeeld huidige structuur:**
```json
{
  "generated_at": "2025-12-11T14:30:00",
  "stations": {
    "176-036-00021": {
      "status": "aan",
      "debiet": 3.456,
      "timestamp": 1733926200
    }
  }
}
```

#### ✅ Spatial Data
**Huidige implementatie:**
- Peilgebied polygonen in PostgreSQL met PostGIS
- Gemaal locaties als GeoJSON
- **Storage**: PostgreSQL PostGIS extension
- **Status**: Uitstekend geïmplementeerd

**Voorbeelden:**
```sql
-- Spatial queries mogelijk
SELECT naam, ST_Area(geometry::geography) / 10000 as oppervlakte_ha
FROM peilbesluiten.peilgebieden_rijnland
WHERE ST_Contains(geometry, ST_SetSRID(ST_MakePoint(5.1, 52.1), 4326));
```

#### ⚠️ Unstructured Data
**Huidige implementatie:**
- Geen systematische opslag van documenten
- Peilbesluit URLs verwijzen naar externe sites
- **Storage**: Geen
- **Status**: Ontbreekt

**Mogelijke toevoegingen:**
- PDFs van peilbesluiten
- Gemaal foto's en documentatie
- Onderhoudsrapporten

#### ⚠️ Derived Data
**Huidige implementatie:**
- Aggregaties worden real-time berekend (`total_debiet_m3s`, `active_stations`)
- Geen feature store of ML features
- **Storage**: Geen dedicated storage
- **Status**: Basis aggregaties aanwezig, maar geen ML features

### 2.2 Data Sources

#### ✅ External APIs
**Huidige implementatie:**
- **Hydronet Water Control Room API**: Real-time gemaal data
- **ArcGIS REST Services**: HDSR en Rijnland kaartlagen
- **Integration method**: REST API calls via Python scripts
- **Status**: Goed geïmplementeerd

**Voorbeeld:**
```python
# Hydronet API call
url = f"{HYDRONET_BASE_URL}/chart/{CHART_ID}"
params = {'featureIdentifier': gemaal_code}
response = requests.get(url, params=params)
```

#### ✅ Batch Downloads
**Huidige implementatie:**
- GeoJSON downloads van ArcGIS services
- Scripts voor volledige dataset downloads
- **Status**: Goed geïmplementeerd

**Voorbeeld:**
```bash
# Download alle Rijnland kaartlagen
python download_rijnland_layers.py

# Update alleen dynamische data
python update_dynamische_data.py
```

#### ⚠️ Streaming Data
**Huidige implementatie:**
- Polling-based (elke 15-30 minuten)
- Geen echte streaming
- **Status**: Basis polling werkt, maar geen sliding windows of real-time processing

### 2.3 Data Structures

#### ✅ Relational (PostgreSQL)
**Gebruik**: Reference data, spatial data
- Peilbesluiten metadata
- Peilgebied polygonen
- **Status**: Goed geïmplementeerd met PostGIS

#### ⚠️ Columnar/Timeseries
**Gebruik**: Timeseries data
- **Huidig**: JSON files (niet optimaal)
- **Gewenst**: Timeseries database (InfluxDB, TimescaleDB)
- **Status**: Vereist verbetering

#### ❌ Graph Structure
**Gebruik**: Relaties tussen assets
- **Huidig**: Geen
- **Gewenst**: Relaties tussen gemalen, peilgebieden, meetpunten
- **Status**: Ontbreekt

#### ❌ Document Structure
**Gebruik**: Flexibele configuraties
- **Huidig**: JSON files (ad-hoc)
- **Gewenst**: Gestructureerde document store
- **Status**: Basis aanwezig maar niet systematisch

### 2.4 Data Ingestion

#### ✅ Batch Ingestion
**Implementatie:**
- `download_rijnland_layers.py`: Volledige dataset downloads
- `update_dynamische_data.py`: Incrementele updates
- **Status**: Goed geïmplementeerd met hash-based change detection

#### ⚠️ Streaming Ingestion
**Implementatie:**
- `generate_gemaal_status.py`: Polling elke 15-30 minuten
- Geen sliding window aggregaties
- Geen real-time processing
- **Status**: Basis polling werkt, maar mist advanced features

#### ✅ API Integration
**Implementatie:**
- REST API calls naar Hydronet en ArcGIS
- Rate limiting (0.2-1s delays)
- Error handling
- **Status**: Goed geïmplementeerd

### 2.5 Storage Solutions

#### ✅ PostgreSQL + PostGIS
**Gebruik**: Reference en spatial data
- **Status**: Uitstekend geïmplementeerd
- Spatial indexing, queries werken goed

#### ⚠️ JSON Files
**Gebruik**: Timeseries data (tijdelijk)
- `gemaal_status_latest.json`: Alleen laatste status
- Geen historische data
- **Status**: Werkt maar niet schaalbaar

#### ❌ Timeseries Database
**Gebruik**: Timeseries data
- **Status**: Ontbreekt
- **Impact**: Geen historische trends, geen efficiente time-based queries

#### ❌ Object Storage
**Gebruik**: Unstructured data
- **Status**: Ontbreekt
- **Impact**: Geen opslag voor documenten/media

#### ❌ Graph Database
**Gebruik**: Asset relaties
- **Status**: Ontbreekt
- **Impact**: Geen modellering van complexe relaties

### 2.6 Data Lifecycle Management

**Huidige situatie:**
- ❌ Geen lifecycle management
- ❌ Alle data in "hot" storage
- ❌ Geen archivering
- ❌ Geen tiering strategie

**Gewenst:**
- Hot: Laatste 24 uur gemaal data
- Warm: Laatste 30 dagen (gecomprimeerd)
- Cold: Historische data (> 30 dagen, archief)

---

## 3. Aanbevelingen voor Verbetering

### 3.1 Prioriteit 1: Critical (Must Have)

#### 3.1.1 Implementeer Timeseries Database

**Probleem:**
- Huidige JSON file storage is niet geschikt voor timeseries data
- Geen historische data mogelijk
- Geen efficiente time-based queries

**Oplossing:**
Implementeer TimescaleDB (PostgreSQL extensie) of InfluxDB voor gemaal timeseries data.

**Voordelen:**
- Automatische compressie
- Time-based partitioning
- Efficiente aggregaties
- Historische data opslag

**Implementatie:**
```sql
-- TimescaleDB setup
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Timeseries tabel voor gemaal data
CREATE TABLE gemaal_timeseries (
    time TIMESTAMPTZ NOT NULL,
    gemaal_code VARCHAR(50) NOT NULL,
    debiet DOUBLE PRECISION,
    status VARCHAR(20),
    PRIMARY KEY (time, gemaal_code)
);

-- Convert to hypertable
SELECT create_hypertable('gemaal_timeseries', 'time');

-- Automatische aggregatie views
CREATE MATERIALIZED VIEW gemaal_hourly_avg
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', time) AS hour,
    gemaal_code,
    AVG(debiet) AS avg_debiet,
    COUNT(*) AS readings
FROM gemaal_timeseries
GROUP BY hour, gemaal_code;
```

**Python integratie:**
```python
# Update generate_gemaal_status.py
import psycopg2
from psycopg2.extras import execute_values

def save_to_timeseries_db(data_points):
    conn = psycopg2.connect("postgresql://...")
    cursor = conn.cursor()
    
    # Bulk insert
    execute_values(
        cursor,
        """INSERT INTO gemaal_timeseries (time, gemaal_code, debiet, status)
           VALUES %s ON CONFLICT DO NOTHING""",
        [(dp['timestamp'], dp['code'], dp['debiet'], dp['status']) 
         for dp in data_points]
    )
    conn.commit()
```

**Impact:**
- ✅ Historische trends mogelijk
- ✅ Efficiente queries op tijd
- ✅ Automatische compressie
- ✅ Schaalbaar voor jaren data

#### 3.1.2 Implementeer Data Lifecycle Management

**Probleem:**
- Alle data blijft in "hot" storage
- Geen archivering
- Kosten groeien oneindig

**Oplossing:**
Implementeer tiering strategie met automatische migratie.

**Implementatie:**
```python
# lifecycle_manager.py
from datetime import datetime, timedelta

class DataLifecycleManager:
    def __init__(self, db_conn):
        self.db = db_conn
    
    def archive_old_data(self, days_threshold=30):
        """Archiveer data ouder dan X dagen"""
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        
        # Move to archive table
        self.db.execute("""
            INSERT INTO gemaal_timeseries_archive
            SELECT * FROM gemaal_timeseries
            WHERE time < %s
        """, (cutoff_date,))
        
        # Delete from main table
        self.db.execute("""
            DELETE FROM gemaal_timeseries
            WHERE time < %s
        """, (cutoff_date,))
        
        # Compress archive
        self.db.execute("""
            SELECT compress_chunk(chunk)
            FROM timescaledb_information.chunks
            WHERE hypertable_name = 'gemaal_timeseries_archive'
            AND range_end < %s
        """, (cutoff_date,))
```

**Cron job:**
```bash
# Archiveer wekelijks oude data
0 2 * * 0 cd /path/to/peilbesluiten && python lifecycle_manager.py --archive
```

**Impact:**
- ✅ Lagere storage kosten
- ✅ Betere performance voor recente data
- ✅ Behoud van historische data

#### 3.1.3 Verbeter Streaming Data Processing

**Probleem:**
- Geen sliding window aggregaties
- Geen real-time trend detectie
- Polling is te simpel

**Oplossing:**
Implementeer sliding window processing voor trends.

**Implementatie:**
```python
# streaming_processor.py
from collections import deque
from datetime import datetime, timedelta

class SlidingWindowProcessor:
    def __init__(self, window_minutes=30):
        self.window = timedelta(minutes=window_minutes)
        self.data_points = deque()
    
    def add_data_point(self, timestamp, value):
        """Voeg datapunt toe en verwijder oude punten"""
        cutoff = datetime.now() - self.window
        
        # Remove old points
        while self.data_points and self.data_points[0][0] < cutoff:
            self.data_points.popleft()
        
        # Add new point
        self.data_points.append((timestamp, value))
    
    def get_trend(self):
        """Bereken trend over sliding window"""
        if len(self.data_points) < 2:
            return None
        
        # Simple linear regression
        times = [(dp[0] - self.data_points[0][0]).total_seconds() 
                 for dp in self.data_points]
        values = [dp[1] for dp in self.data_points]
        
        # Calculate slope
        n = len(times)
        sum_x = sum(times)
        sum_y = sum(values)
        sum_xy = sum(times[i] * values[i] for i in range(n))
        sum_x2 = sum(t**2 for t in times)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
        
        return {
            'slope': slope,
            'trend': 'increasing' if slope > 0.01 else 'decreasing' if slope < -0.01 else 'stable',
            'window_size': len(self.data_points),
            'avg_value': sum_y / n
        }
```

**Integratie in generate_gemaal_status.py:**
```python
# Per gemaal sliding window
processors = {}
for code in codes:
    processors[code] = SlidingWindowProcessor(window_minutes=30)

# Bij elke update
data = fetcher.fetch_gemaal_data(code)
if data:
    processors[code].add_data_point(timestamp, debiet)
    trend = processors[code].get_trend()
    
    summary_data["stations"][code]["trend"] = trend
```

**Impact:**
- ✅ Real-time trend detectie
- ✅ Noise filtering via sliding windows
- ✅ Betere besluitvorming mogelijk

### 3.2 Prioriteit 2: Important (Should Have)

#### 3.2.1 Implementeer Object Storage voor Unstructured Data

**Probleem:**
- Geen opslag voor documenten/media
- Peilbesluit PDFs niet beschikbaar
- Gemaal foto's niet opgeslagen

**Oplossing:**
Implementeer object storage (lokaal of S3-compatible) voor documenten.

**Implementatie:**
```python
# object_storage.py
from pathlib import Path
import boto3
from datetime import datetime

class ObjectStorage:
    def __init__(self, base_path="storage/documents"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def store_peilbesluit_document(self, peilbesluit_id, pdf_url, pdf_content):
        """Sla peilbesluit PDF op"""
        # Organiseer per jaar/maand
        now = datetime.now()
        path = self.base_path / "peilbesluiten" / str(now.year) / f"{now.month:02d}"
        path.mkdir(parents=True, exist_ok=True)
        
        filename = path / f"peilbesluit_{peilbesluit_id}.pdf"
        filename.write_bytes(pdf_content)
        
        # Update database met referentie
        return str(filename.relative_to(self.base_path))
    
    def store_gemaal_photo(self, gemaal_code, image_data):
        """Sla gemaal foto op"""
        path = self.base_path / "gemalen" / gemaal_code
        path.mkdir(parents=True, exist_ok=True)
        
        filename = path / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filename.write_bytes(image_data)
        
        return str(filename.relative_to(self.base_path))
```

**Database schema uitbreiding:**
```sql
-- Voeg document referenties toe aan peilbesluiten tabel
ALTER TABLE peilbesluiten.peilbesluiten
ADD COLUMN document_path VARCHAR(500);

-- Nieuwe tabel voor gemaal media
CREATE TABLE peilbesluiten.gemaal_media (
    id SERIAL PRIMARY KEY,
    gemaal_code VARCHAR(50) NOT NULL,
    media_type VARCHAR(20) NOT NULL, -- 'photo', 'manual', 'diagram'
    file_path VARCHAR(500) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);
```

**Impact:**
- ✅ Centrale opslag voor documenten
- ✅ Mogelijkheid tot document search
- ✅ Completere digital twin

#### 3.2.2 Implementeer Graph Database voor Relaties

**Probleem:**
- Geen modellering van relaties tussen assets
- Geen efficiente traversals mogelijk
- Complexe queries moeilijk

**Oplossing:**
Implementeer graph database (Memgraph of Neo4j) voor asset relaties.

**Use cases:**
- Welke gemalen beïnvloeden welk peilgebied?
- Wat is de impact van een gemaal storing?
- Welke meetpunten zijn gerelateerd aan een gemaal?

**Implementatie:**
```python
# graph_storage.py
from memgraph import Memgraph

class AssetGraph:
    def __init__(self):
        self.db = Memgraph()
    
    def create_gemaal_peilgebied_relation(self, gemaal_code, peilgebied_code):
        """Creëer relatie tussen gemaal en peilgebied"""
        self.db.execute("""
            MATCH (g:Gemaal {code: $gemaal_code})
            MATCH (p:Peilgebied {code: $peilgebied_code})
            MERGE (g)-[:BEÏNVLOEDT]->(p)
        """, gemaal_code=gemaal_code, peilgebied_code=peilgebied_code)
    
    def find_affected_peilgebieden(self, gemaal_code):
        """Vind alle peilgebieden beïnvloed door een gemaal"""
        result = self.db.execute("""
            MATCH (g:Gemaal {code: $code})-[:BEÏNVLOEDT]->(p:Peilgebied)
            RETURN p.code, p.naam, p.zomerpeil
        """, code=gemaal_code)
        return result
    
    def find_upstream_gemalen(self, peilgebied_code):
        """Vind alle gemalen die een peilgebied beïnvloeden"""
        result = self.db.execute("""
            MATCH (g:Gemaal)-[:BEÏNVLOEDT]->(p:Peilgebied {code: $code})
            RETURN g.code, g.naam, g.status
        """, code=peilgebied_code)
        return result
```

**Impact:**
- ✅ Complexe relatie queries mogelijk
- ✅ Impact analyse van storingen
- ✅ Betere systeem begrip

#### 3.2.3 Implementeer Feature Store voor ML

**Probleem:**
- Geen gestructureerde ML features
- Geen feature versioning
- Geen consistentie tussen training en serving

**Oplossing:**
Implementeer feature store voor ML features.

**Features voor peilbeheer:**
- Gemiddeld debiet laatste 24 uur
- Trend laatste 7 dagen
- Seizoenspatronen
- Anomalie scores

**Implementatie:**
```python
# feature_store.py
import pandas as pd
from datetime import datetime, timedelta

class FeatureStore:
    def __init__(self, db_conn):
        self.db = db_conn
    
    def compute_gemaal_features(self, gemaal_code, timestamp):
        """Bereken features voor een gemaal op een moment"""
        # Laad historische data
        df = self.db.query(f"""
            SELECT time, debiet, status
            FROM gemaal_timeseries
            WHERE gemaal_code = '{gemaal_code}'
            AND time BETWEEN '{timestamp - timedelta(days=7)}' AND '{timestamp}'
            ORDER BY time
        """)
        
        features = {
            'gemaal_code': gemaal_code,
            'timestamp': timestamp,
            # 24h features
            'avg_debiet_24h': df[df['time'] > timestamp - timedelta(hours=24)]['debiet'].mean(),
            'max_debiet_24h': df[df['time'] > timestamp - timedelta(hours=24)]['debiet'].max(),
            'min_debiet_24h': df[df['time'] > timestamp - timedelta(hours=24)]['debiet'].min(),
            # 7d features
            'avg_debiet_7d': df['debiet'].mean(),
            'trend_7d': self._calculate_trend(df),
            # Seizoensfeatures
            'hour_of_day': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'month': timestamp.month,
            # Anomalie score
            'anomaly_score': self._calculate_anomaly_score(df)
        }
        
        return features
    
    def _calculate_trend(self, df):
        """Bereken trend over dataframe"""
        if len(df) < 2:
            return 0
        return (df['debiet'].iloc[-1] - df['debiet'].iloc[0]) / len(df)
    
    def _calculate_anomaly_score(self, df):
        """Bereken anomalie score"""
        if len(df) < 10:
            return 0
        
        recent = df['debiet'].iloc[-1]
        mean = df['debiet'].mean()
        std = df['debiet'].std()
        
        if std == 0:
            return 0
        
        return abs(recent - mean) / std
```

**Impact:**
- ✅ Consistente ML features
- ✅ Feature versioning
- ✅ Betere ML modellen mogelijk

### 3.3 Prioriteit 3: Nice to Have (Could Have)

#### 3.3.1 Implementeer Data Quality Monitoring

**Probleem:**
- Geen validatie van data kwaliteit
- Geen detectie van outliers
- Geen monitoring van data freshness

**Oplossing:**
Implementeer data quality checks en monitoring.

**Implementatie:**
```python
# data_quality.py
from datetime import datetime, timedelta

class DataQualityMonitor:
    def __init__(self, db_conn):
        self.db = db_conn
    
    def validate_gemaal_reading(self, gemaal_code, debiet, timestamp):
        """Valideer een gemaal reading"""
        issues = []
        
        # Check 1: Realistic range
        if debiet < 0:
            issues.append("Negatief debiet")
        if debiet > 100:  # Onrealistisch hoog voor dit type gemaal
            issues.append(f"Debiet te hoog: {debiet} m³/s")
        
        # Check 2: Timestamp freshness
        age = datetime.now() - timestamp
        if age > timedelta(hours=2):
            issues.append(f"Data te oud: {age}")
        
        # Check 3: Consistency met historische data
        historical_avg = self._get_historical_avg(gemaal_code, days=7)
        if historical_avg and abs(debiet - historical_avg) > 3 * self._get_historical_std(gemaal_code, days=7):
            issues.append(f"Afwijking van historisch gemiddelde: {debiet} vs {historical_avg}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'quality_score': max(0, 100 - len(issues) * 25)
        }
    
    def monitor_data_freshness(self):
        """Monitor data freshness voor alle gemalen"""
        cutoff = datetime.now() - timedelta(minutes=45)
        
        stale = self.db.query("""
            SELECT gemaal_code, MAX(time) as last_update
            FROM gemaal_timeseries
            GROUP BY gemaal_code
            HAVING MAX(time) < %s
        """, (cutoff,))
        
        return {
            'stale_count': len(stale),
            'stale_gemalen': stale
        }
```

**Impact:**
- ✅ Betere data kwaliteit
- ✅ Vroege detectie van problemen
- ✅ Betrouwbaardere digital twin

#### 3.3.2 Implementeer Caching Strategie

**Probleem:**
- Geen caching van API responses
- Herhaalde calls naar zelfde data
- Onnodige API belasting

**Oplossing:**
Implementeer multi-layer caching.

**Implementatie:**
```python
# cache_manager.py
from functools import lru_cache
from datetime import datetime, timedelta
import redis
import json

class CacheManager:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.memory_cache = {}
    
    def get_cached_gemaal_data(self, gemaal_code, ttl_minutes=5):
        """Haal gecachte gemaal data op"""
        cache_key = f"gemaal:{gemaal_code}"
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            cached_time, data = self.memory_cache[cache_key]
            if datetime.now() - cached_time < timedelta(minutes=ttl_minutes):
                return data
        
        # Check Redis cache
        cached = self.redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            self.memory_cache[cache_key] = (datetime.now(), data)
            return data
        
        return None
    
    def cache_gemaal_data(self, gemaal_code, data, ttl_minutes=5):
        """Cache gemaal data"""
        cache_key = f"gemaal:{gemaal_code}"
        
        # Memory cache
        self.memory_cache[cache_key] = (datetime.now(), data)
        
        # Redis cache
        self.redis.setex(
            cache_key,
            timedelta(minutes=ttl_minutes),
            json.dumps(data)
        )
```

**Impact:**
- ✅ Snellere response tijden
- ✅ Minder API belasting
- ✅ Lagere kosten

---

## 4. Implementatie Roadmap

### Fase 1: Foundation (Week 1-2)

**Doel**: Basis timeseries storage en lifecycle management

**Taken:**
1. ✅ Install TimescaleDB extensie in PostgreSQL
2. ✅ Creëer timeseries tabel voor gemaal data
3. ✅ Update `generate_gemaal_status.py` om naar database te schrijven
4. ✅ Implementeer basis lifecycle management
5. ✅ Test met historische data

**Deliverables:**
- Timeseries database operationeel
- Historische data opslag werkend
- Automatische archivering ingesteld

### Fase 2: Enhancement (Week 3-4)

**Doel**: Verbeter streaming processing en data kwaliteit

**Taken:**
1. ✅ Implementeer sliding window processor
2. ✅ Voeg trend detectie toe
3. ✅ Implementeer data quality monitoring
4. ✅ Voeg caching toe
5. ✅ Dashboard updates voor trends

**Deliverables:**
- Real-time trend detectie
- Data quality dashboard
- Verbeterde performance

### Fase 3: Expansion (Week 5-6)

**Doel**: Uitbreiden met object storage en graph database

**Taken:**
1. ✅ Setup object storage (lokaal of S3)
2. ✅ Implementeer document opslag
3. ✅ Setup graph database (Memgraph)
4. ✅ Modelleer asset relaties
5. ✅ Implementeer graph queries

**Deliverables:**
- Object storage operationeel
- Graph database met relaties
- Document management systeem

### Fase 4: Advanced (Week 7-8)

**Doel**: ML features en geavanceerde analytics

**Taken:**
1. ✅ Implementeer feature store
2. ✅ Bereken ML features
3. ✅ Feature versioning
4. ✅ Integratie met ML pipeline
5. ✅ Anomalie detectie

**Deliverables:**
- Feature store operationeel
- ML features beschikbaar
- Anomalie detectie werkend

---

## 5. Conclusie

### Huidige Sterke Punten

✅ **Spatial data management**: Uitstekend geïmplementeerd met PostGIS  
✅ **Reference data**: Goed gestructureerd in PostgreSQL  
✅ **API integration**: Robuuste implementatie met error handling  
✅ **Batch ingestion**: Goed geïmplementeerd met change detection

### Belangrijkste Verbeterpunten

⚠️ **Timeseries storage**: JSON files zijn niet geschikt voor schaal  
⚠️ **Historische data**: Geen opslag van historische trends  
⚠️ **Lifecycle management**: Geen archivering of tiering  
⚠️ **Unstructured data**: Geen opslag voor documenten  
⚠️ **Graph relations**: Geen modellering van asset relaties

### Aanbevolen Volgorde

1. **Week 1-2**: Timeseries database (kritiek voor schaal)
2. **Week 3-4**: Streaming processing en data kwaliteit
3. **Week 5-6**: Object storage en graph database
4. **Week 7-8**: ML features en advanced analytics

### Success Criteria

Het project is **production-ready** wanneer:
- ✅ Timeseries data wordt opgeslagen in dedicated database
- ✅ Historische trends zijn beschikbaar (minimaal 1 jaar)
- ✅ Data lifecycle management is geïmplementeerd
- ✅ Data quality monitoring is actief
- ✅ Object storage is operationeel voor documenten
- ✅ Graph database modelleert asset relaties

---

**Einde Document**

