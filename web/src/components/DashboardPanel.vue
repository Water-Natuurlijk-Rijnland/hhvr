<template>
  <div 
    v-if="visible" 
    class="fixed top-4 left-1/2 transform -translate-x-1/2 bg-white/90 backdrop-blur-sm rounded-xl shadow-lg border border-blue-100 p-4 z-20"
    role="region"
    aria-label="Gemaal status dashboard"
    aria-live="polite"
    aria-atomic="true"
  >
    <!-- Data actualiteit waarschuwing -->
    <div 
      v-if="isStale || isVeryStale" 
      class="absolute -top-8 left-0 right-0 flex justify-center mb-2"
    >
      <div 
        :class="[
          'px-3 py-1 rounded text-xs font-semibold',
          isVeryStale ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
        ]"
        role="alert"
        :aria-live="isVeryStale ? 'assertive' : 'polite'"
      >
        <span v-if="isVeryStale">⚠️</span>
        <span v-else>ℹ️</span>
        Data is {{ dataAgeText }} oud
        <span v-if="isVeryStale"> - mogelijk niet actueel</span>
      </div>
    </div>

    <!-- Main Stats Row -->
    <div class="flex gap-6 items-center">
      <!-- Active Stations -->
      <div class="flex items-center gap-3">
        <div class="p-2 bg-green-100 rounded-full" aria-hidden="true">
          <span class="text-xl">🏭</span>
        </div>
        <div>
          <p class="text-xs text-gray-500 font-semibold uppercase tracking-wider">Actieve Gemalen</p>
          <p class="text-xl font-bold text-gray-800">
            <span :aria-label="`${activeStations} van ${totalStations} gemalen actief`">
              {{ activeStations }} <span class="text-sm text-gray-400 font-normal">/ {{ totalStations }}</span>
            </span>
          </p>
          <p v-if="expectedActiveRange" class="text-xs text-gray-500 mt-1">
            Normaal: {{ expectedActiveRange.min }}-{{ expectedActiveRange.max }} actief
          </p>
        </div>
      </div>

      <div class="h-10 w-px bg-gray-200" aria-hidden="true"></div>

      <!-- Total Flow -->
      <div class="flex items-center gap-3">
        <div class="p-2 bg-blue-100 rounded-full" aria-hidden="true">
          <span class="text-xl">💧</span>
        </div>
        <div>
          <p class="text-xs text-gray-500 font-semibold uppercase tracking-wider">Totaal Debiet</p>
          <div class="flex items-center gap-2">
            <p class="text-xl font-bold text-gray-800">
              <span :aria-label="`${totalDebiet} kubieke meter per seconde`">
                {{ totalDebiet }} <span class="text-sm text-gray-400 font-normal">m³/s</span>
              </span>
            </p>
            <TrendIndicator 
              v-if="overallTrend" 
              :trend="overallTrend" 
              :show-label="false"
              size="small"
            />
          </div>
          <p v-if="expectedDebietRange" class="text-xs text-gray-500 mt-1">
            Normaal: {{ expectedDebietRange.min }}-{{ expectedDebietRange.max }} m³/s
          </p>
        </div>
      </div>

      <div class="h-10 w-px bg-gray-200" aria-hidden="true"></div>

      <!-- Last Update -->
      <div class="text-right">
        <p class="text-xs text-gray-400">Laatste update</p>
        <p 
          class="text-xs font-mono text-gray-600"
          :title="`Data gegenereerd op ${fullTimestamp}`"
        >
          {{ lastUpdate }}
        </p>
        <p class="text-xs text-gray-400 mt-1">
          {{ dataAgeText }} geleden
        </p>
      </div>

      <!-- Help button -->
      <button
        @click="showHelp = !showHelp"
        class="ml-2 text-gray-400 hover:text-gray-600 text-sm"
        aria-label="Uitleg over dashboard"
        title="Klik voor uitleg"
      >
        ℹ️
      </button>
    </div>

    <!-- Trend Summary Row (expandable) -->
    <div v-if="hasTrendData" class="mt-3 pt-3 border-t border-gray-200">
      <button
        @click="trendsExpanded = !trendsExpanded"
        class="w-full flex items-center justify-between text-xs text-gray-600 hover:text-gray-800 transition-colors"
      >
        <span class="font-semibold">📈 Trend Overzicht</span>
        <span>{{ trendsExpanded ? '−' : '+' }}</span>
      </button>
      
      <div v-if="trendsExpanded" class="mt-3 grid grid-cols-3 gap-4">
        <!-- 30 min trend -->
        <div class="bg-gray-50 rounded-lg p-2">
          <p class="text-xs text-gray-500 mb-1">30 min</p>
          <TrendIndicator 
            :trend="aggregateTrends['30_min']" 
            :show-label="true"
            size="small"
          />
          <p v-if="aggregateTrends['30_min']" class="text-xs text-gray-400 mt-1">
            {{ getTrendCount('30_min', 'increasing') }}↑ 
            {{ getTrendCount('30_min', 'decreasing') }}↓ 
            {{ getTrendCount('30_min', 'stable') }}→
          </p>
        </div>

        <!-- 60 min trend -->
        <div class="bg-gray-50 rounded-lg p-2">
          <p class="text-xs text-gray-500 mb-1">1 uur</p>
          <TrendIndicator 
            :trend="aggregateTrends['60_min']" 
            :show-label="true"
            size="small"
          />
          <p v-if="aggregateTrends['60_min']" class="text-xs text-gray-400 mt-1">
            {{ getTrendCount('60_min', 'increasing') }}↑ 
            {{ getTrendCount('60_min', 'decreasing') }}↓ 
            {{ getTrendCount('60_min', 'stable') }}→
          </p>
        </div>

        <!-- 180 min trend -->
        <div class="bg-gray-50 rounded-lg p-2">
          <p class="text-xs text-gray-500 mb-1">3 uur</p>
          <TrendIndicator 
            :trend="aggregateTrends['180_min']" 
            :show-label="true"
            size="small"
          />
          <p v-if="aggregateTrends['180_min']" class="text-xs text-gray-400 mt-1">
            {{ getTrendCount('180_min', 'increasing') }}↑ 
            {{ getTrendCount('180_min', 'decreasing') }}↓ 
            {{ getTrendCount('180_min', 'stable') }}→
          </p>
        </div>
      </div>
    </div>

    <!-- Help panel -->
    <div 
      v-if="showHelp"
      class="fixed top-24 left-1/2 transform -translate-x-1/2 bg-white rounded-lg shadow-xl border border-gray-200 p-4 z-30 max-w-md mt-2"
      role="dialog"
      aria-labelledby="help-title"
    >
      <h4 id="help-title" class="font-bold text-gray-800 mb-2">Uitleg Dashboard</h4>
      <ul class="text-sm text-gray-600 space-y-2">
        <li>
          <strong>Actieve Gemalen:</strong> Aantal gemalen dat momenteel water pompt.
          Normaal gesproken zijn 5-15% van alle gemalen actief, afhankelijk van het seizoen.
        </li>
        <li>
          <strong>Totaal Debiet:</strong> Totale hoeveelheid water die door alle actieve gemalen wordt gepompt.
          Wordt elke 30 minuten bijgewerkt via de Hydronet API.
        </li>
        <li>
          <strong>Laatste update:</strong> Wanneer de data voor het laatst is bijgewerkt.
          Data ouder dan 30 minuten kan mogelijk niet actueel zijn.
        </li>
      </ul>
      <button
        @click="showHelp = false"
        class="mt-3 text-sm text-blue-600 hover:text-blue-800"
      >
        Sluiten
      </button>
    </div>

    <!-- Screen reader alleen tekst -->
    <div class="sr-only" aria-live="polite">
      <p>
        Gemaal status dashboard. 
        {{ activeStations }} van {{ totalStations }} gemalen zijn actief.
        Totaal debiet is {{ totalDebiet }} kubieke meter per seconde.
        Laatste update was {{ dataAgeText }} geleden.
        <span v-if="isStale">Waarschuwing: data is mogelijk niet actueel.</span>
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import TrendIndicator from './TrendIndicator.vue'

const props = defineProps({
  stats: {
    type: Object,
    default: () => null
  }
})

const trendsExpanded = ref(false)
const showHelp = ref(false)

const visible = computed(() => !!props.stats)

const activeStations = computed(() => props.stats?.active_stations || 0)
const totalStations = computed(() => props.stats?.total_stations || 0)
const totalDebiet = computed(() => props.stats?.total_debiet_m3s?.toFixed(1) || '0.0')

const lastUpdate = computed(() => {
  if (!props.stats?.generated_at) return '-'
  return new Date(props.stats.generated_at).toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' })
})

const fullTimestamp = computed(() => {
  if (!props.stats?.generated_at) return '-'
  return new Date(props.stats.generated_at).toLocaleString('nl-NL')
})

// Data actualiteit berekening (CCG richtlijn)
const dataAge = computed(() => {
  if (!props.stats?.generated_at) return null
  const now = Date.now()
  const generated = new Date(props.stats.generated_at).getTime()
  return now - generated
})

const dataAgeText = computed(() => {
  if (!dataAge.value) return 'onbekend'
  const minutes = Math.floor(dataAge.value / 60000)
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) {
    return `${hours} uur${hours > 1 ? 'en' : ''}`
  } else if (minutes > 0) {
    return `${minutes} minuten`
  } else {
    return 'minder dan een minuut'
  }
})

const isStale = computed(() => {
  if (!dataAge.value) return false
  return dataAge.value > 30 * 60 * 1000 // 30 minuten
})

const isVeryStale = computed(() => {
  if (!dataAge.value) return false
  return dataAge.value > 60 * 60 * 1000 // 1 uur
})

// Normale waarden referentie (CCG richtlijn)
const expectedActiveRange = computed(() => {
  // Normaal gesproken zijn 5-15% van alle gemalen actief
  const total = totalStations.value
  if (!total) return null
  return {
    min: Math.floor(total * 0.05),
    max: Math.floor(total * 0.15)
  }
})

const expectedDebietRange = computed(() => {
  // Normaal debiet ligt tussen 20-60 m³/s voor Rijnland gebied
  return {
    min: 20,
    max: 60
  }
})

// Check if trend data is available
const hasTrendData = computed(() => {
  if (!props.stats?.stations) return false
  return Object.values(props.stats.stations).some(station => 
    station.trends && Object.keys(station.trends).length > 0
  )
})

// Calculate overall trend from aggregate trends
const overallTrend = computed(() => {
  if (!props.stats?.aggregate_trends) return null
  
  const trends30 = props.stats.aggregate_trends['30_min']
  if (!trends30) return null
  
  // Determine overall direction based on counts
  const total = trends30.increasing + trends30.decreasing + trends30.stable
  if (total === 0) return null
  
  const increasingPct = trends30.increasing / total
  const decreasingPct = trends30.decreasing / total
  
  if (increasingPct > 0.5) {
    return { direction: 'increasing', strength: increasingPct > 0.7 ? 'strong' : 'moderate' }
  } else if (decreasingPct > 0.5) {
    return { direction: 'decreasing', strength: decreasingPct > 0.7 ? 'strong' : 'moderate' }
  } else {
    return { direction: 'stable', strength: 'weak' }
  }
})

// Get aggregate trends per window
const aggregateTrends = computed(() => {
  if (!props.stats?.aggregate_trends) {
    return {
      '30_min': null,
      '60_min': null,
      '180_min': null
    }
  }
  
  const trends = props.stats.aggregate_trends
  const result = {}
  
  // Calculate dominant trend for each window
  for (const window of ['30_min', '60_min', '180_min']) {
    const windowTrends = trends[window]
    if (!windowTrends) {
      result[window] = null
      continue
    }
    
    const total = windowTrends.increasing + windowTrends.decreasing + windowTrends.stable
    if (total === 0) {
      result[window] = null
      continue
    }
    
    const increasingPct = windowTrends.increasing / total
    const decreasingPct = windowTrends.decreasing / total
    
    if (increasingPct > decreasingPct && increasingPct > 0.4) {
      result[window] = { 
        direction: 'increasing', 
        strength: increasingPct > 0.6 ? 'strong' : increasingPct > 0.5 ? 'moderate' : 'weak'
      }
    } else if (decreasingPct > increasingPct && decreasingPct > 0.4) {
      result[window] = { 
        direction: 'decreasing', 
        strength: decreasingPct > 0.6 ? 'strong' : decreasingPct > 0.5 ? 'moderate' : 'weak'
      }
    } else {
      result[window] = { direction: 'stable', strength: 'weak' }
    }
  }
  
  return result
})

// Get trend count for a specific window and direction
const getTrendCount = (window, direction) => {
  if (!props.stats?.aggregate_trends?.[window]) return 0
  return props.stats.aggregate_trends[window][direction] || 0
})
</script>

<style scoped>
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>
