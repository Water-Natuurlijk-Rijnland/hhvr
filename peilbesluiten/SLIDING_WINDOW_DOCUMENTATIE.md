# Sliding Window Processor Documentatie

## Overzicht

De sliding window processor implementeert real-time trend detectie en aggregaties voor gemaal timeseries data, gebaseerd op hoofdstuk 4 van het Digital Twins boek.

## Functionaliteit

### Wat doet het?

In plaats van alleen het laatste datapunt te gebruiken, analyseert de sliding window processor **alle datapunten binnen een tijdvenster** om:

1. **Trends te detecteren**: Is het debiet stijgend, dalend of stabiel?
2. **Aggregaties te berekenen**: Gemiddelde, min, max over het venster
3. **Veranderingen te meten**: Percentage verandering over tijd
4. **Betrouwbaarheid te bepalen**: R² waarde voor trend kwaliteit

### Waarom sliding windows?

- **Noise filtering**: Enkele uitschieters worden gefilterd door naar trends te kijken
- **Real-time**: Geen wachten op batch completion, trends worden continu bijgewerkt
- **Meerdere tijdvensters**: Kort termijn (30 min) vs lang termijn (3 uur) trends

## Gebruik

### Basis Gebruik

```python
from sliding_window_processor import SlidingWindowProcessor
from datetime import datetime, timedelta

# Maak processor met 30 minuten venster
processor = SlidingWindowProcessor(window_minutes=30)

# Voeg datapunten toe
processor.add_data_point(datetime.now(), 2.5)  # debiet in m³/s
processor.add_data_point(datetime.now() - timedelta(minutes=5), 2.3)
processor.add_data_point(datetime.now() - timedelta(minutes=10), 2.1)

# Haal metrics op
metrics = processor.get_all_metrics()
print(f"Trend: {metrics['trend']['direction']}")
print(f"Gemiddeld: {metrics['avg_debiet']} m³/s")
```

### Met Timeseries Data

```python
from sliding_window_processor import process_gemaal_series

# Series data zoals van Hydronet API
series_data = [
    {
        'timestamp_ms': 1733926200000,
        'value': 2.5,
        'status': 'aan'
    },
    # ... meer punten
]

# Verwerk met meerdere vensters
result = process_gemaal_series(
    gemaal_code="176-036-00021",
    series_data=series_data,
    windows_minutes=[30, 60, 180]  # 30 min, 1 uur, 3 uur
)

print(f"Kort termijn trend: {result['summary']['short_term_trend']}")
```

### Multi-Window Processor

Voor verschillende tijdvensters tegelijk:

```python
from sliding_window_processor import MultiWindowProcessor

processor = MultiWindowProcessor(windows_minutes=[30, 60, 180])

# Voeg data toe (wordt automatisch aan alle vensters toegevoegd)
processor.add_data_point(timestamp, value)

# Haal alle metrics op
all_metrics = processor.get_all_metrics()

# Kort termijn (30 min)
print(all_metrics['30_min']['trend'])

# Lang termijn (180 min)
print(all_metrics['180_min']['trend'])
```

## Integratie in generate_gemaal_status.py

De sliding window processor is geïntegreerd in `generate_gemaal_status.py`. Bij elke run worden nu automatisch trends berekend:

```json
{
  "stations": {
    "176-036-00021": {
      "status": "aan",
      "debiet": 3.456,
      "trends": {
        "30_min": {
          "direction": "increasing",
          "slope_per_hour": 0.15,
          "strength": "moderate",
          "r_squared": 0.85
        },
        "60_min": { ... },
        "180_min": { ... }
      },
      "window_stats": {
        "30_min": {
          "count": 6,
          "avg": 3.2,
          "min": 2.8,
          "max": 3.6
        }
      },
      "summary": {
        "overall_status": "increasing",
        "short_term_trend": { ... }
      }
    }
  }
}
```

## Output Structuur

### Trend Object

```python
{
    "direction": "increasing" | "decreasing" | "stable",
    "slope": 0.0000417,  # Verandering per seconde
    "slope_per_hour": 0.15,  # Verandering per uur (handiger)
    "strength": "strong" | "moderate" | "weak",
    "r_squared": 0.85  # Betrouwbaarheid (0-1)
}
```

### Window Stats

```python
{
    "count": 6,  # Aantal datapunten in venster
    "min": 2.8,
    "max": 3.6,
    "avg": 3.2,
    "sum": 19.2,
    "first_value": 2.8,
    "last_value": 3.6,
    "window_start": "2025-12-11T14:00:00",
    "window_end": "2025-12-11T14:30:00",
    "window_duration_minutes": 30
}
```

## Venster Groottes

Aanbevolen venster groottes voor gemaal data:

- **30 minuten**: Kort termijn trends, snelle veranderingen
- **60 minuten**: Medium termijn, dagelijkse patronen
- **180 minuten (3 uur)**: Lang termijn trends, seizoenspatronen
- **360 minuten (6 uur)**: Zeer lang termijn, dag/nacht cycli

## Algoritme Details

### Trend Berekening

De trend wordt berekend met **lineaire regressie**:

```
y = mx + b

waar:
- y = debiet waarde
- x = tijd (seconden vanaf eerste punt)
- m = slope (trend)
- b = intercept
```

De **R² waarde** geeft aan hoe goed de lineaire trend past:
- R² > 0.8: Sterke trend
- R² > 0.5: Matige trend
- R² < 0.5: Zwakke trend (veel variatie)

### Sliding Window Mechanisme

1. Nieuw datapunt wordt toegevoegd
2. Oude punten buiten het venster worden verwijderd
3. Statistieken worden herberekend
4. Trend wordt opnieuw berekend

Dit gebeurt **continu** zonder te wachten op batch completion.

## Testen

Run de test script om de functionaliteit te testen:

```bash
cd peilbesluiten
python test_sliding_window.py
```

Dit test:
- Basis sliding window functionaliteit
- Multi-window processor
- Gemaal series processing
- Edge cases (te weinig data, constante waarden)

## Performance

- **Memory**: O(n) waar n = aantal punten in venster
- **Time**: O(n) voor trend berekening
- **Typisch**: 30 min venster = ~6 punten (elke 5 min) = zeer snel

## Toekomstige Uitbreidingen

Mogelijke verbeteringen:
- [ ] Exponential moving average voor smoothing
- [ ] Anomalie detectie binnen venster
- [ ] Seizoenspatroon detectie
- [ ] Voorspelling op basis van trends
- [ ] Persistente storage van window state

## Referenties

- Hoofdstuk 4: "Data integration and management" - Digital Twins boek
- Sectie 4.4.2: "Streaming data ingestion" - Sliding windows
- Figuur 4.8: Sliding window illustratie

