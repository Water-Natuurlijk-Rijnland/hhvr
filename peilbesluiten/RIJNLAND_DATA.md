# Rijnland ArcGIS Server - Beschikbare Data

## Overzicht
De Rijnland ArcGIS server (https://rijnland.enl-mcs.nl/arcgis/rest/services) bevat 90+ services met geospatiale data over waterbeheer in het beheergebied van Hoogheemraadschap van Rijnland.

## Water Infrastructuur Datasets

### 1. Watergangen (Waterways)
- **Watergang_vlak** (FeatureServer & MapServer)
  - Geometrie: Polygonen
  - Inhoud: Lijnvormige waterlichamen (kanalen, sloten, etc.)
  
- **Watergang_as** (MapServer)
  - Geometrie: Lijnen
  - Inhoud: Assen van watergangen

- **Watergang_zone** (MapServer)
  - Geometrie: Polygonen
  - Inhoud: Zones rondom watergangen

- **Vaarweg** (MapServer)
  - Inhoud: Bevaarbare waterwegen

### 2. Kunstwerken (Hydraulic Structures)

#### Gemalen (Pumping Stations)
- **Gemaal** (MapServer)
  - Geometrie: Punten
  - Inhoud: Pompen voor watertransport tussen peilniveaus
  
- **Gemaal_opgrootte** (MapServer)
  - Inhoud: Gemalen gegroepeerd op capaciteit

#### Stuwen (Weirs)
- **Stuw** (MapServer)
  - Geometrie: Punten
  - Inhoud: Vaste/beweegbare constructies voor waterpeilregulering

#### Sluizen (Locks/Sluices)
- **Sluis** (MapServer)
  - Geometrie: Punten
  - Inhoud: Schutsluizen en spuisluizen

#### Duikers (Culverts)
- **Duiker** (MapServer)
  - Geometrie: Lijnen
  - Inhoud: Constructies die watergangen verbinden door grondlichamen
  
- **Duiker_punt** (MapServer)
  - Geometrie: Punten
  - Inhoud: Duikers als puntlocaties

### 3. Peilbeheer (Water Level Management)

- **Peilgebied_vigerend_besluit** (MapServer)
  - Inhoud: 780 vigerende peilgebieden met zomer/winterpeilen
  - Data: CODE, NAAM, ZOMERPEIL, WINTERPEIL, SOORTPEILBEHEER, etc.

- **Peilgebied_praktijk_soort_gebied** (MapServer)
  - Inhoud: Peilgebieden volgens praktijksituatie

- **Peilenkaart_praktijk** (MapServer)
  - Inhoud: Actuele peilen in de praktijk

- **Peilafwijking_praktijk** (MapServer)
  - Inhoud: Afwijkingen van vastgestelde peilen

- **Peilafwijking_vigerend_besluit** (MapServer)
  - Inhoud: Vergunde peilafwijkingen

### 4. Afvalwater & Riolering (Wastewater & Sewage)

- **Afvalwaterzuivering** (MapServer)
  - Inhoud: Rioolwaterzuiveringsinstallaties (RWZI's)

- **Rioolgemaal_influent** (MapServer)
  - Inhoud: Rioolgemalen (influent zijde)

- **Lozingspunt** (MapServer)
  - Inhoud: Punten waar water geloosd wordt

- **Overstortconstructie** (MapServer)
  - Inhoud: Noodoverstorten in rioolstelsel

- **Rioolstelsel** (MapServer)
  - Inhoud: Rioleringsnetwerk

- **Rioleringsgebied_stelsel_gerealiseerd** (MapServer)
  - Inhoud: Gerealiseerde rioleringsgebieden

### 5. Administratieve Gebieden

- **Boezemgebied** (MapServer)
  - Inhoud: Hoofdwatersysteem gebieden

- **Polder** (MapServer)
  - Inhoud: Poldergebieden

- **Gemeente** (MapServer)
  - Inhoud: Gemeentegrenzen

- **Werkingsgebieden** (Folder)
  - Inhoud: Beheergebieden van verschillende afdelingen

### 6. Waterkeringen (Flood Defenses)

- **Primaire_kering** (MapServer)
  - Inhoud: Primaire waterkeringen (dijken)

- **Regionale_kering** (MapServer)
  - Inhoud: Regionale waterkeringen

### 7. Transport & Utilities

- **Transportleiding** (MapServer)
  - Inhoud: Transport leidingen

- **Transportleidingsegment_Rijnland** (MapServer)
  - Inhoud: Segmenten van transportleidingen

## Data Formaten
- GeoJSON
- JSON
- PBF (Protocol Buffers)
- KML/KMZ

## Coördinatensysteem
- EPSG:28992 (RD New - Rijksdriehoekscoördinaten)
- WGS84 (EPSG:4326) voor web maps

## API Versie
ArcGIS Server 11.5

## Toegang
- REST API
- SOAP API
- Public access (geen authenticatie vereist voor meeste services)
- Max 1000 features per query

## Gebruik voor Peilbeheer Visualisatie
De volgende datasets zijn vooral interessant voor uitbreiding van de peilbeheer kaart:
1. **Gemalen** - Toon pomplocaties en capaciteiten
2. **Stuwen** - Visualiseer peilregulerende constructies
3. **Watergangen** - Overlay met watergangnetwerk
4. **Peilafwijkingen** - Toon afwijkingen van vastgestelde peilen
5. **Duikers** - Toon verbindingen tussen watergangen

