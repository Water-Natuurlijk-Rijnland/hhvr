<template>
  <div
    v-if="showIndicator"
    class="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-white rounded-lg shadow-lg border-2 p-3 z-30 flex items-center gap-3 max-w-md"
    :class="{
      'border-green-200 bg-green-50': quality === 'good',
      'border-yellow-200 bg-yellow-50': quality === 'warning',
      'border-red-200 bg-red-50': quality === 'error'
    }"
    role="status"
    :aria-live="quality === 'error' ? 'assertive' : 'polite'"
  >
    <span class="text-xl">{{ qualityIcon }}</span>
    <div class="flex-1">
      <p class="text-sm font-semibold" :class="qualityTextColor">
        {{ qualityMessage }}
      </p>
      <p v-if="details" class="text-xs mt-1" :class="qualityTextColor">
        {{ details }}
      </p>
    </div>
    <button
      @click="showIndicator = false"
      class="text-gray-400 hover:text-gray-600"
      aria-label="Sluit indicator"
    >
      ×
    </button>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  stats: {
    type: Object,
    default: null
  },
  successRate: {
    type: Number,
    default: null
  },
  lastError: {
    type: String,
    default: null
  }
})

const showIndicator = ref(true)

const quality = computed(() => {
  if (!props.stats) return 'error'
  
  const dataAge = Date.now() - new Date(props.stats.generated_at).getTime()
  const ageMinutes = dataAge / 60000
  
  // Error als data ouder dan 2 uur
  if (ageMinutes > 120) return 'error'
  
  // Warning als data ouder dan 30 minuten of success rate < 80%
  if (ageMinutes > 30 || (props.successRate && props.successRate < 0.8)) {
    return 'warning'
  }
  
  return 'good'
})

const qualityIcon = computed(() => {
  switch (quality.value) {
    case 'good': return '✅'
    case 'warning': return '⚠️'
    case 'error': return '❌'
    default: return 'ℹ️'
  }
})

const qualityMessage = computed(() => {
  switch (quality.value) {
    case 'good':
      return 'Data is actueel en betrouwbaar'
    case 'warning':
      return 'Data kan mogelijk niet volledig actueel zijn'
    case 'error':
      return 'Data is mogelijk niet beschikbaar of verouderd'
    default:
      return 'Data status onbekend'
  }
})

const qualityTextColor = computed(() => {
  switch (quality.value) {
    case 'good': return 'text-green-800'
    case 'warning': return 'text-yellow-800'
    case 'error': return 'text-red-800'
    default: return 'text-gray-800'
  }
})

const details = computed(() => {
  if (!props.stats) return null
  
  const dataAge = Date.now() - new Date(props.stats.generated_at).getTime()
  const ageMinutes = Math.floor(dataAge / 60000)
  
  let detail = `Laatste update: ${ageMinutes} minuten geleden`
  
  if (props.successRate) {
    const successPercent = Math.round(props.successRate * 100)
    detail += ` | Success rate: ${successPercent}%`
  }
  
  if (props.lastError) {
    detail += ` | Laatste fout: ${props.lastError}`
  }
  
  return detail
})

// Auto-hide na 10 seconden voor goede kwaliteit
watch(quality, (newQuality) => {
  if (newQuality === 'good') {
    setTimeout(() => {
      showIndicator.value = false
    }, 10000)
  } else {
    showIndicator.value = true
  }
})
</script>

