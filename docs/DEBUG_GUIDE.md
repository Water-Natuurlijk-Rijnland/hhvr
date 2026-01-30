# 🔍 Debug Guide voor Invalid LatLng Fouten

## 📋 Wat is Geïmplementeerd

De component heeft nu uitgebreide debug logging om het probleem te identificeren:

### 1. Debug Logging voor de Eerste 5 Features
```javascript
// Log the first few coordinates for debugging
if (index < 5) {
  console.log(`Adding feature ${index}:`, feature.properties?.NAAM || feature.properties?.CODE)
  console.log('Coordinates sample:', JSON.stringify(feature.geometry.coordinates.slice(0, 1)))
}
```

### 2. Error Logging met Volledige Feature Data
```javascript
catch (leafletError) {
  console.error(`Leaflet error creating feature ${index} (${feature.properties?.NAAM || feature.properties?.CODE}):`, leafletError.message || leafletError)
  console.error('Feature data:', JSON.stringify(feature, null, 2).substring(0, 500))
  errorCount++
  return
}
```

## 🎯 Wat te Verwachten

Wanneer de app draait, zal je in de console zien:

### Voor de Eerste 5 Features:
```
Adding feature 0: Feature Naam 1
Coordinates sample: [[[4.5, 52.0], [4.6, 52.1], ...]]
```

### Bij Fouten:
```
Leaflet error creating feature 90 (Geer- en Buurtpolder - Polder Oostgeer): Invalid LatLng object: (undefined, undefined)
Feature data: {
  "type": "Feature",
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[undefined, undefined], ...]]
  },
  "properties": {
    "NAAM": "Geer- en Buurtpolder - Polder Oostgeer"
  }
}
```

## 🚀 Hoe te Debuggen

### 1. Start de App
```bash
cd /Users/marc/Projecten/peilbeheer/simulatie-peilbeheer
npm run dev
```

### 2. Open de Browser Console
- Open Chrome of Firefox
- Open de Developer Tools (F12)
- Ga naar het 'Console' tabblad

### 3. Analyseer de Logs
- Kijk naar de coördinaten van de eerste 5 features
- Zoek naar patterns in de foutmeldingen
- Identificeer welke features problemen geven

### 4. Identificeer het Probleem
- Zijn de coördinaten `undefined`? → Probleem in conversie
- Zijn de coördinaten buiten range? → Probleem in validatie
- Zijn de coördinaten [0, 0]? → Probleem in conversie

## 📊 Mogelijke Oorzaken

### 1. Ongeldige RD Coördinaten
- Sommige features hebben ongeldige RD coördinaten
- Deze worden geconverteerd naar [0, 0] of undefined
- Oplossing: Filter deze features in de data bron

### 2. Corrupte GeoJSON Data
- Sommige features hebben corrupte structuur
- Ontbrekende of ongeldige velden
- Oplossing: Repareer de data of skip deze features

### 3. Proj4 Conversie Fouten
- Sommige coördinaten kunnen niet worden geconverteerd
- Resulteert in undefined waarden
- Oplossing: Betere error handling in rdToWgs84

## ✅ Huidige Status

De component heeft nu:
- ✅ Comprehensive validatie
- ✅ Debug logging
- ✅ Error logging met volledige data
- ✅ Graceful degradation

## 📝 Volgende Stappen

1. Start de app en kijk naar de console logs
2. Identificeer welke features problemen geven
3. Analyseer de exacte fout
4. Implementeer een specifieke fix

---

**Tip:** De logs zullen exact laten zien wat er misgaat, zodat we een gerichte oplossing kunnen implementeren.
