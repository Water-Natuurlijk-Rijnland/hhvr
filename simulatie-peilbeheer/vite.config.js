import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { readFileSync, existsSync, readdirSync, writeFileSync, statSync } from 'fs'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    {
      name: 'serve-rijnland-kaartlagen',
      configureServer(server) {
        server.middlewares.use((req, res, next) => {
          // Serve bestanden uit peilbesluiten/rijnland_kaartlagen
          if (req.url?.includes('/peilbesluiten/rijnland_kaartlagen/')) {
            try {
              // Verwijder base URL en leading slash
              const relativePath = req.url.replace(/^\/simulatie-peilbeheer\//, '').replace(/^\//, '')
              const filePath = resolve(__dirname, '..', relativePath)
              
              if (existsSync(filePath)) {
                const content = readFileSync(filePath)
                res.setHeader('Content-Type', 'application/json')
                res.setHeader('Access-Control-Allow-Origin', '*')
                res.end(content)
                return
              }
            } catch (e) {
              console.error('Error serving file:', e)
            }
          }
          next()
        })
      }
    },
    {
      name: 'hydronet-api-proxy',
      configureServer(server) {
        // Endpoint om lijst van gemalen met data op te halen (alleen opgeslagen data - geen API checks bij opstart)
        server.middlewares.use('/api/gemalen-met-data', async (req, res, next) => {
          try {
            const realtimeDataDir = resolve(__dirname, '..', 'peilbesluiten', 'realtime_gemaal_data')
            let files = []
            try {
              if (existsSync(realtimeDataDir)) {
                files = readdirSync(realtimeDataDir)
              }
            } catch (e) {
              console.warn(`[Proxy] Kon directory niet lezen: ${e.message}`)
            }
            
            // Extraheer unieke gemaal codes - alle gemalen met opgeslagen data worden gemarkeerd
            // (De filtering op laatste 3 uur gebeurt alleen bij het tonen van de grafiek)
            const gemalenSet = new Set()
            
            // Groepeer bestanden per gemaal code
            const gemaalFilesMap = new Map()
            files.forEach(file => {
              const match = file.match(/^gemaal_([^_]+)_/)
              if (match) {
                const code = match[1]
                if (!gemaalFilesMap.has(code)) {
                  gemaalFilesMap.set(code, [])
                }
                gemaalFilesMap.get(code).push(file)
              }
            })
            
            // Check voor elk gemaal of er data beschikbaar is (ongeacht hoe oud)
            for (const [code, fileList] of gemaalFilesMap.entries()) {
              // Sorteer op datum (nieuwste eerst)
              fileList.sort().reverse()
              const latestFile = fileList[0]
              const filePath = resolve(realtimeDataDir, latestFile)
              
              try {
                const fileContent = readFileSync(filePath, 'utf-8')
                const savedData = JSON.parse(fileContent)
                
                // Als er data is (ongeacht hoe oud), markeer het gemaal als "met data"
                if (savedData.data && savedData.data.series && savedData.data.series.length > 0) {
                  const series = savedData.data.series[0]
                  if (series.data && series.data.length > 0) {
                    // Heeft data beschikbaar - markeer als groen
                    gemalenSet.add(code)
                  }
                }
              } catch (e) {
                // Skip dit bestand als het niet gelezen kan worden
                console.warn(`[Proxy] Kon bestand niet lezen: ${latestFile}`)
              }
            }
            
            // GEEN API check bij opstart - alleen opgeslagen data gebruiken voor groene markering
            // API checks gebeuren alleen wanneer gebruiker op een gemaal klikt
            
            const result = {
              gemalen: Array.from(gemalenSet),
              totaal: gemalenSet.size,
              opgeslagen: gemalenSet.size
            }
            
            res.setHeader('Content-Type', 'application/json')
            res.setHeader('Access-Control-Allow-Origin', '*')
            res.end(JSON.stringify(result))
          } catch (error) {
            console.error('[Proxy] Fout bij ophalen gemalen lijst:', error)
            res.statusCode = 500
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify({ error: error.message || 'Onbekende fout' }))
          }
        })
        
        // Endpoint om lijst van gemalen met data op te halen (alleen opgeslagen data - geen API checks bij opstart)
        server.middlewares.use('/api/gemalen-met-data', async (req, res, next) => {
          try {
            const realtimeDataDir = resolve(__dirname, '..', 'peilbesluiten', 'realtime_gemaal_data')
            let files = []
            try {
              if (existsSync(realtimeDataDir)) {
                files = readdirSync(realtimeDataDir)
              }
            } catch (e) {
              console.warn(`[Proxy] Kon directory niet lezen: ${e.message}`)
            }
            
            // Extraheer unieke gemaal codes - alle gemalen met opgeslagen data worden gemarkeerd
            // (De filtering op laatste 3 uur gebeurt alleen bij het tonen van de grafiek)
            const gemalenSet = new Set()
            
            // Groepeer bestanden per gemaal code
            const gemaalFilesMap = new Map()
            files.forEach(file => {
              const match = file.match(/^gemaal_([^_]+)_/)
              if (match) {
                const code = match[1]
                if (!gemaalFilesMap.has(code)) {
                  gemaalFilesMap.set(code, [])
                }
                gemaalFilesMap.get(code).push(file)
              }
            })
            
            // Check voor elk gemaal of er data beschikbaar is (ongeacht hoe oud)
            for (const [code, fileList] of gemaalFilesMap.entries()) {
              // Sorteer op datum (nieuwste eerst)
              fileList.sort().reverse()
              const latestFile = fileList[0]
              const filePath = resolve(realtimeDataDir, latestFile)
              
              try {
                const fileContent = readFileSync(filePath, 'utf-8')
                const savedData = JSON.parse(fileContent)
                
                // Als er data is (ongeacht hoe oud), markeer het gemaal als "met data"
                if (savedData.data && savedData.data.series && savedData.data.series.length > 0) {
                  const series = savedData.data.series[0]
                  if (series.data && series.data.length > 0) {
                    // Heeft data beschikbaar - markeer als groen
                    gemalenSet.add(code)
                  }
                }
              } catch (e) {
                // Skip dit bestand als het niet gelezen kan worden
                console.warn(`[Proxy] Kon bestand niet lezen: ${latestFile}`)
              }
            }
            
            // GEEN API check bij opstart - alleen opgeslagen data gebruiken voor groene markering
            // API checks gebeuren alleen wanneer gebruiker op een gemaal klikt
            
            const result = {
              gemalen: Array.from(gemalenSet),
              totaal: gemalenSet.size,
              opgeslagen: gemalenSet.size
            }
            
            res.setHeader('Content-Type', 'application/json')
            res.setHeader('Access-Control-Allow-Origin', '*')
            res.end(JSON.stringify(result))
          } catch (error) {
            console.error('[Proxy] Fout bij ophalen gemalen lijst:', error)
            res.statusCode = 500
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify({ error: error.message || 'Onbekende fout' }))
          }
        })
        
        server.middlewares.use('/api/gemaal', async (req, res, next) => {
          // Proxy voor Hydronet API - gebruikt eerst lokale opgeslagen data
          const url = new URL(req.url, `http://${req.headers.host}`)
          const gemaalCode = url.searchParams.get('code')
          
          if (!gemaalCode) {
            res.statusCode = 400
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify({ error: 'Gemaal code is vereist' }))
            return
          }

          try {
            // Stap 1: Probeer eerst lokale opgeslagen data te vinden
            const realtimeDataDir = resolve(__dirname, '..', 'peilbesluiten', 'realtime_gemaal_data')
            let files = []
            try {
              if (existsSync(realtimeDataDir)) {
                files = readdirSync(realtimeDataDir)
              }
            } catch (e) {
              console.warn(`[Proxy] Kon directory niet lezen: ${e.message}`)
            }
            
            // Zoek het meest recente bestand voor dit gemaal
            const gemaalFiles = files.filter(f => f.startsWith(`gemaal_${gemaalCode}_`) && f.endsWith('.json'))
            
            let useLocalData = false
            let localDataAge = Infinity
            
            if (gemaalFiles.length > 0) {
              // Sorteer op datum (nieuwste eerst)
              gemaalFiles.sort().reverse()
              const latestFile = gemaalFiles[0]
              const filePath = resolve(realtimeDataDir, latestFile)
              
              try {
                const fileStats = statSync(filePath)
                const fileContent = readFileSync(filePath, 'utf-8')
                const savedData = JSON.parse(fileContent)
                
                const now = Date.now()
                localDataAge = now - fileStats.mtimeMs
                const thirtyMinutesAgo = now - (30 * 60 * 1000)
                
                // Gebruik lokale data alleen als deze nieuwer is dan 30 minuten
                if (localDataAge <= 30 * 60 * 1000 && savedData.data && savedData.data.series && savedData.data.series.length > 0) {
                  const threeHoursAgo = now - (3 * 60 * 60 * 1000)
                  
                  const result = {
                    gemaalCode,
                    series: savedData.data.series.map(s => ({
                      name: s.name || 'Debiet',
                      data: s.data
                        .map(point => {
                          // Converteer timestamp naar Date object
                          const timestamp = point.timestamp_ms || new Date(point.timestamp).getTime()
                          return {
                            timestamp: new Date(timestamp),
                            timestampMs: timestamp,
                            value: point.value || 0
                          }
                        })
                        .filter(point => {
                          // Filter alleen laatste 3 uur
                          return point.timestampMs >= threeHoursAgo && point.timestampMs <= now
                        })
                        .sort((a, b) => a.timestampMs - b.timestampMs) // Sorteer op tijd
                    }))
                  }
                  
                  // Alleen terugsturen als er data is van laatste 3 uur
                  if (result.series[0].data.length > 0) {
                    console.log(`[Proxy] Gebruik lokale data voor gemaal ${gemaalCode} (${Math.round(localDataAge / 60000)} minuten oud)`)
                    res.setHeader('Content-Type', 'application/json')
                    res.setHeader('Access-Control-Allow-Origin', '*')
                    res.end(JSON.stringify(result))
                    return
                  }
                }
                
                // Lokale data is ouder dan 30 minuten of heeft geen data van laatste 3 uur
                if (localDataAge > 30 * 60 * 1000) {
                  console.log(`[Proxy] Lokale data voor ${gemaalCode} is ${Math.round(localDataAge / 60000)} minuten oud - haal nieuwe data op via API`)
                } else {
                  console.log(`[Proxy] Lokale data voor ${gemaalCode} heeft geen data van laatste 3 uur - haal nieuwe data op via API`)
                }
              } catch (fileError) {
                console.warn(`[Proxy] Fout bij lezen lokale data: ${fileError.message}`)
                // Vervolg naar API fallback
              }
            } else {
              console.log(`[Proxy] Geen lokale data gevonden voor gemaal ${gemaalCode} - haal op via API`)
            }
            
            // Stap 2: Haal data op via API (als lokale data niet beschikbaar is of ouder dan 30 minuten)
            
            const HYDRONET_CHART_ID = 'e743fb87-2a02-4f3e-ac6c-03d03401aab8'
            const HYDRONET_BASE_URL = 'https://watercontrolroom.hydronet.com/service/efsserviceprovider/api/chart'
            const apiUrl = `${HYDRONET_BASE_URL}/${HYDRONET_CHART_ID}?featureIdentifier=${gemaalCode}`
            
            const response = await fetch(apiUrl, {
              headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8',
                'Referer': 'https://rijnland.maps.arcgis.com/',
                'Origin': 'https://rijnland.maps.arcgis.com'
              }
            })

            if (!response.ok) {
              res.statusCode = response.status
              res.setHeader('Content-Type', 'application/json')
              res.end(JSON.stringify({ 
                error: `API fout: ${response.status} ${response.statusText}` 
              }))
              return
            }

            const html = await response.text()
            
            // Parse Highcharts data
            const pattern = /Highcharts\.chart\(['"]container['"],\s*(\{.*?\})\);/s
            const match = html.match(pattern)
            
            if (!match) {
              res.statusCode = 500
              res.setHeader('Content-Type', 'application/json')
              res.end(JSON.stringify({ error: 'Kon Highcharts data niet parsen' }))
              return
            }

            const config = JSON.parse(match[1])
            const series = config.series || []

            if (series.length === 0 || !series[0].data || series[0].data.length === 0) {
              res.statusCode = 404
              res.setHeader('Content-Type', 'application/json')
              res.end(JSON.stringify({ error: 'Geen data beschikbaar voor dit gemaal' }))
              return
            }

            // Sla nieuwe data op voor volgende keer
            try {
              const parsedData = {
                feature_identifier: gemaalCode,
                timestamp: new Date().toISOString(),
                time_range: {
                  min: config.xAxis?.[0]?.min,
                  max: config.xAxis?.[0]?.max
                },
                yAxis: (config.yAxis || []).map(y => ({
                  title: y.title?.text || '',
                  min: y.min,
                  max: y.max,
                  id: y.id || ''
                })),
                series: series.map(s => ({
                  name: s.name || 'Debiet',
                  type: s.type || 'line',
                  color: s.color || '',
                  data: (s.data || []).map(point => {
                    const timestamp_ms = point.x || 0
                    const value = point.y || 0
                    const timestamp_dt = new Date(timestamp_ms)
                    return {
                      timestamp: timestamp_dt.toISOString(),
                      timestamp_ms: timestamp_ms,
                      value: value,
                      status: value > 0.001 ? 'aan' : 'uit'
                    }
                  })
                }))
              }
              
              const timestamp = new Date()
              const filename = `gemaal_${gemaalCode}_${timestamp.toISOString().replace(/[:.]/g, '-').slice(0, 19).replace('T', '_')}.json`
              const filePath = resolve(realtimeDataDir, filename)
              
              const saveData = {
                timestamp: timestamp.toISOString(),
                feature_identifier: gemaalCode,
                chart_id: HYDRONET_CHART_ID,
                data: parsedData
              }
              
              writeFileSync(filePath, JSON.stringify(saveData, null, 2), 'utf-8')
              console.log(`[Proxy] ✓ Nieuwe data opgeslagen voor gemaal ${gemaalCode}`)
            } catch (saveError) {
              console.warn(`[Proxy] Kon data niet opslaan: ${saveError.message}`)
            }

            // Converteer naar tijdreeks data en filter laatste 3 uur
            const now = Date.now()
            const threeHoursAgo = now - (3 * 60 * 60 * 1000)
            
            const timeSeriesData = series[0].data
              .map(point => ({
                timestamp: new Date(point.x),
                timestampMs: point.x,
                value: point.y || 0
              }))
              .filter(point => {
                // Filter alleen laatste 3 uur
                return point.timestampMs >= threeHoursAgo && point.timestampMs <= now
              })
              .sort((a, b) => a.timestampMs - b.timestampMs) // Sorteer op tijd

            if (timeSeriesData.length === 0) {
              res.statusCode = 404
              res.setHeader('Content-Type', 'application/json')
              res.end(JSON.stringify({ 
                error: 'Geen data beschikbaar voor laatste 3 uur voor dit gemaal' 
              }))
              return
            }

            const result = {
              gemaalCode,
              series: [{
                name: series[0].name || 'Debiet',
                data: timeSeriesData
              }]
            }

            res.setHeader('Content-Type', 'application/json')
            res.setHeader('Access-Control-Allow-Origin', '*')
            res.end(JSON.stringify(result))
          } catch (error) {
            console.error('[Proxy] Fout bij ophalen gemaal data:', error)
            res.statusCode = 500
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify({ 
              error: error.message || 'Onbekende fout bij ophalen data' 
            }))
          }
        })
      }
    }
  ],
  // Voor GitHub Pages deployment
  base: process.env.GITHUB_PAGES === 'true' ? '/hhvr/' : '/simulatie-peilbeheer/',
  server: {
    fs: {
      allow: ['..']
    }
  }
})
