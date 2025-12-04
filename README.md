# Peilbeheer HHVR

Dit project bevat tools en simulaties voor peilbeheer van Hoogheemraadschap van Rijnland.

## 📁 Project Structuur

- **`peilbesluiten/`** - Data en scripts voor peilbesluiten
  - `rijnland_kaartlagen/` - GeoJSON kaartlagen (niet in git vanwege grote bestandsgrootte)
  - Scripts voor realtime data ophalen
  
- **`simulatie-peilbeheer/`** - Interactieve web applicatie
  - Vue + Vite applicatie
  - Leaflet kaarten voor visualisatie
  - Hosted op GitHub Pages

## 🌐 Live Demo

De simulatie applicatie is live beschikbaar op GitHub Pages:
**https://water-natuurlijk-rijnland.github.io/hhvr/**

## 🚀 Lokaal Draaien

### Simulatie Applicatie

```bash
cd simulatie-peilbeheer
npm install
npm run dev
```

Open http://localhost:5173/simulatie-peilbeheer/ in je browser.

### Bouwen voor Productie

```bash
npm run build
```

## 📦 Deployment

De applicatie wordt automatisch gedeployed naar GitHub Pages bij elke push naar de `main` branch via GitHub Actions.

## ⚠️ Belangrijk

- Grote GeoJSON kaartlagen worden niet in git opgeslagen (zie `.gitignore`)
- Lokaal moeten de kaartlagen aanwezig zijn in `peilbesluiten/rijnland_kaartlagen/`
- De `dist/` folder is build output en wordt niet gecommit

## 📝 Licentie

Copyright © Hoogheemraadschap van Rijnland
