# Gemaal Data Skill - Gebruiksdocumentatie

Deze Claude skill biedt functionaliteit voor het ophalen en analyseren van gemaal data van de Hydronet Water Control Room API, inclusief geavanceerde sliding window trend analyse.

## Overzicht

De `gemaal-data` skill bestaat uit vier hoofdfuncties:

1. **fetch-gemaal-data** - Haal real-time data op voor een specifiek gemaal
2. **process-sliding-windows** - Analyseer tijdreeks data met sliding window trend detectie
3. **refresh-all-gemalen** - Ververs alle gemaal data en genereer nieuwe JSON output
4. **auto-refresh-gemaal-data** - Automatische periodieke data refresh elke 30 minuten

## Installatie

De skill is automatisch beschikbaar in je Claude Code omgeving. De benodigde Python dependencies worden beheerd via een lokale virtual environment in `.claude/skills/venv/`.

### Vereisten

- Python 3.8+
- `requests` library (automatisch geïnstalleerd in skills venv)

Als de skills niet werken, voer dan uit:

```bash
cd .claude/skills
python3 -m venv venv
venv/bin/pip install requests
```

## Gebruik

### 1. Fetch Gemaal Data

Haal real-time data op voor een specifiek gemaal van de Hydronet API.

**Syntax:**
```bash
.claude/skills/fetch-gemaal-data.sh <gemaal_code> [options]
```

**Parameters:**
- `gemaal_code` (vereist): De code van het gemaal (bijv. `176-036-00021`)
- `--output-format {json,pretty,summary}`: Output formaat (default: pretty)
- `--include-raw`: Inclusief ruwe API response in output

**Voorbeelden:**

```bash
# Pretty formatted output (menselijk leesbaar)
.claude/skills/fetch-gemaal-data.sh 176-036-00021

# Compacte samenvatting
.claude/skills/fetch-gemaal-data.sh 176-036-00021 --output-format summary

# JSON output voor verdere verwerking
.claude/skills/fetch-gemaal-data.sh 176-036-00021 --output-format json
```

**Output (summary format):**
```json
{
  "gemaal": "176-036-00021",
  "status": "aan",
  "debiet": "0.200 m³/s",
  "timestamp": "2025-12-18T12:05:00",
  "datapunten": 650
}
```

**Output (pretty format):**
```
============================================================
GEMAAL DATA REPORT: 176-036-00021
============================================================

Status:           AAN
Debiet:           0.200 m³/s
Timestamp:        2025-12-18T12:05:07
Totaal punten:    650

Tijd range:
  Start:  2025-12-04T23:35:07
  Eind:   2025-12-18T12:05:07

Statistieken:
  Min:    0.000 m³/s
  Max:    0.400 m³/s
  Gem:    0.055 m³/s

============================================================
```

---

### 2. Process Sliding Windows

Verwerk tijdreeks data met geavanceerde sliding window analyse voor trend detectie.

**Syntax:**
```bash
.claude/skills/process-sliding-windows.sh [options]
```

**Parameters:**
- `--gemaal-code <code>`: Code van het gemaal (vereist bij `--data-source api`)
- `--data-source {api,json}`: Data bron (default: api)
  - `api`: Haal data op van Hydronet API
  - `json`: Gebruik bestaande JSON file
- `--json-path <path>`: Pad naar JSON bestand (voor data-source=json)
- `--window-sizes <sizes>`: Comma-separated window sizes in minuten (default: 30,60,180)
- `--output-format {json,pretty,trends-only}`: Output formaat (default: pretty)

**Voorbeelden:**

```bash
# Analyse met standaard windows (30, 60, 180 min)
.claude/skills/process-sliding-windows.sh --gemaal-code 176-036-00021

# Custom window sizes (15, 30, 45 minuten)
.claude/skills/process-sliding-windows.sh \
  --gemaal-code 176-036-00021 \
  --window-sizes 15,30,45

# Alleen trends output (compact)
.claude/skills/process-sliding-windows.sh \
  --gemaal-code 176-036-00021 \
  --output-format trends-only

# Analyseer data uit bestaand JSON bestand
.claude/skills/process-sliding-windows.sh \
  --gemaal-code 176-036-00021 \
  --data-source json \
  --json-path simulatie-peilbeheer/public/data/gemaal_status_latest.json
```

**Output (trends-only format):**
```json
{
  "gemaal": "176-036-00021",
  "trends": {
    "30_min": {
      "slope": -0.000111,
      "slope_per_hour": -0.4,
      "direction": "stable",
      "r_squared": 1.0,
      "strength": "weak"
    },
    "60_min": {
      "slope": -0.000056,
      "slope_per_hour": -0.2,
      "direction": "stable",
      "r_squared": 0.75,
      "strength": "weak"
    },
    "180_min": {
      "slope": 0.000036,
      "slope_per_hour": 0.129,
      "direction": "stable",
      "r_squared": 0.596,
      "strength": "weak"
    }
  },
  "overall": "stable"
}
```

**Output (pretty format):**
```
======================================================================
SLIDING WINDOW ANALYSE: 176-036-00021
======================================================================

Data bron:        api
Verwerkte punten: 650
Window sizes:     30, 60, 180 minuten

----------------------------------------------------------------------
WINDOW: 30 minuten
----------------------------------------------------------------------

Statistieken:
  Punten:       2
  Min:          0.200 m³/s
  Max:          0.400 m³/s
  Gemiddeld:    0.300 m³/s
  Totaal:       0.600 m³

Trend:
  Richting:     → STABLE
  Sterkte:      WEAK
  Slope/uur:    -0.4000 m³/s
  R²:           1.000
  Verandering:  0.0%

[... meer windows ...]

======================================================================
OVERALL STATUS: STABLE
======================================================================

Short-term:  stable (weak)
Medium-term: stable (weak)
Long-term:   stable (weak)
```

---

### 3. Refresh All Gemalen

Ververs alle gemaal data en genereer nieuwe JSON output met sliding window trends.

**Syntax:**
```bash
python3 peilbesluiten/generate_gemaal_status.py [options]
```

**Parameters:**
- `--output-path <path>`: Pad voor output JSON (default: simulatie-peilbeheer/public/data/gemaal_status_latest.json)
- `--rate-limit-seconds <sec>`: Seconden tussen API requests (default: 0.5)

**Voorbeeld:**
```bash
cd /Users/marc/Projecten/peilbeheer
python3 peilbesluiten/generate_gemaal_status.py
```

**Output:**
Genereert een JSON bestand met data voor ~377 gemalen inclusief:
- Status (aan/uit)
- Debiet (m³/s)
- Timestamp
- Sliding window trends (30, 60, 180 min)
- Window statistieken
- Overall trend samenvatting

---

### 4. Auto Refresh Gemaal Data

Automatische periodieke data refresh die elke 30 minuten (configureerbaar) nieuwe gemaal data ophaalt.

**Syntax:**
```bash
.claude/skills/auto-refresh-gemaal-data.sh [options]
```

**Parameters:**
- `--interval <minuten>`: Interval tussen refreshes in minuten (default: 30)
- `--max-cycles <aantal>`: Maximum aantal refresh cycli, 0 = oneindig (default: 0)
- `--run-once`: Voer slechts één refresh uit en stop
- `--output-path <path>`: Pad naar output JSON bestand
- `--log-file <path>`: Optioneel log bestand

**Voorbeelden:**

```bash
# Start auto-refresh met standaard 30 minuten interval (blijft draaien)
.claude/skills/auto-refresh-gemaal-data.sh

# Custom interval van 15 minuten
.claude/skills/auto-refresh-gemaal-data.sh --interval 15

# Voer 5 refresh cycli uit en stop
.claude/skills/auto-refresh-gemaal-data.sh --max-cycles 5

# Eenmalige refresh (handig voor cron jobs)
.claude/skills/auto-refresh-gemaal-data.sh --run-once

# Met custom interval en log bestand
.claude/skills/auto-refresh-gemaal-data.sh \
  --interval 20 \
  --log-file /var/log/gemaal-refresh.log
```

**Output (JSON per cyclus):**
```json
{
  "success": true,
  "timestamp": "2025-12-18T23:17:55.123456",
  "duration_seconds": 125.5,
  "output_file": "/path/to/gemaal_status_latest.json",
  "file_updated": "2025-12-18T23:17:55"
}
```

**Gebruik als service (systemd):**

Maak een systemd service voor continue auto-refresh:

```bash
# /etc/systemd/system/gemaal-auto-refresh.service
[Unit]
Description=Gemaal Data Auto Refresh Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/peilbeheer
ExecStart=/path/to/peilbeheer/.claude/skills/auto-refresh-gemaal-data.sh --interval 30
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Gebruik met cron (alternatief):**

Voor periodieke updates zonder continue proces:

```bash
# Elke 30 minuten
*/30 * * * * cd /path/to/peilbeheer && .claude/skills/auto-refresh-gemaal-data.sh --run-once

# Elk uur
0 * * * * cd /path/to/peilbeheer && .claude/skills/auto-refresh-gemaal-data.sh --run-once
```

**Graceful shutdown:**

Het proces kan gestopt worden met `Ctrl+C` of `SIGTERM` signal. Het zal de huidige cyclus afmaken voordat het stopt.

```bash
# Stop het proces
pkill -TERM -f auto_refresh_gemaal_data.py

# Of met Ctrl+C in de terminal
```

---

## Trend Analyse Uitleg

### Trend Direction
- **increasing** (↗): Debiet neemt toe
- **decreasing** (↘): Debiet neemt af  
- **stable** (→): Debiet blijft stabiel

**Thresholds:**
- Stable: |slope| < 0.001 m³/s per seconde
- Moderate: 0.001 ≤ |slope| ≤ 0.01
- Strong: |slope| > 0.01

### Trend Strength
- **weak**: Lage betrouwbaarheid (R² < 0.5)
- **moderate**: Gemiddelde betrouwbaarheid (0.5 ≤ R² < 0.8)
- **strong**: Hoge betrouwbaarheid (R² ≥ 0.8)

### Metrics Uitleg

- **slope**: Verandering per seconde (m³/s per seconde)
- **slope_per_hour**: Verandering per uur (m³/s per uur)
- **r_squared**: Betrouwbaarheid van lineaire regressie (0-1)
- **change_percentage**: Percentage verandering tussen eerste en laatste waarde

---

## Gebruik in Claude Code

Je kunt deze skills gebruiken in conversaties met Claude Code:

**Voorbeelden:**

> "Haal de data op voor gemaal 176-036-00021"

Claude zal automatisch de fetch-gemaal-data skill gebruiken.

> "Analyseer de trends voor gemaal 176-036-00021 met 30, 60 en 180 minuten windows"

Claude zal de process-sliding-windows skill gebruiken.

> "Ververs alle gemaal data"

Claude zal de refresh-all-gemalen functie aanroepen.

---

## Technische Details

### Architectuur

```
.claude/skills/
├── gemaal-data.skill           # Skill configuratie
├── fetch-gemaal-data.sh        # Wrapper voor fetch skill
├── process-sliding-windows.sh  # Wrapper voor sliding window skill
├── venv/                       # Python virtual environment
│   └── lib/python3.x/
│       └── site-packages/
│           └── requests/       # API client library
└── README.md                   # Deze documentatie

peilbesluiten/skills/
├── fetch_gemaal_data_skill.py         # Fetch implementatie
└── process_sliding_windows_skill.py   # Sliding window implementatie

peilbesluiten/
├── fetch_hydronet_gemaal_data.py   # Hydronet API wrapper
├── sliding_window_processor.py     # Trend analyse algoritmes
└── generate_gemaal_status.py       # Batch verversing
```

### Data Flow

```
Hydronet API
    ↓
fetch_hydronet_gemaal_data.py (API wrapper)
    ↓
sliding_window_processor.py (trend analyse)
    ↓
JSON output / Skill output
```

### Dependencies

- **Python 3.8+**: Runtime
- **requests**: HTTP client voor Hydronet API
- **pathlib**: Bestandspad handling
- **datetime**: Tijdstempel verwerking
- **json**: JSON parsing en generatie
- **argparse**: Command-line argument parsing

---

## Troubleshooting

### Error: "Python with 'requests' module not found"

**Oplossing:**
```bash
cd .claude/skills
python3 -m venv venv
venv/bin/pip install requests
```

### Error: "Geen data gevonden voor dit gemaal"

**Mogelijke oorzaken:**
- Gemaal code is incorrect
- Gemaal heeft geen data in Hydronet systeem
- API is tijdelijk niet beschikbaar

**Oplossing:**
- Controleer gemaal code spelling
- Probeer een andere gemaal code
- Wacht enkele minuten en probeer opnieuw

### Rate Limiting

Bij het ophalen van veel gemalen kan je rate limiting tegenkomen.

**Oplossing:**
- Verhoog `--rate-limit-seconds` parameter
- Gebruik 0.5-1.0 seconden tussen requests (aanbevolen)

---

## CCG Richtlijnen (Verantwoord Gegevensgebruik)

Deze skill implementeert CCG richtlijnen:

1. **Data Validatie**: 
   - Debiet tussen 0-1000 m³/s
   - Data niet ouder dan 2 uur

2. **Privacy**: 
   - Alleen technische gemaal data (geen persoonlijke gegevens)
   - Publieke API data

3. **Rate Limiting**: 
   - Respect voor API server (0.5s tussen requests)
   - Geen excessive polling

4. **Error Handling**: 
   - Graceful degradation bij API fouten
   - Logging voor debugging

---

## Changelog

### Version 1.1.0 (2025-12-18)
- **NIEUW**: Auto-refresh gemaal data skill
  - Periodieke data updates elke 30 minuten (configureerbaar)
  - Geschikt voor systemd service of cron jobs
  - Graceful shutdown support
  - JSON output per cyclus
- Correctie: 377 gemalen (niet 203)
- Verbeterde documentatie met deployment voorbeelden

### Version 1.0.0 (2025-12-18)
- Initiële release
- Fetch gemaal data skill
- Sliding window processing skill
- Support voor meerdere output formats
- CCG compliance
- Volledige documentatie

---

## Licentie

Deze skill is onderdeel van het Peilbeheer project.

## Contact

Voor vragen of problemen, raadpleeg de repository documentatie of maak een issue aan.
