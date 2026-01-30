# Peilbeheer Visualisatie - Rijnland Kaartlagen

Interactieve kaart applicatie voor het visualiseren van Rijnland waterbeheer data, inclusief peilgebieden, gemalen, stuwen en andere infrastructuur.

## Features

- 🗺️ **Alle Rijnland Kaartlagen**: 60+ kaartlagen beschikbaar
- 📊 **Hover Informatie**: Zomer- en winterpeil bij hover over peilgebieden
- 🏭 **Real-time Gemaal Data**: Live pompsnelheden en status
- 🎨 **Interactieve Legenda**: Categorieën met laagbeheer
- 📱 **Responsive Design**: Werkt op desktop en mobiel

## Lokale Development

```bash
# Installeer dependencies
npm install

# Start development server
npm run dev

# Build voor productie
npm run build
```

## GitHub Pages Deployment

De applicatie wordt automatisch gedeployed naar GitHub Pages via GitHub Actions wanneer er naar de `main` branch wordt gepusht.

### Kaartlagen Setup

De kaartlagen (GeoJSON bestanden) zijn nodig voor de volledige functionaliteit. Er zijn twee opties:

#### Optie 1: Lokale Kaartlagen (Aanbevolen voor Development)

1. Download de kaartlagen met het Python script:
```bash
cd ../peilbesluiten
python3 download_rijnland_layers.py
```

2. De kaartlagen worden automatisch gekopieerd naar `public/peilbesluiten/rijnland_kaartlagen/` tijdens de build

#### Optie 2: Server Fallback

Als lokale kaartlagen niet beschikbaar zijn, gebruikt de applicatie automatisch de ArcGIS server als fallback.

### GitHub Pages Configuratie

1. Ga naar **Settings** → **Pages** in je GitHub repository
2. Selecteer **Source**: `GitHub Actions`
3. De workflow zal automatisch draaien bij elke push naar `main`

De applicatie is beschikbaar op: `https://water-natuurlijk-rijnland.github.io/hhvr/`

## Structuur

```
simulatie-peilbeheer/
├── src/
│   ├── components/
│   │   ├── AllLayersMap.vue      # Hoofdcomponent met alle lagen
│   │   ├── PolderMap.vue        # Polder simulatie
│   │   └── ...
│   └── App.vue
├── public/
│   └── peilbesluiten/           # Kaartlagen worden hier gekopieerd
├── scripts/
│   └── copy-kaartlagen.js       # Script om kaartlagen te kopiëren
└── .github/
    └── workflows/
        └── deploy.yml           # GitHub Actions deployment
```

## Technologie

- **Vue 3** - Frontend framework
- **Leaflet** - Kaart visualisatie
- **Tailwind CSS** - Styling
- **Vite** - Build tool
- **Proj4** - Coördinaat transformatie (RD → WGS84)

## Licentie

Water Natuurlijk Rijnland
