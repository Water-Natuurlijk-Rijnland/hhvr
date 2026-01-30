# 🔍 Debug Ready: Regenbui Simulatie Component

## ✅ Wat is Gedaan

Ik heb uitgebreide debug logging toegevoegd aan de component om het laden van peilgebieden te monitoren.

### 1. Debug Logging voor Eerste 3 Features
```javascript
// Log for debugging (first 3 features)
if (index < 3) {
  console.log(`Feature ${index}: ${feature.properties?.NAAM || feature.properties?.CODE}, coords:`, feature.geometry.coordinates[0]?.[0]?.[0])
}
```

### 2. Final Summary na Laden
```javascript
// Final summary
console.log(`✓ Peilgebieden geladen: ${addedCount} van ${validFeatures.length} features toegevoegd (${errorCount} errors)`)
if (addedCount > 0) {
  console.log('✓ Features zijn toegevoegd aan de kaart!')
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

### 3. Wat te Verwachten

#### Voor de Eerste 3 Features:
```
Feature 0: Naam van feature 1, coords: [4.5, 52.0]
Feature 1: Naam van feature 2, coords: [4.6, 52.1]
Feature 2: Naam van feature 3, coords: [4.7, 52.2]
```

#### Na het Laden:
```
✓ Peilgebieden geladen: 89 van 94 features toegevoegd (5 errors)
✓ Features zijn toegevoegd aan de kaart!
```

## 📊 Wat te Controleren

### 1. Coördinaten
- Zijn de coördinaten geldige getallen? (niet undefined/NaN)
- Zitten de coördinaten binnen range? (-180..180 voor lng, -90..90 voor lat)
- Zijn de coördinaten niet [0, 0]? (indicator van conversie fout)

### 2. Feature Count
- Hoeveel features zijn toegevoegd? (moet > 0 zijn)
- Hoeveel errors zijn er? (moet < 94 zijn)

### 3. Kaart Weergave
- Zie je oranje lijnen op de kaart? (dat zijn de peilgebieden)
- Kun je op peilgebieden klikken? (dat werkt als de features goed zijn toegevoegd)

## 🎯 Mogelijke Problemen

### Probleem 1: Geen Features Toegevoegd
- **Oorzaak:** Alle features hebben ongeldige coördinaten
- **Oplossing:** Controleer de data bron (lokaal bestand of ArcGIS service)

### Probleem 2: Alleen Few Features Toegevoegd
- **Oorzaak:** Sommige features hebben ongeldige coördinaten
- **Oplossing:** Check de console logs om te zien welke features problemen geven

### Probleem 3: Geen Oranje Lijnen Zichtbaar
- **Oorzaak:** De layer group is niet toegevoegd aan de kaart
- **Oplossing:** Controleer of `geoJsonLayer.addTo(map.value)` wordt uitgevoerd

## ✅ Huidige Status

- ✅ Debug logging toegevoegd
- ✅ Final summary toegevoegd
- ✅ Comprehensive validatie aanwezig
- ✅ Proper error handling aanwezig

## 📝 Volgende Stappen

1. Start de app en kijk naar de console logs
2. Controleer of features worden geladen
3. Check of coördinaten geldig zijn
4. Verifieer dat de kaart oranje lijnen toont

---

**Tip:** De logs zullen exact laten zien wat er gebeurt, zodat we het probleem kunnen identificeren en oplossen.
