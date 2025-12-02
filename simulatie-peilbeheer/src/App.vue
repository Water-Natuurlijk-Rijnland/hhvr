<script setup>
import { ref } from 'vue'
import PolderMap from './components/PolderMap.vue'
import AllLayersMap from './components/AllLayersMap.vue'

const activeTab = ref('simulatie')

const setActiveTab = (tab) => {
  activeTab.value = tab
}
</script>

<template>
  <div class="h-screen w-screen flex flex-col">
    <!-- Tab Navigation -->
    <div class="fixed top-0 left-0 right-0 z-50 bg-white shadow-md border-b border-gray-200">
      <div class="flex">
        <button
          @click="setActiveTab('simulatie')"
          :class="[
            'flex-1 px-4 py-4 text-sm font-semibold transition-all duration-200',
            activeTab === 'simulatie'
              ? 'bg-blue-600 text-white border-b-4 border-blue-700'
              : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border-b-4 border-transparent'
          ]"
        >
          <span class="flex items-center justify-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            <span class="hidden md:inline">Simulatie</span>
          </span>
        </button>
        <button
          @click="setActiveTab('allelagen')"
          :class="[
            'flex-1 px-4 py-4 text-sm font-semibold transition-all duration-200',
            activeTab === 'allelagen'
              ? 'bg-blue-600 text-white border-b-4 border-blue-700'
              : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border-b-4 border-transparent'
          ]"
        >
          <span class="flex items-center justify-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
            <span class="hidden md:inline">Alle Lagen</span>
          </span>
        </button>
      </div>
    </div>

    <!-- Tab Content -->
    <div class="flex-1 pt-16">
      <PolderMap v-if="activeTab === 'simulatie'" />
      <AllLayersMap v-if="activeTab === 'allelagen'" />
    </div>
  </div>
</template>

<style scoped>
</style>
