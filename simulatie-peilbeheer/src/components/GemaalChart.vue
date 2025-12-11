<template>
  <div class="fixed top-20 right-4 bg-white rounded-lg shadow-2xl border border-gray-200 p-6 z-30 w-96 max-h-[calc(100vh-120px)] overflow-y-auto">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-lg font-bold text-gray-800">📊 Gemaal Grafiek</h3>
      <button
        @click="$emit('close')"
        class="text-gray-400 hover:text-gray-600 text-xl"
      >
        ×
      </button>
    </div>

    <div v-if="loading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <p class="mt-2 text-sm text-gray-600">Data ophalen...</p>
    </div>

    <div v-else-if="error" class="text-center py-8">
      <p class="text-red-600 mb-2">{{ error }}</p>
      <button
        @click="loadGemaalData"
        class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Opnieuw proberen
      </button>
    </div>

    <div v-else-if="chartData">
      <div class="mb-4">
        <h4 class="font-semibold text-gray-800">{{ props.gemaalNaam || props.gemaalCode }}</h4>
        <p class="text-sm text-gray-600">Code: {{ props.gemaalCode }}</p>
        <p class="text-xs text-gray-500 mt-1">Laatste 3 uur</p>
      </div>

      <div class="mb-4">
        <canvas ref="chartCanvas"></canvas>
      </div>

      <div class="text-xs text-gray-500 space-y-1">
        <div>Data punten: {{ filteredData.length }}</div>
        <div>Status: <span :class="status === 'aan' ? 'text-green-600' : 'text-gray-500'">{{ status.toUpperCase() }}</span></div>
        <div v-if="filteredData.length > 0">
          Huidig debiet: <strong>{{ currentDebiet }} m³/s</strong>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({
  gemaalCode: {
    type: String,
    required: true
  },
  gemaalNaam: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['close'])

// API configuratie (niet meer nodig, gebruiken server-side proxy)

const loading = ref(false)
const error = ref(null)
const chartCanvas = ref(null)
const chart = ref(null)
const chartData = ref(null)
const filteredData = ref([])
const status = ref('uit')
const currentDebiet = ref('0.000')

// Laad gemaal data wanneer component wordt gemount of props veranderen
const loadGemaalData = async () => {
  if (!props.gemaalCode) return
  
  loading.value = true
  error.value = null
  chartData.value = null

  try {
    // Haal real-time data op voor het geselecteerde gemaal
    await fetchGemaalData(props.gemaalCode)
  } catch (e) {
    console.error('Fout bij laden gemaal:', e)
    error.value = e.message || 'Onbekende fout'
    loading.value = false
  }
}

// Haal gemaal data op via server-side proxy (geen CORS problemen)
const fetchGemaalData = async (code) => {
  try {
    // Gebruik server-side proxy endpoint
    const proxyUrl = `/api/gemaal?code=${encodeURIComponent(code)}`
    const response = await fetch(proxyUrl)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`)
    }

    const data = await response.json()

    if (!data || !data.series || data.series.length === 0) {
      throw new Error('Geen data beschikbaar voor dit gemaal. Mogelijk heeft dit gemaal geen real-time data.')
    }

    // Converteer de data naar het verwachte formaat
    chartData.value = {
      series: data.series.map(s => ({
        name: s.name,
        data: s.data.map(point => ({
          timestamp: new Date(point.timestamp),
          timestampMs: point.timestampMs,
          value: point.value
        }))
      }))
    }
    
    filterLast3Hours(chartData.value)
    loading.value = false
  } catch (e) {
    console.error('Fout bij ophalen gemaal data:', e)
    error.value = e.message || 'Kon data niet ophalen. Controleer of dit gemaal real-time data heeft.'
    loading.value = false
  }
}

// Parse functie niet meer nodig - server-side proxy doet dit al

// Filter data van laatste 3 uur
const filterLast3Hours = (data) => {
  if (!data || !data.series || data.series.length === 0 || !data.series[0].data || data.series[0].data.length === 0) {
    error.value = 'Geen data beschikbaar voor dit gemaal'
    loading.value = false
    return
  }

  const now = new Date()
  const threeHoursAgo = new Date(now.getTime() - 3 * 60 * 60 * 1000)

  // Filter alleen data punten van de laatste 3 uur
  const allDataPoints = data.series[0].data
  const filtered = allDataPoints.filter(point => {
    // Handle both Date objects and timestamp strings/numbers
    let pointTime
    if (point.timestamp instanceof Date) {
      pointTime = point.timestamp
    } else if (point.timestampMs) {
      pointTime = new Date(point.timestampMs)
    } else {
      pointTime = new Date(point.timestamp)
    }
    return pointTime >= threeHoursAgo && pointTime <= now
  })

  // Sorteer op timestamp (oudste eerst)
  filtered.sort((a, b) => {
    const timeA = a.timestamp instanceof Date ? a.timestamp : (a.timestampMs ? new Date(a.timestampMs) : new Date(a.timestamp))
    const timeB = b.timestamp instanceof Date ? b.timestamp : (b.timestampMs ? new Date(b.timestampMs) : new Date(b.timestamp))
    return timeA.getTime() - timeB.getTime()
  })

  filteredData.value = filtered

  // Bepaal status en huidig debiet
  if (filtered.length > 0) {
    const lastPoint = filtered[filtered.length - 1]
    currentDebiet.value = (lastPoint.value || 0).toFixed(3)
    status.value = (lastPoint.value || 0) > 0.001 ? 'aan' : 'uit'
    
    // Maak grafiek met gefilterde data
    // Wacht even zodat de DOM is geüpdatet
    setTimeout(() => {
      createChart(filtered)
    }, 100)
  } else {
    // Geen data van laatste 3 uur beschikbaar
    if (allDataPoints.length > 0) {
      const newestPoint = allDataPoints[allDataPoints.length - 1]
      const newestTime = newestPoint.timestamp instanceof Date ? newestPoint.timestamp : (newestPoint.timestampMs ? new Date(newestPoint.timestampMs) : new Date(newestPoint.timestamp))
      
      const hoursAgo = Math.round((now.getTime() - newestTime.getTime()) / (1000 * 60 * 60))
      
      if (hoursAgo > 3) {
        error.value = `Geen data beschikbaar voor laatste 3 uur. Meest recente data is van ${hoursAgo} uur geleden (${newestTime.toLocaleString('nl-NL')}).`
      } else {
        error.value = 'Geen data beschikbaar voor laatste 3 uur'
      }
    } else {
      error.value = 'Geen data beschikbaar voor dit gemaal'
    }
    loading.value = false
  }
}

// Maak Chart.js grafiek
const createChart = (dataPoints) => {
  if (chart.value) {
    chart.value.destroy()
    chart.value = null
  }

  if (!chartCanvas.value) {
    console.warn('Chart canvas niet beschikbaar')
    return
  }

  if (!dataPoints || dataPoints.length === 0) {
    console.warn('Geen data punten voor grafiek')
    return
  }

  const labels = dataPoints.map(p => {
    let date
    if (p.timestamp instanceof Date) {
      date = p.timestamp
    } else if (p.timestampMs) {
      date = new Date(p.timestampMs)
    } else {
      date = new Date(p.timestamp)
    }
    return date.toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' })
  })

  const values = dataPoints.map(p => p.value || 0)

  chart.value = new Chart(chartCanvas.value, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Debiet (m³/s)',
        data: values,
        borderColor: 'rgb(37, 99, 235)',
        backgroundColor: 'rgba(37, 99, 235, 0.1)',
        tension: 0.4,
        fill: true,
        pointRadius: 2,
        pointHoverRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          callbacks: {
            label: function(context) {
              return `Debiet: ${context.parsed.y.toFixed(3)} m³/s`
            }
          }
        }
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: 'Tijd'
          },
          ticks: {
            maxRotation: 45,
            minRotation: 45
          }
        },
        y: {
          display: true,
          title: {
            display: true,
            text: 'Debiet (m³/s)'
          },
          beginAtZero: true
        }
      }
    }
  })
}

onMounted(() => {
  loadGemaalData()
})

watch(() => props.gemaalCode, () => {
  if (props.gemaalCode) {
    loadGemaalData()
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

