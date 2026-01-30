<!-- ControlPanel.vue -->
<template>
  <div class="fixed top-4 right-4 w-80 bg-white rounded-lg shadow-2xl border border-gray-200 p-4 z-40">
    
    <!-- Header -->
    <h3 class="text-lg font-semibold text-gray-800 mb-4">Scenario Instellingen</h3>


    <!-- Peilindexatie Controls -->
    <div class="mb-6 space-y-3">
      <h4 class="text-md font-medium text-gray-700">Peilindexatie</h4>
      <div class="flex gap-2">
        <button
          v-for="preset in presetValues"
          :key="preset"
          @click="setPeilindexatie(preset)"
          :class="[
            'flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer',
            selectedPeilindexatie === preset
              ? 'bg-[#0083F1] text-white'
              : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200'
          ]"
        >
          {{ preset }}%
        </button>
      </div>
    </div>

    <!-- Year Controls -->
    <div class="mb-6 space-y-3">
      <!-- Year Slider -->
      <div class="space-y-2">
        <div class="flex justify-between text-sm text-gray-600">
          <span>2025</span>
          <span class="font-medium text-lg">{{ currentYear }}</span>
          <span>2075</span>
        </div>
        <input 
          v-model.number="currentYear"
          type="range" 
          min="2025" 
          max="2075" 
          step="1"
          class="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          @input="onYearChange"
        >
      </div>
    </div>

    <!-- Play Button -->
    <div class="flex items-center justify-center">
      <button 
        @click="togglePlay"
        class="px-4 py-2 bg-[#0083F1] hover:bg-blue-600 text-white rounded text-sm font-medium transition-colors cursor-pointer flex flex-row items-center"
      >
        <div class="mr-2">
          <svg v-if="!isPlaying" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="size-4">
            <path d="M3 3.732a1.5 1.5 0 0 1 2.305-1.265l6.706 4.267a1.5 1.5 0 0 1 0 2.531l-6.706 4.268A1.5 1.5 0 0 1 3 12.267V3.732Z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="size-4">
            <path d="M4.5 2a.5.5 0 0 0-.5.5v11a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-11a.5.5 0 0 0-.5-.5h-1ZM10.5 2a.5.5 0 0 0-.5.5v11a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-11a.5.5 0 0 0-.5-.5h-1Z" />
          </svg>
        </div>
        {{ isPlaying ? 'Pauzeren' : 'Afspelen' }}
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// Define emits for parent communication
const emit = defineEmits(['yearChange', 'peilindexatieChange'])

// Animation state
const currentYear = ref(2025)
const isPlaying = ref(false)
const animationInterval = ref(null)

// Peilindexatie state
const presetValues = [0, 25, 50, 75]
const selectedPeilindexatie = ref(50)

// Constants
const startYear = 2025
const endYear = 2075

// Animation controls
const togglePlay = () => {
  isPlaying.value = !isPlaying.value
  if (isPlaying.value) {
    startAnimation()
  } else {
    stopAnimation()
  }
}

const startAnimation = () => {
  animationInterval.value = setInterval(() => {
    if (currentYear.value >= endYear) {
      currentYear.value = startYear
    } else {
      currentYear.value += 1
    }
    
    // Emit year change
    emit('yearChange', {
      year: currentYear.value,
      peilindexatie: selectedPeilindexatie.value
    })
  }, 200)
}

const stopAnimation = () => {
  isPlaying.value = false
  if (animationInterval.value) {
    clearInterval(animationInterval.value)
    animationInterval.value = null
  }
}

// const resetToStart = () => {
//   stopAnimation()
//   currentYear.value = startYear
  
//   // Emit reset
//   emit('yearChange', {
//     year: currentYear.value,
//     peilindexatie: selectedPeilindexatie.value
//   })
//   emit('playStateChange', {
//     isPlaying: false,
//     currentYear: currentYear.value
//   })
// }

const onYearChange = () => {
  if (isPlaying.value) {
    stopAnimation()
  }
  
  // Emit manual year change
  emit('yearChange', {
    year: currentYear.value,
    peilindexatie: selectedPeilindexatie.value
  })
}

// Peilindexatie controls
const setPeilindexatie = (value) => {
  selectedPeilindexatie.value = value
  
  // Reset to 2025 when peilindexatie changes
  currentYear.value = startYear
  stopAnimation()
  
  // Emit peilindexatie change
  emit('peilindexatieChange', {
    peilindexatie: value,
    currentYear: currentYear.value
  })
  
  // Also emit year change since we reset to 2025
  emit('yearChange', {
    year: currentYear.value,
    peilindexatie: value
  })
}

// Cleanup on unmount
onUnmounted(() => {
  stopAnimation()
})

// Auto-start animation after mount
onMounted(() => {
  // Emit initial state
  emit('yearChange', {
    year: currentYear.value,
    peilindexatie: selectedPeilindexatie.value
  })
})
</script>

<style scoped>
.slider::-webkit-slider-thumb {
  appearance: none;
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
}

.slider::-moz-range-thumb {
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: none;
}
</style>