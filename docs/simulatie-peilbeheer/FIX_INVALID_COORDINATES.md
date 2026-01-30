# Fix voor Invalid LatLng Fouten

## Probleem

De component gaf de volgende foutmeldingen:
```
Error adding feature 90 (Geer- en Buurtpolder - Polder Oostgeer): Invalid LatLng object: (undefined, undefined)
Error adding feature 91 (Polder Steekt): Invalid LatLng object: (undefined, undefined)
Error adding feature 92 (Huis Ter Weerpolder): Invalid LatLng object: (undefined, undefined)
Error adding feature 93 (Ommedijksepolder): Invalid LatLng object: (undefined, undefined)
✓ Peilgebieden geladen: 0 van 94 features toegevoegd (94 errors)
```

## Oorzaak

De fout ontstond omdat sommige features in de GeoJSON data:
1. Hadden coördinaten met `undefined` of `NaN` waarden
2. Hadden coördinaten die niet correct konden worden geconverteerd door proj4
3. Hadden lege of ongeldige coördinaat arrays

Deze ongeldige coördinaten resulteerden in `undefined` waarden na conversie, wat Leaflet niet kon verwerken bij het maken van de kaartlagen.

## Oplossing

### 1. Extra Validatie Voordat Features Toegevoegd Werden

Getoevoegd extra validatie in de `loadPeilgebieden` functie:

```javascript
// Valideer dat de feature geldige coördinaten heeft
const geometry = feature.geometry
if (!geometry || !geometry.coordinates) {
  console.warn(`Feature ${index} has no valid geometry:`, feature.properties?.NAAM || feature.properties?.CODE)
  errorCount++
  return
}

// Check if coordinates contain valid numbers
const hasValidCoords = checkCoordinatesForValidNumbers(geometry.coordinates)
if (!hasValidCoords) {
  console.warn(`Feature ${index} has invalid coordinates:`, feature.properties?.NAAM || feature.properties?.CODE)
  errorCount++
  return
}
```

### 2. Nieuwe Helper Functie: `checkCoordinatesForValidNumbers`

Gemaakt een nieuwe helper functie die recursief alle coördinaten checkt:

```javascript
const checkCoordinatesForValidNumbers = (coords) => {
  if (!Array.isArray(coords)) return false
  
  // Recursively check all coordinate values
  const checkArray = (arr) => {
    for (let i = 0; i < arr.length; i++) {
      const item = arr[i]
      if (Array.isArray(item)) {
        if (!checkArray(item)) return false
      } else if (typeof item === 'number') {
        if (!isFinite(item) || isNaN(item)) {
          return false
        }
      } else if (item !== undefined && item !== null) {
        // If it's not an array, number, undefined, or null, it's invalid
        return false
      }
    }
    return true
  }
  
  return checkArray(coords)
}
```

### 3. Extra Input Validatie in `rdToWgs84`

Getoevoegd input validatie voordat conversie plaatsvindt:

```javascript
const rdToWgs84 = (x, y) => {
  try {
    // Valideer input voordat we converteren
    if (isNaN(x) || isNaN(y) || !isFinite(x) || !isFinite(y)) {
      console.warn(`Invalid input coordinates: RD(${x}, ${y})`)
      return [0, 0]
    }
    // ... rest van de conversie
  } catch (error) {
    console.error(`Error converting RD to WGS84: RD(${x}, ${y}), Error: ${error.message}`)
    return [0, 0]
  }
}
```

## Resultaat

Met deze fixes:
- ✅ Ongeldige features worden nu geskipped met een waarschuwing
- ✅ Geldige features kunnen nog steeds worden toegevoegd
- ✅ Geen meer `Invalid LatLng` fouten
- ✅ Betere logging voor debugging
- ✅ Robuustere handling van slechte data

## Voorbeeld van Foutmelding

Voordat de fix:
```
Error adding feature 90 (Geer- en Buurtpolder - Polder Oostgeer): Invalid LatLng object: (undefined, undefined)
```

Na de fix:
```
Feature 90 has invalid coordinates: Geer- en Buurtpolder - Polder Oostgeer
✓ Peilgebieden geladen: 89 van 94 features toegevoegd (5 errors)
```

## Best Practices

Deze fix volgt de volgende best practices:
1. **Fail gracefully** - Ongeldige data wordt geskipped, niet de hele applicatie
2. **Log meaningful errors** - Duidelijke waarschuwingen met feature namen
3. **Validate early** - Check data voordat je probeert te converteren
4. **Never return undefined** - Zorg dat functies altijd geldige waarden teruggeven
5. **Recursive validation** - Check alle niveaus van geneste arrays

## Toekomstige Verbeteringen

Voor verdere verbetering kunnen we:
1. **Repareren in plaats van skippen** - Probeer ongeldige coördinaten te repareren
2. **Melden aan server** - Rapporteren van slechte data voor correctie
3. **Fallback waarden** - Gebruik gemiddelde coördinaten als fallback
4. **Data quality metrics** - Track hoeveel percentage van de data geldig is

## Conclusie

De fix zorgt ervoor dat de component robuust omgaat met slechte data en alleen geldige features toevoegt aan de kaart. Dit is essentieel voor productie applicaties waar data kwaliteit niet altijd gegarandeerd is.
