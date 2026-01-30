# Peilbeheer Visualisatie - Rijnland Kaartlagen

Interactieve kaart applicatie voor het visualiseren van Rijnland waterbeheer data, inclusief peilgebieden, gemalen, stuwen en een geavanceerde regen-simulatie.

## Features

- 🗺️ **Alle Rijnland Kaartlagen**: 60+ kaartlagen beschikbaar (Peilgebieden, Gemalen, Stuwen, etc.).
- 📊 **Real-time Digital Twin**: Live status van gemalen (blauw = actief, grijs = stand-by).
- 🌧️ **Regenbui Simulatie**: Simuleer wateroverlast in specifieke peilgebieden.
- ⛽ **Slimme Pompsturing**: Geavanceerde **PID-regeling** voor gemalen in de simulatie voor stabiel peilbeheer.
- 📈 **Interactieve Grafiek**: Visualisatie van waterstand, regenintensiteit en gemaal-inzet.
- 📱 **Responsive Design**: Optimaal voor gebruik op diverse schermen.

## Lokale Development

```bash
# Ga naar de web directory
cd web

# Installeer dependencies
npm install

# Start development server
npm run dev
```

## Structuur

```
web/
├── src/
│   ├── components/
│   │   ├── RegenbuiSimulatie.vue  # Hoofdkaart simulatie & monitoring
│   │   ├── SimulatiePanel.vue     # Interactief paneel voor parameters
│   │   ├── WaterstandGrafiek.vue  # Chart.js grafiek met PID-output
│   │   ├── AllLayersMap.vue       # Overzichtskaart alle lagen
│   │   └── ...
│   ├── utils/
│   │   └── waterbalans.js         # Kern-engine met PID-algoritme
│   └── App.vue
├── public/
│   └── data/                      # GeoJSON en status JSON data
└── vite.config.js
```

## Technologie

- **Vue 3** - Frontend framework (Composition API)
- **Leaflet** - Kaart visualisatie met `shallowRef` voor performance
- **Chart.js** - Data visualisatie voor waterstanden
- **Tailwind CSS** - Moderne UI styling
- **Vite** - Build tool
- **Proj4** - RD naar WGS84 coördinaat transformaties

## Licentie

Water Natuurlijk Rijnland
