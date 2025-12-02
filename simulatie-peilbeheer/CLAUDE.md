# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Vue 3 + Vite application that simulates water level management (peilbeheer) in Dutch polders over time (2025-2075). The application visualizes how different peat subsidence compensation strategies (peilindexatie percentages) affect soil conditions and water levels in polder areas.

## Development Commands

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Architecture

### Core Components

**PolderMap.vue** - Main map component that:
- Renders an interactive Leaflet map with polder polygons from `public/polders.json`
- Manages all simulation state (current year, peilindexatie percentage, selected polder)
- Implements the core subsidence calculation logic with yearly data caching
- Colors polders based on drooglegging (soil depth above water) using a gradient from green (≤40cm) to red (≥70cm)
- Handles polder selection and map interactions

**ControlPanel.vue** - Fixed sidebar that:
- Provides peilindexatie preset buttons (0%, 25%, 50%, 75%)
- Year slider (2025-2075) with play/pause animation
- Emits `yearChange` and `peilindexatieChange` events to parent
- Auto-resets to 2025 when peilindexatie changes

**AnimationPanel.vue** - Detail visualization that:
- Shows cross-section animation of selected polder with SVG
- Visualizes peat layer shrinkage, water level (sloot), and drooglegging measurement
- Displays current year, drooglegging, and water level (zomerpeil_ondergrens) in NAP

### Simulation Logic

The core calculation (`calculateYearlyDataForPolder` in PolderMap.vue):

1. **Peat subsidence**: 0.7 cm/year constant rate
2. **Peilindexatie**: Water level compensation as percentage (0-100%)
3. **Drooglegging formula**: 
   - Normal: `drooglegging = previous - 0.7 + (0.7 × peilindexatie/100)`
   - At minimum (40cm): drooglegging locked, water level drops by full 0.7cm/year
4. **Water level**: `zomerpeil_ondergrens = previous - (0.7 × peilindexatie/100)` until minimum drooglegging reached

All yearly data is pre-calculated and cached per polder per peilindexatie percentage for performance.

### Data Structure

**public/polders.json**: Array of polder objects with:
- `id`: Unique identifier
- `name`: Display name
- `drooglegging_2025`: Initial soil depth above water (cm)
- `zomerpeil_ondergrens_2025`: Initial summer water level lower boundary (cm NAP)
- `geometry`: GeoJSON polygon geometry

### Styling

- Tailwind CSS v4 with Vite plugin
- Custom CSS in components for Leaflet overrides and slider styling
- Color scheme: Blue (`#0083F1`) for primary actions and water
- Drooglegging gradient: Green → Yellow → Light Orange → Dark Orange → Red

### Build Configuration

- Base path: `/simulatie-peilbeheer/` (configured in vite.config.js for GitHub Pages)
- Vite with Vue 3 plugin and Tailwind
- Uses ES modules (`type: "module"` in package.json)

## Key Implementation Details

- **Reactivity**: Vue 3 Composition API with `ref()` and `computed()`
- **Map library**: Leaflet with custom styling and event handlers
- **Performance**: Yearly data is pre-calculated once per polder/peilindexatie combination and cached
- **State management**: Parent-child component communication via events (no Vuex/Pinia)
- **Coordinate system**: NAP (Normaal Amsterdams Peil) for water levels, converted from cm to meters for display
