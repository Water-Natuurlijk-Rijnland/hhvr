<template>
  <div class="fixed bottom-4 left-4 right-4 bg-white rounded-lg shadow-2xl border border-gray-200 p-6 z-30 max-h-[40vh]">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-lg font-bold text-gray-800">📈 Waterstand Over Tijd</h3>
      <button
        @click="expanded = !expanded"
        class="text-gray-400 hover:text-gray-600 text-xl"
      >
        {{ expanded ? '−' : '+' }}
      </button>
    </div>

    <div v-if="expanded">
      <div v-if="!tijdstappen || tijdstappen.length === 0" class="text-center py-8 text-gray-500">
        Geen simulatie data beschikbaar
      </div>

      <div v-else>
        <div class="mb-4" style="height: 250px; position: relative;">
          <canvas ref="chartCanvas"></canvas>
        </div>

        <!-- Legenda -->
        <div class="flex flex-wrap gap-4 text-xs">
          <div class="flex items-center gap-2">
            <div class="w-4 h-0.5 bg-blue-600"></div>
            <span class="text-gray-600">Waterstand</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-4 h-0.5 bg-green-600 border-dashed"></div>
            <span class="text-gray-600">Streefpeil</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-4 h-0.5 bg-orange-600 border-dashed"></div>
            <span class="text-gray-600">Maaiveld</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-4 h-2 bg-yellow-100 border border-yellow-300"></div>
            <span class="text-gray-600">Drooglegging Marge</span>
          </div>
        </div>

        <!-- Info -->
        <div class="mt-3 text-xs text-gray-500 space-y-1">
          <div>Simulatie periode: {{ simulatieDuur }} minuten</div>
          <div v-if="maxWaterstand !== null">
            Max waterstand: {{ maxWaterstand.toFixed(3) }} m NAP
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref,  shallowRef, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({
  tijdstappen: {
    type: Array,
    default: () => []
  },
  maaiveldNiveau: {
    type: Number,
    default: null
  },
  streefpeil: {
    type: Number,
    default: null
  },
  marge: {
    type: Number,
    default: 5 // cm
  },
  gemaalCapaciteit: {
    type: Number,
    default: 0
  }
})

const chartCanvas = ref(null)
const chart = shallowRef(null)
const expanded = ref(true)

const simulatieDuur = ref(0)
const maxWaterstand = ref(null)

// Update chart wanneer data verandert
watch(() => [props.tijdstappen, props.maaiveldNiveau, props.streefpeil, props.marge, props.gemaalCapaciteit], () => {
  if (props.tijdstappen && props.tijdstappen.length > 0) {
    nextTick(() => {
      updateChart()
    })
  }
}, { immediate: true })

// Update chart
const updateChart = () => {
  if (!chartCanvas.value || !props.tijdstappen || props.tijdstappen.length === 0) {
    return
  }

  // Prepare data
  const labels = props.tijdstappen.map(s => `${s.tijd} min`)
  const waterstandData = props.tijdstappen.map(s => s.waterstand)

  // Calculate marge zone
  const margeMeters = props.marge / 100 // Convert cm to m
  const minimaleWaterstand = props.streefpeil !== null 
    ? props.streefpeil - margeMeters 
    : null
  const maximaleWaterstand = props.streefpeil !== null 
    ? props.streefpeil + margeMeters 
    : null

  // Find max waterstand
  if (waterstandData.length > 0) {
    maxWaterstand.value = Math.max(...waterstandData)
  }

  // Calculate simulation duration
  if (props.tijdstappen.length > 0) {
    simulatieDuur.value = props.tijdstappen[props.tijdstappen.length - 1].tijd
  }

  // Create datasets
  const datasets = [
    // Waterstand lijn
    {
      label: 'Waterstand',
      data: waterstandData,
      borderColor: 'rgb(37, 99, 235)', // blue-600
      backgroundColor: 'rgba(37, 99, 235, 0.1)',
      borderWidth: 2,
      fill: false,
      tension: 0.1,
      pointRadius: 2,
      pointHoverRadius: 4,
      yAxisID: 'y'
    }
  ]

  // Add streefpeil lijn
  if (props.streefpeil !== null) {
    datasets.push({
      label: 'Streefpeil',
      data: Array(props.tijdstappen.length).fill(props.streefpeil),
      borderColor: 'rgb(22, 163, 74)', // green-600
      backgroundColor: 'transparent',
      borderWidth: 2,
      borderDash: [5, 5],
      fill: false,
      pointRadius: 0,
      yAxisID: 'y'
    })
  }

  // Add maaiveld lijn
  if (props.maaiveldNiveau !== null) {
    datasets.push({
      label: 'Maaiveld',
      data: Array(props.tijdstappen.length).fill(props.maaiveldNiveau),
      borderColor: 'rgb(234, 88, 12)', // orange-600
      backgroundColor: 'transparent',
      borderWidth: 2,
      borderDash: [5, 5],
      fill: false,
      pointRadius: 0,
      yAxisID: 'y'
    })
  }

  // Add marge zone (filled area)
  if (props.streefpeil !== null && minimaleWaterstand !== null && maximaleWaterstand !== null) {
    // Bottom of the band (invisible line)
    datasets.push({
      label: 'Drooglegging Marge Min',
      data: Array(props.tijdstappen.length).fill(minimaleWaterstand),
      borderColor: 'transparent',
      backgroundColor: 'transparent',
      borderWidth: 0,
      fill: false,
      pointRadius: 0,
      yAxisID: 'y'
    })

    // Top of the band (fills to previous dataset)
    datasets.push({
      label: 'Drooglegging Marge',
      data: Array(props.tijdstappen.length).fill(maximaleWaterstand),
      borderColor: 'transparent',
      backgroundColor: 'rgba(253, 224, 71, 0.2)', // yellow-200
      borderWidth: 0,
      fill: '-1', // Fill to previous dataset
      pointRadius: 0,
      yAxisID: 'y'
    })
  }

  // Add Pump Capacity Usage (%)
  const pumpUsageData = props.tijdstappen.map(s => {
    // Als er een capaciteit is insteld, bereken %, anders 0 of 100 based on isPompAan
    if (props.gemaalCapaciteit > 0) {
      return (s.waterAfvoer / props.gemaalCapaciteit) * 100
    }
    return s.isPompAan ? 100 : 0
  })

  // Only show if there is any usage
  if (pumpUsageData.some(v => v > 0)) {
    datasets.push({
      label: 'Gemaal Inzet (%)',
      data: pumpUsageData,
      borderColor: 'rgba(239, 68, 68, 0.8)', // red-500
      backgroundColor: 'rgba(239, 68, 68, 0.2)',
      borderWidth: 1,
      fill: true,
      stepped: true,
      pointRadius: 0,
      yAxisID: 'yPercentage'
    })
  }

  // Init or Update chart
  if (chart.value) {
    chart.value.data.labels = labels
    chart.value.data.datasets = datasets
    chart.value.update('none') // Update without animation for better performance
  } else {
    chart.value = new Chart(chartCanvas.value, {
      type: 'line',
      data: {
        labels: labels,
        datasets: datasets
      },
      options: {
        animation: false,
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false 
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            callbacks: {
              label: function(context) {
                const label = context.dataset.label || ''
                if (label === 'Gemaal Inzet (%)') {
                  const val = context.raw.toFixed(1)
                  return `Gemaal inzet: ${val}% (${(props.gemaalCapaciteit * context.raw / 100).toFixed(1)} m³/s)`
                }
                if (label.includes('Min') || label.includes('Max')) return null
                
                const value = context.parsed.y.toFixed(3)
                return `${label}: ${value} m NAP`
              }
            }
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Tijd (minuten)'
            },
            grid: {
              display: true,
              color: 'rgba(0, 0, 0, 0.05)'
            }
          },
          y: {
            type: 'linear',
            display: true,
            position: 'left',
            title: {
              display: true,
              text: 'Waterstand (m NAP)'
            },
            grid: {
              display: true,
              color: 'rgba(0, 0, 0, 0.05)'
            }
          },
          yPercentage: {
             type: 'linear',
             display: true,
             position: 'right',
             min: 0,
             max: 100,
             title: {
               display: true,
               text: 'Gemaal Capaciteit (%)',
               color: 'rgb(239, 68, 68)'
             },
             grid: {
               display: false
             },
             ticks: {
               color: 'rgb(239, 68, 68)'
             }
          }
        },
        interaction: {
          mode: 'nearest',
          axis: 'x',
          intersect: false
        }
      }
    })
  }
}

onMounted(() => {
  if (props.tijdstappen && props.tijdstappen.length > 0) {
    nextTick(() => {
      updateChart()
    })
  }
})

onUnmounted(() => {
  if (chart.value) {
    chart.value.destroy()
  }
})
</script>

<style scoped>
canvas {
  max-height: 300px;
}
</style>

