<!-- AnimationPanel.vue -->
<template>
  <div class="bg-white rounded-lg shadow-2xl border border-gray-200 flex flex-col overflow-hidden">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 p-4 rounded-t-lg">
      <div class="flex justify-between items-start">
        <div class="flex-1">
          <h2 class="text-lg font-semibold text-gray-800 mb-4">{{ polderData.name }}</h2>
          <div class="flex flex-col gap-2 text-sm text-gray-600 mb-4">
            <div>
              <span class="font-medium">Jaar:</span> {{ currentYear }}
            </div>
            <div>
              <span class="font-medium">Drooglegging:</span> {{ currentYearData.drooglegging.toFixed(1) }} cm
            </div>
            <div>
              <span class="font-medium">Ondergrens zomerpeil:</span> {{ (currentYearData.zomerpeil_ondergrens / 100).toFixed(2) }} m NAP
            </div>
          </div>
        </div>
        <button 
          @click="$emit('close')"
          class="text-gray-500 hover:text-gray-700 p-1 rounded-full hover:bg-gray-100 transition-colors ml-4 cursor-pointer"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    </div>
    
    <!-- Animation Container -->
    <div class="flex-1">
      <svg 
        width="100%" 
        height="100%" 
        viewBox="0 0 500 300" 
        class="block w-full h-full bg-red-500"
        preserveAspectRatio="xMidYMid meet"
      >
        <!-- Background (sky) -->
        <rect width="500" height="300" fill="#e0f2fe"/>
        
        <!-- Peat layer (brown) - on top, shrinks over time -->
        <rect 
          x="0" 
          :y="currentPeatLayerTop" 
          width="500" 
          :height="currentPeatLayerHeight"
          fill="#8b4513"
          opacity="0.8"
        />
        
        <!-- Mineral layer (light brown/sand) - below peat -->
        <rect 
          x="0" 
          :y="mineralLayerTop" 
          width="500"
          height="500"
          fill="#d2b48c"
          opacity="0.8"
        />
        
        <!-- 2025 Maaiveld marker line (reference level) -->
        <line 
          x1="0" 
          :y1="reference2025Level" 
          x2="500" 
          :y2="reference2025Level" 
          stroke="#0A1" 
          stroke-width="2"
          stroke-dasharray="10,5"
        />
        <text 
          x="10" 
          :y="reference2025Level - 8" 
          fill="#0A1" 
          font-size="16" 
          font-weight="bold"
        >
          Maaiveld 2025
        </text>
        
        <!-- Current surface level (maaiveld) -->
        <line 
          x1="0" 
          :y1="currentSurfaceLevel" 
          x2="200" 
          :y2="currentSurfaceLevel" 
          stroke="#0A1" 
          stroke-width="4"
        />
        <line 
          x1="300" 
          :y1="currentSurfaceLevel" 
          x2="500" 
          :y2="currentSurfaceLevel" 
          stroke="#0A1" 
          stroke-width="4"
        />
        
        <!-- Sloot (ditch) - depth = drooglegging + water height -->
        <!-- Sloot background (sky color) -->
        <polygon 
          :points="`200,${currentSurfaceLevel} 220,${slootBottom} 280,${slootBottom} 300,${currentSurfaceLevel}`"
          fill="#e0f2fe"
        />
        
        <!-- Water in sloot -->
        <polygon 
          :points="waterPolygonPoints"
          fill="#0083F1"
          opacity="0.7"
        />
        
        <!-- Sloot edges -->
        <line x1="200" :y1="currentSurfaceLevel" x2="220" :y2="slootBottom" stroke="#8b5cf6" stroke-width="2"/>
        <line x1="300" :y1="currentSurfaceLevel" x2="280" :y2="slootBottom" stroke="#8b5cf6" stroke-width="2"/>
        <line x1="220" :y1="slootBottom" x2="280" :y2="slootBottom" stroke="#8b5cf6" stroke-width="2"/>
        
        <!-- Grass on surface -->
        <g v-for="i in 25" :key="'grass-left-' + i">
          <line 
            :x1="i * 8" 
            :y1="currentSurfaceLevel" 
            :x2="i * 8 + (Math.sin(i) * 3)" 
            :y2="currentSurfaceLevel - 8 - (Math.cos(i) * 3)" 
            stroke="#0A1" 
            stroke-width="2"
          />
        </g>
        <g v-for="i in 25" :key="'grass-right-' + i">
          <line 
            :x1="300 + i * 8" 
            :y1="currentSurfaceLevel" 
            :x2="300 + i * 8 + (Math.sin(i) * 3)" 
            :y2="currentSurfaceLevel - 8 - (Math.cos(i) * 3)" 
            stroke="#0A1" 
            stroke-width="2"
          />
        </g>
        
        <!-- Drooglegging measurement -->
        <line 
          x1="50" 
          :y1="currentSurfaceLevel" 
          x2="50" 
          :y2="currentWaterLevel" 
          stroke="#ffffff" 
          stroke-width="3"
          stroke-dasharray="5,3"
        />
        <text 
          x="55" 
          :y="(currentSurfaceLevel + currentWaterLevel) / 2 + 5" 
          fill="#ffffff" 
          font-size="16" 
          font-weight="bold"
        >
          {{ currentYearData.drooglegging.toFixed(1) }}cm
        </text>
        
        <!-- NAP value display under water level (in meters, no "NAP" text) -->
        <text 
          x="250" 
          :y="currentWaterLevel + 25" 
          fill="#1e40af" 
          font-size="16" 
          font-weight="bold"
          text-anchor="middle"
        >
          {{ (currentYearData.zomerpeil_ondergrens / 100).toFixed(2) }} m
        </text>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  polderData: {
    type: Object,
    required: true
  },
  currentYear: {
    type: Number,
    default: 2025
  },
  peilindexatie: {
    type: Number,
    default: 50
  }
})

const emit = defineEmits(['close'])

// Constants
const baselineY = 50
const pixelsPerCm = 0.8

// Get current year data using the polder's getYearData method
const currentYearData = computed(() => {
  return props.polderData.getYearData(props.currentYear, props.peilindexatie)
})

// Calculate peat thickness for current year (200cm - 0.7cm per year)
const currentPeatThickness = computed(() => {
  return 200 - (props.currentYear - 2025) * 0.7
})

// 2025 reference level
const reference2025Level = computed(() => baselineY)

// Current surface level moves down as peat shrinks
const totalPeatLoss = computed(() => 200 - currentPeatThickness.value)
const currentSurfaceLevel = computed(() => reference2025Level.value + (totalPeatLoss.value * pixelsPerCm))

// Peat layer
const currentPeatLayerHeight = computed(() => currentPeatThickness.value * pixelsPerCm)
const currentPeatLayerTop = computed(() => currentSurfaceLevel.value)

// Mineral layer
const mineralLayerTop = computed(() => currentPeatLayerTop.value + currentPeatLayerHeight.value)

// Water level - drooglegging distance below surface
const currentWaterLevel = computed(() => currentSurfaceLevel.value + (currentYearData.value.drooglegging * pixelsPerCm))

// Ditch dimensions - depth = drooglegging + water height (60cm constant)
const waterHeight = 60
const ditchDepth = computed(() => currentYearData.value.drooglegging + waterHeight)
const slootBottom = computed(() => currentSurfaceLevel.value + (ditchDepth.value * pixelsPerCm))

// Water polygon for the ditch
const waterPolygonPoints = computed(() => {
  if (waterHeight <= 0) return ""

  const waterTop = slootBottom.value - (waterHeight * pixelsPerCm)
  const waterBottom = slootBottom.value

  const ditchTotalDepth = ditchDepth.value * pixelsPerCm
  const waterDepthFromSurface = waterTop - currentSurfaceLevel.value
  const ratioFromSurface = Math.abs(waterDepthFromSurface) / ditchTotalDepth

  const leftX = 200 + (20 * ratioFromSurface)
  const rightX = 300 - (20 * ratioFromSurface)

  return `${leftX},${waterTop} ${rightX},${waterTop} 280,${waterBottom} 220,${waterBottom}`
})
</script>