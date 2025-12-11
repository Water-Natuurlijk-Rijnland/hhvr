<template>
  <div v-if="visible" class="fixed top-4 left-1/2 transform -translate-x-1/2 bg-white/90 backdrop-blur-sm rounded-xl shadow-lg border border-blue-100 p-4 z-20 flex gap-6 items-center">
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
        <p class="text-xl font-bold text-gray-800">
          {{ totalDebiet }} <span class="text-sm text-gray-400 font-normal">m³/s</span>
        </p>
      </div>
    </div>

    <div class="h-10 w-px bg-gray-200"></div>

    <!-- Last Update -->
    <div class="text-right">
      <p class="text-xs text-gray-400">Laatste update</p>
      <p class="text-xs font-mono text-gray-600">{{ lastUpdate }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  stats: {
    type: Object,
    default: () => null
  }
})

const visible = computed(() => !!props.stats)

const activeStations = computed(() => props.stats?.active_stations || 0)
const totalStations = computed(() => props.stats?.total_stations || 0)
const totalDebiet = computed(() => props.stats?.total_debiet_m3s?.toFixed(1) || '0.0')

const lastUpdate = computed(() => {
  if (!props.stats?.generated_at) return '-'
  return new Date(props.stats.generated_at).toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' })
})
</script>
