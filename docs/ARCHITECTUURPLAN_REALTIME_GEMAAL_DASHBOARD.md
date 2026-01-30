# Architectuurplan: Real-time Gemaal Dashboard voor Digital Twin

**Datum**: 2025-12-11
**Auteur**: Claude Code
**Versie**: 1.0

## Executive Summary

Dit architectuurplan beschrijft de integratie van real-time gemaaldata in de Digital Twin visualisatie voor het Hoogheemraadschap van Rijnland. Het systeem haalt live data op van gemalen (pompstations) via de Hydronet Water Control Room API en visualiseert deze in een Vue.js frontend applicatie met een dashboard panel.

---

## 1. Systeemoverzicht

### 1.1 Doelstellingen
- **Real-time monitoring**: Visualiseer actuele status van alle gemalen in het Rijnland gebied
- **Aggregatie**: Toon totaaloverzicht van actieve gemalen en totaal debiet
- **Gebruiksvriendelijkheid**: Presenteer complexe data in een intuïtief dashboard
- **Performance**: Efficiënt ophalen en verwerken van data voor ~200+ gemalen

### 1.2 Architectuur op hoog niveau

```
┌─────────────────────────────────────────────────────────────┐
│                     Hydronet API                             │
│  (https://watercontrolroom.hydronet.com)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ HTTPS/JSON
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend Data Generator (Python)                 │
│  ┌────────────────────────────────────────────────────┐     │
│  │ generate_gemaal_status.py                          │     │
│  │  - Fetches data voor alle gemalen                  │     │
│  │  - Aggregeert statistieken                         │     │
│  │  - Genereert JSON summary                          │     │
│  └─────────────────────┬──────────────────────────────┘     │
│                        │                                     │
│  ┌─────────────────────▼──────────────────────────────┐     │
│  │ fetch_hydronet_gemaal_data.py                      │     │
│  │  - HydronetGemaalDataFetcher class                 │     │
│  │  - API wrapper met retry logic                     │     │
│  │  - Highcharts config parser                        │     │
│  └────────────────────────────────────────────────────┘     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ File System
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Static Data File                                │
│  public/data/gemaal_status_latest.json                       │
│  {                                                           │
│    "generated_at": "2025-12-11T14:30:00",                   │
│    "total_stations": 203,                                   │
│    "active_stations": 12,                                   │
│    "total_debiet_m3s": 45.3,                                │
│    "stations": { ... }                                      │
│  }                                                           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ HTTP GET
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Frontend Visualisatie (Vue.js)                  │
│  ┌────────────────────────────────────────────────────┐     │
│  │ AllLayersMap.vue (Main Component)                  │     │
│  │  - Leaflet map integration                         │     │
│  │  - Fetches gemaal_status_latest.json              │     │
│  │  - Passes data to DashboardPanel                   │     │
│  └─────────────────────┬──────────────────────────────┘     │
│                        │                                     │
│  ┌─────────────────────▼──────────────────────────────┐     │
│  │ DashboardPanel.vue (UI Component)                  │     │
│  │  - Displays aggregated statistics                  │     │
│  │  - Shows active/total stations                     │     │
│  │  - Shows total debiet                              │     │
│  │  - Last update timestamp                           │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Componenten Review

### 2.1 Backend: `generate_gemaal_status.py`

**Bestandslocatie**: `peilbesluiten/generate_gemaal_status.py`

#### Functionaliteit
- **Hoofddoel**: Genereer een geaggregeerde JSON summary van alle gemalen
- **Input**: GeoJSON bestand met alle gemaal locaties (`Gemaal_layer0.geojson`)
- **Output**: JSON bestand met real-time status (`gemaal_status_latest.json`)

#### Proces flow
```
1. Load gemaal codes from GeoJSON
   └─> ~203 gemalen geladen

2. For each gemaal:
   └─> Fetch real-time data via HydronetGemaalDataFetcher
   └─> Extract laatste data point (debiet, status, timestamp)
   └─> Update aggregatie counters

3. Generate summary:
   └─> total_stations: aantal gemalen
   └─> active_stations: aantal met status='aan'
   └─> total_debiet_m3s: som van alle debieten
   └─> stations: per-gemaal details

4. Save to public/data/gemaal_status_latest.json
```

#### Sterke punten
✅ **Separation of concerns**: Gebruikt `HydronetGemaalDataFetcher` voor API calls
✅ **Error handling**: Try-catch per gemaal, script faalt niet bij 1 fout
✅ **Rate limiting**: 0.2s delay tussen requests
✅ **Progress tracking**: Print voortgang tijdens fetch
✅ **Aggregatie logica**: Correcte berekening actieve stations en totaal debiet

#### Verbeterpunten
⚠️ **Geen scheduling**: Script moet handmatig gerund worden (zie aanbevelingen)
⚠️ **Rate limiting**: 0.2s is erg snel voor 203 gemalen (40 sec totaal), overweeg 0.5-1s
⚠️ **Geen data validatie**: Controleert niet of debiet realistisch is
⚠️ **Temp directory**: Maakt `temp_data/` aan maar gebruikt het niet effectief

#### Data structuur output
```json
{
  "generated_at": "2025-12-11T14:30:00.123456",
  "total_stations": 203,
  "active_stations": 12,
  "total_debiet_m3s": 45.327,
  "stations": {
    "176-036-00021": {
      "status": "aan",
      "debiet": 3.456,
      "timestamp": 1733926200,
      "last_update": "2025-12-11T14:30:00"
    },
    "176-036-00022": {
      "status": "uit",
      "debiet": 0.0,
      "timestamp": 1733926200,
      "last_update": "2025-12-11T14:30:00"
    }
  }
}
```

---

### 2.2 Backend: `fetch_hydronet_gemaal_data.py`

**Bestandslocatie**: `peilbesluiten/fetch_hydronet_gemaal_data.py`

#### Klasse: `HydronetGemaalDataFetcher`

**Verantwoordelijkheden**:
- API communicatie met Hydronet Water Control Room
- Parsing van Highcharts configuratie uit HTML responses
- Data extractie en normalisatie
- GeoJSON parsing voor gemaal codes

#### API Details
- **Base URL**: `https://watercontrolroom.hydronet.com/service/efsserviceprovider/api`
- **Endpoint**: `/chart/{chart_id}?featureIdentifier={gemaal_code}`
- **Chart ID**: `e743fb87-2a02-4f3e-ac6c-03d03401aab8` (Rijnland)
- **Response format**: HTML met Highcharts.chart() configuratie

#### Proces flow
```
fetch_gemaal_data(feature_identifier)
│
├─> HTTP GET naar API
│   └─> Headers: User-Agent, Accept, Referer
│   └─> Params: featureIdentifier
│
├─> Response type check
│   ├─> JSON? → Return direct
│   └─> HTML? → Parse Highcharts config
│
└─> parse_highcharts_config()
    ├─> Regex match: Highcharts.chart('container', {...})
    ├─> JSON.parse() configuratie
    ├─> Extract series data
    ├─> Convert timestamps (ms → datetime)
    ├─> Determine status (debiet > 0.001 → 'aan')
    └─> Return normalized data structure
```

#### Sterke punten
✅ **Robuuste parsing**: Kan zowel JSON als HTML responses verwerken
✅ **Timestamp conversie**: Converteert Unix timestamps naar ISO format
✅ **Status bepaling**: Intelligente logica (debiet > 0.001 m³/s = 'aan')
✅ **Logging**: Uitgebreide logging voor debugging
✅ **Fallback**: Slaat raw responses op bij parse fouten

#### Verbeterpunten
⚠️ **Magic number**: `0.001` threshold voor status hardcoded
⚠️ **Geen retry logic**: Bij 429/503 errors faalt request direct
⚠️ **Geen caching**: Elke call is vers, geen optimalisatie mogelijk
⚠️ **Response parsing**: Regex kan fragiel zijn bij HTML wijzigingen

---

### 2.3 Frontend: `DashboardPanel.vue`

**Bestandslocatie**: `simulatie-peilbeheer/src/components/DashboardPanel.vue`

#### Functionaliteit
Vue 3 component voor visualisatie van geaggregeerde gemaal statistieken.

#### Props
```typescript
interface Props {
  stats: {
    active_stations: number
    total_stations: number
    total_debiet_m3s: number
    generated_at: string
  } | null
}
```

#### UI Structuur
```
┌──────────────────────────────────────────────────────┐
│  DashboardPanel (fixed, top-center)                  │
│  ┌────────────┬──────────────┬─────────────────┐    │
│  │ 🏭 Actieve │ │ 💧 Totaal   │ │ Laatste update │    │
│  │ Gemalen    │ │ Debiet      │ │               │    │
│  │ 12 / 203   │ │ 45.3 m³/s   │ │ 14:30         │    │
│  └────────────┴──────────────┴─────────────────┘    │
└──────────────────────────────────────────────────────┘
```

#### Styling
- **Positioning**: Fixed top-center met transform translate
- **Background**: White with 90% opacity + backdrop blur
- **Design**: Modern card met rounded corners, shadow, blue border
- **Layout**: Flexbox horizontal met dividers
- **Responsive**: Icon + metric + label per section

#### Sterke punten
✅ **Conditional rendering**: `v-if="visible"` voorkomt lege render
✅ **Computed properties**: Efficiënte reactieve data processing
✅ **Null safety**: Fallbacks voor alle data velden
✅ **Formatting**: Debiet afgerond op 1 decimaal, tijd in NL formaat
✅ **Visual hierarchy**: Goede typografie en color contrast

#### Verbeterpunten
⚠️ **Hardcoded emojis**: Overweeg SVG icons voor betere styling control
⚠️ **Geen loading state**: Geen indicator tijdens data fetch
⚠️ **Geen error state**: Geen fallback UI bij data fetch errors
⚠️ **Fixed z-index**: `z-20` kan conflicteren met andere overlays

---

### 2.4 Frontend: `AllLayersMap.vue` (Relevant sections)

**Bestandslocatie**: `simulatie-peilbeheer/src/components/AllLayersMap.vue`

#### Integratie met Dashboard

**Import**:
```javascript
import DashboardPanel from './DashboardPanel.vue'
```

**Usage**:
```vue
<DashboardPanel :stats="gemaalStatus" />
```

#### Data flow (verwacht)
```javascript
// 1. Component mount
onMounted(async () => {
  // 2. Fetch gemaal status
  const response = await fetch('/data/gemaal_status_latest.json')
  gemaalStatus.value = await response.json()

  // 3. DashboardPanel krijgt data via props
  // 4. Panel rendert automatisch via reactivity
})
```

#### Sterke punten
✅ **Component compositie**: Clean separation tussen map en dashboard
✅ **Reactive data**: Vue 3 reactivity zorgt voor auto-updates
✅ **Z-index management**: Dashboard heeft `z-20`, map heeft `z-10`

#### Verbeterpunten
⚠️ **Polling interval**: Geen auto-refresh van data (zie aanbevelingen)
⚠️ **Error handling**: Geen fallback bij failed fetch
⚠️ **Loading state**: Geen indicator tijdens initiële load

---

## 3. Data Flow Analyse

### 3.1 Complete Data Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Data Generation (Cron/Manual)                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
    python generate_gemaal_status.py
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: API Fetching (40-200 seconds)                       │
│                                                              │
│  For each gemaal in GeoJSON:                                │
│    ├─> HydronetGemaalDataFetcher.fetch_gemaal_data()       │
│    ├─> Parse Highcharts config                             │
│    ├─> Extract latest data point                           │
│    └─> Aggregate stats                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: File Write                                          │
│                                                              │
│  Write to: public/data/gemaal_status_latest.json            │
│  Size: ~50-100KB (depends on number of stations)            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Frontend Fetch (on mount / polling)                 │
│                                                              │
│  AllLayersMap.vue:                                          │
│    └─> fetch('/data/gemaal_status_latest.json')            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 5: UI Rendering                                        │
│                                                              │
│  DashboardPanel.vue:                                        │
│    ├─> Receives stats prop                                 │
│    ├─> Computes derived values                             │
│    └─> Renders UI                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Timing Analyse

**Hydronet API Update Frequentie**:
- **Data interval: 30 minuten** - De Hydronet Water Control Room API levert data met 30-minuten intervallen
- Nieuwe datapunten verschijnen op :19 en :49 minuten van elk uur
- Vaker pollen dan elke 15 minuten is niet zinvol (data verandert niet)

**Backend (Python)**:
- Fetch per gemaal: ~0.3-0.5 seconden (API call + parsing)
- Rate limiting: 0.2 seconden tussen calls
- Totaal voor 203 gemalen: **~40-100 seconden**

**Frontend (Vue)**:
- JSON fetch: ~50-200ms (afhankelijk van file size)
- Parse + render: ~10-50ms
- Totaal: **~100-300ms**

**Update cycle**:
- Handmatig: Op aanroep van script
- **Aanbevolen: Elke 15-30 minuten via cron** (afgestemd op API data interval)

---

## 4. Technische Overwegingen

### 4.1 Performance

#### Backend optimalisaties
1. **Parallel fetching**:
   - Huidige implementatie: Sequentieel (40-100 sec)
   - Optimalisatie: Asyncio/concurrent.futures (10-20 sec)

2. **Caching**:
   - Cache API responses voor 1-2 minuten
   - Vermijd duplicate calls binnen korte tijd

3. **Incremental updates**:
   - Alleen fetch voor gemalen die actief zijn (filtering)
   - Update prioriteit: actieve > inactieve gemalen

#### Frontend optimalisaties
1. **Lazy loading**:
   - Laad dashboard data alleen als user navigeert naar map

2. **Polling interval**:
   - Aanbevolen: 5-15 minuten
   - Vermijd te frequente polls (rate limiting)

3. **Cache headers**:
   - Set `Cache-Control: max-age=300` (5 min)

### 4.2 Reliability

#### Error scenarios

| Scenario | Huidige handling | Aanbeveling |
|----------|------------------|-------------|
| API timeout | Exception log, skip gemaal | ✅ OK, maar tel failures |
| Invalid JSON response | Exception log | ✅ OK |
| Missing GeoJSON | Script exit | ✅ OK |
| Alle gemalen falen | Genereert lege summary | ⚠️ Add validation check |
| Frontend fetch fails | Geen UI feedback | ⚠️ Add error state |

#### Recommendations
1. **Health check**: Valideer dat minimaal X% gemalen succesvol zijn
2. **Fallback data**: Behoud vorige versie bij volledige failure
3. **Error UI**: Toon waarschuwing in dashboard bij oude/missing data

### 4.3 Scalability

#### Huidige limieten
- **203 gemalen**: ~40-100 sec fetch tijd (acceptabel)
- **500+ gemalen**: ~100-250 sec (te traag voor sync)

#### Scalability strategie
1. **Asyncio implementation**:
   ```python
   import asyncio
   import aiohttp

   async def fetch_all_gemalen_async(codes):
       async with aiohttp.ClientSession() as session:
           tasks = [fetch_gemaal_async(session, code) for code in codes]
           return await asyncio.gather(*tasks)
   ```

2. **Distributed fetching**:
   - Split gemalen in batches
   - Run multiple workers parallel
   - Merge results

3. **Filtering**:
   - Prioriteer actieve gemalen
   - Less frequent updates voor inactieve gemalen

### 4.4 Security

#### API Access
- ✅ Geen authenticatie vereist (publieke data)
- ✅ HTTPS communicatie
- ⚠️ Rate limiting: Respecteer server limits
- ⚠️ User-Agent spoofing: Overweeg officiële UA

#### Data Exposure
- ✅ Data is publiek beschikbaar
- ✅ Geen privacy gevoelige informatie
- ⚠️ Overweeg rate limiting op frontend API

---

## 5. Aanbevelingen & Roadmap

### 5.1 Prioriteit 1: Critical (Must Have)

#### 1.1 Implement Scheduling
**Probleem**: Script moet handmatig gerund worden

**Oplossing**: Cron job
```bash
# Elke 15 minuten (afgestemd op 30-min API interval)
*/15 * * * * cd /path/to/peilbeheer/peilbesluiten && python3 generate_gemaal_status.py >> logs/cron_gemaal.log 2>&1

# Of elke 30 minuten (minimale frequentie, exact op API interval)
*/30 * * * * cd /path/to/peilbeheer/peilbesluiten && python3 generate_gemaal_status.py >> logs/cron_gemaal.log 2>&1

# Of via systemd timer
[Unit]
Description=Generate Gemaal Status

[Timer]
OnBootSec=5min
OnUnitActiveSec=15min

[Install]
WantedBy=timers.target
```

> **Let op**: De Hydronet API update data elke 30 minuten. Vaker pollen dan elke 15 minuten is niet zinvol.

#### 1.2 Frontend Data Fetching
**Probleem**: `AllLayersMap.vue` heeft geen fetch logic voor gemaal status

**Oplossing**: Implementeer in `AllLayersMap.vue`
```javascript
const gemaalStatus = ref(null)

onMounted(async () => {
  await loadGemaalStatus()
  // Poll elke 15 minuten (afgestemd op 30-min API data interval)
  setInterval(loadGemaalStatus, 15 * 60 * 1000)
})

async function loadGemaalStatus() {
  try {
    const response = await fetch('/data/gemaal_status_latest.json')
    if (response.ok) {
      gemaalStatus.value = await response.json()
    }
  } catch (error) {
    console.error('Failed to load gemaal status:', error)
  }
}
```

#### 1.3 Error Handling UI
**Probleem**: Geen feedback bij data fetch failures

**Oplossing**: Extend `DashboardPanel.vue`
```vue
<template>
  <div v-if="visible" class="dashboard-panel">
    <div v-if="isStale" class="warning-badge">
      ⚠️ Data is ouder dan 30 minuten
    </div>
    <!-- Rest of template -->
  </div>
</template>

<script setup>
const isStale = computed(() => {
  if (!props.stats?.generated_at) return false
  const age = Date.now() - new Date(props.stats.generated_at)
  return age > 30 * 60 * 1000 // 30 minutes
})
</script>
```

### 5.2 Prioriteit 2: Important (Should Have)

#### 2.1 Async Data Fetching
**Probleem**: Sequentiële API calls te traag (40-100 sec)

**Oplossing**: Implementeer asyncio variant
```python
import asyncio
import aiohttp

async def fetch_all_gemalen_async(codes):
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(10)  # Max 10 concurrent
        tasks = [fetch_with_semaphore(session, code, semaphore)
                 for code in codes]
        return await asyncio.gather(*tasks, return_exceptions=True)

# Verwachte tijd: 10-20 seconden
```

#### 2.2 Health Monitoring
**Probleem**: Geen validatie of data quality goed is

**Oplossing**: Add health checks
```python
def validate_summary(summary_data):
    total = summary_data['total_stations']
    success = len([s for s in summary_data['stations'].values()
                   if 'error' not in s])

    success_rate = success / total

    if success_rate < 0.8:
        logger.warning(f"Low success rate: {success_rate:.1%}")
        # Send notification / alert

    return success_rate
```

#### 2.3 Data Caching
**Probleem**: Geen caching, elke call is fresh

**Oplossing**: Implementeer simpele file cache
```python
import hashlib
from datetime import datetime, timedelta

class CachedFetcher(HydronetGemaalDataFetcher):
    def __init__(self, *args, cache_ttl_minutes=5):
        super().__init__(*args)
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)

    def fetch_gemaal_data(self, code):
        cache_file = self.cache_dir / f"{code}.json"

        # Check cache
        if cache_file.exists():
            age = datetime.now() - datetime.fromtimestamp(
                cache_file.stat().st_mtime
            )
            if age < self.cache_ttl:
                with open(cache_file) as f:
                    return json.load(f)

        # Fetch fresh
        data = super().fetch_gemaal_data(code)

        # Update cache
        if data:
            with open(cache_file, 'w') as f:
                json.dump(data, f)

        return data
```

### 5.3 Prioriteit 3: Nice to Have (Could Have)

#### 3.1 Historical Data Storage
**Probleem**: Alleen laatste status, geen trend data

**Oplossing**: Time-series database
```python
# Append to CSV of time-series DB
import pandas as pd

def append_historical_data(summary_data):
    df = pd.DataFrame([{
        'timestamp': summary_data['generated_at'],
        'active_stations': summary_data['active_stations'],
        'total_debiet': summary_data['total_debiet_m3s']
    }])

    df.to_csv('historical_data.csv', mode='a', header=False)
```

#### 3.2 Trend Visualization
**Probleem**: Dashboard toont alleen huidige status

**Oplossing**: Add mini sparkline charts
```vue
<template>
  <div class="trend-chart">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import Chart.js for sparklines
// Show last 24h trend of active stations
</script>
```

#### 3.3 Per-gemaal Details
**Probleem**: Alleen aggregatie, geen details per gemaal

**Oplossing**: Extend AllLayersMap.vue
```javascript
// On gemaal marker click
function showGemaalDetails(gemaalCode) {
  const details = gemaalStatus.value.stations[gemaalCode]

  selectedFeature.value = {
    title: `Gemaal ${gemaalCode}`,
    type: 'Gemaal',
    properties: {
      'Status': details.status === 'aan' ? '🟢 Actief' : '⚫ Uit',
      'Debiet': `${details.debiet} m³/s`,
      'Laatste update': new Date(details.last_update).toLocaleString('nl-NL')
    }
  }
}
```

### 5.4 Prioriteit 4: Future (Won't Have Now)

#### 4.1 Real-time WebSocket Updates
- Replace polling with WebSocket connection
- Instant updates wanneer gemaal status wijzigt

#### 4.2 Predictive Analytics
- ML model voor flow prediction
- Anomaly detection (onverwachte status changes)

#### 4.3 Alert System
- Email/SMS alerts bij critical events
- Threshold-based notifications

---

## 6. Implementation Roadmap

### Phase 1: Baseline (Week 1) ✅ COMPLETED
- [x] Implement `generate_gemaal_status.py`
- [x] Implement `HydronetGemaalDataFetcher`
- [x] Create `DashboardPanel.vue`
- [x] Integrate in `AllLayersMap.vue`

### Phase 2: Production Ready (Week 2)
- [ ] Implement frontend data fetching
- [ ] Add error handling UI
- [ ] Setup cron job for automatic updates
- [ ] Add data staleness detection
- [ ] Testing & bug fixes

### Phase 3: Optimization (Week 3)
- [ ] Implement async fetching (asyncio)
- [ ] Add data caching
- [ ] Health monitoring
- [ ] Performance testing
- [ ] Documentation

### Phase 4: Enhancement (Week 4)
- [ ] Historical data storage
- [ ] Trend visualization
- [ ] Per-gemaal detail view
- [ ] Alert system (basic)

---

## 7. Testing Strategy

### 7.1 Backend Testing

#### Unit Tests
```python
# test_generate_gemaal_status.py
import pytest
from generate_gemaal_status import main

def test_summary_structure():
    # Mock fetcher
    # Run generation
    # Assert JSON structure
    pass

def test_aggregation_logic():
    # Test met mock data
    # Verify active_stations count
    # Verify total_debiet calculation
    pass
```

#### Integration Tests
```python
def test_api_fetch():
    fetcher = HydronetGemaalDataFetcher(CHART_ID, temp_dir)
    data = fetcher.fetch_gemaal_data("176-036-00021")

    assert data is not None
    assert 'series' in data
    assert len(data['series']) > 0
```

### 7.2 Frontend Testing

#### Component Tests
```javascript
import { mount } from '@vue/test-utils'
import DashboardPanel from './DashboardPanel.vue'

describe('DashboardPanel', () => {
  it('renders stats correctly', () => {
    const wrapper = mount(DashboardPanel, {
      props: {
        stats: {
          active_stations: 12,
          total_stations: 203,
          total_debiet_m3s: 45.327,
          generated_at: '2025-12-11T14:30:00'
        }
      }
    })

    expect(wrapper.text()).toContain('12 / 203')
    expect(wrapper.text()).toContain('45.3')
  })

  it('hides when stats is null', () => {
    const wrapper = mount(DashboardPanel, {
      props: { stats: null }
    })

    expect(wrapper.html()).toBe('')
  })
})
```

### 7.3 End-to-End Testing

```javascript
// Using Playwright/Cypress
describe('Gemaal Dashboard', () => {
  it('loads and displays dashboard', async () => {
    await page.goto('/map')

    // Wait for data fetch
    await page.waitForSelector('.dashboard-panel')

    // Verify data is displayed
    const activeText = await page.textContent('.active-stations')
    expect(activeText).toMatch(/\d+ \/ \d+/)
  })
})
```

---

## 8. Monitoring & Observability

### 8.1 Metrics te Tracken

**Backend Metrics**:
- Fetch duration per gemaal (p50, p95, p99)
- Success rate per run
- Total run duration
- API error rate
- Data freshness

**Frontend Metrics**:
- JSON fetch time
- Render time
- User interactions with dashboard
- Error rate

### 8.2 Logging Strategy

**Backend**:
```python
logger.info(f"Fetch started: {len(codes)} gemalen")
logger.info(f"[{i}/{total}] Processing {code}")
logger.error(f"Failed to fetch {code}: {error}")
logger.info(f"Fetch completed: {success}/{total} successful")
```

**Frontend**:
```javascript
console.log('[GemaalDashboard] Fetching status...')
console.error('[GemaalDashboard] Fetch failed:', error)
console.warn('[GemaalDashboard] Data is stale:', age)
```

### 8.3 Alerting

**Critical Alerts**:
- Script failure (no JSON generated)
- Success rate < 50%
- Data older than 30 minutes
- API completely down

**Warning Alerts**:
- Success rate < 80%
- Fetch duration > 2 minutes
- Individual gemaal failures

---

## 9. Documentatie Referenties

### Bestaande Documentatie
1. **[RIJNLAND_DYNAMISCHE_DATA.md](peilbesluiten/RIJNLAND_DYNAMISCHE_DATA.md)**
   - API endpoints Rijnland
   - Update frequenties
   - Data structuren
   - Beperkingen

### Nieuwe Documentatie Needed
1. **DEPLOYMENT.md**
   - Setup instructies
   - Cron configuratie
   - Environment variables

2. **API.md**
   - Hydronet API details
   - Rate limits
   - Error codes

3. **TROUBLESHOOTING.md**
   - Common errors
   - Debug procedures
   - FAQ

---

## 10. Conclusie

### Huidige Status: MVP ✅

Het systeem is **functioneel** maar mist **productionisatie** features:

**✅ Werkt**:
- Data wordt correct opgehaald
- JSON wordt gegenereerd met correcte structuur
- Dashboard toont data mooi

**⚠️ Mist**:
- Automatische scheduling
- Frontend data fetch logic
- Error handling
- Performance optimalisatie

### Next Steps (Priority Order)

1. **Week 1**: Implement frontend fetch + cron scheduling
2. **Week 2**: Error handling + monitoring
3. **Week 3**: Performance optimization (async)
4. **Week 4**: Enhancements (historical, trends)

### Success Criteria

Het systeem is **production-ready** wanneer:
- ✅ Data wordt automatisch elke 10 min bijgewerkt
- ✅ Frontend haalt data op en toont dashboard
- ✅ Error states worden correct afgehandeld
- ✅ Fetch tijd < 30 seconden (met async)
- ✅ Success rate > 90%
- ✅ Monitoring en alerting actief

---

**Einde Architectuurplan**
