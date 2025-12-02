<template>
  <div class="h-screen w-screen relative overflow-hidden">
    <!-- Full Screen Map -->
    <div id="peilbesluiten-map" class="w-full h-full z-10"></div>

    <a href="https://waternatuurlijk.nl/" class="fixed bottom-4 left-4 w-36 z-20">
      <img src="/logo_water_natuurlijk.svg" alt="Water Natuurlijk"></img>
    </a>

    <!-- Legend -->
    <div class="fixed top-4 left-4 bg-white rounded-lg shadow-2xl border border-gray-200 p-4 z-20">
      <h4 class="text-sm font-semibold text-gray-800 mb-3">Waterschappen</h4>
      <div class="space-y-2">
        <div class="flex items-center gap-2">
          <div class="w-6 h-4 rounded" style="background-color: #3388ff"></div>
          <span class="text-xs text-gray-700">HDSR Peilbesluiten</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-6 h-4 rounded" style="background-color: #ff7800"></div>
          <span class="text-xs text-gray-700">Rijnland Peilgebieden</span>
        </div>
      </div>

      <div class="mt-4 pt-4 border-t border-gray-200">
        <h4 class="text-xs font-semibold text-gray-600 mb-2">Selectie</h4>
        <div class="space-y-1">
          <label class="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" v-model="showHDSR" @change="toggleLayer('hdsr')" class="w-4 h-4">
            <span class="text-xs text-gray-700">Toon HDSR ({{ hdsrCount }})</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" v-model="showRijnland" @change="toggleLayer('rijnland')" class="w-4 h-4">
            <span class="text-xs text-gray-700">Toon Rijnland ({{ rijnlandCount }})</span>
          </label>
        </div>
      </div>
    </div>

    <!-- Info Panel -->
    <div
      v-if="selectedPeilbesluit"
      class="fixed top-4 right-4 w-96 bg-white rounded-lg shadow-2xl border border-gray-200 p-6 z-30 max-h-[calc(100vh-40px)] overflow-y-auto"
    >
      <div class="flex justify-between items-start mb-4">
        <h3 class="text-lg font-bold text-gray-800">{{ selectedPeilbesluit.name }}</h3>
        <button
          @click="closeInfo"
          class="text-gray-400 hover:text-gray-600 text-2xl leading-none"
        >
          ×
        </button>
      </div>

      <div class="space-y-3">
        <!-- Peilinformatie -->
        <div v-if="selectedPeilbesluit.zomerpeil !== null || selectedPeilbesluit.winterpeil !== null" class="bg-blue-50 rounded-lg p-3 border border-blue-200">
          <p class="text-xs font-semibold text-blue-800 uppercase mb-2">🌊 Actuele Peilen (m NAP)</p>
          <div class="grid grid-cols-2 gap-3">
            <div v-if="selectedPeilbesluit.zomerpeil !== null">
              <p class="text-xs text-gray-600">☀️ Zomerpeil</p>
              <p class="text-lg font-bold text-blue-700">{{ formatPeil(selectedPeilbesluit.zomerpeil) }}</p>
            </div>
            <div v-if="selectedPeilbesluit.winterpeil !== null">
              <p class="text-xs text-gray-600">❄️ Winterpeil</p>
              <p class="text-lg font-bold text-blue-700">{{ formatPeil(selectedPeilbesluit.winterpeil) }}</p>
            </div>
          </div>
          <div v-if="selectedPeilbesluit.soortPeilbeheer" class="mt-2 pt-2 border-t border-blue-200">
            <p class="text-xs text-gray-600">Soort peilbeheer</p>
            <p class="text-sm text-gray-800">{{ selectedPeilbesluit.soortPeilbeheer }}</p>
          </div>
        </div>

        <div v-if="selectedPeilbesluit.gebiedsplan">
          <p class="text-xs font-semibold text-gray-500 uppercase">Gebiedsplan</p>
          <p class="text-sm text-gray-800">{{ selectedPeilbesluit.gebiedsplan }}</p>
        </div>

        <div v-if="selectedPeilbesluit.goedkeuring">
          <p class="text-xs font-semibold text-gray-500 uppercase">Datum Goedkeuring</p>
          <p class="text-sm text-gray-800">{{ formatDate(selectedPeilbesluit.goedkeuring) }}</p>
        </div>

        <div v-if="selectedPeilbesluit.oppervlakte">
          <p class="text-xs font-semibold text-gray-500 uppercase">Oppervlakte</p>
          <p class="text-sm text-gray-800">{{ selectedPeilbesluit.oppervlakte.toFixed(2) }} ha</p>
        </div>

        <div>
          <p class="text-xs font-semibold text-gray-500 uppercase">Waterschap</p>
          <p class="text-sm text-gray-800">{{ selectedPeilbesluit.waterschap }}</p>
        </div>

        <div v-if="selectedPeilbesluit.besluitUrl">
          <a
            :href="selectedPeilbesluit.besluitUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800 hover:underline"
          >
            <span>Bekijk officieel besluit</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.leaflet-container {
  outline: none !important;
}
.leaflet-container:focus {
  outline: none !important;
}
.leaflet-interactive {
  outline: none !important;
}
.leaflet-interactive:focus {
  outline: none !important;
}
</style>

<script setup>
import { ref, onMounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const map = ref(null)
const hdsrLayer = ref(null)
const rijnlandLayer = ref(null)
const selectedPeilbesluit = ref(null)
const selectedLayer = ref(null)

// Layer visibility
const showHDSR = ref(true)
const showRijnland = ref(true)

// Counts
const hdsrCount = ref(0)
const rijnlandCount = ref(0)

const initMap = () => {
  map.value = L.map('peilbesluiten-map').setView([52.1, 5.0], 10)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map.value)
}

// Calculate area in hectares from GeoJSON geometry
const calculateArea = (geometry) => {
  try {
    if (geometry.type === 'Polygon') {
      const coordinates = geometry.coordinates[0]
      return calculatePolygonArea(coordinates)
    } else if (geometry.type === 'MultiPolygon') {
      return geometry.coordinates.reduce((total, polygon) => {
        return total + calculatePolygonArea(polygon[0])
      }, 0)
    }
  } catch (error) {
    console.error('Error calculating area:', error)
  }
  return null
}

// Simple area calculation using shoelace formula (approximate for lat/lng)
const calculatePolygonArea = (coordinates) => {
  let area = 0
  const numPoints = coordinates.length

  for (let i = 0; i < numPoints - 1; i++) {
    const [x1, y1] = coordinates[i]
    const [x2, y2] = coordinates[i + 1]
    area += x1 * y2 - x2 * y1
  }

  area = Math.abs(area) / 2
  // Convert to hectares (rough approximation: 1 degree² ≈ 12363 km² at 52°N)
  const hectares = area * 12363 * 100
  return hectares
}

const getPolderStyle = (color, isSelected = false) => {
  return {
    color: color,
    weight: isSelected ? 3 : 1.5,
    fillOpacity: isSelected ? 0.7 : 0.3,
    fillColor: color
  }
}

const resetLayerStyle = (layer, color) => {
  layer.setStyle(getPolderStyle(color, false))
}

const setSelectedStyle = (layer, color) => {
  layer.setStyle(getPolderStyle(color, true))
}

const formatDate = (timestamp) => {
  if (!timestamp) return 'Onbekend'
  const date = new Date(timestamp)
  return date.toLocaleDateString('nl-NL', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatPeil = (peil) => {
  if (peil === null || peil === undefined) return 'N/A'
  return `${peil.toFixed(2)} m`
}

const loadHDSR = async () => {
  try {
    const response = await fetch(`${import.meta.env.BASE_URL}data/peilbesluiten_hdsr.geojson`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()

    hdsrCount.value = data.features.length

    hdsrLayer.value = L.geoJSON(data, {
      style: () => getPolderStyle('#3388ff', false),
      onEachFeature: (feature, layer) => {
        const props = feature.properties
        const oppervlakte = calculateArea(feature.geometry)

        layer.on('mouseover', () => {
          const tooltipContent = `
            <strong>${props.WS_PBNAAM || 'Onbekend'}</strong><br/>
            ${oppervlakte ? `Oppervlakte: ${oppervlakte.toFixed(2)} ha` : ''}
          `
          layer.bindTooltip(tooltipContent, {
            permanent: false,
            direction: 'top',
            className: 'bg-white px-2 py-1 rounded shadow-lg border'
          }).openTooltip()

          if (selectedLayer.value !== layer) {
            layer.setStyle({ fillOpacity: 0.6, weight: 2 })
          }
        })

        layer.on('mouseout', () => {
          layer.closeTooltip()
          if (selectedLayer.value !== layer) {
            resetLayerStyle(layer, '#3388ff')
          }
        })

        layer.on('click', () => {
          if (selectedLayer.value) {
            const prevColor = selectedLayer.value.feature.properties._waterschap === 'HDSR' ? '#3388ff' : '#ff7800'
            resetLayerStyle(selectedLayer.value, prevColor)
          }

          selectedLayer.value = layer
          setSelectedStyle(layer, '#3388ff')

          selectedPeilbesluit.value = {
            name: props.WS_PBNAAM || 'Onbekend peilbesluit',
            gebiedsplan: props.WS_GPNAAM,
            goedkeuring: props.WS_DTM_GOED,
            besluitUrl: props.WS_INFO,
            oppervlakte: oppervlakte,
            waterschap: 'HDSR (Hoogheemraadschap De Stichtse Rijnlanden)',
            zomerpeil: null,
            winterpeil: null,
            soortPeilbeheer: null
          }

          const bounds = layer.getBounds()
          map.value.fitBounds(bounds, {
            padding: [100, 100],
            maxZoom: 14,
            animate: true,
            duration: 0.5
          })
        })

        // Store waterschap for styling
        feature.properties._waterschap = 'HDSR'
      }
    })

    if (showHDSR.value) {
      hdsrLayer.value.addTo(map.value)
    }

  } catch (error) {
    console.error('Error loading HDSR data:', error)
  }
}

const loadRijnland = async () => {
  try {
    const response = await fetch(`${import.meta.env.BASE_URL}data/peilgebieden_rijnland.geojson`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()

    rijnlandCount.value = data.features.length

    rijnlandLayer.value = L.geoJSON(data, {
      style: () => getPolderStyle('#ff7800', false),
      onEachFeature: (feature, layer) => {
        const props = feature.properties
        const oppervlakte = calculateArea(feature.geometry)

        layer.on('mouseover', () => {
          const name = props.CODE || props.NAAM || props.Name || 'Onbekend'
          let peilInfo = ''
          if (props.ZOMERPEIL || props.WINTERPEIL) {
            peilInfo = '<br/>'
            if (props.ZOMERPEIL) peilInfo += `☀️ Zomer: ${props.ZOMERPEIL} m NAP`
            if (props.ZOMERPEIL && props.WINTERPEIL) peilInfo += ' | '
            if (props.WINTERPEIL) peilInfo += `❄️ Winter: ${props.WINTERPEIL} m NAP`
          }
          const tooltipContent = `
            <strong>${name}</strong><br/>
            ${oppervlakte ? `Oppervlakte: ${oppervlakte.toFixed(2)} ha` : ''}
            ${peilInfo}
          `
          layer.bindTooltip(tooltipContent, {
            permanent: false,
            direction: 'top',
            className: 'bg-white px-2 py-1 rounded shadow-lg border'
          }).openTooltip()

          if (selectedLayer.value !== layer) {
            layer.setStyle({ fillOpacity: 0.6, weight: 2 })
          }
        })

        layer.on('mouseout', () => {
          layer.closeTooltip()
          if (selectedLayer.value !== layer) {
            resetLayerStyle(layer, '#ff7800')
          }
        })

        layer.on('click', () => {
          if (selectedLayer.value) {
            const prevColor = selectedLayer.value.feature.properties._waterschap === 'HDSR' ? '#3388ff' : '#ff7800'
            resetLayerStyle(selectedLayer.value, prevColor)
          }

          selectedLayer.value = layer
          setSelectedStyle(layer, '#ff7800')

          const name = props.CODE || props.NAAM || props.Name || 'Onbekend peilgebied'
          selectedPeilbesluit.value = {
            name: name,
            gebiedsplan: null,
            goedkeuring: props.DATUMGOEDKEURINGVV || null,
            besluitUrl: props.HYPERLINK || null,
            oppervlakte: oppervlakte,
            waterschap: 'Rijnland (Hoogheemraadschap van Rijnland)',
            zomerpeil: props.ZOMERPEIL,
            winterpeil: props.WINTERPEIL,
            soortPeilbeheer: props.SOORTPEILBEHEER
          }

          const bounds = layer.getBounds()
          map.value.fitBounds(bounds, {
            padding: [100, 100],
            maxZoom: 14,
            animate: true,
            duration: 0.5
          })
        })

        // Store waterschap for styling
        feature.properties._waterschap = 'Rijnland'
      }
    })

    if (showRijnland.value) {
      rijnlandLayer.value.addTo(map.value)
    }

  } catch (error) {
    console.error('Error loading Rijnland data:', error)
  }
}

const toggleLayer = (layerName) => {
  if (layerName === 'hdsr' && hdsrLayer.value) {
    if (showHDSR.value) {
      hdsrLayer.value.addTo(map.value)
    } else {
      map.value.removeLayer(hdsrLayer.value)
    }
  } else if (layerName === 'rijnland' && rijnlandLayer.value) {
    if (showRijnland.value) {
      rijnlandLayer.value.addTo(map.value)
    } else {
      map.value.removeLayer(rijnlandLayer.value)
    }
  }
}

const closeInfo = () => {
  if (selectedLayer.value) {
    const color = selectedLayer.value.feature.properties._waterschap === 'HDSR' ? '#3388ff' : '#ff7800'
    resetLayerStyle(selectedLayer.value, color)
    selectedLayer.value = null
  }
  selectedPeilbesluit.value = null
}

const loadAllData = async () => {
  await Promise.all([
    loadHDSR(),
    loadRijnland()
  ])

  // Fit map to show all layers
  setTimeout(() => {
    const allLayers = []
    if (hdsrLayer.value && showHDSR.value) allLayers.push(hdsrLayer.value)
    if (rijnlandLayer.value && showRijnland.value) allLayers.push(rijnlandLayer.value)

    if (allLayers.length > 0) {
      const group = L.featureGroup(allLayers)
      map.value.fitBounds(group.getBounds(), { padding: [50, 50] })
    }

    map.value.invalidateSize()
  }, 100)
}

onMounted(() => {
  initMap()
  loadAllData()
})
</script>
