<template>
  <!-- 
    Regenbui Simulatie Component
    
    Dit component toont een interactieve kaart met peilgebieden waar gebruikers op kunnen klikken
    om regenbui simulaties uit te voeren. De component bestaat uit:
    
    1. Full-screen Leaflet map met peilgebieden (polygons)
    2. SimulatiePanel - Toont simulatie-opties en start simulatie
    3. WaterstandGrafiek - Toont resultaten van de simulatie
    4. Info panel - Toont instructies wanneer geen peilgebied geselecteerd is
    5. Loading indicator - Toont tijdens het laden van peilgebieden data
    
    Data flow:
    - Component laadt peilgebieden data (lokaal of van ArcGIS service)
    - Gebruiker selecteert peilgebied door erop te klikken
    - SimulatiePanel ontvangt peilgebied data en stelt simulatie in
    - Simulatie resultaten worden doorgegeven aan WaterstandGrafiek
  -->
  <div class="h-screen w-screen relative overflow-hidden">
    <!-- Full Screen Map -->
    <div id="regenbui-simulatie-map" class="w-full h-full z-10" style="position: relative;"></div>

    <!-- Simulatie Panel -->
    <SimulatiePanel
      v-if="selectedPeilgebied"
      :peilgebied="selectedPeilgebied"
      @update-simulation="handleSimulationUpdate"
    />

    <!-- Waterstand Grafiek -->
    <WaterstandGrafiek
      v-if="simulationData"
      :tijdstappen="simulationData.tijdstappen"
      :maaiveld-niveau="simulationData.maaiveldNiveau"
      :streefpeil="simulationData.streefpeil"
      :marge="simulationData.marge"
      :gemaal-capaciteit="simulationData.gemaalCapaciteit"
    />

    <!-- Info Panel -->
    <div
      v-if="!selectedPeilgebied"
      class="fixed top-20 left-1/2 transform -translate-x-1/2 bg-white rounded-lg shadow-xl border border-gray-200 p-6 z-30 max-w-md"
    >
      <div class="text-center">
        <h3 class="text-lg font-bold text-gray-800 mb-2">🌧️ Regenbui Simulatie</h3>
        <p class="text-sm text-gray-600">
          Klik op een peilgebied op de kaart om een regenbui simulatie te starten
        </p>
      </div>
    </div>

    <!-- Loading Indicator -->
    <div
      v-if="loading"
      class="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-lg shadow-2xl p-6 z-40"
    >
      <div class="flex items-center gap-3">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span class="text-sm font-semibold text-gray-700">Peilgebieden laden...</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, shallowRef, onMounted, onUnmounted, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import proj4 from 'proj4'
import SimulatiePanel from './SimulatiePanel.vue'
import WaterstandGrafiek from './WaterstandGrafiek.vue'

// Configureer proj4 voor RD naar WGS84 conversie
// RD (Amersfoort / Dutch national grid) EPSG:28992
proj4.defs("EPSG:28992", "+proj=sterea +lat_0=52.15616055555557 +lon_0=5.387638888888892 +k_0=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel +units=m +no_defs")

const map = shallowRef(null)
const selectedPeilgebied = ref(null)
const simulationData = ref(null)
const loading = ref(false)
const peilgebiedenLayer = shallowRef(null)
const featureLayers = shallowRef([])

/**
 * Converteer RD (Dutch national grid) coördinaten naar WGS84 (lat/lng)
 * Gebruikt proj4 library voor maximale nauwkeurigheid
 * 
 * @param {number} x - RD x-coördinaat
 * @param {number} y - RD y-coördinaat
 * @returns {[number, number]} - [longitude, latitude] in WGS84
 */
const rdToWgs84 = (x, y) => {
  try {
    // Valideer input voordat we converteren
    if (isNaN(x) || isNaN(y) || !isFinite(x) || !isFinite(y)) {
      console.warn(`Invalid input coordinates: RD(${x}, ${y})`)
      return null  // Return null instead of [0, 0] to indicate invalid
    }
    
    // Converteer met proj4 voor maximale nauwkeurigheid
    const [lng, lat] = proj4("EPSG:28992", "WGS84", [x, y])
    
    // Valideer resultaat
    if (isNaN(lng) || isNaN(lat) || !isFinite(lng) || !isFinite(lat)) {
      console.warn(`Invalid coordinate conversion result: RD(${x}, ${y}) -> WGS84(${lng}, ${lat})`)
      return null  // Return null instead of [0, 0] to indicate invalid
    }
    
    // Valideer dat coördinaten binnen redelijke range zijn
    if (lng < -180 || lng > 180 || lat < -90 || lat > 90) {
      console.warn(`Coordinate out of valid range: RD(${x}, ${y}) -> WGS84(${lng}, ${lat})`)
      return null  // Return null instead of [0, 0] to indicate invalid
    }
    
    return [lng, lat]
  } catch (error) {
    console.error(`Error converting RD to WGS84: RD(${x}, ${y}), Error: ${error.message}`)
    return null  // Return null instead of [0, 0] to indicate invalid
  }
}

/**
 * Valideer of een coördinaat geldig is
 * @param {Array} coord - [x, y] array
 * @returns {boolean} - Of coördinaat geldig is
 */
const isValidCoordinate = (coord) => {
  return Array.isArray(coord) && 
         coord.length === 2 && 
         typeof coord[0] === 'number' && 
         typeof coord[1] === 'number' &&
         isFinite(coord[0]) && 
         isFinite(coord[1]) &&
         coord[0] !== undefined && 
         coord[1] !== undefined &&
         coord[0] !== null && 
         coord[1] !== null
}

/**
 * Valideer coordinates structuur recursief
 * @param {Array} coords - Coordinates array
 * @param {number} depth - Recursiediepte (voor beveiliging)
 * @returns {boolean} - Of coordinates geldig zijn
 */
const validateCoordinates = (coords, depth = 0) => {
  if (depth > 3) return false // Te diep genest
  if (!Array.isArray(coords)) return false
  if (depth === 2) {
    // Op het laagste niveau moeten het [lng, lat] arrays zijn
    return isValidCoordinate(coords)
  }
  return coords.every(c => validateCoordinates(c, depth + 1))
}

/**
 * Check if coordinates contain any undefined or invalid numbers
 * @param {Array} coords - Coordinates array
 * @returns {boolean} - Of coordinates geldige nummers bevatten
 */
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

/**
 * Check if a feature has valid coordinates (either RD or WGS84) that can be processed
 * @param {Object} feature - GeoJSON feature
 * @returns {boolean} - Of de feature geldige coördinaten heeft
 */
const checkFeatureForValidLatLng = (feature) => {
  if (!feature || !feature.geometry || !feature.geometry.coordinates) {
    return false
  }
  
  const coords = feature.geometry.coordinates
  
  // Check the structure based on geometry type
  if (feature.geometry.type === 'Polygon' || feature.geometry.type === 'MultiPolygon') {
    // For Polygon: [[[lng, lat], ...], ...]
    // For MultiPolygon: [[[[lng, lat], ...], ...], ...]
    const rings = feature.geometry.type === 'Polygon' ? coords : coords[0]
    
    if (!rings || !Array.isArray(rings)) {
      return false
    }
    
    // Check each coordinate pair
    for (let i = 0; i < rings.length; i++) {
      const ring = rings[i]
      if (!Array.isArray(ring)) {
        return false
      }
      
      for (let j = 0; j < ring.length; j++) {
        const coord = ring[j]
        if (!Array.isArray(coord) || coord.length < 2) {
          return false
        }
        
        const x = coord[0]
        const y = coord[1]
        
        // Check if coordinates are valid numbers
        if (typeof x !== 'number' || typeof y !== 'number' || isNaN(x) || isNaN(y) || !isFinite(x) || !isFinite(y)) {
          return false
        }
        
        // Check if coordinates are within valid ranges (either RD or WGS84)
        // RD: x and y are typically between 0 and 300,000
        // WGS84: lng between -180 and 180, lat between -90 and 90
        const isRD = (x > 10000 && x < 300000) && (y > 10000 && y < 300000)
        const isWGS84 = (x >= -180 && x <= 180) && (y >= -90 && y <= 90)
        
        if (!isRD && !isWGS84) {
          return false
        }
        
        // Reject coordinates that are exactly [0, 0] as they likely indicate conversion errors
        if (x === 0 && y === 0) {
          return false
        }
      }
    }
  }
  
  return true
}

/**
 * Converteer een enkele ring van coördinaten
 * @param {Array} ring - Array van coördinaten
 * @param {boolean} isRD - Of coördinaten in RD zijn
 * @returns {Array|null} - Geconverteerde ring of null bij fout
 */
const convertRing = (ring, isRD) => {
  if (!Array.isArray(ring) || ring.length === 0) {
    return null
  }
  
  const convertedRing = ring.map((coord) => {
    if (!coord || !Array.isArray(coord) || coord.length < 2) {
      return null
    }
    
    // Parse coördinaten
    const x = typeof coord[0] === 'number' ? coord[0] : parseFloat(coord[0])
    const y = typeof coord[1] === 'number' ? coord[1] : parseFloat(coord[1])
    
    if (isNaN(x) || isNaN(y) || !isFinite(x) || !isFinite(y)) {
      return null
    }
    
    if (isRD) {
      try {
        const result = rdToWgs84(x, y)
        // If conversion returns null, skip this coordinate
        if (result === null) {
          console.warn(`Skipping coordinate RD(${x}, ${y}) - conversion failed`)
          return null
        }
        return result
      } catch (e) {
        console.warn(`Error converting RD to WGS84: ${e.message}`)
        return null
      }
    }
    
    // Als al WGS84, valideer range
    if (x < -180 || x > 180 || y < -90 || y > 90) {
      // Mogelijk zijn x en y omgedraaid (lat, lng in plaats van lng, lat)
      if (y >= -180 && y <= 180 && x >= -90 && x <= 90) {
        return [y, x] // Draai om
      }
      return null
    }
    
    return [x, y]
  }).filter(c => c !== null && isValidCoordinate(c))
  
  if (convertedRing.length < 3) {
    return null
  }
  
  return convertedRing
}

/**
 * Converteer ArcGIS rings naar GeoJSON geometry
 * @param {Object} geometry - ArcGIS geometry object
 * @returns {Object|null} - GeoJSON geometry of null bij fout
 */
const convertArcGISGeometry = (geometry) => {
  if (!geometry || !geometry.rings) {
    return null
  }
  
  // Detecteer of coördinaten in RD zijn (Dutch national grid)
  let isRD = false
  if (geometry.rings[0] && geometry.rings[0][0] && Array.isArray(geometry.rings[0][0])) {
    const firstCoord = geometry.rings[0][0]
    isRD = Math.abs(firstCoord[0]) > 10000 && Math.abs(firstCoord[1]) > 10000
  }
  
  const coordinates = geometry.rings.map((ring, ringIndex) => {
    return convertRing(ring, isRD)
  }).filter(ring => ring !== null && ring.length >= 3)
  
  if (coordinates.length === 0) {
    return null
  }
  
  // Voor Polygon: coordinates moet array van rings zijn [[[lng,lat],...], ...]
  // Voor MultiPolygon: coordinates moet array van polygons zijn [[[[lng,lat],...], ...], ...]
  if (coordinates.length === 1) {
    return {
      type: 'Polygon',
      coordinates: coordinates[0] // Eerste ring array
    }
  } else {
    return {
      type: 'MultiPolygon',
      coordinates: coordinates // Array van polygon arrays
    }
  }
}

/**
 * Converteer een ArcGIS feature naar GeoJSON feature
 * @param {Object} feature - ArcGIS feature
 * @returns {Object|null} - GeoJSON feature of null bij fout
 */
const convertArcGISFeature = (feature) => {
  // Converteer attributes naar properties (ArcGIS gebruikt 'attributes', GeoJSON gebruikt 'properties')
  const properties = feature.attributes || feature.properties || {}
  
  // Handle geometry
  let geometry = feature.geometry
  
  // Als geometry ArcGIS formaat is (rings), converteer naar GeoJSON
  if (geometry && geometry.rings) {
    geometry = convertArcGISGeometry(geometry)
    if (!geometry) {
      console.warn('Failed to convert ArcGIS geometry for feature:', properties.NAAM || properties.CODE)
      return null
    }
  }
  
  // Als geometry al GeoJSON formaat is, gebruik direct
  if (!geometry || !geometry.type || !geometry.coordinates) {
    console.warn('Feature has invalid geometry:', properties.NAAM || properties.CODE)
    return null
  }
  
  // Valideer coordinates structuur
  if (!validateCoordinates(geometry.coordinates)) {
    console.warn('Feature has invalid coordinates structure:', properties.NAAM || properties.CODE)
    return null
  }
  
  return {
    type: 'Feature',
    geometry: geometry,
    properties: properties
  }
}

/**
 * Converteer data naar geldige GeoJSON FeatureCollection
 * @param {Object} data - Inkomende data (kann ArcGIS of GeoJSON)
 * @returns {Object} - GeoJSON FeatureCollection
 * @throws {Error} - Als conversie mislukt
 */
const convertToGeoJSON = (data) => {
  // Als data al geldige GeoJSON FeatureCollection is, gebruik direct
  if (data.type === 'FeatureCollection' && data.features && Array.isArray(data.features)) {
    // Check of features al correct formaat hebben
    const firstFeature = data.features[0]
    if (firstFeature && firstFeature.type === 'Feature' && firstFeature.geometry && firstFeature.properties) {
      // Al correct GeoJSON formaat
      return data
    }
    
    // Features hebben mogelijk attributes in plaats van properties, of ArcGIS geometry
    return {
      type: 'FeatureCollection',
      features: data.features.map(f => convertArcGISFeature(f)).filter(f => f !== null)
    }
  }
  
  // Als data geen FeatureCollection is, probeer te converteren
  if (data.features && data.features[0]) {
    const firstFeature = data.features[0]
    const hasAttributes = firstFeature.attributes && !firstFeature.properties
    const hasRings = firstFeature.geometry && firstFeature.geometry.rings

    if (hasAttributes || hasRings) {
      return {
        type: 'FeatureCollection',
        features: data.features.map(f => convertArcGISFeature(f)).filter(f => f !== null)
      }
    }
  }
  
  // Als we hier komen, is data niet in verwacht formaat
  throw new Error(`Invalid GeoJSON object: type=${data.type}, features=${data.features ? data.features.length : 'none'}`)
}

/**
 * Laad peilgebieden data van lokale bron of ArcGIS service
 * @throws {Error} - Als laden mislukt
 */
const loadPeilgebieden = async () => {
  loading.value = true
  featureLayers.value = [] // Reset feature layers
  
  try {
    let data = null
    let dataSource = 'unknown'
    
    // Probeer eerst lokaal bestand in public/data
    try {
      const localUrl = './data/peilgebieden_rijnland.geojson'
      const response = await fetch(localUrl)
      
      if (response.ok) {
        const contentType = response.headers.get('content-type')
        if (contentType && contentType.includes('application/json')) {
          data = await response.json()
          dataSource = 'local file'
        } else {
          // Probeer als JSON te parsen ook al is content-type niet correct
          const text = await response.text()
          data = JSON.parse(text)
          dataSource = 'local file (non-JSON content-type)'
        }
      }
    } catch (e) {
      console.warn('Lokaal bestand niet gevonden of onleesbaar:', e.message)
    }
    
    // Fallback naar ArcGIS service als lokaal bestand niet werkt
    if (!data) {
      console.log('Lokaal bestand niet gevonden, probeer ArcGIS service...')
      const arcgisUrl = 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Peilgebied_vigerend_besluit/MapServer/0/query?where=1%3D1&outFields=*&f=geojson'
      const response = await fetch(arcgisUrl)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        data = await response.json()
        dataSource = 'ArcGIS service'
      } else {
        // Probeer als JSON te parsen
        const text = await response.text()
        if (text.trim().startsWith('<!')) {
          console.error('HTML response ontvangen in plaats van JSON:', text.substring(0, 200))
          throw new Error('Server retourneerde HTML in plaats van JSON. Mogelijk CORS probleem of verkeerde URL.')
        }
        data = JSON.parse(text)
        dataSource = 'ArcGIS service (non-JSON content-type)'
      }
    }

    if (!data) {
      throw new Error('Geen data ontvangen van enige bron')
    }
    
    console.log(`Data ontvangen van ${dataSource}, type:`, data.type, 'features:', data.features?.length)
    
    // Converteer naar GeoJSON
    let geojsonData
    try {
      geojsonData = convertToGeoJSON(data)
    } catch (error) {
      console.error('Fout bij converteren GeoJSON:', error)
      console.error('Data sample:', JSON.stringify(data).substring(0, 500))
      throw new Error(`Invalid GeoJSON object: ${error.message}`)
    }

    if (!geojsonData || !geojsonData.features || geojsonData.features.length === 0) {
      throw new Error(`Invalid GeoJSON object: geen features gevonden (${geojsonData?.features?.length || 0} features)`)
    }
    
    console.log(`GeoJSON geconverteerd: ${geojsonData.features.length} features`)
    
    // Filter features met ongeldige geometry
    const validFeatures = geojsonData.features.filter(f => {
      if (!f.geometry || !f.geometry.coordinates) {
        return false
      }
      
      // First validate the structure
      if (!validateCoordinates(f.geometry.coordinates)) {
        return false
      }
      
      // Then check for valid numbers
      if (!checkCoordinatesForValidNumbers(f.geometry.coordinates)) {
        return false
      }
      
      return true
    })
    
    console.log(`Valide features: ${validFeatures.length} van ${geojsonData.features.length}`)
    
    if (validFeatures.length === 0) {
      throw new Error('Geen valide features gevonden na validatie')
    }

    // Maak een nieuwe layer group
    const geoJsonLayer = L.layerGroup()
    let addedCount = 0
    let errorCount = 0
    
    // Voeg features toe aan de kaart
    validFeatures.forEach((feature, index) => {
      try {
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
        
        // Log for debugging (first 3 features)
        if (index < 3) {
          console.log(`Feature ${index}: ${feature.properties?.NAAM || feature.properties?.CODE}, coords:`, feature.geometry.coordinates[0]?.[0]?.[0])
        }
        
        // Try to create the feature layer and catch any Leaflet errors
        let featureLayer
        try {
          // First check if the feature has any coordinates that would cause issues
          const hasValidLatLng = checkFeatureForValidLatLng(feature)
          if (!hasValidLatLng) {
            console.warn(`Feature ${index} has invalid LatLng coordinates:`, feature.properties?.NAAM || feature.properties?.CODE)
            errorCount++
            return
          }
          
          // Log the first few coordinates for debugging
          if (index < 5) {
            console.log(`Adding feature ${index}:`, feature.properties?.NAAM || feature.properties?.CODE)
            console.log('Coordinates sample:', JSON.stringify(feature.geometry.coordinates.slice(0, 1)))
          }
          
          featureLayer = L.geoJSON(feature, {
            style: {
              color: '#ff7800',
              weight: 2,
              opacity: 0.7,
              fillColor: '#ff7800',
              fillOpacity: 0.2,
              interactive: true,
              clickable: true
            },
            onEachFeature: (f, l) => {
              // Hover effect
              l.on({
                mouseover: (e) => {
                  const layer = e.target
                  layer.setStyle({
                    weight: 3,
                    fillOpacity: 0.4
                  })
                },
                mouseout: (e) => {
                  if (selectedPeilgebied.value?.properties.CODE !== f.properties.CODE) {
                    const layer = e.target
                    layer.setStyle({
                      weight: 2,
                      fillOpacity: 0.2
                    })
                  }
                }
              })
              
              // Click handler
              l.on('click', (e) => {
                e.originalEvent?.stopPropagation()
                selectPeilgebied(f, l)
              })
            }
          })
        } catch (leafletError) {
          console.error(`Leaflet error creating feature ${index} (${feature.properties?.NAAM || feature.properties?.CODE}):`, leafletError.message || leafletError)
          console.error('Feature data:', JSON.stringify(feature, null, 2).substring(0, 500))
          errorCount++
          return
        }
        
        // Verify the layer was created successfully
        if (!featureLayer) {
          console.error(`Feature ${index} layer not created:`, feature.properties?.NAAM || feature.properties?.CODE)
          errorCount++
          return
        }
        
        featureLayer.addTo(geoJsonLayer)
        featureLayers.value.push(featureLayer)
        addedCount++
      } catch (e) {
        console.warn(`Error adding feature ${index} (${feature.properties?.NAAM || feature.properties?.CODE}):`, e.message || e)
        errorCount++
      }
    })
    
    // Final summary
    console.log(`✓ Peilgebieden geladen: ${addedCount} van ${validFeatures.length} features toegevoegd (${errorCount} errors)`)
    if (addedCount > 0) {
      console.log('✓ Features zijn toegevoegd aan de kaart!')
    }
    
    // Voeg layer group toe aan kaart
    peilgebiedenLayer.value = geoJsonLayer
    geoJsonLayer.addTo(map.value)

    console.log(`✓ Peilgebieden geladen: ${addedCount} van ${validFeatures.length} features toegevoegd (${errorCount} errors)`)
    
    // Fit bounds alleen als we features hebben toegevoegd
    if (addedCount > 0) {
      try {
        // Voor layerGroup moeten we bounds verzamelen van alle layers
        let bounds = null
        geoJsonLayer.eachLayer((layer) => {
          try {
            if (layer.getBounds && layer.getBounds().isValid()) {
              if (!bounds) {
                bounds = layer.getBounds()
              } else {
                bounds.extend(layer.getBounds())
              }
            }
          } catch (e) {
            // Skip layers zonder bounds
          }
        })
        
        if (bounds && bounds.isValid()) {
          map.value.fitBounds(bounds, { padding: [50, 50] })
        }
      } catch (e) {
        console.warn('Error fitting bounds:', e)
      }
    }
  } catch (error) {
    console.error('Fout bij laden peilgebieden:', error)
    // Toon foutmelding voor gebruiker
    alert(`Fout bij laden peilgebieden: ${error.message}\nControleer console voor meer details.`)
  } finally {
    loading.value = false
  }
}

const gemalenData = ref(null)
const gemaalStatussen = ref({})
const gemalenLayer = shallowRef(null)

// Haal gemaal statussen op
const fetchGemaalStatussen = async () => {
  try {
    const response = await fetch('./data/gemaal_status_latest.json')
    if (response.ok) {
      const data = await response.json()
      if (data.stations) {
        gemaalStatussen.value = data.stations
        console.log('Gemaal statussen geladen:', Object.keys(data.stations).length)
        updateGemalenIcons()
      }
    }
  } catch (e) {
    console.warn('Kon gemaal status niet laden:', e)
  }
}

// Update gemaal icons op basis van status
const updateGemalenIcons = () => {
  if (!gemalenLayer.value) return
  
  gemalenLayer.value.eachLayer(layer => {
    if (layer instanceof L.Marker && layer.feature && layer.feature.properties) {
      const code = layer.feature.properties.CODE
      const status = gemaalStatussen.value[code]
      const isActive = status && status.status === 'aan'
      
      const color = isActive ? '#2563eb' : '#4b5563' // Blue vs Gray-600
      const shadow = isActive ? 'text-shadow: 0 0 10px #3b82f6;' : ''
      
      const icon = L.divIcon({
        html: `<div style="font-size: 20px; color: ${color}; ${shadow}">🏭</div>`,
        className: 'custom-gemaal-icon',
        iconSize: [24, 24],
        iconAnchor: [12, 12]
      })
      
      layer.setIcon(icon)
      
      // Update popup content if active
      if (isActive) {
        let popupContent = `<strong>${layer.feature.properties.NAAM || code}</strong><br/>`
        popupContent += `<span style="color: #2563eb; font-weight: bold;">Status: ACTIEF</span><br/>`
        popupContent += `Debiet: ${status.debiet} m³/s`
        layer.bindPopup(popupContent)
      }
    }
  })
}

// Laad gemalen data en voeg toe aan kaart
const loadGemalen = async () => {
  try {
    const response = await fetch('./data/gemalen_rijnland.geojson')
    if (response.ok) {
      gemalenData.value = await response.json()
      console.log('Gemalen geladen:', gemalenData.value?.features?.length)
      
      if (map.value && gemalenData.value) {
        gemalenLayer.value = L.geoJSON(gemalenData.value, {
          pointToLayer: (feature, latlng) => {
            const icon = L.divIcon({
              html: `<div style="font-size: 20px; color: #4b5563;">🏭</div>`,
              className: 'custom-gemaal-icon',
              iconSize: [24, 24],
              iconAnchor: [12, 12]
            })
            return L.marker(latlng, { icon })
          },
          onEachFeature: (feature, layer) => {
             layer.bindPopup(`<strong>${feature.properties.NAAM || feature.properties.CODE}</strong>`)
          }
        }).addTo(map.value)
        
        // Initial sturing
        updateGemalenIcons()
      }
    }
  } catch (e) {
    console.warn('Kon gemalen niet laden:', e)
  }
}

/**
 * Vind dichtstbijzijnde gemaal voor een peilgebied
 * @param {Object} feature - Peilgebied feature
 * @returns {Object|null} - Dichtstbijzijnde gemaal feature
 */
const findNearestGemaal = (feature) => {
  if (!gemalenData.value || !feature.geometry) return null
  
  // Bereken center van peilgebied (simpel average van coordinaten)
  let center = null
  const coords = feature.geometry.coordinates
  let points = []
  
  // Verzamel alle punten (handling Polygon en MultiPolygon)
  if (feature.geometry.type === 'Polygon') {
    points = coords[0]
  } else if (feature.geometry.type === 'MultiPolygon') {
    coords.forEach(poly => points.push(...poly[0]))
  }
  
  if (points.length > 0) {
    const sum = points.reduce((acc, p) => [acc[0] + p[0], acc[1] + p[1]], [0, 0])
    center = [sum[0] / points.length, sum[1] / points.length]
  }
  
  if (!center) return null
  
  // Vind dichtstbijzijnde gemaal
  let nearest = null
  let minDist = Infinity
  
  gemalenData.value.features.forEach(gemaal => {
    if (gemaal.geometry && gemaal.geometry.coordinates) {
      const gCoord = gemaal.geometry.coordinates
      // Simpele Euclidean distance (goed genoeg voor selectie dichtstbijzijnde)
      const dx = gCoord[0] - center[0]
      const dy = gCoord[1] - center[1]
      const dist = dx*dx + dy*dy
      
      if (dist < minDist) {
        minDist = dist
        nearest = gemaal
      }
    }
  })
  
  return nearest
}

/**
 * Selecteer een peilgebied en highlight het op de kaart
 * @param {Object} feature - GeoJSON feature
 * @param {Object} layer - Leaflet layer
 */
const selectPeilgebied = (feature, layer) => {
  // Reset vorige selectie
  if (peilgebiedenLayer.value) {
    peilgebiedenLayer.value.eachLayer((l) => {
      if (l !== layer) {
        l.setStyle({
          weight: 2,
          fillOpacity: 0.2,
          color: '#ff7800',
          fillColor: '#ff7800'
        })
      }
    })
  }

  // Highlight geselecteerd peilgebied
  layer.setStyle({
    weight: 4,
    fillOpacity: 0.5,
    color: '#3b82f6',
    fillColor: '#3b82f6'
  })

  // Extract peilgebied data
  const props = feature.properties
  const oppervlakte = props.OPPERVLAKTE || props.oppervlakte || null
  const oppervlakteHa = oppervlakte ? oppervlakte / 10000 : null

  // Vind dichtstbijzijnde gemaal
  const nearestGemaal = findNearestGemaal(feature)
  const gemaalCapaciteit = nearestGemaal?.properties?.MAXIMALECAPACITEIT || 0
  
  // Show gemaal on map
  if (nearestGemaal && map.value) {
    // Verwijder oude gemaal marker indien aanwezig
    if (window.selectedGemaalLayer) {
      window.selectedGemaalLayer.remove()
    }
    
    // Maak nieuwe marker
    const gCoords = nearestGemaal.geometry.coordinates
    // Let op: GeoJSON is [lng, lat], Leaflet wil [lat, lng]
    // Check of we coordinaat moeten converteren (als het RD is)
    // Maar gemalen_rijnland.geojson lijkt WGS84 te zijn (vanuit earlier steps)
    // Als coords > 180 is het waarschijnlijk RD
    let latLng = [gCoords[1], gCoords[0]]
    if (gCoords[0] > 180 || gCoords[1] > 180) {
       // RD coordinaten -> converteer
       const converted = rdToWgs84(gCoords[0], gCoords[1])
       if (converted) {
         latLng = [converted[1], converted[0]]
       }
    }
    
    const icon = L.divIcon({
      html: '<div style="font-size: 24px;">⛽</div>',
      className: 'gemaal-marker',
      iconSize: [30, 30],
      iconAnchor: [15, 15]
    })
    
    window.selectedGemaalLayer = L.marker(latLng, { icon: icon })
      .bindPopup(`<strong>${nearestGemaal.properties.NAAM || nearestGemaal.properties.CODE}</strong><br>Capaciteit: ${gemaalCapaciteit} m³/s`)
      .addTo(map.value)
      .openPopup()
  }

  selectedPeilgebied.value = {
    ...feature,
    properties: {
      ...props,
      oppervlakteHa: oppervlakteHa,
      oppervlakteM2: oppervlakte,
      nearestGemaal: nearestGemaal ? {
        naam: nearestGemaal.properties.NAAM || nearestGemaal.properties.CODE,
        capaciteit: gemaalCapaciteit,
        code: nearestGemaal.properties.CODE
      } : null
    }
  }

  // Pan naar geselecteerd peilgebied
  if (layer.getBounds && layer.getBounds().isValid()) {
    map.value.fitBounds(layer.getBounds(), { padding: [100, 100], maxZoom: 14 })
  }
}

// Handle simulation update
const handleSimulationUpdate = (data) => {
  if (data && data.tijdstappen && data.tijdstappen.length > 0) {
    simulationData.value = data
  } else {
    simulationData.value = null
  }
}

// Initialize map
const initMap = () => {
  // Center op Rijnland gebied
  map.value = L.map('regenbui-simulatie-map', {
    zoomControl: true,
    attributionControl: true,
    preferCanvas: false // Zorg dat interactiviteit werkt
  }).setView([52.15, 4.5], 10)

  // Add OpenStreetMap tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(map.value)
  
  // Wacht even zodat kaart volledig geladen is
  map.value.whenReady(() => {
    console.log('Kaart is klaar voor gebruik')
  })
}

onMounted(async () => {
  // Wacht even zodat DOM volledig geladen is
  await nextTick()
  await new Promise(resolve => setTimeout(resolve, 200))
  
  initMap()
  
  // Wacht tot kaart klaar is voordat we peilgebieden laden
  if (map.value) {
    map.value.whenReady(async () => {
      console.log('Kaart is ready, laad peilgebieden...')
      await fetchGemaalStatussen()
      await loadGemalen()
      await loadPeilgebieden()
    })
  }

  // Elke minuut status verversen
  const statusInterval = setInterval(() => {
    fetchGemaalStatussen()
  }, 60000)

  onUnmounted(() => {
    clearInterval(statusInterval)
  })
})

/**
 * Cleanup functie voor component lifecycle
 * Verwijdert map en event listeners om memory leaks te voorkomen
 */
const cleanup = () => {
  // Verwijder alle feature layers
  featureLayers.value.forEach(layer => {
    try {
      if (layer.remove) {
        layer.remove()
      }
      // Verwijder event listeners
      if (layer.off) {
        layer.off()
      }
    } catch (e) {
      console.warn('Error cleaning up feature layer:', e)
    }
  })
  featureLayers.value = []
  
  // Verwijder layer group
  if (peilgebiedenLayer.value) {
    try {
      if (peilgebiedenLayer.value.remove) {
        peilgebiedenLayer.value.remove()
      }
      if (peilgebiedenLayer.value.off) {
        peilgebiedenLayer.value.off()
      }
    } catch (e) {
      console.warn('Error cleaning up peilgebieden layer:', e)
    }
    peilgebiedenLayer.value = null
  }
  
  // Verwijder map
  if (map.value) {
    try {
      map.value.remove()
    } catch (e) {
      console.warn('Error removing map:', e)
    }
    map.value = null
  }
  
  // Reset andere refs
  selectedPeilgebied.value = null
  simulationData.value = null
}

onUnmounted(cleanup)
</script>

<style scoped>
#regenbui-simulatie-map {
  width: 100%;
  height: 100%;
}
</style>

