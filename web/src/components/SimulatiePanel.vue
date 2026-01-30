<template>
  <div class="fixed top-20 right-4 bg-white rounded-lg shadow-2xl border border-gray-200 p-6 z-30 w-96 max-h-[calc(100vh-120px)] overflow-y-auto">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-lg font-bold text-gray-800">🌧️ Simulatie Parameters</h3>
    </div>

    <!-- Peilgebied Info -->
    <div v-if="peilgebied" class="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
      <h4 class="font-semibold text-blue-900 mb-1">{{ peilgebied.properties.NAAM || peilgebied.properties.CODE }}</h4>
      <div class="text-xs text-blue-700 space-y-1">
        <div v-if="peilgebied.properties.oppervlakteHa">
          Oppervlakte: <strong>{{ peilgebied.properties.oppervlakteHa.toFixed(2) }} ha</strong>
        </div>
        <div v-if="peilgebied.properties.ZOMERPEIL !== null && peilgebied.properties.ZOMERPEIL !== undefined">
          Zomerpeil: <strong>{{ peilgebied.properties.ZOMERPEIL.toFixed(2) }} m NAP</strong>
        </div>
        <div v-if="peilgebied.properties.WINTERPEIL !== null && peilgebied.properties.WINTERPEIL !== undefined">
          Winterpeil: <strong>{{ peilgebied.properties.WINTERPEIL.toFixed(2) }} m NAP</strong>
        </div>
        <div v-if="peilgebied.properties.nearestGemaal" class="pt-2 mt-2 border-t border-blue-200">
           Dichtstbijzijnde gemaal:<br/>
           <strong>{{ peilgebied.properties.nearestGemaal.naam }}</strong>
           <span v-if="peilgebied.properties.nearestGemaal.capaciteit"> ({{ peilgebied.properties.nearestGemaal.capaciteit }} m³/s)</span>
        </div>
      </div>
    </div>

    <!-- Parameters -->
    <div class="space-y-4">
      <!-- Maaiveld Niveau -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-1">
          Maaiveld Niveau (m NAP)
        </label>
        <input
          v-model.number="parameters.maaiveldNiveau"
          type="number"
          step="0.01"
          class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          @input="recalculate"
        />
      </div>

      <!-- Streefpeil -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-1">
          Streefpeil (m NAP)
        </label>
        <select
          v-model="parameters.streefpeil"
          class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          @change="recalculate"
        >
          <option v-if="peilgebied?.properties.ZOMERPEIL !== null && peilgebied?.properties.ZOMERPEIL !== undefined" 
                  :value="peilgebied.properties.ZOMERPEIL">
            Zomerpeil: {{ peilgebied.properties.ZOMERPEIL.toFixed(2) }} m NAP
          </option>
          <option v-if="peilgebied?.properties.WINTERPEIL !== null && peilgebied?.properties.WINTERPEIL !== undefined"
                  :value="peilgebied.properties.WINTERPEIL">
            Winterpeil: {{ peilgebied.properties.WINTERPEIL.toFixed(2) }} m NAP
          </option>
          <option v-if="peilgebied?.properties.VASTPEIL !== null && peilgebied?.properties.VASTPEIL !== undefined"
                  :value="peilgebied.properties.VASTPEIL">
            Vastpeil: {{ peilgebied.properties.VASTPEIL.toFixed(2) }} m NAP
          </option>
        </select>
      </div>

      <!-- Drooglegging Marge -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-1">
          Drooglegging Marge (cm)
        </label>
        <input
          v-model.number="parameters.marge"
          type="number"
          step="0.1"
          min="0"
          class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          @input="recalculate"
        />
      </div>

      <!-- Regenintensiteit -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-1">
          Regenintensiteit (mm/uur)
        </label>
        <input
          v-model.number="parameters.regenIntensiteit"
          type="number"
          step="0.1"
          min="0"
          class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          @input="recalculate"
        />
      </div>

      <!-- Regenduur -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-1">
          Regenduur (minuten)
        </label>
        <input
          v-model.number="parameters.regenDuur"
          type="number"
          step="1"
          min="1"
          class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          @input="recalculate"
        />
      </div>

      <!-- Start Waterstand -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-1">
          Start Waterstand (m NAP)
        </label>
        <input
          v-model.number="parameters.startWaterstand"
          type="number"
          step="0.01"
          class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          @input="recalculate"
        />
      </div>

      <!-- Gemaal Capaciteit (optioneel) -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-1">
          Gemaal Capaciteit (m³/s)
        </label>
        <div class="flex items-center gap-2 mb-1">
           <input
            v-model="parameters.smartControl"
            type="checkbox"
            class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
            @change="recalculate"
          />
          <span class="text-xs text-gray-600">Slimme sturing (aan/uit op basis van marge)</span>
        </div>
        <input
          v-model.number="parameters.gemaalDebiet"
          type="number"
          step="0.1"
          min="0"
          placeholder="Capaciteit wanneer aan"
          class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          @input="recalculate"
        />
      </div>

      <!-- Verdamping -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-1">
          Verdamping (mm/uur)
        </label>
        <input
          v-model.number="parameters.verdamping"
          type="number"
          step="0.1"
          min="0"
          class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          @input="recalculate"
        />
      </div>

      <!-- Infiltratie -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-1">
          Infiltratie (mm/uur)
        </label>
        <input
          v-model.number="parameters.infiltratie"
          type="number"
          step="0.1"
          min="0"
          class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          @input="recalculate"
        />
      </div>
    </div>

    <!-- Resultaten -->
    <div v-if="resultaten" class="mt-6 pt-6 border-t border-gray-200">
      <h4 class="text-sm font-bold text-gray-800 mb-3">📊 Resultaten</h4>

      <!-- Status Indicator -->
      <div class="mb-4 p-3 rounded-lg" :class="statusClass">
        <div class="flex items-center gap-2">
          <span class="text-xl">{{ statusIcon }}</span>
          <span class="font-semibold" :class="statusTextClass">{{ resultaten.status }}</span>
        </div>
        <p v-if="resultaten.message" class="text-xs mt-1" :class="statusTextClass">
          {{ resultaten.message }}
        </p>
      </div>

      <!-- Benodigd Debiet -->
      <div v-if="resultaten.minimaalDebiet !== null" class="mb-3 p-3 bg-gray-50 rounded-lg">
        <div class="text-xs text-gray-600 mb-1">Benodigd Debiet</div>
        <div class="text-2xl font-bold text-blue-600">
          {{ resultaten.minimaalDebiet.toFixed(2) }} <span class="text-sm">m³/s</span>
        </div>
      </div>

      <!-- Maximale Waterstand -->
      <div v-if="resultaten.maxWaterstand !== null" class="mb-3 p-3 bg-gray-50 rounded-lg">
        <div class="text-xs text-gray-600 mb-1">Maximale Waterstand</div>
        <div class="text-lg font-semibold text-gray-800">
          {{ resultaten.maxWaterstand.toFixed(3) }} <span class="text-sm">m NAP</span>
        </div>
        <div class="text-xs text-gray-500 mt-1">
          Na {{ resultaten.maxTijd }} minuten
        </div>
      </div>

      <!-- Drooglegging Overschrijding -->
      <div v-if="resultaten.maxOverschrijding !== null && resultaten.maxOverschrijding > 0" 
           class="mb-3 p-3 bg-red-50 rounded-lg border border-red-200">
        <div class="text-xs text-red-700 mb-1">Drooglegging Overschrijding</div>
        <div class="text-lg font-semibold text-red-800">
          {{ resultaten.maxOverschrijding.toFixed(1) }} <span class="text-sm">cm</span>
        </div>
      </div>

      <!-- Info -->
      <div class="text-xs text-gray-500 space-y-1 mt-3">
        <div v-if="resultaten.tijdstappen">
          Simulatie punten: {{ resultaten.tijdstappen.length }}
        </div>
        <div v-if="resultaten.oppervlakte">
          Oppervlakte: {{ (resultaten.oppervlakte / 10000).toFixed(2) }} ha
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="calculating" class="mt-4 text-center">
      <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
      <p class="text-xs text-gray-500 mt-2">Berekenen...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { 
  calculateTimeSeries, 
  findMinimumDebiet, 
  findMaxWaterstand,
  calculateDrooglegging 
} from '../utils/waterbalans.js'

const props = defineProps({
  peilgebied: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update-simulation', 'close'])

// Parameters
const parameters = ref({
  maaiveldNiveau: 1.0, // m NAP
  streefpeil: null, // m NAP
  marge: 5, // cm
  regenIntensiteit: 10, // mm/uur
  regenDuur: 60, // minuten
  startWaterstand: null, // m NAP
  gemaalDebiet: 0, // m³/s (optioneel)
  smartControl: false, // Nieuwe parameter
  verdamping: 0.5, // mm/uur
  infiltratie: 0.2 // mm/uur
})

const resultaten = ref(null)
const calculating = ref(false)

// Status berekening
const statusClass = computed(() => {
  if (!resultaten.value) return 'bg-gray-100'
  if (resultaten.value.success) return 'bg-green-50 border border-green-200'
  if (resultaten.value.maxOverschrijding > 0) return 'bg-yellow-50 border border-yellow-200'
  return 'bg-red-50 border border-red-200'
})

const statusIcon = computed(() => {
  if (!resultaten.value) return '⏳'
  if (resultaten.value.success) return '✅'
  if (resultaten.value.maxOverschrijding > 0) return '⚠️'
  return '❌'
})

const statusTextClass = computed(() => {
  if (!resultaten.value) return 'text-gray-700'
  if (resultaten.value.success) return 'text-green-800'
  if (resultaten.value.maxOverschrijding > 0) return 'text-yellow-800'
  return 'text-red-800'
})

// Initialize parameters bij peilgebied wijziging
watch(() => props.peilgebied, (newPeilgebied) => {
  if (newPeilgebied) {
    // Set streefpeil (prioriteit: zomerpeil > winterpeil > vastpeil)
    if (newPeilgebied.properties.ZOMERPEIL !== null && newPeilgebied.properties.ZOMERPEIL !== undefined) {
      parameters.value.streefpeil = newPeilgebied.properties.ZOMERPEIL
    } else if (newPeilgebied.properties.WINTERPEIL !== null && newPeilgebied.properties.WINTERPEIL !== undefined) {
      parameters.value.streefpeil = newPeilgebied.properties.WINTERPEIL
    } else if (newPeilgebied.properties.VASTPEIL !== null && newPeilgebied.properties.VASTPEIL !== undefined) {
      parameters.value.streefpeil = newPeilgebied.properties.VASTPEIL
    }

    // Set start waterstand = streefpeil
    if (parameters.value.streefpeil !== null) {
      parameters.value.startWaterstand = parameters.value.streefpeil
    }

    // Laad maaiveld niveau uit localStorage (per peilgebied)
    const code = newPeilgebied.properties.CODE
    if (code) {
      const savedMaaiveld = localStorage.getItem(`maaiveld_${code}`)
      if (savedMaaiveld) {
        parameters.value.maaiveldNiveau = parseFloat(savedMaaiveld)
      }
    }

    // Set gemaal capaciteit van dichtstbijzijnde gemaal
    if (newPeilgebied.properties.nearestGemaal) {
      parameters.value.gemaalDebiet = parseFloat(newPeilgebied.properties.nearestGemaal.capaciteit) || 0
      parameters.value.smartControl = true // Auto-enable smart control als we een capaciteit hebben
    }

    // Recalculate na initialisatie
    setTimeout(() => recalculate(), 100)
  }
}, { immediate: true })

// Recalculate simulatie
const recalculate = () => {
  if (!props.peilgebied) return

  const oppervlakte = props.peilgebied.properties.oppervlakteM2 || props.peilgebied.properties.OPPERVLAKTE
  if (!oppervlakte) {
    console.warn('Geen oppervlakte beschikbaar voor peilgebied')
    return
  }

  if (parameters.value.streefpeil === null) {
    console.warn('Geen streefpeil ingesteld')
    return
  }

  if (parameters.value.startWaterstand === null) {
    parameters.value.startWaterstand = parameters.value.streefpeil
  }

  calculating.value = true

  // Debounce voor performance
  setTimeout(() => {
    try {
      // Als gemaal debiet is ingesteld, gebruik die
      if (parameters.value.gemaalDebiet > 0) {
        // Bereken tijdreeks met ingesteld debiet
        const tijdstappen = calculateTimeSeries({
          startWaterstand: parameters.value.startWaterstand,
          regenIntensiteit: parameters.value.regenIntensiteit,
          regenDuur: parameters.value.regenDuur,
          oppervlakte: oppervlakte,
          gemaalDebiet: parameters.value.gemaalDebiet,
          verdamping: parameters.value.verdamping,
          infiltratie: parameters.value.infiltratie,
          smartControl: parameters.value.smartControl,
          streefpeil: parameters.value.streefpeil,
          marge: parameters.value.marge
        })

        // Vind maximale waterstand
        const maxWaterstandData = findMaxWaterstand(tijdstappen)

        // Bereken drooglegging overschrijding
        let maxOverschrijding = 0
        for (const stap of tijdstappen) {
          const drooglegging = calculateDrooglegging({
            maaiveldNiveau: parameters.value.maaiveldNiveau,
            waterstand: stap.waterstand,
            streefpeil: parameters.value.streefpeil,
            marge: parameters.value.marge
          })
          if (drooglegging.overschrijding > 0) {
            maxOverschrijding = Math.max(maxOverschrijding, drooglegging.overschrijdingCm)
          }
        }

        resultaten.value = {
          minimaalDebiet: parameters.value.gemaalDebiet,
          maxWaterstand: maxWaterstandData.maxWaterstand,
          maxTijd: maxWaterstandData.tijd,
          maxOverschrijding: maxOverschrijding,
          status: maxOverschrijding === 0 ? 'Binnen marge' : 'Overschrijding',
          message: maxOverschrijding === 0 
            ? 'Drooglegging blijft binnen marge' 
            : `Overschrijding van ${maxOverschrijding.toFixed(1)} cm`,
          tijdstappen: tijdstappen,
          oppervlakte: oppervlakte,
          success: maxOverschrijding === 0
        }
      } else {
        // Vind minimaal benodigd debiet
        const debietResult = findMinimumDebiet({
          startWaterstand: parameters.value.startWaterstand,
          regenIntensiteit: parameters.value.regenIntensiteit,
          regenDuur: parameters.value.regenDuur,
          oppervlakte: oppervlakte,
          maaiveldNiveau: parameters.value.maaiveldNiveau,
          streefpeil: parameters.value.streefpeil,
          marge: parameters.value.marge,
          verdamping: parameters.value.verdamping,
          infiltratie: parameters.value.infiltratie
        })

        // Vind maximale waterstand
        const maxWaterstandData = findMaxWaterstand(debietResult.tijdstappen || [])

        resultaten.value = {
          minimaalDebiet: debietResult.minimaalDebiet,
          maxWaterstand: maxWaterstandData.maxWaterstand,
          maxTijd: maxWaterstandData.tijd,
          maxOverschrijding: debietResult.maxOverschrijding || 0,
          status: debietResult.success ? 'Succesvol' : 'Fout',
          message: debietResult.success 
            ? 'Minimaal debiet berekend' 
            : (debietResult.message || 'Kan geen debiet vinden'),
          tijdstappen: debietResult.tijdstappen || [],
          oppervlakte: oppervlakte,
          success: debietResult.success
        }
      }

      // Emit update naar parent
      emit('update-simulation', {
        tijdstappen: resultaten.value.tijdstappen,
        maaiveldNiveau: parameters.value.maaiveldNiveau,
        streefpeil: parameters.value.streefpeil,
        marge: parameters.value.marge,
        gemaalCapaciteit: parameters.value.gemaalDebiet // Emit capaciteit
      })

      // Sla maaiveld niveau op in localStorage
      const code = props.peilgebied.properties.CODE
      if (code) {
        localStorage.setItem(`maaiveld_${code}`, parameters.value.maaiveldNiveau.toString())
      }
    } catch (error) {
      console.error('Fout bij berekenen simulatie:', error)
      resultaten.value = {
        status: 'Fout',
        message: error.message || 'Onbekende fout bij berekenen',
        success: false
      }
    } finally {
      calculating.value = false
    }
  }, 300) // 300ms debounce
}

// Watch parameters voor auto-recalculate
watch(() => [
  parameters.value.maaiveldNiveau,
  parameters.value.streefpeil,
  parameters.value.marge,
  parameters.value.regenIntensiteit,
  parameters.value.regenDuur,
  parameters.value.startWaterstand,
  parameters.value.gemaalDebiet,
  parameters.value.smartControl,
  parameters.value.verdamping,
  parameters.value.infiltratie
], () => {
  recalculate()
})
</script>

