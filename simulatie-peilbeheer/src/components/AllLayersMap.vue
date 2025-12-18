<template>
  <div class="h-screen w-screen relative overflow-hidden">
    <!-- Full Screen Map -->
    <div id="all-layers-map" class="w-full h-full z-10"></div>

    <a href="https://waternatuurlijk.nl/" class="fixed bottom-4 left-4 w-36 z-20">
      <img src="/logo_water_natuurlijk.svg" alt="Water Natuurlijk"></img>
    </a>

    <!-- Legend Panel -->
    <div class="fixed top-4 left-4 bg-white rounded-lg shadow-2xl border border-gray-200 p-4 z-20 max-h-[calc(100vh-40px)] overflow-y-auto w-80">
      <div class="flex justify-between items-center mb-4">
        <h4 class="text-lg font-bold text-gray-800">🗺️ Legenda</h4>
        <button
          @click="toggleLegend"
          class="text-gray-400 hover:text-gray-600 text-xl"
        >
          {{ legendExpanded ? '−' : '+' }}
        </button>
      </div>

      <div v-if="legendExpanded" id="legend-content" class="space-y-4">
        <!-- Categorieën -->
        <div v-for="category in categories" :key="category.name" class="border-b border-gray-200 pb-3 last:border-b-0">
          <div class="flex items-center justify-between mb-2">
            <h5 class="text-sm font-bold text-gray-700">{{ category.name }}</h5>
            <span class="text-xs text-gray-500">{{ getCategoryCount(category.layers) }}</span>
          </div>
          <div class="space-y-1 max-h-60 overflow-y-auto">
            <label
              v-for="layer in category.layers"
              :key="layer.key"
              class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded text-xs"
            >
              <input
                type="checkbox"
                v-model="layers[layer.key].visible"
                @change="toggleLayer(layer.key)"
                class="w-3 h-3"
              />
              <div
                v-if="layer.type === 'point'"
                class="text-base"
              >{{ layer.icon }}</div>
              <div
                v-else-if="layer.type === 'polygon'"
                class="w-4 h-4 rounded border-2"
                :style="{ borderColor: layer.color, backgroundColor: layer.color + '40' }"
              ></div>
              <div
                v-else-if="layer.type === 'line'"
                class="w-4 h-1"
                :style="{ backgroundColor: layer.color }"
              ></div>
              <span class="text-gray-700 flex-1 truncate">{{ layer.label }}</span>
              <span class="text-gray-400 text-xs">{{ layers[layer.key].count || 0 }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Samenvatting -->
      <div class="mt-4 pt-4 border-t border-gray-200">
        <div class="text-xs text-gray-600">
          <div>Zichtbaar: <strong>{{ visibleLayersCount }}</strong> / {{ totalLayersCount }}</div>
          <div>Geladen: <strong>{{ loadedLayersCount }}</strong></div>
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
        
        <!-- Gemaal Trend Information -->
        <div v-if="selectedFeature.type === 'gemalen' && selectedGemaalTrends" class="mt-4 pt-4 border-t border-gray-200">
          <h4 class="text-sm font-bold text-gray-700 mb-3">📈 Trend Analyse</h4>
          
          <div class="space-y-3">
            <!-- Current Status -->
            <div v-if="selectedGemaalStatus" class="bg-gray-50 rounded-lg p-3">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-semibold text-gray-600">Huidige Status</span>
                <span 
                  class="text-xs font-bold px-2 py-1 rounded"
                  :class="selectedGemaalStatus.status === 'aan' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'"
                >
                  {{ selectedGemaalStatus.status.toUpperCase() }}
                </span>
              </div>
              <p class="text-lg font-bold text-gray-800">
                {{ selectedGemaalStatus.debiet?.toFixed(3) || '0.000' }} <span class="text-sm font-normal text-gray-500">m³/s</span>
              </p>
            </div>
            
            <!-- Trends per Window -->
            <div v-if="selectedGemaalTrends.trends" class="space-y-2">
              <div 
                v-for="(trend, windowKey) in selectedGemaalTrends.trends" 
                :key="windowKey"
                v-if="trend"
                class="bg-gray-50 rounded-lg p-2"
              >
                <div class="flex items-center justify-between mb-1">
                  <span class="text-xs font-semibold text-gray-600">{{ getWindowLabel(windowKey) }}</span>
                  <span 
                    class="text-xs font-medium"
                    :class="getTrendColorClass(trend.direction)"
                  >
                    {{ getTrendLabel(trend.direction) }} ({{ trend.strength }})
                  </span>
                </div>
                <div class="flex items-center gap-2 text-xs text-gray-600">
                  <span>↗</span>
                  <span>{{ trend.slope_per_hour?.toFixed(3) || '0.000' }} m³/s/uur</span>
                  <span class="text-gray-400">•</span>
                  <span>R²: {{ (trend.r_squared * 100).toFixed(0) }}%</span>
                </div>
              </div>
            </div>
            
            <!-- Window Stats -->
            <div v-if="selectedGemaalTrends.window_stats" class="space-y-2">
              <p class="text-xs font-semibold text-gray-600 mb-2">Statistieken</p>
              <div 
                v-for="(stats, windowKey) in selectedGemaalTrends.window_stats" 
                :key="windowKey"
                v-if="stats"
                class="text-xs text-gray-600 bg-gray-50 rounded p-2"
              >
                <div class="font-semibold mb-1">{{ getWindowLabel(windowKey) }}</div>
                <div class="grid grid-cols-2 gap-1">
                  <span>Gemiddeld: <strong>{{ stats.avg?.toFixed(3) || '0.000' }}</strong></span>
                  <span>Min-Max: <strong>{{ stats.min?.toFixed(3) || '0.000' }}</strong> - <strong>{{ stats.max?.toFixed(3) || '0.000' }}</strong></span>
                  <span>Punten: <strong>{{ stats.count || 0 }}</strong></span>
                  <span>Duur: <strong>{{ stats.window_duration_minutes?.toFixed(0) || 0 }} min</strong></span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Indicator (CCG richtlijn - verbeterde loading state) -->
    <div 
      v-if="loading" 
      class="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-lg shadow-2xl p-6 z-40"
      role="status"
      aria-live="polite"
      aria-label="Data wordt geladen"
    >
      <div class="flex items-center gap-3">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <div>
          <span class="text-sm font-semibold text-gray-700">Laden...</span>
          <p v-if="loadingMessage" class="text-xs text-gray-500 mt-1">{{ loadingMessage }}</p>
        </div>
      </div>
    </div>

    <!-- Error State Panel (CCG richtlijn) -->
    <div
      v-if="dataError"
      class="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-red-50 border-2 border-red-200 rounded-lg shadow-lg p-4 z-40 max-w-md"
      role="alert"
      aria-live="assertive"
    >
      <div class="flex items-start gap-3">
        <span class="text-2xl">⚠️</span>
        <div class="flex-1">
          <h4 class="font-bold text-red-800 mb-1">Probleem met data ophalen</h4>
          <p class="text-sm text-red-700 mb-2">{{ dataError }}</p>
          <button
            @click="retryDataLoad"
            class="text-sm px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
            aria-label="Probeer opnieuw data op te halen"
          >
            Opnieuw proberen
          </button>
        </div>
        <button
          @click="dataError = null"
          class="text-red-400 hover:text-red-600"
          aria-label="Sluit waarschuwing"
        >
          ×
        </button>
      </div>
    </div>

    <!-- Data Quality Indicator (CCG richtlijn) -->
    <DataQualityIndicator 
      v-if="gemaalStatus"
      :stats="gemaalStatus"
      :success-rate="dataSuccessRate"
      :last-error="dataError"
    />

    <!-- Gemaal Grafiek Component -->
    <GemaalChart 
      v-if="showChart && selectedGemaal" 
      :gemaal-code="selectedGemaal.code"
      :gemaal-naam="selectedGemaal.naam"
      @close="showChart = false; selectedGemaal = null" 
    />
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

.peilgebied-tooltip {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  font-size: 13px;
  line-height: 1.5;
  max-width: 250px;
}

.peilgebied-tooltip strong {
  color: #111827;
  font-weight: 600;
}
</style>

<script setup>
import { ref, onMounted, onUnmounted, reactive, computed, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import GemaalChart from './GemaalChart.vue'
import DataQualityIndicator from './DataQualityIndicator.vue'

const map = ref(null)
const selectedFeature = ref(null)
const loading = ref(false)
const loadingMessage = ref('')
const legendExpanded = ref(true)
const gemaalRealtimeData = ref({}) // Cache voor real-time gemaal data
const hoveredGemaal = ref(null)
const gemaalStatus = ref(null) // Global status for all gemalen
const showChart = ref(false) // Toon/verberg grafiek component
const selectedGemaal = ref(null) // Geselecteerd gemaal voor grafiek
const gemalenMetData = ref(new Set()) // Set van gemaal codes die data hebben
const dataError = ref(null) // Error state voor data ophalen (CCG richtlijn)
const dataSuccessRate = ref(null) // Success rate voor data kwaliteit (CCG richtlijn)

// Hydronet API configuratie
const HYDRONET_CHART_ID = 'e743fb87-2a02-4f3e-ac6c-03d03401aab8'
const HYDRONET_BASE_URL = 'https://watercontrolroom.hydronet.com/service/efsserviceprovider/api/chart'

// Layer configuratie - alle beschikbare lagen
const layers = reactive({
  // Peilbeheer
  peilgebieden: { visible: false, layer: null, count: 0, color: '#ff7800', type: 'polygon' },
  peilgebied_praktijk: { visible: false, layer: null, count: 0, color: '#ff9500', type: 'polygon' },
  peilenkaart_praktijk: { visible: false, layer: null, count: 0, color: '#ffb340', type: 'polygon' },
  peilafwijking_praktijk: { visible: false, layer: null, count: 0, color: '#ff6b6b', type: 'polygon' },
  peilafwijking_vigerend: { visible: false, layer: null, count: 0, color: '#ee5a6f', type: 'polygon' },
  
  // Kunstwerken
  gemalen: { visible: false, layer: null, count: 0, icon: '🏭', type: 'point' },
  gemaal_opgrootte: { visible: false, layer: null, count: 0, icon: '🏭', type: 'point' },
  effluentgemaal: { visible: false, layer: null, count: 0, icon: '💧', type: 'point' },
  rioolgemaal: { visible: false, layer: null, count: 0, icon: '🚰', type: 'point' },
  stuwen: { visible: false, layer: null, count: 0, icon: '🌊', type: 'point' },
  sluizen: { visible: false, layer: null, count: 0, icon: '🚪', type: 'point' },
  duikers: { visible: false, layer: null, count: 0, icon: '🔲', type: 'line' },
  duiker_punt: { visible: false, layer: null, count: 0, icon: '🔲', type: 'point' },
  afsluiter: { visible: false, layer: null, count: 0, icon: '🔧', type: 'point' },
  afsluitmiddel: { visible: false, layer: null, count: 0, icon: '⚙️', type: 'point' },
  inlaat: { visible: false, layer: null, count: 0, icon: '💨', type: 'point' },
  inlaatrijnland: { visible: false, layer: null, count: 0, icon: '💨', type: 'point' },
  coupure: { visible: false, layer: null, count: 0, icon: '🚧', type: 'point' },
  dam: { visible: false, layer: null, count: 0, icon: '🏔️', type: 'point' },
  brug: { visible: false, layer: null, count: 0, icon: '🌉', type: 'point' },
  aquaduct: { visible: false, layer: null, count: 0, icon: '🌉', type: 'point' },
  
  // Watergangen
  watergang_vlak: { visible: false, layer: null, count: 0, color: '#1E90FF', type: 'polygon' },
  watergang_as: { visible: false, layer: null, count: 0, color: '#4169E1', type: 'line' },
  watergang_zone: { visible: false, layer: null, count: 0, color: '#6495ED', type: 'polygon' },
  vaarweg: { visible: false, layer: null, count: 0, color: '#0000CD', type: 'line' },
  
  // Waterkeringen
  primaire_kering: { visible: false, layer: null, count: 0, color: '#8B4513', type: 'line' },
  regionale_kering: { visible: false, layer: null, count: 0, color: '#A0522D', type: 'line' },
  regionale_kering_zone: { visible: false, layer: null, count: 0, color: '#CD853F', type: 'polygon' },
  noodwaterkering: { visible: false, layer: null, count: 0, color: '#D2691E', type: 'line' },
  dijkverbetering: { visible: false, layer: null, count: 0, color: '#F4A460', type: 'polygon' },
  
  // Afvalwater & Riolering
  afvalwaterzuivering: { visible: false, layer: null, count: 0, icon: '🏭', type: 'point' },
  lozingspunt: { visible: false, layer: null, count: 0, icon: '💧', type: 'point' },
  overstortconstructie: { visible: false, layer: null, count: 0, icon: '🌊', type: 'point' },
  rioolstelsel: { visible: false, layer: null, count: 0, color: '#8B008B', type: 'line' },
  rioleringsgebied: { visible: false, layer: null, count: 0, color: '#9370DB', type: 'polygon' },
  rioleringsgebied_awzi: { visible: false, layer: null, count: 0, color: '#BA55D3', type: 'polygon' },
  rioleringsgebied_stelsel: { visible: false, layer: null, count: 0, color: '#DA70D6', type: 'polygon' },
  riolering_gebied_stroomrichting: { visible: false, layer: null, count: 0, color: '#DDA0DD', type: 'polygon' },
  riolering_gebied_planvorming: { visible: false, layer: null, count: 0, color: '#EE82EE', type: 'polygon' },
  rioolproject: { visible: false, layer: null, count: 0, color: '#FF00FF', type: 'polygon' },
  
  // Administratief
  polder: { visible: false, layer: null, count: 0, color: '#8B4513', type: 'polygon' },
  boezemgebied: { visible: false, layer: null, count: 0, color: '#A0522D', type: 'polygon' },
  gemeente: { visible: false, layer: null, count: 0, color: '#696969', type: 'polygon' },
  bebouwde_kom: { visible: false, layer: null, count: 0, color: '#808080', type: 'polygon' },
  afwateringseenheid: { visible: false, layer: null, count: 0, color: '#778899', type: 'polygon' },
  
  // Transport & Utilities
  transportleiding: { visible: false, layer: null, count: 0, color: '#FF4500', type: 'line' },
  transportleidingsegment: { visible: false, layer: null, count: 0, color: '#FF6347', type: 'line' },
  transportleidingmeetpunt: { visible: false, layer: null, count: 0, icon: '📊', type: 'point' },
  
  // Meetlocaties
  meetlocatie_waterkwantiteit: { visible: false, layer: null, count: 0, icon: '📈', type: 'point' },
  meetlocatie_waterkwaliteit: { visible: false, layer: null, count: 0, icon: '🔬', type: 'point' },
  
  // Overig
  contour: { visible: false, layer: null, count: 0, color: '#2F4F4F', type: 'line' },
  duingebied: { visible: false, layer: null, count: 0, color: '#F5DEB3', type: 'polygon' },
  baggeren_project: { visible: false, layer: null, count: 0, color: '#DEB887', type: 'polygon' },
  bouwwerk: { visible: false, layer: null, count: 0, icon: '🏗️', type: 'point' },
  bord: { visible: false, layer: null, count: 0, icon: '🚏', type: 'point' },
  afrastering: { visible: false, layer: null, count: 0, color: '#D3D3D3', type: 'line' },
  inspectieput: { visible: false, layer: null, count: 0, icon: '🔍', type: 'point' },
  molen: { visible: false, layer: null, count: 0, icon: '⚙️', type: 'point' },
  vispassage: { visible: false, layer: null, count: 0, icon: '🐟', type: 'point' },
  natuurvriendelijke_oever: { visible: false, layer: null, count: 0, color: '#90EE90', type: 'line' },
  natuurvriendelijke_oever_vlak: { visible: false, layer: null, count: 0, color: '#98FB98', type: 'polygon' },
  sifon: { visible: false, layer: null, count: 0, icon: '💧', type: 'line' },
  sifon_punt: { visible: false, layer: null, count: 0, icon: '💧', type: 'point' },
  put: { visible: false, layer: null, count: 0, icon: '🕳️', type: 'point' },
  steiger: { visible: false, layer: null, count: 0, icon: '⚓', type: 'point' },
  voorde: { visible: false, layer: null, count: 0, icon: '🚶', type: 'point' },
  marker: { visible: false, layer: null, count: 0, icon: '📍', type: 'point' },
  verdediging: { visible: false, layer: null, count: 0, icon: '🛡️', type: 'point' },
  verbeterinstallatie: { visible: false, layer: null, count: 0, icon: '🔧', type: 'point' },
  verbindingsstuk: { visible: false, layer: null, count: 0, icon: '🔗', type: 'point' },
  ontluchter: { visible: false, layer: null, count: 0, icon: '💨', type: 'point' },
  overnamepunt: { visible: false, layer: null, count: 0, icon: '📌', type: 'point' },
  mantelbuis: { visible: false, layer: null, count: 0, color: '#708090', type: 'line' },
  kathodischebescherming: { visible: false, layer: null, count: 0, icon: '⚡', type: 'point' },
  randvoorziening: { visible: false, layer: null, count: 0, icon: '🔧', type: 'point' },
  opstelplaats_noodbemaling: { visible: false, layer: null, count: 0, icon: '🚨', type: 'point' },
  opstelplaatsnoodbemleiding: { visible: false, layer: null, count: 0, icon: '🚨', type: 'point' },
  pig_lanceerinrichting: { visible: false, layer: null, count: 0, icon: '🔧', type: 'point' },
  iba: { visible: false, layer: null, count: 0, icon: '🏭', type: 'point' },
  installatie: { visible: false, layer: null, count: 0, icon: '⚙️', type: 'point' },
  primaire_kering_zone: { visible: false, layer: null, count: 0, color: '#8B4513', type: 'polygon' },
  transportleidingsegment_derden: { visible: false, layer: null, count: 0, color: '#FF7F50', type: 'line' },
  transportleidingsegment_noodleiding: { visible: false, layer: null, count: 0, color: '#FF4500', type: 'line' },
  rioleringsgebied_awzi_planvorming: { visible: false, layer: null, count: 0, color: '#C71585', type: 'polygon' },
  peilbesluitgebied_overzicht: { visible: false, layer: null, count: 0, color: '#FF8C00', type: 'polygon' },
  indeling_watergebiedsplannen: { visible: false, layer: null, count: 0, color: '#FFA500', type: 'polygon' },
})

// Categorieën voor legenda
const categories = [
  {
    name: 'Peilbeheer',
    layers: [
      { key: 'peilgebieden', label: 'Peilgebieden', type: 'polygon', color: '#ff7800' },
      { key: 'peilgebied_praktijk', label: 'Peilgebied Praktijk', type: 'polygon', color: '#ff9500' },
      { key: 'peilenkaart_praktijk', label: 'Peilenkaart Praktijk', type: 'polygon', color: '#ffb340' },
      { key: 'peilafwijking_praktijk', label: 'Peilafwijking Praktijk', type: 'polygon', color: '#ff6b6b' },
      { key: 'peilafwijking_vigerend', label: 'Peilafwijking Vigerend', type: 'polygon', color: '#ee5a6f' },
    ]
  },
  {
    name: 'Kunstwerken',
    layers: [
      { key: 'gemalen', label: 'Gemalen', type: 'point', icon: '🏭' },
      { key: 'gemaal_opgrootte', label: 'Gemaal Opgrootte', type: 'point', icon: '🏭' },
      { key: 'effluentgemaal', label: 'Effluentgemaal', type: 'point', icon: '💧' },
      { key: 'rioolgemaal', label: 'Rioolgemaal', type: 'point', icon: '🚰' },
      { key: 'stuwen', label: 'Stuwen', type: 'point', icon: '🌊' },
      { key: 'sluizen', label: 'Sluizen', type: 'point', icon: '🚪' },
      { key: 'duikers', label: 'Duikers', type: 'line', color: '#4169E1' },
      { key: 'duiker_punt', label: 'Duiker Punt', type: 'point', icon: '🔲' },
      { key: 'afsluiter', label: 'Afsluiter', type: 'point', icon: '🔧' },
      { key: 'afsluitmiddel', label: 'Afsluitmiddel', type: 'point', icon: '⚙️' },
      { key: 'inlaat', label: 'Inlaat', type: 'point', icon: '💨' },
      { key: 'inlaatrijnland', label: 'Inlaat Rijnland', type: 'point', icon: '💨' },
      { key: 'coupure', label: 'Coupure', type: 'point', icon: '🚧' },
      { key: 'dam', label: 'Dam', type: 'point', icon: '🏔️' },
      { key: 'brug', label: 'Brug', type: 'point', icon: '🌉' },
      { key: 'aquaduct', label: 'Aquaduct', type: 'point', icon: '🌉' },
    ]
  },
  {
    name: 'Watergangen',
    layers: [
      { key: 'watergang_vlak', label: 'Watergang Vlak', type: 'polygon', color: '#1E90FF' },
      { key: 'watergang_as', label: 'Watergang As', type: 'line', color: '#4169E1' },
      { key: 'watergang_zone', label: 'Watergang Zone', type: 'polygon', color: '#6495ED' },
      { key: 'vaarweg', label: 'Vaarweg', type: 'line', color: '#0000CD' },
    ]
  },
  {
    name: 'Waterkeringen',
    layers: [
      { key: 'primaire_kering', label: 'Primaire Kering', type: 'line', color: '#8B4513' },
      { key: 'regionale_kering', label: 'Regionale Kering', type: 'line', color: '#A0522D' },
      { key: 'regionale_kering_zone', label: 'Regionale Kering Zone', type: 'polygon', color: '#CD853F' },
      { key: 'noodwaterkering', label: 'Noodwaterkering', type: 'line', color: '#D2691E' },
      { key: 'dijkverbetering', label: 'Dijkverbetering', type: 'polygon', color: '#F4A460' },
    ]
  },
  {
    name: 'Afvalwater & Riolering',
    layers: [
      { key: 'afvalwaterzuivering', label: 'Afvalwaterzuivering', type: 'point', icon: '🏭' },
      { key: 'lozingspunt', label: 'Lozingspunt', type: 'point', icon: '💧' },
      { key: 'overstortconstructie', label: 'Overstortconstructie', type: 'point', icon: '🌊' },
      { key: 'rioolstelsel', label: 'Rioolstelsel', type: 'line', color: '#8B008B' },
      { key: 'rioleringsgebied', label: 'Rioleringsgebied', type: 'polygon', color: '#9370DB' },
      { key: 'rioleringsgebied_awzi', label: 'Rioleringsgebied AWZI', type: 'polygon', color: '#BA55D3' },
      { key: 'rioleringsgebied_stelsel', label: 'Rioleringsgebied Stelsel', type: 'polygon', color: '#DA70D6' },
      { key: 'riolering_gebied_stroomrichting', label: 'Riolering Stroomrichting', type: 'polygon', color: '#DDA0DD' },
      { key: 'riolering_gebied_planvorming', label: 'Riolering Planvorming', type: 'polygon', color: '#EE82EE' },
      { key: 'rioolproject', label: 'Rioolproject', type: 'polygon', color: '#FF00FF' },
    ]
  },
  {
    name: 'Administratief',
    layers: [
      { key: 'polder', label: 'Polder', type: 'polygon', color: '#8B4513' },
      { key: 'boezemgebied', label: 'Boezemgebied', type: 'polygon', color: '#A0522D' },
      { key: 'gemeente', label: 'Gemeente', type: 'polygon', color: '#696969' },
      { key: 'bebouwde_kom', label: 'Bebouwde Kom', type: 'polygon', color: '#808080' },
      { key: 'afwateringseenheid', label: 'Afwateringseenheid', type: 'polygon', color: '#778899' },
    ]
  },
  {
    name: 'Transport & Utilities',
    layers: [
      { key: 'transportleiding', label: 'Transportleiding', type: 'line', color: '#FF4500' },
      { key: 'transportleidingsegment', label: 'Transportleiding Segment', type: 'line', color: '#FF6347' },
      { key: 'transportleidingmeetpunt', label: 'Transportleiding Meetpunt', type: 'point', icon: '📊' },
    ]
  },
  {
    name: 'Meetlocaties',
    layers: [
      { key: 'meetlocatie_waterkwantiteit', label: 'Meetlocatie Waterkwantiteit', type: 'point', icon: '📈' },
      { key: 'meetlocatie_waterkwaliteit', label: 'Meetlocatie Waterkwaliteit', type: 'point', icon: '🔬' },
    ]
  },
  {
    name: 'Overig',
    layers: [
      { key: 'contour', label: 'Contour', type: 'line', color: '#2F4F4F' },
      { key: 'duingebied', label: 'Duingebied', type: 'polygon', color: '#F5DEB3' },
      { key: 'baggeren_project', label: 'Baggeren Project', type: 'polygon', color: '#DEB887' },
      { key: 'bouwwerk', label: 'Bouwwerk', type: 'point', icon: '🏗️' },
      { key: 'bord', label: 'Bord', type: 'point', icon: '🚏' },
      { key: 'afrastering', label: 'Afrastering', type: 'line', color: '#D3D3D3' },
      { key: 'inspectieput', label: 'Inspectieput', type: 'point', icon: '🔍' },
      { key: 'molen', label: 'Molen', type: 'point', icon: '⚙️' },
      { key: 'vispassage', label: 'Vispassage', type: 'point', icon: '🐟' },
      { key: 'natuurvriendelijke_oever', label: 'Natuurvriendelijke Oever', type: 'line', color: '#90EE90' },
      { key: 'natuurvriendelijke_oever_vlak', label: 'Natuurvriendelijke Oever Vlak', type: 'polygon', color: '#98FB98' },
      { key: 'sifon', label: 'Sifon', type: 'line', color: '#4169E1' },
      { key: 'sifon_punt', label: 'Sifon Punt', type: 'point', icon: '💧' },
      { key: 'put', label: 'Put', type: 'point', icon: '🕳️' },
      { key: 'steiger', label: 'Steiger', type: 'point', icon: '⚓' },
      { key: 'voorde', label: 'Voorde', type: 'point', icon: '🚶' },
      { key: 'marker', label: 'Marker', type: 'point', icon: '📍' },
      { key: 'verdediging', label: 'Verdediging', type: 'point', icon: '🛡️' },
      { key: 'verbeterinstallatie', label: 'Verbeterinstallatie', type: 'point', icon: '🔧' },
      { key: 'verbindingsstuk', label: 'Verbindingsstuk', type: 'point', icon: '🔗' },
      { key: 'ontluchter', label: 'Ontluchter', type: 'point', icon: '💨' },
      { key: 'overnamepunt', label: 'Overnamepunt', type: 'point', icon: '📌' },
      { key: 'mantelbuis', label: 'Mantelbuis', type: 'line', color: '#708090' },
      { key: 'kathodischebescherming', label: 'Kathodische Bescherming', type: 'point', icon: '⚡' },
      { key: 'randvoorziening', label: 'Randvoorziening', type: 'point', icon: '🔧' },
      { key: 'opstelplaats_noodbemaling', label: 'Opstelplaats Noodbemaling', type: 'point', icon: '🚨' },
      { key: 'opstelplaatsnoodbemleiding', label: 'Opstelplaats Noodbem Leiding', type: 'point', icon: '🚨' },
      { key: 'pig_lanceerinrichting', label: 'PIG Lanceerinrichting', type: 'point', icon: '🔧' },
      { key: 'iba', label: 'IBA', type: 'point', icon: '🏭' },
      { key: 'installatie', label: 'Installatie', type: 'point', icon: '⚙️' },
    ]
  }
]

// Helper functie om lokale bestandsnaam te vinden
const getLocalLayerUrl = (layerName) => {
  // Map layer names naar directory namen en bestandsnamen in rijnland_kaartlagen
  const dirMap = {
    'peilgebieden': { dir: 'Peilgebied_vigerend_besluit', file: 'PeilgebiedVigerend_layer0.geojson' },
    'peilgebied_praktijk': { dir: 'Peilgebied_praktijk_soort_gebied', file: 'Peilgebied_praktijk_soort_gebied_layer0.geojson' },
    'peilenkaart_praktijk': { dir: 'Peilenkaart_praktijk', file: 'Peilenkaart (praktijk)_layer0.geojson' },
    'peilafwijking_praktijk': { dir: 'Peilafwijking_praktijk', file: 'PeilafwijkingGebied_layer0.geojson' },
    'peilafwijking_vigerend': { dir: 'Peilafwijking_vigerend_besluit', file: 'PeilafwijkingGebied_layer0.geojson' },
    'gemalen': { dir: 'Gemaal', file: 'Gemaal_layer0.geojson' },
    'gemaal_opgrootte': { dir: 'Gemaal_opgrootte', file: 'Gemaal_layer0.geojson' },
    'effluentgemaal': { dir: 'Effluentgemaal', file: 'Effluentgemaal_layer0.geojson' },
    'rioolgemaal': { dir: 'Rioolgemaal_influent', file: 'Rioolgemaal_influent_layer0.geojson' },
    'stuwen': { dir: 'Stuw', file: 'Stuw_layer0.geojson' },
    'sluizen': { dir: 'Sluis', file: 'Sluis_layer0.geojson' },
    'duikers': { dir: 'Duiker', file: 'Duiker_layer0.geojson' },
    'duiker_punt': { dir: 'Duiker_punt', file: 'DuikerSifonHevelPunt_layer0.geojson' },
    'afsluiter': { dir: 'Afsluiter', file: 'Afsluiter_layer0.geojson' },
    'afsluitmiddel': { dir: 'Afsluitmiddel', file: 'Afsluitmiddel_layer0.geojson' },
    'inlaat': { dir: 'Inlaat', file: 'Inlaat_layer0.geojson' },
    'inlaatrijnland': { dir: 'InlaatRijnland', file: 'InlaatRijnland_layer0.geojson' },
    'coupure': { dir: 'Coupure', file: 'Coupure_layer0.geojson' },
    'dam': { dir: 'Dam', file: 'Dam_layer0.geojson' },
    'brug': { dir: 'Brug', file: 'Brug_layer0.geojson' },
    'aquaduct': { dir: 'Aquaduct', file: 'Aquaduct_layer0.geojson' },
    'watergang_vlak': { dir: 'Watergang_vlak', file: 'WatergangVlak_layer0.geojson' },
    'watergang_as': { dir: 'Watergang_as', file: 'Watergang_as_layer0.geojson' },
    'watergang_zone': { dir: 'Watergang_zone', file: 'Watergang_zone_layer0.geojson' },
    'vaarweg': { dir: 'Vaarweg', file: 'Vaarweg_layer0.geojson' },
    'primaire_kering': { dir: 'Primaire_kering', file: 'Primaire_kering_layer0.geojson' },
    'regionale_kering': { dir: 'Regionale_kering', file: 'Regionale_kering_layer0.geojson' },
    'regionale_kering_zone': { dir: 'Regionale_Kering_zone', file: 'RegionaleKeringZones_layer0.geojson' },
    'noodwaterkering': { dir: 'Noodwaterkering', file: 'Noodwaterkering_layer0.geojson' },
    'dijkverbetering': { dir: 'Dijkverbetering', file: 'Dijkverbetering_layer0.geojson' },
    'afvalwaterzuivering': { dir: 'Afvalwaterzuivering', file: 'Afvalwaterzuivering_layer0.geojson' },
    'lozingspunt': { dir: 'Lozingspunt', file: 'Lozingspunt_layer0.geojson' },
    'overstortconstructie': { dir: 'Overstortconstructie', file: 'Overstortconstructie_layer0.geojson' },
    'rioolstelsel': { dir: 'Rioolstelsel', file: 'Rioolstelsel_layer0.geojson' },
    'rioleringsgebied': { dir: 'Rioleringsgebied_stelsel_gerealiseerd', file: 'Rioleringsgebied_stelsel_gerealiseerd_layer0.geojson' },
    'rioleringsgebied_awzi': { dir: 'Rioleringsgebied_AWZI_gebied_gerealiseerd', file: 'Rioleringsgebied_AWZI_gebied_gerealiseerd_layer0.geojson' },
    'rioleringsgebied_stelsel': { dir: 'Rioleringsgebied_stelsel_gerealiseerd', file: 'Rioleringsgebied_stelsel_gerealiseerd_layer0.geojson' },
    'riolering_gebied_stroomrichting': { dir: 'Rioleringsgebied_stroomrichting', file: 'Rioleringsgebied_stroomrichting_layer0.geojson' },
    'riolering_gebied_planvorming': { dir: 'Rioleringsgebied_stelsel_planvorming', file: 'Rioleringsgebied_stelsel_planvorming_layer0.geojson' },
    'rioolproject': { dir: 'Rioolproject', file: 'Rioolproject_layer0.geojson' },
    'polder': { dir: 'Polder', file: 'Polder_layer0.geojson' },
    'boezemgebied': { dir: 'Boezemgebied', file: 'Boezemgebied_layer0.geojson' },
    'gemeente': { dir: 'Gemeente', file: 'Gemeente_layer0.geojson' },
    'bebouwde_kom': { dir: 'Bebouwde_kom', file: 'Bebouwde_kom_layer0.geojson' },
    'afwateringseenheid': { dir: 'Afwateringseenheid', file: 'Afwateringseenheid_layer0.geojson' },
    'transportleiding': { dir: 'Transportleiding', file: 'Transportleiding_layer0.geojson' },
    'transportleidingsegment': { dir: 'Transportleidingsegment_Rijnland', file: 'Transportleidingsegment_Rijnland_layer0.geojson' },
    'transportleidingmeetpunt': { dir: 'TransportleidingMeetpunt', file: 'TransportleidingMeetpunt_layer0.geojson' },
    'meetlocatie_waterkwantiteit': { dir: 'Meetlocatie_waterkwantiteit', file: 'Meetlocatie_waterkwantiteit_layer0.geojson' },
    'meetlocatie_waterkwaliteit': { dir: 'Meetlocatie_waterkwaltiteit', file: 'Meetlocatie_waterkwaltiteit_layer0.geojson' },
    'contour': { dir: 'Contour', file: 'Contour_layer0.geojson' },
    'duingebied': { dir: 'Duingebied', file: 'Duingebied_layer0.geojson' },
    'baggeren_project': { dir: 'Baggeren_project', file: 'Baggertraject_layer0.geojson' },
    'bouwwerk': { dir: 'Bouwwerk', file: 'Bouwwerk_layer0.geojson' },
    'bord': { dir: 'Bord', file: 'Bord_layer0.geojson' },
    'afrastering': { dir: 'Afrastering', file: 'Afrastering_layer0.geojson' },
    'inspectieput': { dir: 'Inspectieput', file: 'Inspectieput_layer0.geojson' },
    'molen': { dir: 'Molen', file: 'Molen_layer0.geojson' },
    'vispassage': { dir: 'Vispassage', file: 'Vispassage_layer0.geojson' },
    'natuurvriendelijke_oever': { dir: 'Natuurvriendelijke_oever', file: 'Natuurvriendelijke_oever_layer0.geojson' },
    'natuurvriendelijke_oever_vlak': { dir: 'Natuurvriendelijke_oever_vlak', file: 'Natuurvriendelijke_oever_vlak_layer0.geojson' },
    'sifon': { dir: 'Sifon', file: 'Sifon_layer0.geojson' },
    'sifon_punt': { dir: 'Sifon_punt', file: 'Sifon_punt_layer0.geojson' },
    'put': { dir: 'Put', file: 'Put_layer0.geojson' },
    'steiger': { dir: 'Steiger', file: 'Steiger_layer0.geojson' },
    'voorde': { dir: 'Voorde', file: 'Voorde_layer0.geojson' },
    'marker': { dir: 'Marker', file: 'Marker_layer0.geojson' },
    'verdediging': { dir: 'Verdediging', file: 'Verdediging_layer0.geojson' },
    'verbeterinstallatie': { dir: 'Verbeterinstallatie', file: 'Verbeterinstallatie_layer0.geojson' },
    'verbindingsstuk': { dir: 'Verbindingsstuk', file: 'Verbindingsstuk_layer0.geojson' },
    'ontluchter': { dir: 'Ontluchter', file: 'Ontluchter_layer1.geojson' },
    'overnamepunt': { dir: 'Overnamepunt', file: 'Overnamepunt_layer0.geojson' },
    'mantelbuis': { dir: 'Mantelbuis', file: 'Mantelbuis_layer0.geojson' },
    'kathodischebescherming': { dir: 'KathodischeBescherming', file: 'KathodischeBescherming_layer0.geojson' },
    'randvoorziening': { dir: 'Randvoorziening', file: 'Randvoorziening_layer0.geojson' },
    'opstelplaats_noodbemaling': { dir: 'Opstelplaats_noodbemaling', file: 'Opstelplaats_noodbemaling_layer0.geojson' },
    'opstelplaatsnoodbemleiding': { dir: 'OpstelplaatsNoodbemLeiding', file: 'OpstelplaatsNoodbemLeiding_layer0.geojson' },
    'pig_lanceerinrichting': { dir: 'PIG_Lanceerinrichting', file: 'PIG_Lanceerinrichting_layer0.geojson' },
    'iba': { dir: 'Iba', file: 'IBA_layer0.geojson' },
    'installatie': { dir: 'Installatie', file: 'Installatie_layer0.geojson' },
    'primaire_kering_zone': { dir: 'Primaire_kering_zone', file: 'Primaire_kering_zone_layer0.geojson' },
    'transportleidingsegment_derden': { dir: 'Transportleidingsegment_derden', file: 'Transportleidingsegment_derden_layer0.geojson' },
    'transportleidingsegment_noodleiding': { dir: 'Transportleidingsegment_noodleiding', file: 'Transportleidingsegment_noodleiding_layer0.geojson' },
    'rioleringsgebied_awzi_planvorming': { dir: 'Rioleringsgebied_awzi_gebied_planvorming', file: 'Rioleringsgebied_awzi_gebied_planvorming_layer0.geojson' },
    'peilbesluitgebied_overzicht': { dir: 'Peilbesluitgebied_overzicht', file: 'PeilbesluitGebied_layer0.geojson' },
    'indeling_watergebiedsplannen': { dir: 'Indeling_Watergebiedsplannen', file: 'IndelingWatergebiedsplannen_layer0.geojson' }
  }
  
  const mapping = dirMap[layerName]
  if (!mapping) return null
  
  // Gebruik absolute pad vanaf root, niet relatief
  const basePath = import.meta.env.BASE_URL.replace(/\/$/, '') // Remove trailing slash
  return `${basePath}/peilbesluiten/rijnland_kaartlagen/${mapping.dir}/${mapping.file}`
}

// Server URLs voor alle lagen (fallback als lokale bestanden niet beschikbaar zijn)
const serverUrls = {
  peilgebieden: 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Peilgebied_vigerend_besluit/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  peilgebied_praktijk: 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Peilgebied_praktijk_soort_gebied/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  peilenkaart_praktijk: 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Peilenkaart_praktijk/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  peilafwijking_praktijk: 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Peilafwijking_praktijk/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  peilafwijking_vigerend: 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Peilafwijking_vigerend_besluit/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  gemalen: getLocalLayerUrl('gemalen') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Gemaal/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  gemaal_opgrootte: getLocalLayerUrl('gemaal_opgrootte') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Gemaal_opgrootte/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  effluentgemaal: getLocalLayerUrl('effluentgemaal') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Effluentgemaal/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  rioolgemaal: getLocalLayerUrl('rioolgemaal') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Rioolgemaal_influent/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  stuwen: getLocalLayerUrl('stuwen') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Stuw/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  sluizen: getLocalLayerUrl('sluizen') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Sluis/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  duikers: getLocalLayerUrl('duikers') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Duiker/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  duiker_punt: getLocalLayerUrl('duiker_punt') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Duiker_punt/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  afsluiter: getLocalLayerUrl('afsluiter') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Afsluiter/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  afsluitmiddel: getLocalLayerUrl('afsluitmiddel') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Afsluitmiddel/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  inlaat: getLocalLayerUrl('inlaat') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Inlaat/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  inlaatrijnland: getLocalLayerUrl('inlaatrijnland') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/InlaatRijnland/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  coupure: getLocalLayerUrl('coupure') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Coupure/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  dam: getLocalLayerUrl('dam') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Dam/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  brug: getLocalLayerUrl('brug') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Brug/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  aquaduct: getLocalLayerUrl('aquaduct') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Aquaduct/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  watergang_vlak: getLocalLayerUrl('watergang_vlak') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Watergang_vlak/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson',
  watergang_as: getLocalLayerUrl('watergang_as') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Watergang_as/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  watergang_zone: getLocalLayerUrl('watergang_zone') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Watergang_zone/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  vaarweg: getLocalLayerUrl('vaarweg') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Vaarweg/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  primaire_kering: getLocalLayerUrl('primaire_kering') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Primaire_kering/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  regionale_kering: getLocalLayerUrl('regionale_kering') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Regionale_kering/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  regionale_kering_zone: getLocalLayerUrl('regionale_kering_zone') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Regionale_Kering_zone/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  noodwaterkering: getLocalLayerUrl('noodwaterkering') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Noodwaterkering/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  dijkverbetering: getLocalLayerUrl('dijkverbetering') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Dijkverbetering/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  afvalwaterzuivering: getLocalLayerUrl('afvalwaterzuivering') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Afvalwaterzuivering/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  lozingspunt: getLocalLayerUrl('lozingspunt') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Lozingspunt/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  overstortconstructie: getLocalLayerUrl('overstortconstructie') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Overstortconstructie/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  rioolstelsel: getLocalLayerUrl('rioolstelsel') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Rioolstelsel/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  rioleringsgebied: getLocalLayerUrl('rioleringsgebied') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Rioleringsgebied_stelsel_gerealiseerd/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  rioleringsgebied_awzi: getLocalLayerUrl('rioleringsgebied_awzi') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Rioleringsgebied_AWZI_gebied_gerealiseerd/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  rioleringsgebied_stelsel: getLocalLayerUrl('rioleringsgebied_stelsel') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Rioleringsgebied_stelsel_gerealiseerd/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  riolering_gebied_stroomrichting: getLocalLayerUrl('riolering_gebied_stroomrichting') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Rioleringsgebied_stroomrichting/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  riolering_gebied_planvorming: getLocalLayerUrl('riolering_gebied_planvorming') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Rioleringsgebied_stelsel_planvorming/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  rioolproject: getLocalLayerUrl('rioolproject') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Rioolproject/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  polder: getLocalLayerUrl('polder') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Polder/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  boezemgebied: getLocalLayerUrl('boezemgebied') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Boezemgebied/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  gemeente: getLocalLayerUrl('gemeente') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Gemeente/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  bebouwde_kom: getLocalLayerUrl('bebouwde_kom') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Bebouwde_kom/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  afwateringseenheid: getLocalLayerUrl('afwateringseenheid') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Afwateringseenheid/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  transportleiding: getLocalLayerUrl('transportleiding') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Transportleiding/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  transportleidingsegment: getLocalLayerUrl('transportleidingsegment') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Transportleidingsegment_Rijnland/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  transportleidingmeetpunt: getLocalLayerUrl('transportleidingmeetpunt') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/TransportleidingMeetpunt/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  meetlocatie_waterkwantiteit: getLocalLayerUrl('meetlocatie_waterkwantiteit') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Meetlocatie_waterkwantiteit/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  meetlocatie_waterkwaliteit: getLocalLayerUrl('meetlocatie_waterkwaliteit') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Meetlocatie_waterkwaltiteit/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  contour: getLocalLayerUrl('contour') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Contour/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  duingebied: getLocalLayerUrl('duingebied') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Duingebied/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  baggeren_project: getLocalLayerUrl('baggeren_project') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Baggeren_project/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  bouwwerk: getLocalLayerUrl('bouwwerk') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Bouwwerk/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  bord: getLocalLayerUrl('bord') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Bord/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  afrastering: getLocalLayerUrl('afrastering') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Afrastering/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  inspectieput: getLocalLayerUrl('inspectieput') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Inspectieput/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  molen: getLocalLayerUrl('molen') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Molen/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  vispassage: getLocalLayerUrl('vispassage') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Vispassage/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  natuurvriendelijke_oever: getLocalLayerUrl('natuurvriendelijke_oever') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Natuurvriendelijke_oever/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  natuurvriendelijke_oever_vlak: getLocalLayerUrl('natuurvriendelijke_oever_vlak') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Natuurvriendelijke_oever_vlak/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  sifon: getLocalLayerUrl('sifon') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Sifon/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  sifon_punt: getLocalLayerUrl('sifon_punt') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Sifon_punt/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  put: getLocalLayerUrl('put') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Put/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  steiger: getLocalLayerUrl('steiger') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Steiger/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  voorde: getLocalLayerUrl('voorde') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Voorde/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  marker: getLocalLayerUrl('marker') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Marker/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  verdediging: getLocalLayerUrl('verdediging') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Verdediging/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  verbeterinstallatie: getLocalLayerUrl('verbeterinstallatie') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Verbeterinstallatie/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  verbindingsstuk: getLocalLayerUrl('verbindingsstuk') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Verbindingsstuk/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  ontluchter: getLocalLayerUrl('ontluchter') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Ontluchter/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  overnamepunt: getLocalLayerUrl('overnamepunt') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Overnamepunt/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  mantelbuis: getLocalLayerUrl('mantelbuis') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Mantelbuis/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  kathodischebescherming: getLocalLayerUrl('kathodischebescherming') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/KathodischeBescherming/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  randvoorziening: getLocalLayerUrl('randvoorziening') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Randvoorziening/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  opstelplaats_noodbemaling: getLocalLayerUrl('opstelplaats_noodbemaling') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Opstelplaats_noodbemaling/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  opstelplaatsnoodbemleiding: getLocalLayerUrl('opstelplaatsnoodbemleiding') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/OpstelplaatsNoodbemLeiding/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  pig_lanceerinrichting: getLocalLayerUrl('pig_lanceerinrichting') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/PIG_Lanceerinrichting/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  iba: getLocalLayerUrl('iba') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Iba/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  installatie: getLocalLayerUrl('installatie') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Installatie/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  primaire_kering_zone: getLocalLayerUrl('primaire_kering_zone') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Primaire_kering_zone/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  transportleidingsegment_derden: getLocalLayerUrl('transportleidingsegment_derden') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Transportleidingsegment_derden/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  transportleidingsegment_noodleiding: getLocalLayerUrl('transportleidingsegment_noodleiding') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Transportleidingsegment_noodleiding/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  rioleringsgebied_awzi_planvorming: getLocalLayerUrl('rioleringsgebied_awzi_planvorming') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Rioleringsgebied_awzi_gebied_planvorming/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  peilbesluitgebied_overzicht: getLocalLayerUrl('peilbesluitgebied_overzicht') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Peilbesluitgebied_overzicht/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
  indeling_watergebiedsplannen: getLocalLayerUrl('indeling_watergebiedsplannen') || 'https://rijnland.enl-mcs.nl/arcgis/rest/services/Indeling_Watergebiedsplannen/MapServer/0/query?where=1%3D1&outFields=*&f=geojson',
}

const visibleLayersCount = computed(() => {
  return Object.values(layers).filter(l => l.visible).length
})

const totalLayersCount = computed(() => {
  return Object.keys(layers).length
})

const loadedLayersCount = computed(() => {
  return Object.values(layers).filter(l => l.layer !== null).length
})

const getCategoryCount = (categoryLayers) => {
  return categoryLayers.filter(l => layers[l.key].visible).length + ' / ' + categoryLayers.length
}

const toggleLegend = () => {
  legendExpanded.value = !legendExpanded.value
}

const initMap = () => {
  map.value = L.map('all-layers-map').setView([52.15, 4.8], 11)

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
    'HYPERLINK': 'Link',
    'MAXIMALECAPACITEIT': 'Maximale Capaciteit (m³/s)',
    'FUNCTIEGEMAAL': 'Functie Gemaal'
  }
  return keyMap[key] || key.charAt(0).toUpperCase() + key.slice(1).toLowerCase()
}

const createPointIcon = (emoji, status = null, isGemaal = false, gemaalCode = null) => {
  // Voor gemalen: gebruik SVG icoon
  if (isGemaal) {
    // Check of dit gemaal data heeft
    const heeftData = gemaalCode && gemalenMetData.value.has(gemaalCode)
    
    let backgroundColor = 'transparent'
    let borderColor = 'transparent'
    let borderWidth = '0px'
    let iconFilter = ''
    
    if (heeftData) {
      // Groen voor gemalen met data beschikbaar
      backgroundColor = 'rgba(16, 185, 129, 0.3)' // Green background
      borderColor = '#10b981'
      borderWidth = '3px'
      // Maak het icoon groen met CSS filter
      iconFilter = 'brightness(0) saturate(100%) invert(48%) sepia(79%) saturate(2476%) hue-rotate(130deg) brightness(95%) contrast(86%)'
    } else if (status === 'aan') {
      backgroundColor = 'rgba(16, 185, 129, 0.2)' // Green-ish background
      borderColor = '#10b981'
      borderWidth = '2px'
    } else if (status === 'uit') {
      backgroundColor = 'rgba(107, 114, 128, 0.1)' // Gray-ish
      borderColor = '#9ca3af'
      borderWidth = '2px'
    }
    const style = heeftData || status
      ? `background-color: ${backgroundColor}; border: ${borderWidth} solid ${borderColor}; border-radius: 50%; width: 46px; height: 46px; display: flex; align-items: center; justify-content: center; box-shadow: ${heeftData ? '0 0 8px rgba(16, 185, 129, 0.5)' : 'none'};` 
      : 'width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;'

    return L.divIcon({
      html: `<div style="${style}"><img src="${import.meta.env.BASE_URL}gemaal-icon.svg" alt="Gemaal" style="width: 40px; height: 40px; ${iconFilter ? `filter: ${iconFilter};` : ''}" /></div>`,
      className: 'custom-icon gemaal-icon',
      iconSize: [46, 46],
      iconAnchor: [23, 23]
    })
  }

  // Voor andere punten: gebruik emoji
  let backgroundColor = 'transparent'
  let borderColor = 'transparent'
  
  if (status === 'aan') {
    backgroundColor = 'rgba(16, 185, 129, 0.2)' // Green-ish background
    borderColor = '#10b981'
  } else if (status === 'uit') {
    backgroundColor = 'rgba(107, 114, 128, 0.1)' // Gray-ish
    borderColor = '#9ca3af'
  }

  const style = status 
    ? `background-color: ${backgroundColor}; border: 2px solid ${borderColor}; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;` 
    : ''

  return L.divIcon({
    html: `<div style="font-size: 24px; ${style}">${emoji}</div>`,
    className: 'custom-icon',
    iconSize: [40, 40],
    iconAnchor: [20, 20]
  })
}

// RD (EPSG:28992) naar WGS84 (EPSG:4326) conversie
const rdToWgs84 = (x, y) => {
  // Eenvoudige RD naar WGS84 conversie (benadering)
  // Meer accurate conversie zou proj4 gebruiken, maar voor nu gebruiken we een benadering
  const dX = (x - 155000) * 0.00001
  const dY = (y - 463000) * 0.00001
  const sumN = (3235.65389 * dY) + (-32.58297 * Math.pow(dX, 2)) + (-0.2475 * Math.pow(dY, 2)) + (-0.84978 * Math.pow(dX, 2) * dY) + (-0.0655 * Math.pow(dY, 3)) + (-0.01709 * Math.pow(dX, 2) * Math.pow(dY, 2)) + (-0.00738 * dX) + (0.0053 * Math.pow(dX, 3)) + (-0.00039 * Math.pow(dX, 2) * Math.pow(dY, 3)) + (0.00033 * Math.pow(dX, 4)) + (-0.00012 * dX * dY)
  const sumE = (5260.52916 * dX) + (105.94684 * dX * dY) + (2.45656 * dX * Math.pow(dY, 2)) + (-0.81885 * Math.pow(dX, 3)) + (0.05594 * dX * Math.pow(dY, 3)) + (-0.05607 * Math.pow(dX, 3) * dY) + (0.01199 * dY) + (-0.00256 * Math.pow(dX, 3) * Math.pow(dY, 2)) + (0.00128 * dX * Math.pow(dY, 4)) + (0.00022 * Math.pow(dY, 2)) + (-0.00022 * Math.pow(dX, 2)) + (0.00026 * Math.pow(dX, 5))
  
  const latitude = 52.15517440 + (sumN / 3600)
  const longitude = 5.38720621 + (sumE / 3600)
  
  return [longitude, latitude] // GeoJSON gebruikt [lng, lat]
}

// Convert ArcGIS format to GeoJSON and transform RD coordinates to WGS84
const convertToGeoJSON = (data, layerName = null) => {
  // Als het al GeoJSON is (heeft properties en coordinates), voeg alleen layerName toe
  if (data.type === 'FeatureCollection' && data.features && data.features[0]) {
    const firstFeature = data.features[0]
    // Check of het al GeoJSON is (heeft properties en coordinates, geen attributes/rings)
    if (firstFeature.properties && !firstFeature.attributes && 
        firstFeature.geometry && firstFeature.geometry.coordinates && !firstFeature.geometry.rings) {
      // Al GeoJSON, voeg alleen layerName toe
      if (layerName) {
        data.features.forEach(f => {
          if (f.properties) {
            f.properties._layerName = layerName
          }
        })
      }
      return data
    }
  }
  
  // Check if data has ArcGIS format (with attributes) and convert to GeoJSON
  if (data.features && data.features[0]) {
    const firstFeature = data.features[0]
    const hasAttributes = firstFeature.attributes && !firstFeature.properties
    const hasRings = firstFeature.geometry && firstFeature.geometry.rings
    const hasPaths = firstFeature.geometry && firstFeature.geometry.paths
    const hasArcGISPoint = firstFeature.geometry && firstFeature.geometry.x !== undefined && firstFeature.geometry.y !== undefined
    
    // Check if coordinates are RD (large numbers > 10000)
    let isRD = false
    if (hasRings && firstFeature.geometry.rings[0] && firstFeature.geometry.rings[0][0]) {
      isRD = Math.abs(firstFeature.geometry.rings[0][0][0]) > 10000
    } else if (hasPaths && firstFeature.geometry.paths[0] && firstFeature.geometry.paths[0][0]) {
      isRD = Math.abs(firstFeature.geometry.paths[0][0][0]) > 10000
    } else if (hasArcGISPoint) {
      isRD = Math.abs(firstFeature.geometry.x) > 10000
    }
    
    if (hasAttributes || hasRings || hasPaths || hasArcGISPoint) {
      // Convert ArcGIS format to GeoJSON
      return {
        type: 'FeatureCollection',
        features: data.features.map(f => {
          let geometry = f.geometry
          
          // Convert ArcGIS rings to GeoJSON Polygon coordinates
          if (geometry && geometry.rings) {
            const coordinates = geometry.rings.map(ring => {
              return ring.map(coord => {
                // Convert RD to WGS84 if needed
                if (isRD && coord.length >= 2) {
                  return rdToWgs84(coord[0], coord[1])
                }
                return coord
              })
            })
            geometry = {
              type: 'Polygon',
              coordinates: coordinates
            }
          }
          // Convert ArcGIS paths to GeoJSON LineString coordinates
          else if (geometry && geometry.paths) {
            const coordinates = geometry.paths.map(path => {
              return path.map(coord => {
                if (isRD && coord.length >= 2) {
                  return rdToWgs84(coord[0], coord[1])
                }
                return coord
              })
            })
            geometry = {
              type: geometry.paths.length === 1 ? 'LineString' : 'MultiLineString',
              coordinates: geometry.paths.length === 1 ? coordinates[0] : coordinates
            }
          }
          // Convert ArcGIS points to GeoJSON Point coordinates
          else if (geometry && geometry.x !== undefined && geometry.y !== undefined) {
            const coords = isRD ? rdToWgs84(geometry.x, geometry.y) : [geometry.x, geometry.y]
            geometry = {
              type: 'Point',
              coordinates: coords
            }
          }
          
      const feature = {
        type: 'Feature',
        geometry: geometry,
        properties: f.attributes || f.properties || {}
      }
      // Store layer name for styling if provided
      if (layerName) {
        feature.properties._layerName = layerName
      }
      return feature
        })
      }
    }
  }
  return data
}

// Process layer data and add to map
const processLayerData = (layerName, config, geojsonData) => {
  if (!geojsonData || !geojsonData.features || geojsonData.features.length === 0) {
    console.warn(`Geen features gevonden voor ${layerName}`, geojsonData)
    return
  }
  
  console.log(`✓ ${layerName} geladen: ${geojsonData.features.length} features`)
  console.log(`Eerste feature:`, geojsonData.features[0])

  config.count = geojsonData.features.length

  const geoJsonOptions = {
    onEachFeature: (feature, layer) => {
      layer.on('click', () => {
        // Voor gemalen: toon grafiek bij klik
        if (layerName === 'gemalen') {
          const code = feature.properties.CODE
          const naam = feature.properties.NAAM || code || 'Onbekend'
          if (code) {
            selectedGemaal.value = { code, naam }
            showChart.value = true
          }
        } else {
          // Voor andere lagen: toon normale info panel
          selectedFeature.value = {
            title: feature.properties.NAAM || feature.properties.CODE || feature.properties.Name || 'Onbekend',
            type: layerName,
            properties: feature.properties
          }
        }
      })
      
      // Voor peilgebieden: toon zomer- en winterpeil bij hover
      if ((layerName === 'peilgebieden' || layerName === 'peilgebied_praktijk' || 
           layerName === 'peilenkaart_praktijk' || layerName === 'peilafwijking_praktijk' || 
           layerName === 'peilafwijking_vigerend') && !(layer instanceof L.Marker)) {
        // Store layer name in feature for styling
        feature.properties._layerName = layerName
        layer.on('mouseover', () => {
          showPeilgebiedTooltip(feature, layer, layerName)
        })
        layer.on('mouseout', () => {
          hidePeilgebiedTooltip(layer, layerName)
        })
      }
    }
  }

  // Style based on geometry type
  const firstFeature = geojsonData.features[0]
  if (!firstFeature || !firstFeature.geometry) {
    console.error(`Geen geometry gevonden in eerste feature voor ${layerName}`)
    return
  }

  const geometryType = firstFeature.geometry.type
  console.log(`Geometry type voor ${layerName}: ${geometryType}`)

  if (geometryType === 'Point') {
    geoJsonOptions.pointToLayer = (feature, latlng) => {
      let icon = config.icon
      let status = null
      
      // Speciale handling voor gemalen status
      if (layerName === 'gemalen' && gemaalStatus.value) {
        const code = feature.properties.CODE
        if (code && gemaalStatus.value.stations && gemaalStatus.value.stations[code]) {
          const stationStatus = gemaalStatus.value.stations[code]
          status = stationStatus.status
        }
      }
      
      const isGemaal = layerName === 'gemalen' || layerName === 'gemaal_opgrootte' || layerName === 'effluentgemaal' || layerName === 'rioolgemaal'
      const code = feature.properties.CODE
      return L.marker(latlng, { icon: createPointIcon(config.icon, status, isGemaal, code) })
    }
  } else if (geometryType === 'Polygon' || geometryType === 'MultiPolygon') {
    geoJsonOptions.style = {
      color: config.color || '#ff7800',
      weight: 2,
      fillOpacity: 0.3,
      fillColor: config.color || '#ff7800'
    }
  } else if (geometryType === 'LineString' || geometryType === 'MultiLineString') {
    geoJsonOptions.style = {
      color: config.color || '#1E90FF',
      weight: 3,
      opacity: 0.7
    }
  }

  try {
    config.layer = L.geoJSON(geojsonData, geoJsonOptions)
    console.log(`Layer aangemaakt voor ${layerName}, zichtbaar: ${config.visible}`)

    if (config.visible) {
      config.layer.addTo(map.value)
      console.log(`Layer toegevoegd aan kaart voor ${layerName}`)
      
      // Fit bounds als het een polygon layer is
      if (geometryType === 'Polygon' || geometryType === 'MultiPolygon') {
        const bounds = config.layer.getBounds()
        if (bounds.isValid()) {
          map.value.fitBounds(bounds, { padding: [50, 50] })
        }
      }
    }
    
    // Update iconen voor gemalen laag als de lijst al beschikbaar is
    if (layerName === 'gemalen' && gemalenMetData.value.size > 0) {
      // Wacht even zodat de laag volledig is geladen
      setTimeout(() => {
        updateGemaalIconen()
      }, 100)
    }
  } catch (error) {
    console.error(`Fout bij aanmaken layer voor ${layerName}:`, error)
  }
}

const loadLayer = async (layerName, config) => {
  if (config.layer) return // Already loaded

  try {
    loading.value = true
    
    // ALTIJD eerst lokale bestand proberen
    const localUrl = getLocalLayerUrl(layerName)
    const serverUrl = serverUrls[layerName]
    
    // Probeer eerst lokale bestand
    if (localUrl) {
      console.log(`Laden van ${layerName} vanaf lokaal bestand: ${localUrl}`)
      try {
        const response = await fetch(localUrl)
        if (response.ok) {
          const data = await response.json()
          const geojsonData = convertToGeoJSON(data, layerName)
          processLayerData(layerName, config, geojsonData)
          loading.value = false
          return
        } else {
          console.warn(`Lokaal bestand niet beschikbaar (${response.status}) voor ${layerName}, probeer server...`)
        }
      } catch (e) {
        console.warn(`Fout bij laden lokaal bestand voor ${layerName}:`, e.message, '- probeer server...')
      }
    }
    
    // Fallback naar server URL als lokaal bestand niet beschikbaar is
    const fallbackUrl = serverUrl
    if (fallbackUrl && !fallbackUrl.includes('/peilbesluiten/') && !fallbackUrl.includes('/data/')) {
      console.log(`Laden van ${layerName} vanaf server: ${fallbackUrl}`)
      try {
        const response = await fetch(fallbackUrl)
        if (response.ok) {
          const data = await response.json()
          const geojsonData = convertToGeoJSON(data, layerName)
          processLayerData(layerName, config, geojsonData)
          loading.value = false
          return
        } else {
          console.error(`HTTP error voor ${layerName}: ${response.status} - ${response.statusText}`)
        }
      } catch (e) {
        console.error(`Fout bij laden vanaf server voor ${layerName}:`, e.message)
      }
    } else if (!localUrl && !fallbackUrl) {
      console.error(`Geen beschikbare URL voor ${layerName} (noch lokaal, noch server)`)
    }

  } catch (error) {
    console.error(`Error loading ${layerName}:`, error)
  } finally {
    loading.value = false
  }
}

const toggleLayer = async (layerName) => {
  const config = layers[layerName]

  // Als de laag nog niet geladen is en visible is true, laad de laag
  if (!config.layer && config.visible) {
    loading.value = true
    try {
      await loadLayer(layerName, config)
    } catch (error) {
      console.error(`Fout bij laden van laag ${layerName}:`, error)
      // Reset visibility bij error
      config.visible = false
      loading.value = false
      return
    }
    loading.value = false
  }

  // Voeg toe aan of verwijder van kaart op basis van visibility
  if (config.layer) {
    if (config.visible) {
      // Alleen toevoegen als de laag niet al op de kaart staat
      if (!map.value.hasLayer(config.layer)) {
        config.layer.addTo(map.value)
      }
      
      // Update iconen voor gemalen laag als de lijst beschikbaar is
      if (layerName === 'gemalen' && gemalenMetData.value.size > 0) {
        setTimeout(() => {
          updateGemaalIconen()
        }, 100)
      }
    } else {
      // Verwijder van kaart als deze erop staat
      if (map.value.hasLayer(config.layer)) {
        map.value.removeLayer(config.layer)
      }
    }
  }
}

const closeInfo = () => {
  selectedFeature.value = null
}

// Keyboard shortcuts (CCG richtlijn - toegankelijkheid)
const handleKeyPress = (event) => {
  // Escape sluit modals
  if (event.key === 'Escape') {
    if (selectedFeature.value) {
      closeInfo()
    }
    if (showChart.value) {
      showChart.value = false
    }
    if (dataError.value) {
      dataError.value = null
    }
  }
  
  // L toggle legenda
  if ((event.key === 'l' || event.key === 'L') && !event.ctrlKey && !event.metaKey) {
    legendExpanded.value = !legendExpanded.value
  }
}

// Keyboard shortcuts (CCG richtlijn - toegankelijkheid)
const handleKeyPress = (event) => {
  // Escape sluit modals
  if (event.key === 'Escape') {
    if (selectedFeature.value) {
      closeInfo()
    }
    if (showChart.value) {
      showChart.value = false
    }
    if (dataError.value) {
      dataError.value = null
    }
  }
  
  // L toggle legenda
  if ((event.key === 'l' || event.key === 'L') && !event.ctrlKey && !event.metaKey) {
    legendExpanded.value = !legendExpanded.value
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
})

// Get gemaal trend data for selected feature
const selectedGemaalTrends = computed(() => {
  if (!selectedFeature.value || selectedFeature.value.type !== 'gemalen') return null
  if (!gemaalStatus.value?.stations) return null
  
  const gemaalCode = selectedFeature.value.properties?.CODE
  if (!gemaalCode) return null
  
  const stationData = gemaalStatus.value.stations[gemaalCode]
  if (!stationData) return null
  
  return {
    trends: stationData.trends || null,
    window_stats: stationData.window_stats || null,
    summary: stationData.summary || null
  }
})

// Get gemaal status for selected feature
const selectedGemaalStatus = computed(() => {
  if (!selectedFeature.value || selectedFeature.value.type !== 'gemalen') return null
  if (!gemaalStatus.value?.stations) return null
  
  const gemaalCode = selectedFeature.value.properties?.CODE
  if (!gemaalCode) return null
  
  return gemaalStatus.value.stations[gemaalCode] || null
})

// Helper functions for trend display
const getWindowLabel = (windowKey) => {
  const labels = {
    '30_min': '30 minuten',
    '60_min': '1 uur',
    '180_min': '3 uur'
  }
  return labels[windowKey] || windowKey
}

const getTrendLabel = (direction) => {
  const labels = {
    'increasing': 'Stijgend',
    'decreasing': 'Dalend',
    'stable': 'Stabiel'
  }
  return labels[direction] || direction
}

const getTrendColorClass = (direction) => {
  if (direction === 'increasing') return 'text-green-600'
  if (direction === 'decreasing') return 'text-red-600'
  return 'text-gray-600'
}

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

// Toon peilgebied tooltip met zomer- en winterpeil
const showPeilgebiedTooltip = (feature, layer, layerName) => {
  const props = feature.properties
  const naam = props.NAAM || props.CODE || 'Onbekend'
  
  let tooltipContent = `<div style="min-width: 200px;"><strong>${naam}</strong><br/>`
  
  if (props.ZOMERPEIL !== null && props.ZOMERPEIL !== undefined) {
    tooltipContent += `<div style="margin-top: 6px;">☀️ Zomerpeil: <strong style="color: #f59e0b;">${props.ZOMERPEIL.toFixed(2)} m NAP</strong></div>`
  }
  
  if (props.WINTERPEIL !== null && props.WINTERPEIL !== undefined) {
    tooltipContent += `<div style="margin-top: 4px;">❄️ Winterpeil: <strong style="color: #3b82f6;">${props.WINTERPEIL.toFixed(2)} m NAP</strong></div>`
  }
  
  if (props.SOORTPEILBEHEER) {
    tooltipContent += `<div style="margin-top: 6px; padding-top: 6px; border-top: 1px solid #e5e7eb; font-size: 0.85em; color: #6b7280;">${props.SOORTPEILBEHEER}</div>`
  }
  
  if (!props.ZOMERPEIL && !props.WINTERPEIL && !props.SOORTPEILBEHEER) {
    tooltipContent += `<div style="margin-top: 4px; font-size: 0.85em; color: #9ca3af;">Geen peilgegevens beschikbaar</div>`
  }
  
  tooltipContent += `</div>`
  
  layer.bindTooltip(tooltipContent, {
    permanent: false,
    direction: 'top',
    className: 'peilgebied-tooltip bg-white px-3 py-2 rounded shadow-lg border border-gray-300',
    offset: [0, -10]
  }).openTooltip()
  
  // Highlight de laag
  if (layer.setStyle) {
    const config = layers[layerName]
    layer.setStyle({
      weight: 3,
      fillOpacity: 0.5,
      fillColor: config?.color || '#ff7800',
      color: config?.color || '#ff7800'
    })
  }
}

// Verberg peilgebied tooltip
const hidePeilgebiedTooltip = (layer, layerName) => {
  layer.closeTooltip()
  
  // Reset style - gebruik de originele layer config
  if (layer.setStyle && layerName) {
    const config = layers[layerName]
    if (config && config.color) {
      layer.setStyle({
        weight: 2,
        fillOpacity: 0.3,
        fillColor: config.color,
        color: config.color
      })
    }
  }
}

const loadInitialLayers = async () => {
  // Geen lagen standaard laden - gebruiker moet ze zelf aanzetten
  // Dit voorkomt dat alle lagen direct worden geladen bij het openen
}

const fetchGemaalStatus = async () => {
  try {
    loading.value = true
    loadingMessage.value = 'Gemaal status ophalen...'
    dataError.value = null
    
    const response = await fetch('./data/gemaal_status_latest.json')
    if (response.ok) {
      const data = await response.json()
      gemaalStatus.value = data
      
      // Bereken success rate (CCG richtlijn)
      if (data.stations) {
        const total = Object.keys(data.stations).length
        const successful = Object.values(data.stations).filter(s => 
          s.status && s.status !== 'error' && s.status !== 'unknown'
        ).length
        dataSuccessRate.value = total > 0 ? successful / total : null
      }
      
      console.log('Global gemaal status loaded:', data.active_stations, 'active stations')
      
      loading.value = false
      loadingMessage.value = ''
      
      // Update gemalen met data lijst als die al geladen is
      if (gemalenMetData.value.size > 0) {
        const statusGemalen = Object.keys(data.stations || {})
        statusGemalen.forEach(code => {
          gemalenMetData.value.add(code)
        })
        console.log(`Gemalen met data uitgebreid met status data: ${gemalenMetData.value.size} totaal`)
        
        // Update iconen als laag al geladen is
        if (layers.gemalen.layer) {
          updateGemaalIconen()
        }
      }
    }
  } catch (e) {
    console.error('Could not load global gemaal status:', e)
    loading.value = false
    loadingMessage.value = ''
    dataError.value = `Fout bij ophalen gemaal status: ${e.message || 'Onbekende fout'}`
    dataSuccessRate.value = null
  }
}

// Retry data load functie (CCG richtlijn)
const retryDataLoad = () => {
  dataError.value = null
  fetchGemaalStatus()
}

// Laad lijst van gemalen met beschikbare data
const loadGemalenMetData = async () => {
  try {
    // Haal lijst op via proxy endpoint die de directory leest
    const response = await fetch('/api/gemalen-met-data')
    if (response.ok) {
      const data = await response.json()
      gemalenMetData.value = new Set(data.gemalen || [])
      console.log(`Gemalen met opgeslagen data: ${gemalenMetData.value.size} gemalen`)
      
      // Voeg ook gemalen toe uit gemaal_status_latest.json (hebben ook data via API)
      if (gemaalStatus.value && gemaalStatus.value.stations) {
        const statusGemalen = Object.keys(gemaalStatus.value.stations)
        statusGemalen.forEach(code => {
          gemalenMetData.value.add(code)
        })
        console.log(`Totaal gemalen met data (opgeslagen + status): ${gemalenMetData.value.size} gemalen`)
      }
      
      // Update iconen voor gemalen laag als deze al geladen is
      if (layers.gemalen.layer) {
        updateGemaalIconen()
      }
    }
  } catch (e) {
    console.warn('Kon lijst van gemalen met data niet laden:', e)
    // Fallback: gebruik alleen gemaalStatus als die beschikbaar is
    if (gemaalStatus.value && gemaalStatus.value.stations) {
      gemalenMetData.value = new Set(Object.keys(gemaalStatus.value.stations))
      if (layers.gemalen.layer) {
        updateGemaalIconen()
      }
    }
  }
}

// Update iconen voor alle gemalen op de kaart
const updateGemaalIconen = () => {
  if (!layers.gemalen.layer) {
    console.log('Gemaal laag niet geladen, kan iconen niet updaten')
    return
  }
  
  let updated = 0
  layers.gemalen.layer.eachLayer((layer) => {
    if (layer instanceof L.Marker) {
      const feature = layer.feature
      if (feature && feature.properties) {
        const code = feature.properties.CODE
        const status = gemaalStatus.value?.stations?.[code]?.status || null
        const isGemaal = true
        const heeftData = code && gemalenMetData.value.has(code)
        const newIcon = createPointIcon('🏭', status, isGemaal, code)
        layer.setIcon(newIcon)
        if (heeftData) updated++
      }
    }
  })
  console.log(`Gemaal iconen geüpdatet: ${updated} gemalen met data gemarkeerd`)
}

onMounted(async () => {
  initMap()
  await fetchGemaalStatus()
  await loadGemalenMetData()
  await loadInitialLayers()
})
</script>

