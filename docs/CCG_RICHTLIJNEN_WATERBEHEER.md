# CCG Richtlijnen voor Verantwoord Gegevensgebruik in Waterbeheer

**Datum**: 2025-12-11  
**Bron**: Centrale Commissie Gegevensgebruik - "Vertrouwen door verantwoord gegevensgebruik"  
**Toepassing**: Waterbeheer en peilbeheer projecten

---

## Samenvatting CCG Document

### Kernboodschap

Het document "Vertrouwen door verantwoord gegevensgebruik" van de Centrale Commissie Gegevensgebruik (CCG) beschrijft de visie op verantwoorde gegevensuitwisseling tussen overheidsorganisaties. De commissie is opgericht in 2024 om knelpunten bij gegevensgebruik op te lossen en richt zich op onderliggende problemen die het hele systeem rond gegevensuitwisseling verbeteren.

### Belangrijkste Bevindingen

1. **Afnemend vertrouwen in de overheid**
   - Burgers en ondernemers voelen zich niet altijd gehoord
   - Complexiteit van datalandschap en wetgeving neemt toe
   - Overheid werkt te langzaam en onduidelijk

2. **Behoefte aan responsieve overheid**
   - Overheid moet snel, doelmatig en verantwoord reageren op maatschappelijke veranderingen
   - Nieuwe digitale technologie moet optimaal ingezet worden
   - Andere aanpak nodig: vooruitdenken en actief handelen

3. **Problemen bij gegevensdeling**
   - Institutionele complexiteit en slechte afstemming tussen organisaties
   - Sociale differentiatie: niet iedereen kan gelijk deelnemen
   - Exponentieel toenemende digitalisering
   - Nederlandse burger staat in 250-500 databanken geregistreerd

### Leidende Principes

Het document beschrijft verschillende principes voor verantwoord gegevensgebruik:

1. **Doelgerichtheid**: Gegevens delen met een duidelijk doel
2. **Proportionaliteit**: Alleen de gegevens delen die nodig zijn
3. **Transparantie**: Duidelijk uitleggen wat er gebeurt met gegevens
4. **Rechtmatigheid**: Handelen binnen de kaders van de wet
5. **Doelmatigheid**: Efficiënt en effectief gebruik van gegevens
6. **Mensgerichtheid**: Recht doen aan de bedoeling van de wet, niet alleen de letter

---

## Richtlijnen voor Waterbeheer

### 1. Gegevensuitwisseling tussen Waterbeheerorganisaties

#### 1.1 Transparantie en Documentatie

**Richtlijn**: Documenteer altijd welke gegevens worden gedeeld, met wie, en waarom.

**Toepassing voor dit project**:
- ✅ **Goed**: Documentatie in `RIJNLAND_DATA.md` en `RIJNLAND_DYNAMISCHE_DATA.md` beschrijft welke data beschikbaar is
- ⚠️ **Verbeter**: Voeg toe aan documentatie:
  - Doel van gegevensuitwisseling (bijv. "Real-time monitoring voor waterveiligheid")
  - Welke organisaties toegang hebben (Rijnland, Rijkswaterstaat, gemeenten)
  - Hoe lang data wordt bewaard
  - Privacy overwegingen (indien van toepassing)

**Implementatie**:
```markdown
## Gegevensuitwisseling Protocol

### Doel
Real-time monitoring van gemaalstatus voor:
- Waterveiligheid monitoring
- Operationeel beheer
- Publieke transparantie

### Deelnemende Organisaties
- Hoogheemraadschap van Rijnland (databron)
- Hydronet (dataleverancier)
- [Gemeenten/Provincies] (gebruikers)

### Data Retentie
- Real-time data: 30 dagen
- Geaggregeerde statistieken: 1 jaar
```

#### 1.2 Proportionaliteit

**Richtlijn**: Deel alleen de gegevens die nodig zijn voor het specifieke doel.

**Toepassing voor dit project**:
- ✅ **Goed**: Alleen gemaalstatus en debiet worden opgehaald (niet persoonlijke gegevens)
- ✅ **Goed**: Geaggregeerde data wordt gebruikt waar mogelijk (`gemaal_status_latest.json`)
- ⚠️ **Verbeter**: Overweeg data minimalisatie:
  - Alleen actieve gemalen ophalen indien mogelijk
  - Historische data beperken tot relevante periode
  - Geen onnodige metadata opslaan

**Implementatie**:
```python
# In generate_gemaal_status.py
# Alleen essentiële velden opslaan
minimal_data = {
    "gemaal_code": code,
    "status": "aan" | "uit",
    "debiet_m3s": debiet,
    "timestamp": timestamp
    # Geen: volledige historie, metadata, etc.
}
```

#### 1.3 Rechtmatigheid en Toestemming

**Richtlijn**: Zorg dat gegevensuitwisseling binnen de kaders van de wet valt.

**Toepassing voor dit project**:
- ✅ **Goed**: Publieke data wordt gebruikt (Hydronet API, ArcGIS services)
- ⚠️ **Verbeter**: Controleer:
  - API terms of service van Hydronet
  - ArcGIS server gebruiksvoorwaarden
  - AVG/GDPR compliance (indien van toepassing)
  - Licenties voor hergebruik van data

**Checklist**:
- [ ] API gebruiksvoorwaarden gelezen en begrepen
- [ ] Data is publiek beschikbaar of toestemming verkregen
- [ ] Geen persoonlijke gegevens worden verwerkt
- [ ] Data wordt gebruikt conform oorspronkelijk doel

### 2. Technische Implementatie

#### 2.1 Data Kwaliteit en Betrouwbaarheid

**Richtlijn**: Zorg voor betrouwbare en actuele gegevens.

**Toepassing voor dit project**:
- ✅ **Goed**: Data wordt regelmatig bijgewerkt (30-minuten interval)
- ✅ **Goed**: Error handling bij API failures
- ⚠️ **Verbeter**: Voeg toe:
  - Data validatie (realistische waarden)
  - Staleness detection (waarschuwing bij oude data)
  - Health monitoring (success rate tracking)

**Implementatie**:
```python
# Data validatie
def validate_gemaal_data(data):
    """Valideer dat gemaaldata realistisch is"""
    if data['debiet'] < 0 or data['debiet'] > 1000:  # Onrealistisch
        logger.warning(f"Onrealistisch debiet: {data['debiet']}")
        return False
    if data['timestamp'] < time.time() - 3600:  # Ouder dan 1 uur
        logger.warning("Data is te oud")
        return False
    return True
```

#### 2.2 Transparantie in Technische Keuzes

**Richtlijn**: Maak technische keuzes uitlegbaar en documenteer deze.

**Toepassing voor dit project**:
- ✅ **Goed**: Architectuurplan documenteert systeemontwerp
- ⚠️ **Verbeter**: Documenteer ook:
  - Waarom bepaalde API's worden gebruikt
  - Waarom bepaalde update frequenties zijn gekozen
  - Welke beperkingen er zijn
  - Hoe fouten worden afgehandeld

**Implementatie**:
```markdown
## Technische Beslissingen

### API Keuze: Hydronet Water Control Room
**Reden**: Enige beschikbare bron voor real-time gemaaldata
**Beperkingen**: 
- 30-minuten update interval
- Geen historische data beschikbaar
- Rate limiting mogelijk

### Update Frequentie: 15 minuten
**Reden**: 
- API update elke 30 minuten
- 15 minuten geeft goede balans tussen actualiteit en server load
- Voldoende voor operationeel gebruik
```

### 3. Gebruikerservaring en Toegankelijkheid

#### 3.1 Duidelijkheid voor Gebruikers

**Richtlijn**: Maak duidelijk wat gebruikers zien en wat het betekent.

**Huidige situatie in project**:
- ✅ **Goed**: `DashboardPanel.vue` toont duidelijk actieve gemalen en debiet
- ✅ **Goed**: `AllLayersMap.vue` heeft tooltips met informatie
- ✅ **Goed**: `GemaalChart.vue` toont real-time grafieken
- ⚠️ **Mist**: 
  - Data actualiteit indicatie (hoe oud is de data?)
  - Contextuele uitleg (wat betekenen de cijfers?)
  - Waarschuwingen bij oude of incomplete data
  - Normale waarden referentie

**Concrete implementatie voor DashboardPanel.vue**:

```vue
<template>
  <div 
    v-if="visible" 
    class="fixed top-4 left-1/2 transform -translate-x-1/2 bg-white/90 backdrop-blur-sm rounded-xl shadow-lg border border-blue-100 p-4 z-20 flex gap-6 items-center"
    role="region"
    aria-label="Gemaal status dashboard"
  >
    <!-- Data actualiteit waarschuwing -->
    <div 
      v-if="isStale || isVeryStale" 
      class="absolute -top-8 left-0 right-0 flex justify-center"
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

    <!-- Active Stations -->
    <div class="flex items-center gap-3">
      <div class="p-2 bg-green-100 rounded-full" aria-hidden="true">
        <span class="text-xl">🏭</span>
      </div>
      <div>
        <p class="text-xs text-gray-500 font-semibold uppercase tracking-wider">
          Actieve Gemalen
        </p>
        <p class="text-xl font-bold text-gray-800">
          <span aria-label="{{ activeStations }} van {{ totalStations }} gemalen actief">
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
        <p class="text-xs text-gray-500 font-semibold uppercase tracking-wider">
          Totaal Debiet
        </p>
        <p class="text-xl font-bold text-gray-800">
          <span aria-label="{{ totalDebiet }} kubieke meter per seconde">
            {{ totalDebiet }} <span class="text-sm text-gray-400 font-normal">m³/s</span>
          </span>
        </p>
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

    <!-- Help tooltip -->
    <button
      @click="showHelp = !showHelp"
      class="ml-2 text-gray-400 hover:text-gray-600 text-sm"
      aria-label="Uitleg over dashboard"
      title="Klik voor uitleg"
    >
      ℹ️
    </button>
  </div>

  <!-- Help panel -->
  <div 
    v-if="showHelp"
    class="fixed top-24 left-1/2 transform -translate-x-1/2 bg-white rounded-lg shadow-xl border border-gray-200 p-4 z-30 max-w-md"
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
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  stats: {
    type: Object,
    default: () => null
  }
})

const showHelp = ref(false)

const visible = computed(() => !!props.stats)

const activeStations = computed(() => props.stats?.active_stations || 0)
const totalStations = computed(() => props.stats?.total_stations || 0)
const totalDebiet = computed(() => props.stats?.total_debiet_m3s?.toFixed(1) || '0.0')

const lastUpdate = computed(() => {
  if (!props.stats?.generated_at) return '-'
  return new Date(props.stats.generated_at).toLocaleTimeString('nl-NL', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
})

const fullTimestamp = computed(() => {
  if (!props.stats?.generated_at) return '-'
  return new Date(props.stats.generated_at).toLocaleString('nl-NL')
})

// Data actualiteit berekening
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

// Normale waarden (kan uit historische data komen of configuratie)
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
  // Dit kan worden aangepast op basis van historische data
  return {
    min: 20,
    max: 60
  }
})
</script>
```

**Concrete implementatie voor AllLayersMap.vue - Verbeterde error states**:

```vue
<!-- Toevoegen aan AllLayersMap.vue -->
<!-- Error State Panel -->
<div
  v-if="dataError"
  class="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-red-50 border-2 border-red-200 rounded-lg shadow-lg p-4 z-40 max-w-md"
  role="alert"
  aria-live="assertive"
>
  <div class="flex items-start gap-3">
    <span class="text-2xl">⚠️</span>
    <div class="flex-1">
      <h4 class="font-bold text-red-800 mb-1">Probleem met data ophalen</h4>
      <p class="text-sm text-red-700 mb-2">{{ dataError }}</p>
      <button
        @click="retryDataLoad"
        class="text-sm px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
      >
        Opnieuw proberen
      </button>
    </div>
    <button
      @click="dataError = null"
      class="text-red-400 hover:text-red-600"
      aria-label="Sluit waarschuwing"
    >
      ×
    </button>
  </div>
</div>

<!-- Loading State Verbetering -->
<div 
  v-if="loading" 
  class="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-lg shadow-2xl p-6 z-40"
  role="status"
  aria-live="polite"
  aria-label="Data wordt geladen"
>
  <div class="flex items-center gap-3">
    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    <div>
      <span class="text-sm font-semibold text-gray-700">Laden...</span>
      <p class="text-xs text-gray-500 mt-1">{{ loadingMessage }}</p>
    </div>
  </div>
</div>
```

**Concrete implementatie voor GemaalChart.vue - Verbeterde context**:

```vue
<!-- Toevoegen aan GemaalChart.vue -->
<div class="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
  <h5 class="text-xs font-semibold text-blue-800 mb-2">ℹ️ Over deze grafiek</h5>
  <ul class="text-xs text-blue-700 space-y-1">
    <li>• Toont debiet (waterafvoer) van de laatste 3 uur</li>
    <li>• Data wordt elke 30 minuten bijgewerkt</li>
    <li>• Status "aan" betekent dat het gemaal water pompt</li>
    <li>• Normaal debiet voor dit gemaal: {{ normalDebietRange }}</li>
  </ul>
</div>
```

#### 3.2 Toegankelijkheid (Accessibility)

**Richtlijn**: Zorg dat informatie toegankelijk is voor alle gebruikers.

**Huidige situatie in project**:
- ✅ **Goed**: Basis HTML structuur met semantische elementen
- ✅ **Goed**: Tooltips met informatie
- ⚠️ **Mist**:
  - ARIA labels en roles
  - Screen reader ondersteuning
  - Keyboard navigatie
  - Kleurcontrast verificatie
  - Focus management

**Concrete implementaties**:

**1. ARIA Labels en Roles toevoegen**:

```vue
<!-- Voor DashboardPanel.vue -->
<div 
  role="region"
  aria-label="Gemaal status dashboard"
  aria-live="polite"
  aria-atomic="true"
>
  <!-- ... -->
</div>

<!-- Voor AllLayersMap.vue -->
<div 
  id="all-layers-map"
  role="application"
  aria-label="Interactieve kaart met waterbeheer informatie"
  tabindex="0"
>
  <!-- ... -->
</div>

<!-- Voor buttons -->
<button
  @click="toggleLegend"
  aria-label="Toggle legenda"
  aria-expanded="legendExpanded"
  aria-controls="legend-panel"
>
  {{ legendExpanded ? '−' : '+' }}
</button>
```

**2. Screen Reader ondersteuning**:

```vue
<!-- Toevoegen aan DashboardPanel.vue -->
<template>
  <!-- Visuele weergave -->
  <div class="dashboard-panel">
    <!-- ... -->
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
</template>

<style>
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
```

**3. Keyboard navigatie**:

```vue
<!-- Toevoegen aan AllLayersMap.vue -->
<script setup>
import { onMounted, onUnmounted } from 'vue'

// Keyboard shortcuts
const handleKeyPress = (event) => {
  // Escape sluit modals
  if (event.key === 'Escape') {
    if (selectedFeature.value) {
      closeInfo()
    }
    if (showChart.value) {
      showChart.value = false
    }
  }
  
  // L toggle legenda
  if (event.key === 'l' || event.key === 'L') {
    if (!event.ctrlKey && !event.metaKey) {
      toggleLegend()
    }
  }
  
  // H toon help
  if (event.key === 'h' || event.key === 'H') {
    if (!event.ctrlKey && !event.metaKey) {
      showHelp.value = !showHelp.value
    }
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
})
</script>
```

**4. Kleurcontrast verbeteren**:

```vue
<!-- Toevoegen aan style.css of component styles -->
<style>
/* WCAG AA compliant kleuren */
.text-gray-800 {
  color: #1f2937; /* Contrast ratio 12.63:1 op wit */
}

.text-gray-600 {
  color: #4b5563; /* Contrast ratio 7.0:1 op wit */
}

.text-gray-500 {
  color: #6b7280; /* Contrast ratio 4.5:1 op wit - voldoet voor grote tekst */
}

/* Waarschuwingen met goede contrast */
.bg-yellow-100 {
  background-color: #fef3c7;
}

.text-yellow-800 {
  color: #92400e; /* Contrast ratio 7.0:1 */
}

.bg-red-100 {
  background-color: #fee2e2;
}

.text-red-800 {
  color: #991b1b; /* Contrast ratio 7.0:1 */
}

/* Focus states voor keyboard navigatie */
button:focus,
a:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Skip link voor screen readers */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #000;
  color: #fff;
  padding: 8px;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
</style>
```

**5. Mobile responsiveness verbeteren**:

```vue
<!-- Responsive DashboardPanel -->
<template>
  <div 
    v-if="visible"
    class="dashboard-panel"
    :class="{
      'flex-col': isMobile,
      'flex-row': !isMobile
    }"
  >
    <!-- ... -->
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'

const isMobile = ref(window.innerWidth < 768)

const handleResize = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style>
@media (max-width: 768px) {
  .dashboard-panel {
    left: 1rem;
    right: 1rem;
    transform: none;
    max-width: calc(100% - 2rem);
  }
  
  .legend-panel {
    width: calc(100% - 2rem);
    max-width: none;
  }
  
  .info-panel {
    width: calc(100% - 2rem);
    max-width: none;
  }
}
</style>
```

**6. Focus management voor modals**:

```vue
<!-- Toevoegen aan GemaalChart.vue -->
<script setup>
import { nextTick, watch } from 'vue'

const chartRef = ref(null)
const closeButtonRef = ref(null)

watch(showChart, async (newVal) => {
  if (newVal) {
    await nextTick()
    // Focus op close button voor keyboard gebruikers
    closeButtonRef.value?.focus()
    
    // Trap focus binnen modal
    const modal = chartRef.value
    if (modal) {
      const focusableElements = modal.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
      const firstElement = focusableElements[0]
      const lastElement = focusableElements[focusableElements.length - 1]
      
      const handleTabKey = (e) => {
        if (e.key !== 'Tab') return
        
        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault()
            lastElement.focus()
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault()
            firstElement.focus()
          }
        }
      }
      
      modal.addEventListener('keydown', handleTabKey)
      
      // Cleanup bij unmount
      onUnmounted(() => {
        modal.removeEventListener('keydown', handleTabKey)
      })
    }
  }
})
</script>
```

#### 3.3 Data Context en Uitleg

**Richtlijn**: Geef gebruikers context over wat ze zien.

**Implementatie - Help component**:

```vue
<!-- Nieuwe component: HelpPanel.vue -->
<template>
  <div
    v-if="visible"
    class="fixed bottom-4 right-4 bg-white rounded-lg shadow-xl border border-gray-200 p-6 z-40 max-w-md"
    role="dialog"
    aria-labelledby="help-title"
    aria-modal="true"
  >
    <div class="flex justify-between items-start mb-4">
      <h3 id="help-title" class="text-lg font-bold text-gray-800">
        ℹ️ Uitleg
      </h3>
      <button
        @click="$emit('close')"
        class="text-gray-400 hover:text-gray-600"
        aria-label="Sluit uitleg"
      >
        ×
      </button>
    </div>
    
    <div class="space-y-4 text-sm text-gray-700">
      <section>
        <h4 class="font-semibold mb-2">📊 Dashboard</h4>
        <ul class="space-y-1 ml-4 list-disc">
          <li><strong>Actieve Gemalen:</strong> Aantal gemalen dat momenteel water pompt</li>
          <li><strong>Totaal Debiet:</strong> Totale hoeveelheid water die wordt gepompt (m³/s)</li>
          <li><strong>Laatste update:</strong> Wanneer data voor het laatst is bijgewerkt</li>
        </ul>
      </section>
      
      <section>
        <h4 class="font-semibold mb-2">🗺️ Kaart</h4>
        <ul class="space-y-1 ml-4 list-disc">
          <li>Klik op een gemaal voor gedetailleerde informatie</li>
          <li>Hover over peilgebieden voor peilgegevens</li>
          <li>Gebruik de legenda om lagen in/uit te schakelen</li>
        </ul>
      </section>
      
      <section>
        <h4 class="font-semibold mb-2">📈 Grafieken</h4>
        <ul class="space-y-1 ml-4 list-disc">
          <li>Toont debiet over de laatste 3 uur</li>
          <li>Data wordt elke 30 minuten bijgewerkt</li>
          <li>Groene lijn = gemaal is actief</li>
        </ul>
      </section>
      
      <section class="pt-4 border-t border-gray-200">
        <h4 class="font-semibold mb-2">⌨️ Sneltoetsen</h4>
        <ul class="space-y-1 ml-4 list-disc">
          <li><kbd>L</kbd> - Toggle legenda</li>
          <li><kbd>H</kbd> - Toggle deze help</li>
          <li><kbd>Esc</kbd> - Sluit modals</li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: Boolean
})

defineEmits(['close'])
</script>
```

#### 3.4 Data Kwaliteit Indicatoren

**Richtlijn**: Toon duidelijk wanneer data mogelijk niet betrouwbaar is.

**Implementatie - Data Quality Indicator component**:

```vue
<!-- Nieuwe component: DataQualityIndicator.vue -->
<template>
  <div
    v-if="showIndicator"
    class="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-white rounded-lg shadow-lg border-2 p-3 z-30 flex items-center gap-3"
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
  stats: Object,
  successRate: Number, // 0-1
  lastError: String
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
```

#### 3.5 Implementatie Checklist voor Gebruikerservaring

**Prioriteit 1 - Direct implementeren**:

- [ ] **DashboardPanel.vue uitbreiden**:
  - [ ] Data actualiteit indicatie toevoegen (isStale, isVeryStale)
  - [ ] Data leeftijd tekst toevoegen ("5 minuten geleden")
  - [ ] Normale waarden referentie toevoegen (expectedActiveRange, expectedDebietRange)
  - [ ] Help tooltip/panel toevoegen
  - [ ] ARIA labels en roles toevoegen
  - [ ] Screen reader tekst toevoegen (.sr-only)

- [ ] **AllLayersMap.vue verbeteren**:
  - [ ] Error state panel toevoegen met retry functionaliteit
  - [ ] Verbeterde loading state met progress informatie
  - [ ] Keyboard shortcuts toevoegen (L, H, Esc)
  - [ ] ARIA labels voor kaart en controls
  - [ ] Focus management voor modals

- [ ] **GemaalChart.vue uitbreiden**:
  - [ ] Contextuele uitleg toevoegen over grafiek
  - [ ] Normale debiet range tonen
  - [ ] Focus management voor modal
  - [ ] Keyboard navigatie binnen modal

**Prioriteit 2 - Binnen 2 weken**:

- [ ] **Nieuwe componenten maken**:
  - [ ] `HelpPanel.vue` - Uitgebreide help sectie
  - [ ] `DataQualityIndicator.vue` - Data kwaliteit status
  - [ ] Screen reader alleen componenten

- [ ] **Toegankelijkheid**:
  - [ ] Kleurcontrast verificatie (WCAG AA)
  - [ ] Skip links toevoegen
  - [ ] Focus states verbeteren
  - [ ] Mobile responsiveness testen en verbeteren

- [ ] **Styling**:
  - [ ] Responsive breakpoints voor mobile
  - [ ] Touch-friendly button sizes
  - [ ] Verbeterde focus states

**Prioriteit 3 - Binnen 1 maand**:

- [ ] **Geavanceerde features**:
  - [ ] Keyboard navigatie voor alle interactieve elementen
  - [ ] Voice over/read aloud functionaliteit
  - [ ] High contrast mode
  - [ ] Font size aanpassing

- [ ] **Testing**:
  - [ ] Screen reader testing (NVDA, JAWS, VoiceOver)
  - [ ] Keyboard-only navigatie testen
  - [ ] Mobile device testing
  - [ ] Browser compatibility testing

#### 3.6 Bestaande Code Integratie

**Huidige bestanden die aangepast moeten worden**:

1. **`simulatie-peilbeheer/src/components/DashboardPanel.vue`**
   - Voeg computed properties toe voor data actualiteit
   - Voeg help panel toe
   - Voeg ARIA attributes toe
   - Voeg screen reader tekst toe

2. **`simulatie-peilbeheer/src/components/AllLayersMap.vue`**
   - Voeg error state handling toe
   - Voeg keyboard shortcuts toe
   - Verbeter loading states
   - Voeg focus management toe

3. **`simulatie-peilbeheer/src/components/GemaalChart.vue`**
   - Voeg contextuele uitleg toe
   - Verbeter error messages
   - Voeg focus management toe

4. **`simulatie-peilbeheer/src/style.css`**
   - Voeg accessibility styles toe (.sr-only, focus states)
   - Voeg responsive breakpoints toe
   - Verbeter kleurcontrast

**Nieuwe bestanden die gemaakt moeten worden**:

1. **`simulatie-peilbeheer/src/components/HelpPanel.vue`**
   - Uitgebreide help sectie met uitleg

2. **`simulatie-peilbeheer/src/components/DataQualityIndicator.vue`**
   - Component voor data kwaliteit status

3. **`simulatie-peilbeheer/src/utils/accessibility.js`**
   - Utility functies voor accessibility (keyboard shortcuts, focus management)

### 4. Verantwoording en Monitoring

#### 4.1 Logging en Audit Trail

**Richtlijn**: Houd bij welke gegevens worden gebruikt en hoe.

**Toepassing voor dit project**:
- ✅ **Goed**: Logging in `logs/` directory
- ⚠️ **Verbeter**: Voeg toe:
  - Logging van data access (wie/wat/wanneer)
  - Error logging met context
  - Performance metrics
  - Data quality metrics

**Implementatie**:
```python
# Uitgebreide logging
logger.info(f"Data fetch gestart: {len(gemalen)} gemalen")
logger.info(f"API call: Hydronet - gemaal {code}")
logger.warning(f"Data validatie gefaald: {reason}")
logger.error(f"API error: {status_code} - {message}")
logger.info(f"Data fetch voltooid: {success}/{total} succesvol")
```

#### 4.2 Monitoring en Alerting

**Richtlijn**: Monitor systeem gezondheid en data kwaliteit.

**Toepassing voor dit project**:
- ⚠️ **Implementeer**:
  - Health checks voor API beschikbaarheid
  - Data staleness monitoring
  - Success rate tracking
  - Alerting bij kritieke problemen

**Implementatie**:
```python
# Health monitoring
def check_system_health():
    metrics = {
        'api_available': check_hydronet_api(),
        'data_freshness': check_data_age(),
        'success_rate': calculate_success_rate(),
        'error_count': count_recent_errors()
    }
    
    if metrics['success_rate'] < 0.8:
        send_alert("Low success rate in gemaal data fetch")
    
    return metrics
```

### 5. Samenwerking en Afstemming

#### 5.1 Duidelijke Afspraken

**Richtlijn**: Maak duidelijke afspraken met databronnen en gebruikers.

**Toepassing voor dit project**:
- ⚠️ **Verbeter**: Documenteer:
  - Service Level Agreements (SLA's) met Hydronet
  - Afspraken over rate limiting
  - Procedures bij API wijzigingen
  - Contactpersonen bij problemen

**Implementatie**:
```markdown
## Service Afspraken

### Hydronet API
- **Contact**: [contactpersoon]
- **SLA**: 99% uptime verwacht
- **Rate Limit**: Max 10 requests/seconde
- **Wijzigingen**: 2 weken vooraf melden
- **Support**: [support email/telefoon]
```

#### 5.2 Proactieve Communicatie

**Richtlijn**: Communiceer proactief over wijzigingen en problemen.

**Toepassing voor dit project**:
- ⚠️ **Implementeer**:
  - Status pagina voor systeem status
  - Notificaties bij API wijzigingen
  - Changelog voor gebruikers
  - Communicatie bij data problemen

### 6. Privacy en Beveiliging

#### 6.1 Privacy by Design

**Richtlijn**: Privacy overwegingen vanaf het begin meenemen.

**Toepassing voor dit project**:
- ✅ **Goed**: Geen persoonlijke gegevens worden verwerkt
- ⚠️ **Verbeter**: Controleer:
  - IP logging (minimaliseer)
  - Cookie gebruik (alleen functioneel)
  - Tracking (geen analytics zonder toestemming)
  - Data encryptie (HTTPS is voldoende voor publieke data)

#### 6.2 Beveiliging

**Richtlijn**: Zorg voor adequate beveiliging van gegevens.

**Toepassing voor dit project**:
- ✅ **Goed**: HTTPS communicatie
- ⚠️ **Verbeter**:
  - Rate limiting op API endpoints
  - Input validatie
  - Error messages zonder gevoelige informatie
  - Regular security updates

---

## Concrete Actiepunten voor dit Project

### Prioriteit 1: Direct implementeren

1. **Documentatie uitbreiden**
   - [ ] Doel van gegevensuitwisseling documenteren
   - [ ] Deelnemende organisaties lijst
   - [ ] Data retentie beleid
   - [ ] Privacy overwegingen

2. **Data validatie toevoegen**
   - [ ] Realistische waarde checks
   - [ ] Staleness detection
   - [ ] Error handling verbeteren

3. **Monitoring implementeren**
   - [ ] Health checks
   - [ ] Success rate tracking
   - [ ] Alerting bij problemen

### Prioriteit 2: Binnen 2 weken

4. **Gebruikerservaring verbeteren**
   - [ ] Data actualiteit indicatie
   - [ ] Contextuele informatie
   - [ ] Waarschuwingen bij oude data

5. **Logging uitbreiden**
   - [ ] Audit trail
   - [ ] Performance metrics
   - [ ] Data quality metrics

6. **Service afspraken documenteren**
   - [ ] SLA's met databronnen
   - [ ] Contactpersonen
   - [ ] Procedures bij problemen

### Prioriteit 3: Binnen 1 maand

7. **Toegankelijkheid verbeteren**
   - [ ] Screen reader support
   - [ ] Kleurcontrast checks
   - [ ] Mobile optimalisatie

8. **Proactieve communicatie**
   - [ ] Status pagina
   - [ ] Changelog
   - [ ] Notificaties bij wijzigingen

---

## Checklist: Verantwoord Gegevensgebruik

Gebruik deze checklist bij het ontwikkelen en onderhouden van het waterbeheer systeem:

### Transparantie
- [ ] Doel van gegevensuitwisseling is duidelijk gedocumenteerd
- [ ] Gebruikers weten welke data wordt gebruikt
- [ ] Technische keuzes zijn uitlegbaar
- [ ] Wijzigingen worden gecommuniceerd

### Proportionaliteit
- [ ] Alleen noodzakelijke gegevens worden opgehaald
- [ ] Data wordt geminimaliseerd waar mogelijk
- [ ] Geen onnodige metadata wordt opgeslagen

### Rechtmatigheid
- [ ] API gebruiksvoorwaarden zijn nageleefd
- [ ] Data wordt gebruikt conform oorspronkelijk doel
- [ ] Toestemming is verkregen waar nodig
- [ ] AVG/GDPR compliance is gecontroleerd

### Betrouwbaarheid
- [ ] Data validatie is geïmplementeerd
- [ ] Staleness detection werkt
- [ ] Error handling is adequaat
- [ ] Health monitoring is actief

### Verantwoording
- [ ] Logging is uitgebreid genoeg
- [ ] Audit trail is beschikbaar
- [ ] Monitoring en alerting werken
- [ ] Performance wordt getrackt

### Samenwerking
- [ ] Afspraken met databronnen zijn gedocumenteerd
- [ ] Contactpersonen zijn bekend
- [ ] Procedures bij problemen zijn duidelijk
- [ ] Communicatie is proactief

---

## Referenties

- **CCG Document**: Centrale Commissie Gegevensgebruik - "Vertrouwen door verantwoord gegevensgebruik" (December 2025)
- **Project Documentatie**: 
  - `ARCHITECTUURPLAN_REALTIME_GEMAAL_DASHBOARD.md`
  - `RIJNLAND_DATA.md`
  - `RIJNLAND_DYNAMISCHE_DATA.md`
- **CCG Website**: ccg@minbzk.nl

---

**Laatste update**: 2025-12-11  
**Volgende review**: 2026-01-11

