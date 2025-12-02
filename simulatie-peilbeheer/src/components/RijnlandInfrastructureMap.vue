<template>
  <div class="h-screen w-screen relative overflow-hidden">
    <!-- Full Screen Map -->
    <div id="infrastructure-map" class="w-full h-full z-10"></div>

    <a href="https://waternatuurlijk.nl/" class="fixed bottom-4 left-4 w-36 z-20">
      <img src="/logo_water_natuurlijk.svg" alt="Water Natuurlijk"></img>
    </a>

    <!-- Layer Control Panel -->
    <div class="fixed top-4 left-4 bg-white rounded-lg shadow-2xl border border-gray-200 p-4 z-20 max-h-[calc(100vh-40px)] overflow-y-auto">
      <h4 class="text-sm font-semibold text-gray-800 mb-3">🗺️ Kaartlagen</h4>

      <!-- Peilgebieden -->
      <div class="mb-4 pb-4 border-b border-gray-200">
        <h5 class="text-xs font-bold text-gray-600 mb-2">Peilbeheer</h5>
        <div class="space-y-1">
          <label class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded">
            <input type="checkbox" v-model="layers.peilgebieden.visible" @change="toggleLayer('peilgebieden')" class="w-4 h-4">
            <div class="w-4 h-4 rounded border-2" :style="{ borderColor: layers.peilgebieden.color, backgroundColor: layers.peilgebieden.color + '40' }"></div>
            <span class="text-xs text-gray-700">Peilgebieden ({{ layers.peilgebieden.count }})</span>
          </label>
        </div>
      </div>

      <!-- Kunstwerken -->
      <div class="mb-4 pb-4 border-b border-gray-200">
        <h5 class="text-xs font-bold text-gray-600 mb-2">Kunstwerken</h5>
        <div class="space-y-1">
          <label class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded">
            <input type="checkbox" v-model="layers.gemalen.visible" @change="toggleLayer('gemalen')" class="w-4 h-4">
            <span class="text-lg">🏭</span>
            <span class="text-xs text-gray-700">Gemalen ({{ layers.gemalen.count }})</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded">
            <input type="checkbox" v-model="layers.stuwen.visible" @change="toggleLayer('stuwen')" class="w-4 h-4">
            <span class="text-lg">🌊</span>
            <span class="text-xs text-gray-700">Stuwen ({{ layers.stuwen.count }})</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded">
            <input type="checkbox" v-model="layers.sluizen.visible" @change="toggleLayer('sluizen')" class="w-4 h-4">
            <span class="text-lg">🚪</span>
            <span class="text-xs text-gray-700">Sluizen ({{ layers.sluizen.count }})</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded">
            <input type="checkbox" v-model="layers.duikers.visible" @change="toggleLayer('duikers')" class="w-4 h-4">
            <span class="text-lg">🔲</span>
            <span class="text-xs text-gray-700">Duikers ({{ layers.duikers.count }})</span>
          </label>
        </div>
      </div>

      <!-- Watergangen -->
      <div class="mb-4 pb-4 border-b border-gray-200">
        <h5 class="text-xs font-bold text-gray-600 mb-2">Watergangen</h5>
        <div class="space-y-1">
          <label class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded">
            <input type="checkbox" v-model="layers.watergangen.visible" @change="toggleLayer('watergangen')" class="w-4 h-4">
            <div class="w-4 h-4 rounded" :style="{ backgroundColor: layers.watergangen.color }"></div>
            <span class="text-xs text-gray-700">Watergangen ({{ layers.watergangen.count }})</span>
          </label>
        </div>
      </div>

      <!-- Afvalwater -->
      <div class="mb-4 pb-4 border-b border-gray-200">
        <h5 class="text-xs font-bold text-gray-600 mb-2">Afvalwater</h5>
        <div class="space-y-1">
          <label class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded">
            <input type="checkbox" v-model="layers.rwzi.visible" @change="toggleLayer('rwzi')" class="w-4 h-4">
            <span class="text-lg">🏭</span>
            <span class="text-xs text-gray-700">RWZI's ({{ layers.rwzi.count }})</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded">
            <input type="checkbox" v-model="layers.lozingspunten.visible" @change="toggleLayer('lozingspunten')" class="w-4 h-4">
            <span class="text-lg">💧</span>
            <span class="text-xs text-gray-700">Lozingspunten ({{ layers.lozingspunten.count }})</span>
          </label>
        </div>
      </div>

      <!-- Administratief -->
      <div class="mb-2">
        <h5 class="text-xs font-bold text-gray-600 mb-2">Administratief</h5>
        <div class="space-y-1">
          <label class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded">
            <input type="checkbox" v-model="layers.polders.visible" @change="toggleLayer('polders')" class="w-4 h-4">
            <div class="w-4 h-4 rounded border-2" style="border-color: #8B4513"></div>
            <span class="text-xs text-gray-700">Polders ({{ layers.polders.count }})</span>
          </label>
        </div>
      </div>
    </div>

    <!-- Info Panel -->
    <div
      v-if="selectedFeature"
      class="fixed top-4 right-4 w-96 bg-white rounded-lg shadow-2xl border border-gray-200 p-6 z-30 max-h-[calc(100vh-40px)] overflow-y-auto"
    >
      <div class="flex justify-between items-start mb-4">
        <div>
          <h3 class="text-lg font-bold text-gray-800">{{ selectedFeature.title }}</h3>
          <p class="text-xs text-gray-500 uppercase">{{ selectedFeature.type }}</p>
        </div>
        <button
          @click="closeInfo"
          class="text-gray-400 hover:text-gray-600 text-2xl leading-none"
        >
          ×
        </button>
      </div>

      <div class="space-y-3">
        <div v-for="(value, key) in selectedFeature.properties" :key="key" v-if="value">
          <p class="text-xs font-semibold text-gray-500 uppercase">{{ formatKey(key) }}</p>
          <p class="text-sm text-gray-800">{{ value }}</p>
        </div>
      </div>
    </div>

    <!-- Loading Indicator -->
    <div v-if="loading" class="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-lg shadow-2xl p-6 z-40">
      <div class="flex items-center gap-3">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span class="text-sm font-semibold text-gray-700">Laden...</span>
      </div>
    </div>
  </div>
</template>

<style>
.leaflet-container {
  outline: none !important;
}

.gemaal-tooltip {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  font-size: 13px;
  line-height: 1.5;
  max-width: 250px;
}

.gemaal-tooltip strong {
  color: #111827;
  font-weight: 600;
}
</style>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const map = ref(null)
const selectedFeature = ref(null)
const loading = ref(false)
const gemaalRealtimeData = ref({}) // Cache voor real-time gemaal data
const hoveredGemaal = ref(null)

// Layer configuration
const layers = reactive({
        peilgebieden: {
          visible: true,
          layer: null,
          count: 0,
          color: '#ff7800',
          url: `${import.meta.env.BASE_URL}../peilbesluiten/rijnland_kaartlagen/Peilgebied_vigerend_besluit/PeilgebiedVigerend_layer0.geojson`
        },
  gemalen: {
    visible: true,
    layer: null,
    count: 0,
    icon: '🏭',
    url: 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Gemaal/MapServer/0/query?where=1%3D1&outFields=*&f=geojson'
  },
  stuwen: {
    visible: true,
    layer: null,
    count: 0,
    icon: '🌊',
    url: 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Stuw/MapServer/0/query?where=1%3D1&outFields=*&f=geojson'
  },
  sluizen: {
    visible: true,
    layer: null,
    count: 0,
    icon: '🚪',
    url: 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Sluis/MapServer/0/query?where=1%3D1&outFields=*&f=geojson'
  },
  duikers: {
    visible: false,
    layer: null,
    count: 0,
    icon: '🔲',
    url: 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Duiker/MapServer/0/query?where=1%3D1&outFields=*&f=geojson'
  },
  watergangen: {
    visible: false,
    layer: null,
    count: 0,
    color: '#1E90FF',
    url: 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Watergang_vlak/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson'
  },
  rwzi: {
    visible: false,
    layer: null,
    count: 0,
    icon: '🏭',
    url: 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Afvalwaterzuivering/MapServer/0/query?where=1%3D1&outFields=*&f=geojson'
  },
  lozingspunten: {
    visible: false,
    layer: null,
    count: 0,
    icon: '💧',
    url: 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Lozingspunt/MapServer/0/query?where=1%3D1&outFields=*&f=geojson'
  },
  polders: {
    visible: false,
    layer: null,
    count: 0,
    color: '#8B4513',
    url: 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Polder/MapServer/0/query?where=1%3D1&outFields=*&f=geojson'
  }
})

const initMap = () => {
  map.value = L.map('infrastructure-map').setView([52.15, 4.8], 11)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map.value)
}

const formatKey = (key) => {
  const keyMap = {
    'CODE': 'Code',
    'NAAM': 'Naam',
    'ZOMERPEIL': 'Zomerpeil (m NAP)',
    'WINTERPEIL': 'Winterpeil (m NAP)',
    'SOORTPEILBEHEER': 'Soort Peilbeheer',
    'OPPERVLAKTE': 'Oppervlakte (m²)',
    'HYPERLINK': 'Link'
  }
  return keyMap[key] || key.charAt(0).toUpperCase() + key.slice(1).toLowerCase()
}

const createPointIcon = (emoji) => {
  return L.divIcon({
    html: `<div style="font-size: 24px;">${emoji}</div>`,
    className: 'custom-icon',
    iconSize: [30, 30],
    iconAnchor: [15, 15]
  })
}

const loadLayer = async (layerName, config) => {
  if (config.layer) return // Already loaded

  try {
    loading.value = true
    const response = await fetch(config.url)
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)

    const data = await response.json()
    config.count = data.features.length

    const geoJsonOptions = {
      onEachFeature: (feature, layer) => {
        layer.on('click', () => {
          selectedFeature.value = {
            title: feature.properties.NAAM || feature.properties.CODE || 'Onbekend',
            type: layerName,
            properties: feature.properties
          }
        })
        
        // Voor gemalen: voeg hover events toe voor real-time data
        if (layerName === 'gemalen' && layer instanceof L.Marker) {
          layer.on('mouseover', async () => {
            await showGemaalRealtimeData(feature, layer)
          })
          layer.on('mouseout', () => {
            hideGemaalTooltip(layer)
          })
        }
      }
    }

    // Style based on geometry type
    if (data.features[0]?.geometry.type === 'Point') {
      geoJsonOptions.pointToLayer = (feature, latlng) => {
        return L.marker(latlng, { icon: createPointIcon(config.icon) })
      }
    } else if (data.features[0]?.geometry.type === 'Polygon' || data.features[0]?.geometry.type === 'MultiPolygon') {
      geoJsonOptions.style = {
        color: config.color,
        weight: 2,
        fillOpacity: 0.3,
        fillColor: config.color
      }
    } else if (data.features[0]?.geometry.type === 'LineString' || data.features[0]?.geometry.type === 'MultiLineString') {
      geoJsonOptions.style = {
        color: config.color || '#1E90FF',
        weight: 3,
        opacity: 0.7
      }
    }

    config.layer = L.geoJSON(data, geoJsonOptions)

    if (config.visible) {
      config.layer.addTo(map.value)
    }

  } catch (error) {
    console.error(`Error loading ${layerName}:`, error)
  } finally {
    loading.value = false
  }
}

const toggleLayer = async (layerName) => {
  const config = layers[layerName]

  if (!config.layer) {
    await loadLayer(layerName, config)
  }

  if (config.layer) {
    if (config.visible) {
      config.layer.addTo(map.value)
    } else {
      map.value.removeLayer(config.layer)
    }
  }
}

const closeInfo = () => {
  selectedFeature.value = null
}

// Hydronet API configuratie
const HYDRONET_CHART_ID = 'e743fb87-2a02-4f3e-ac6c-03d03401aab8'
const HYDRONET_BASE_URL = 'https://watercontrolroom.hydronet.com/service/efsserviceprovider/api/chart'

// Parse Highcharts configuratie uit HTML
const parseHighchartsData = (htmlContent) => {
  try {
    const pattern = /Highcharts\.chart\(['"]container['"],\s*(\{.*?\})\);/s
    const match = htmlContent.match(pattern)
    if (!match) return null
    
    const config = JSON.parse(match[1])
    const series = config.series || []
    
    if (series.length === 0 || !series[0].data || series[0].data.length === 0) {
      return null
    }
    
    // Haal laatste data punt op
    const lastPoint = series[0].data[series[0].data.length - 1]
    const timestamp = new Date(lastPoint.x)
    const debiet = lastPoint.y || 0
    const status = debiet > 0.001 ? 'aan' : 'uit'
    
    // Bereken statistieken
    const values = series[0].data.map(p => p.y).filter(v => v > 0)
    const maxDebiet = values.length > 0 ? Math.max(...values) : 0
    const avgDebiet = values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0
    
    return {
      debiet: debiet.toFixed(3),
      status,
      timestamp: timestamp.toLocaleString('nl-NL'),
      maxDebiet: maxDebiet.toFixed(3),
      avgDebiet: avgDebiet.toFixed(3),
      dataPoints: series[0].data.length
    }
  } catch (e) {
    console.error('Fout bij parsen Highcharts data:', e)
    return null
  }
}

// Haal real-time gemaal data op
const fetchGemaalRealtimeData = async (gemaalCode) => {
  // Check cache (5 minuten geldig)
  const cached = gemaalRealtimeData.value[gemaalCode]
  if (cached && Date.now() - cached.timestamp < 5 * 60 * 1000) {
    return cached.data
  }
  
  try {
    const url = `${HYDRONET_BASE_URL}/${HYDRONET_CHART_ID}?featureIdentifier=${gemaalCode}`
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html',
        'Referer': 'https://rijnland.maps.arcgis.com/'
      }
    })
    
    if (!response.ok) {
      return null
    }
    
    const html = await response.text()
    const data = parseHighchartsData(html)
    
    // Cache data
    if (data) {
      gemaalRealtimeData.value[gemaalCode] = {
        data,
        timestamp: Date.now()
      }
    }
    
    return data
  } catch (error) {
    console.error(`Fout bij ophalen real-time data voor ${gemaalCode}:`, error)
    return null
  }
}

// Toon real-time gemaal data in tooltip
const showGemaalRealtimeData = async (feature, marker) => {
  const gemaalCode = feature.properties.CODE
  if (!gemaalCode) return
  
  hoveredGemaal.value = gemaalCode
  
  // Toon basis info eerst
  const naam = feature.properties.NAAM || gemaalCode
  let tooltipContent = `<strong>${naam}</strong><br/>`
  
  if (feature.properties.MAXIMALECAPACITEIT) {
    tooltipContent += `Capaciteit: ${feature.properties.MAXIMALECAPACITEIT} m³/s<br/>`
  }
  
  tooltipContent += `<small style="color: #666;">Laden real-time data...</small>`
  
  marker.bindTooltip(tooltipContent, {
    permanent: false,
    direction: 'top',
    className: 'gemaal-tooltip bg-white px-3 py-2 rounded shadow-lg border border-gray-300',
    offset: [0, -10]
  }).openTooltip()
  
  // Haal real-time data op
  const realtimeData = await fetchGemaalRealtimeData(gemaalCode)
  
  // Update tooltip met real-time data
  if (realtimeData) {
    const statusColor = realtimeData.status === 'aan' ? '#10b981' : '#6b7280'
    const statusIcon = realtimeData.status === 'aan' ? '🟢' : '⚪'
    
    tooltipContent = `
      <div style="min-width: 200px;">
        <strong>${naam}</strong><br/>
        <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #e5e7eb;">
          <div style="display: flex; align-items: center; gap: 4px; margin-bottom: 4px;">
            <span>${statusIcon}</span>
            <strong style="color: ${statusColor};">${realtimeData.status.toUpperCase()}</strong>
          </div>
          <div style="font-size: 0.9em; color: #374151;">
            <div>Debiet: <strong>${realtimeData.debiet} m³/s</strong></div>
            <div style="margin-top: 4px; font-size: 0.85em; color: #6b7280;">
              Max: ${realtimeData.maxDebiet} m³/s | Gem: ${realtimeData.avgDebiet} m³/s
            </div>
            <div style="margin-top: 4px; font-size: 0.8em; color: #9ca3af;">
              Laatste update: ${realtimeData.timestamp}
            </div>
          </div>
        </div>
      </div>
    `
  } else {
    tooltipContent = `
      <div>
        <strong>${naam}</strong><br/>
        <small style="color: #9ca3af;">Geen real-time data beschikbaar</small>
      </div>
    `
  }
  
  // Update tooltip door opnieuw te binden
  marker.unbindTooltip()
  marker.bindTooltip(tooltipContent, {
    permanent: false,
    direction: 'top',
    className: 'gemaal-tooltip bg-white px-3 py-2 rounded shadow-lg border border-gray-300',
    offset: [0, -10]
  }).openTooltip()
}

// Verberg gemaal tooltip
const hideGemaalTooltip = (marker) => {
  marker.closeTooltip()
  hoveredGemaal.value = null
}

const loadInitialLayers = async () => {
  const visibleLayers = Object.entries(layers).filter(([_, config]) => config.visible)

  for (const [name, config] of visibleLayers) {
    await loadLayer(name, config)
  }

  // Fit bounds to peilgebieden if available
  if (layers.peilgebieden.layer) {
    const bounds = layers.peilgebieden.layer.getBounds()
    if (bounds.isValid()) {
      map.value.fitBounds(bounds, { padding: [50, 50] })
    }
  }
}

onMounted(async () => {
  initMap()
  await loadInitialLayers()
})
</script>
