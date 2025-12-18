<template>
  <div v-if="visible" class="fixed top-4 left-1/2 transform -translate-x-1/2 bg-white/90 backdrop-blur-sm rounded-xl shadow-lg border border-blue-100 p-4 z-20">
    <!-- Main Stats Row -->
    <div class="flex gap-6 items-center">
      <!-- Active Stations -->
      <div class="flex items-center gap-3">
        <div class="p-2 bg-green-100 rounded-full">
          <span class="text-xl">🏭</span>
        </div>
        <div>
          <p class="text-xs text-gray-500 font-semibold uppercase tracking-wider">Actieve Gemalen</p>
          <p class="text-xl font-bold text-gray-800">
            {{ activeStations }} <span class="text-sm text-gray-400 font-normal">/ {{ totalStations }}</span>
          </p>
        </div>
      </div>

      <div class="h-10 w-px bg-gray-200"></div>

      <!-- Total Flow -->
      <div class="flex items-center gap-3">
        <div class="p-2 bg-blue-100 rounded-full">
          <span class="text-xl">💧</span>
        </div>
        <div>
          <p class="text-xs text-gray-500 font-semibold uppercase tracking-wider">Totaal Debiet</p>
          <div class="flex items-center gap-2">
            <p class="text-xl font-bold text-gray-800">
              {{ totalDebiet }} <span class="text-sm text-gray-400 font-normal">m³/s</span>
            </p>
            <TrendIndicator 
              v-if="overallTrend" 
              :trend="overallTrend" 
              :show-label="false"
              size="small"
            />
          </div>
        </div>
      </div>

      <div class="h-10 w-px bg-gray-200"></div>

      <!-- Last Update -->
      <div class="text-right">
        <p class="text-xs text-gray-400">Laatste update</p>
        <p class="text-xs font-mono text-gray-600">{{ lastUpdate }}</p>
      </div>
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

const visible = computed(() => !!props.stats)

const activeStations = computed(() => props.stats?.active_stations || 0)
const totalStations = computed(() => props.stats?.total_stations || 0)
const totalDebiet = computed(() => props.stats?.total_debiet_m3s?.toFixed(1) || '0.0')

const lastUpdate = computed(() => {
  if (!props.stats?.generated_at) return '-'
  return new Date(props.stats.generated_at).toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' })
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
