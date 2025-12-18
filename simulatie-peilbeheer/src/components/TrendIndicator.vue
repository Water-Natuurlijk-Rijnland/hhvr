<template>
  <div class="flex items-center gap-1" :title="tooltip">
    <!-- Trend Arrow -->
    <span 
      v-if="trend"
      class="text-sm font-semibold"
      :class="trendClass"
    >
      {{ trendIcon }}
    </span>
    <span v-else class="text-gray-400 text-xs">—</span>
    
    <!-- Trend Label -->
    <span 
      v-if="showLabel && trend"
      class="text-xs font-medium"
      :class="trendTextClass"
    >
      {{ trendLabel }}
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  trend: {
    type: Object,
    default: null
  },
  showLabel: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: 'normal', // 'small', 'normal', 'large'
    validator: (value) => ['small', 'normal', 'large'].includes(value)
  }
})

const trendIcon = computed(() => {
  if (!props.trend) return '—'
  
  const direction = props.trend.direction || 'stable'
  const strength = props.trend.strength || 'weak'
  
  if (direction === 'increasing') {
    return strength === 'strong' ? '↗' : '↑'
  } else if (direction === 'decreasing') {
    return strength === 'strong' ? '↘' : '↓'
  } else {
    return '→'
  }
})

const trendLabel = computed(() => {
  if (!props.trend) return 'Geen trend'
  
  const direction = props.trend.direction || 'stable'
  const strength = props.trend.strength || 'weak'
  
  const directionLabels = {
    'increasing': 'Stijgend',
    'decreasing': 'Dalend',
    'stable': 'Stabiel'
  }
  
  const strengthLabels = {
    'strong': 'sterk',
    'moderate': 'matig',
    'weak': 'zwak'
  }
  
  return `${directionLabels[direction]} (${strengthLabels[strength]})`
})

const trendClass = computed(() => {
  if (!props.trend) return ''
  
  const direction = props.trend.direction || 'stable'
  const strength = props.trend.strength || 'weak'
  
  const baseClasses = {
    'small': 'text-xs',
    'normal': 'text-sm',
    'large': 'text-lg'
  }[props.size]
  
  if (direction === 'increasing') {
    return strength === 'strong' 
      ? `${baseClasses} text-green-600` 
      : `${baseClasses} text-green-500`
  } else if (direction === 'decreasing') {
    return strength === 'strong'
      ? `${baseClasses} text-red-600`
      : `${baseClasses} text-red-500`
  } else {
    return `${baseClasses} text-gray-500`
  }
})

const trendTextClass = computed(() => {
  if (!props.trend) return ''
  
  const direction = props.trend.direction || 'stable'
  
  if (direction === 'increasing') {
    return 'text-green-600'
  } else if (direction === 'decreasing') {
    return 'text-red-600'
  } else {
    return 'text-gray-500'
  }
})

const tooltip = computed(() => {
  if (!props.trend) return 'Geen trend data beschikbaar'
  
  const slope = props.trend.slope_per_hour || 0
  const r2 = props.trend.r_squared || 0
  
  return `${trendLabel.value}\nSlope: ${slope.toFixed(3)} m³/s/uur\nBetrouwbaarheid: ${(r2 * 100).toFixed(1)}%`
})
</script>

