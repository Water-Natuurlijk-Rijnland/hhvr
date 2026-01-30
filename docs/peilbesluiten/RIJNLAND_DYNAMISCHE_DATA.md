# Dynamische Waterdata Rijnland

Dit document beschrijft de beschikbare dynamische (real-time of regelmatig bijgewerkte) waterdata van het Hoogheemraadschap van Rijnland.

## Overzicht

Rijnland biedt verschillende soorten dynamische waterdata aan via hun ArcGIS Server en andere bronnen. Deze data wordt regelmatig bijgewerkt en geeft inzicht in de actuele waterhuishouding.

## 1. Peilbeheer Data (Actuele Peilen)

### Peilenkaart_praktijk
- **Service**: `https://rijnland.enl-mcs.nl/arcgis/rest/services/Peilenkaart_praktijk/MapServer`
- **Type**: Actuele peilen in de praktijk
- **Update frequentie**: Regelmatig bijgewerkt
- **Data velden**:
  - `ZOMERPEIL`: Actueel zomerpeil
  - `WINTERPEIL`: Actueel winterpeil
  - `VASTPEIL`: Vast peil indien van toepassing
  - `METENDEINSTANTIE`: Instantie die de metingen uitvoert
  - `DATUMINWINNING`: Datum van laatste meting
  - `LAST_EDITED_DATE`: Laatste wijzigingsdatum
- **Grootte**: ~60 MB (veel features)
- **Gebruik**: Visualisatie van actuele waterpeilen per peilgebied

### Peilafwijking_praktijk
- **Service**: `https://rijnland.enl-mcs.nl/arcgis/rest/services/Peilafwijking_praktijk/MapServer`
- **Type**: Afwijkingen van vastgestelde peilen in de praktijk
- **Update frequentie**: Regelmatig bijgewerkt
- **Gebruik**: Monitoring van peilafwijkingen

### Peilgebied_praktijk_soort_gebied
- **Service**: `https://rijnland.enl-mcs.nl/arcgis/rest/services/Peilgebied_praktijk_soort_gebied/MapServer`
- **Type**: Peilgebieden volgens praktijksituatie
- **Update frequentie**: Regelmatig bijgewerkt
- **Gebruik**: Actuele indeling van peilgebieden

## 2. Meetlocaties

### Meetlocatie_waterkwantiteit
- **Service**: `https://rijnland.enl-mcs.nl/arcgis/rest/services/Meetlocatie_waterkwantiteit/MapServer`
- **Type**: Locaties waar waterkwantiteit wordt gemeten
- **Metingen**: Waterstanden, debieten, etc.
- **Update frequentie**: Real-time of regelmatig (afhankelijk van meetfrequentie)
- **Gebruik**: Locaties van meetpunten voor waterkwantiteit

### Meetlocatie_waterkwaliteit
- **Service**: `https://rijnland.enl-mcs.nl/arcgis/rest/services/Meetlocatie_waterkwaltiteit/MapServer`
- **Type**: Locaties waar waterkwaliteit wordt gemeten
- **Metingen**: Waterkwaliteitsparameters
- **Update frequentie**: Regelmatig (meestal wekelijks/maandelijks)
- **Gebruik**: Locaties van meetpunten voor waterkwaliteit

### TransportleidingMeetpunt
- **Service**: `https://rijnland.enl-mcs.nl/arcgis/rest/services/TransportleidingMeetpunt/MapServer`
- **Type**: Meetpunten op transportleidingen
- **Gebruik**: Monitoring van transportleidingen

## 3. Real-time Data Bronnen

### Zomermonitor
- **Bron**: Website Rijnland (https://www.rijnland.net/loket/droogte-zomermonitor/)
- **Type**: Rapportages tijdens droge periodes
- **Update frequentie**: Regelmatig tijdens droogte
- **Inhoud**:
  - Neerslagtekorten
  - Waterpeilen
  - Chloridegehaltes
  - Zwemwaterkwaliteit
  - Verwachtingen voor nabije toekomst
- **Formaat**: PDF/Web rapportages
- **Gebruik**: Monitoring tijdens droogteperiodes

### Waterbeheerprogramma Data
- **Bron**: WBP6 Rijnland (https://wbp6rijnland.nl/)
- **Type**: Strategische data en plannen
- **Update frequentie**: Periodiek (2022-2028)
- **Inhoud**:
  - Waterveiligheid
  - Waterkwaliteit
  - Waterkwantiteit
  - Waterkeringen
  - Inspecties
  - Digitalisering

## 4. API Toegang

### ArcGIS REST API
Alle bovenstaande services zijn toegankelijk via de ArcGIS REST API:

**Basis URL**: `https://rijnland.enl-mcs.nl/arcgis/rest/services`

**Voorbeeld query**:
```bash
# Peilenkaart praktijk
curl "https://rijnland.enl-mcs.nl/arcgis/rest/services/Peilenkaart_praktijk/MapServer/0/query?where=1%3D1&outFields=*&f=geojson"

# Meetlocaties waterkwantiteit
curl "https://rijnland.enl-mcs.nl/arcgis/rest/services/Meetlocatie_waterkwantiteit/MapServer/0/query?where=1%3D1&outFields=*&f=geojson"
```

**Parameters**:
- `where`: SQL WHERE clause (bijv. `CODE='PG001'`)
- `outFields`: Velden om op te halen (`*` voor alle velden)
- `f`: Output formaat (`geojson`, `json`, `pbf`)
- `resultRecordCount`: Max aantal records (max 1000)
- `resultOffset`: Paginering offset

## 5. Real-time Sensor Data

Voor real-time sensor data (waterstanden, debieten) moet mogelijk contact worden opgenomen met Rijnland, of gebruik worden gemaakt van:

### Rijkswaterstaat Data
- **Bron**: https://rijkswaterstaatdata.nl/
- **Type**: Waterstanden, afvoeren, waterkwaliteit
- **Gebied**: Landelijk (inclusief Rijnland gebied)
- **API**: Beschikbaar via Rijkswaterstaat Data API

## 6. Data Updates

### Update Frequenties

#### Hydronet Water Control Room API (Gemaal data)
- **Update interval: 30 minuten**
- Nieuwe datapunten verschijnen op :19 en :49 minuten van elk uur
- Aanbevolen polling: elke 15-30 minuten
- Vaker pollen is niet zinvol (data verandert niet)

#### ArcGIS Services (geschat)
- **Peilenkaart_praktijk**: Dagelijks/wekelijks
- **Meetlocaties**: Real-time tot dagelijks (afhankelijk van sensor)
- **Peilafwijkingen**: Regelmatig bijgewerkt
- **Zomermonitor**: Tijdens droogteperiodes

### Data Freshness Check
Controleer de `LAST_EDITED_DATE` of `DATUMINWINNING` velden in de data om te zien wanneer data voor het laatst is bijgewerkt.

## 7. Gebruik in Visualisaties

### Voorbeeld: Actuele Peilen Tonen
```javascript
// Laad actuele peilen
const praktijkPeilen = await fetch(
  'https://rijnland.enl-mcs.nl/arcgis/rest/services/Peilenkaart_praktijk/MapServer/0/query?where=1%3D1&outFields=CODE,NAAM,ZOMERPEIL,WINTERPEIL&f=geojson'
).then(r => r.json());

// Visualiseer op kaart met kleuren gebaseerd op afwijking van vastgesteld peil
```

### Voorbeeld: Meetlocaties Tonen
```javascript
// Laad meetlocaties
const meetlocaties = await fetch(
  'https://rijnland.enl-mcs.nl/arcgis/rest/services/Meetlocatie_waterkwantiteit/MapServer/0/query?where=1%3D1&outFields=*&f=geojson'
).then(r => r.json());

// Toon op kaart met popup met laatste meetwaarden
```

## 8. Beperkingen

- **Max 1000 features per query**: Gebruik paginering voor grote datasets
- **Geen real-time API**: ArcGIS services zijn niet echt real-time, maar regelmatig bijgewerkt
- **Authenticatie**: Meeste services zijn publiek, maar sommige kunnen authenticatie vereisen
- **Rate limiting**: Respecteer de server door niet te vaak te pollen

## 9. Aanbevelingen

1. **Polling frequentie**: Poll niet vaker dan nodig (bijv. elke 15 minuten voor actuele peilen)
2. **Caching**: Cache data lokaal om serverbelasting te verminderen
3. **Error handling**: Implementeer retry logic voor API calls
4. **Data validatie**: Controleer `LAST_EDITED_DATE` om te zien of data recent is

## 10. Contact

Voor vragen over dynamische data of toegang tot real-time APIs:
- **Website**: https://www.rijnland.net
- **Contact**: Via het loket op de website





