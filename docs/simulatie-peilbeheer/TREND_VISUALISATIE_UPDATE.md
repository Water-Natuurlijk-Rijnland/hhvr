# Trend Visualisatie Update

**Datum**: 2025-12-18  
**Update**: Dashboard uitbreiding met sliding window trend visualisaties

## Wat is er toegevoegd

### 1. TrendIndicator Component (`src/components/TrendIndicator.vue`)

Nieuwe Vue component voor het visueel weergeven van trends:

**Features:**
- Trend richting indicatoren (↑ ↓ →)
- Kleurcodering (groen voor stijgend, rood voor dalend, grijs voor stabiel)
- Trend sterkte (strong/moderate/weak)
- Optionele labels
- Tooltips met gedetailleerde informatie

**Props:**
- `trend`: Trend object met direction, strength, slope_per_hour, r_squared
- `showLabel`: Boolean om label te tonen/verbergen
- `size`: 'small', 'normal', 'large'

### 2. DashboardPanel Uitbreiding (`src/components/DashboardPanel.vue`)

**Nieuwe features:**
- Trend indicator naast totaal debiet
- Uitklapbaar trend overzicht sectie
- Trend statistieken per venster (30 min, 1 uur, 3 uur)
- Trend tellingen (aantal stijgend/dalend/stabiel)

**Visualisatie:**
```
┌─────────────────────────────────────────┐
│ 🏭 Actieve Gemalen    💧 Totaal Debiet ↗│
│   12 / 203            45.3 m³/s        │
│                                        │
│ ──────────────────────────────────────│
│ 📈 Trend Overzicht [+/-]               │
│ ┌─────────┬─────────┬─────────┐      │
│ │ 30 min   │ 1 uur   │ 3 uur   │      │
│ │ ↗ Stijgend│ → Stabiel│ ↗ Stijgend│      │
│ │ 5↑ 2↓ 3→ │ 4↑ 3↓ 3→ │ 6↑ 2↓ 2→ │      │
│ └─────────┴─────────┴─────────┘      │
└─────────────────────────────────────────┘
```

### 3. Info Panel Uitbreiding (`src/components/AllLayersMap.vue`)

**Nieuwe features:**
- Trend analyse sectie voor geselecteerde gemalen
- Huidige status met debiet
- Trends per venster (30 min, 1 uur, 3 uur)
- Statistieken per venster (gemiddeld, min, max, aantal punten)
- Trend richting en sterkte
- R² betrouwbaarheid scores

**Visualisatie:**
```
┌─────────────────────────────────┐
│ Gemaal Zwetterpolder        [×]│
│ GEMALEN                        │
│                                │
│ ... basis properties ...       │
│                                │
│ ──────────────────────────────│
│ 📈 Trend Analyse               │
│                                │
│ Huidige Status                 │
│ [AAN] 0.440 m³/s              │
│                                │
│ 30 minuten                     │
│ Stijgend (moderate)            │
│ ↗ 0.150 m³/s/uur • R²: 85%    │
│                                │
│ Statistieken                   │
│ 30 minuten                     │
│ Gem: 0.420  Min-Max: 0.200-0.6 │
│ Punten: 6  Duur: 30 min        │
└─────────────────────────────────┘
```

## Data Structuur

De sliding window processor voegt de volgende data toe aan elk gemaal:

```json
{
  "stations": {
    "176-036-00021": {
      "status": "aan",
      "debiet": 0.440,
      "trends": {
        "30_min": {
          "direction": "increasing",
          "strength": "moderate",
          "slope_per_hour": 0.150,
          "r_squared": 0.85
        },
        "60_min": { ... },
        "180_min": { ... }
      },
      "window_stats": {
        "30_min": {
          "count": 6,
          "avg": 0.420,
          "min": 0.200,
          "max": 0.600,
          "window_duration_minutes": 30.0
        }
      },
      "summary": {
        "overall_status": "increasing"
      }
    }
  },
  "aggregate_trends": {
    "30_min": {
      "increasing": 5,
      "decreasing": 2,
      "stable": 3
    }
  }
}
```

## Gebruik

### Dashboard Trends

1. Open het dashboard
2. Klik op "📈 Trend Overzicht" om trends uit te klappen
3. Zie trends per venster (30 min, 1 uur, 3 uur)
4. Zie tellingen van stijgend/dalend/stabiel per venster

### Gemaal Trends

1. Klik op een gemaal op de kaart
2. Info panel opent rechts
3. Scroll naar "📈 Trend Analyse" sectie
4. Zie gedetailleerde trends en statistieken

## Kleuren

- **Groen**: Stijgende trend (increasing)
- **Rood**: Dalende trend (decreasing)
- **Grijs**: Stabiele trend (stable)

## Iconen

- **↗**: Sterk stijgend
- **↑**: Matig/zwak stijgend
- **↘**: Sterk dalend
- **↓**: Matig/zwak dalend
- **→**: Stabiel

## Technische Details

### Computed Properties

- `overallTrend`: Berekent overall trend van aggregate trends
- `aggregateTrends`: Berekent dominante trend per venster
- `selectedGemaalTrends`: Haalt trend data op voor geselecteerd gemaal
- `selectedGemaalStatus`: Haalt status data op voor geselecteerd gemaal

### Helper Functions

- `getWindowLabel()`: Converteert window key naar leesbare label
- `getTrendLabel()`: Converteert trend direction naar Nederlands label
- `getTrendColorClass()`: Retourneert CSS class voor trend kleur
- `getTrendCount()`: Telt trends per venster en richting

## Volgende Stappen

1. ✅ Trend visualisatie geïmplementeerd
2. ⏭️ Test met echte data (na `generate_gemaal_status.py` update)
3. ⏭️ Optioneel: Sparkline charts voor trend visualisatie
4. ⏭️ Optioneel: Alert systeem op basis van trends

## Testen

1. Run `generate_gemaal_status.py` om data met trends te genereren
2. Open dashboard in browser
3. Controleer of trends worden getoond
4. Klik op een gemaal en controleer trend analyse

## Notities

- Trends worden alleen getoond als `gemaal_status_latest.json` trend data bevat
- Als er geen trend data is, wordt de trend sectie niet getoond
- Alle trend berekeningen gebeuren server-side in Python
- Frontend toont alleen de berekende trends

