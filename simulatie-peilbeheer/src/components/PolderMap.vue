<!-- PolderMap.vue -->
<template>
  <div class="h-screen w-screen relative overflow-hidden">
    <!-- Full Screen Map -->
    <div id="map" class="w-full h-full z-10"></div>

    <a href="https://waternatuurlijk.nl/" class="fixed bottom-4 left-4 w-36 z-20">
      <img src="/logo_water_natuurlijk.svg"></img>
    </a>

    <!-- Legend -->
    <div class="fixed top-4 left-4 bg-white rounded-lg shadow-2xl border border-gray-200 p-4 z-20">
      <h4 class="text-sm font-semibold text-gray-800 mb-3">Drooglegging</h4>
      <div class="space-y-2">
        <div class="flex items-center gap-2">
          <div class="w-6 h-4 rounded" style="background-color: #006400"></div>
          <span class="text-xs text-gray-700">≤ 40 cm (Goed)</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-6 h-4 rounded" style="background-color: #FFFF00"></div>
          <span class="text-xs text-gray-700">40-50 cm</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-6 h-4 rounded" style="background-color: #FFA500"></div>
          <span class="text-xs text-gray-700">50-60 cm</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-6 h-4 rounded" style="background-color: #FF4500"></div>
          <span class="text-xs text-gray-700">60-70 cm</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-6 h-4 rounded" style="background-color: #FF0000"></div>
          <span class="text-xs text-gray-700">≥ 70 cm (Risico)</span>
        </div>
      </div>
    </div>

    <!-- Control Panel -->
    <ControlPanel
      @yearChange="onYearChange"
      @peilindexatieChange="onPeilindexatieChange"
    />

    <!-- Animation Panel -->
    <div
      v-if="selectedPolder != null"
      class="fixed top-4 bottom-4 right-4 w-80 flex justify-center items-center z-50"
    >
      <div class="w-full h-full">
        <AnimationPanel
          :polderData="selectedPolder"
          :currentYear="currentYear"
          :peilindexatie="currentPeilindexatie"
          @close="closeAnimation"
        />
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
import { ref, onMounted, toRaw } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import AnimationPanel from './AnimationPanel.vue'
import ControlPanel from './ControlPanel.vue'

const map = ref(null)
const polderLayer = ref(null)
const selectedPolder = ref(null)
const selectedLayer = ref(null)

// Control panel state
const currentYear = ref(2025)
const currentPeilindexatie = ref(50)

// Cache for yearly calculations: yearlyDataCache[`${polderID}_${peilindexatie}`][year]
const yearlyDataCache = ref({})

// Store polder info for quick access
const polderInfo = ref({})

const initMap = () => {
  map.value = L.map('map').setView([52.1326, 5.2913], 8)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map.value)
}

// Calculate yearly data for ONE polder with ONE peilindexatie - called during load
const calculateYearlyDataForPolder = (initialDrooglegging, initialZomerpeil, peilindexatiePercent) => {
  const startYear = 2025
  const endYear = 2075
  const subsidencePerYear = 0.7
  const peilindexatieDecimal = peilindexatiePercent / 100
  const minDrooglegging = 40

  const yearlyData = {}

  // Initial values for 2025
  yearlyData[startYear] = {
    drooglegging: initialDrooglegging,
    zomerpeil_ondergrens: initialZomerpeil
  }

  // Calculate each subsequent year
  for (let year = startYear + 1; year <= endYear; year++) {
    const prevYear = yearlyData[year - 1]

    // Calculate what drooglegging would be with current peilindexatie
    let newDrooglegging = prevYear.drooglegging - subsidencePerYear + (subsidencePerYear * peilindexatieDecimal)
    let newZomerpeil_ondergrens

    // Check if we've reached the minimum drooglegging threshold
    if (newDrooglegging <= minDrooglegging) {
      // Lock drooglegging at minimum
      newDrooglegging = minDrooglegging
      // Water level drops by full subsidence (no compensation)
      newZomerpeil_ondergrens = prevYear.zomerpeil_ondergrens - subsidencePerYear
    } else {
      // Normal operation: apply peilindexatie
      // Water level is adjusted: it drops less than ground (partial compensation)
      newZomerpeil_ondergrens = prevYear.zomerpeil_ondergrens - (subsidencePerYear * peilindexatieDecimal)
    }

    yearlyData[year] = {
      drooglegging: Math.max(0, newDrooglegging),
      zomerpeil_ondergrens: newZomerpeil_ondergrens
    }
  }

  return yearlyData
}

// Get or calculate cached yearly data for a polder
const getYearlyData = (polderID, drooglegging_2025, zomerpeil_ondergrens_2025, peilindexatie) => {
  const cacheKey = `${polderID}_${peilindexatie}`

  if (!yearlyDataCache.value[cacheKey]) {
    yearlyDataCache.value[cacheKey] = calculateYearlyDataForPolder(
      drooglegging_2025,
      zomerpeil_ondergrens_2025,
      peilindexatie
    )
  }

  return yearlyDataCache.value[cacheKey]
}

// Get data for a specific year and peilindexatie
const getYearData = (polderID, drooglegging_2025, zomerpeil_ondergrens_2025, year, peilindexatie) => {
  const yearlyData = getYearlyData(polderID, drooglegging_2025, zomerpeil_ondergrens_2025, peilindexatie)
  return yearlyData[year] || yearlyData[2025]
}

// Determine color based on drooglegging value
const getDroogleggingColor = (drooglegging) => {
  if (drooglegging <= 40) return '#006400'  // Green
  if (drooglegging < 50) return '#FFFF00'  // Yellow
  if (drooglegging < 60) return '#FFA500'  // Light orange
  if (drooglegging < 70) return '#FF4500'  // Dark orange
  return '#FF0000'  // Red
}

// Update all polder colors based on current year and peilindexatie
const updatePolderColors = () => {
  if (!polderLayer.value) return

  polderLayer.value.eachLayer((layer) => {
    const props = layer.feature.properties
    const yearData = getYearData(
      props.id,
      props.drooglegging_2025,
      props.zomerpeil_ondergrens_2025,
      currentYear.value,
      currentPeilindexatie.value
    )

    const isSelected = selectedLayer.value === layer
    layer.setStyle(getPolderStyle(yearData.drooglegging, isSelected))
  })
}

// Get style for a polder
const getPolderStyle = (drooglegging, isSelected = false) => {
  const baseColor = getDroogleggingColor(drooglegging)
  return {
    color: baseColor,
    weight: isSelected ? 4 : 2,
    fillOpacity: isSelected ? 0.9 : 0.4,
    fillColor: baseColor
  }
}

const resetLayerStyle = (layer) => {
  const props = layer.feature.properties
  const yearData = getYearData(
    props.id,
    props.drooglegging_2025,
    props.zomerpeil_ondergrens_2025,
    currentYear.value,
    currentPeilindexatie.value
  )
  layer.setStyle(getPolderStyle(yearData.drooglegging, false))
}

const setSelectedStyle = (layer) => {
  const props = layer.feature.properties
  const yearData = getYearData(
    props.id,
    props.drooglegging_2025,
    props.zomerpeil_ondergrens_2025,
    currentYear.value,
    currentPeilindexatie.value
  )
  layer.setStyle(getPolderStyle(yearData.drooglegging, true))
}

const loadPolders = async () => {
  try {
    const response = await fetch(`${import.meta.env.BASE_URL}polders.json`)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const poldersData = await response.json()

    // Convert to GeoJSON with all necessary properties
    const geojsonData = {
      type: "FeatureCollection",
      features: poldersData.map(polder => ({
        type: "Feature",
        properties: {
          id: polder.id,
          name: polder.name,
          drooglegging_2025: polder.drooglegging_2025,
          zomerpeil_ondergrens_2025: polder.zomerpeil_ondergrens_2025
        },
        geometry: polder.geometry
      }))
    }

    // Store polder info for quick access
    poldersData.forEach(polder => {
      polderInfo.value[polder.id] = {
        name: polder.name,
        drooglegging_2025: polder.drooglegging_2025,
        zomerpeil_ondergrens_2025: polder.zomerpeil_ondergrens_2025
      }
    })

    polderLayer.value = L.geoJSON(geojsonData, {
      style: (feature) => {
        const props = feature.properties
        const yearData = getYearData(
          props.id,
          props.drooglegging_2025,
          props.zomerpeil_ondergrens_2025,
          currentYear.value,
          currentPeilindexatie.value
        )
        return getPolderStyle(yearData.drooglegging, false)
      },
      onEachFeature: (feature, layer) => {
        const props = feature.properties

        layer.on('mouseover', () => {
          const yearData = getYearData(
            props.id,
            props.drooglegging_2025,
            props.zomerpeil_ondergrens_2025,
            currentYear.value,
            currentPeilindexatie.value
          )
          const tooltipContent = `${props.name}<br/>Drooglegging: ${yearData.drooglegging.toFixed(1)} cm (${currentYear.value})`
          layer.bindTooltip(tooltipContent, {
            permanent: false,
            direction: 'top',
            className: 'bg-white px-2 py-1 rounded shadow-lg border'
          }).openTooltip()

          if (selectedLayer.value !== layer) {
            layer.setStyle({ fillOpacity: 0.9, weight: 4 })
          }
        })

        layer.on('mouseout', () => {
          layer.closeTooltip()
          if (toRaw(selectedLayer.value) !== layer) {
            resetLayerStyle(layer)
          }
        })

        layer.on('click', () => {
          if (selectedLayer.value) {
            resetLayerStyle(selectedLayer.value)
          }

          selectedLayer.value = layer
          setSelectedStyle(layer)

          // Create selected polder object with all data needed for animation
          selectedPolder.value = {
            id: props.id,
            name: props.name,
            drooglegging_2025: props.drooglegging_2025,
            zomerpeil_ondergrens_2025: props.zomerpeil_ondergrens_2025,
            getYearData: (year, peilindexatie) => getYearData(
              props.id,
              props.drooglegging_2025,
              props.zomerpeil_ondergrens_2025,
              year,
              peilindexatie
            )
          }

          const bounds = layer.getBounds()
          map.value.fitBounds(bounds, {
            padding: [100, 100],
            maxZoom: 13,
            animate: true,
            duration: 0.5
          })
        })
      }
    }).addTo(map.value)

    const bounds = polderLayer.value.getBounds()
    if (bounds.isValid()) {
      map.value.fitBounds(bounds, { padding: [20, 20] })
    }

    setTimeout(() => {
      map.value.invalidateSize()
    }, 100)

  } catch (error) {
    console.error('Error loading polders:', error)
    alert(`Error loading polders: ${error.message}`)
  }
}

// Control panel event handlers
const onYearChange = (data) => {
  currentYear.value = data.year
  currentPeilindexatie.value = data.peilindexatie
  updatePolderColors()
}

const onPeilindexatieChange = (data) => {
  currentPeilindexatie.value = data.peilindexatie
  updatePolderColors()
}

const closeAnimation = () => {
  if (selectedLayer.value) {
    resetLayerStyle(selectedLayer.value)
    selectedLayer.value = null
  }
  selectedPolder.value = null
}

onMounted(() => {
  initMap()
  loadPolders()
})
</script>
