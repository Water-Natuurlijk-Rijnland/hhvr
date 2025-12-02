import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { readFileSync, existsSync } from 'fs'
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
    }
  ],
  // Voor GitHub Pages: gebruik repository naam als base URL
  // Repository: Water-Natuurlijk-Rijnland/hhvr -> base URL is /hhvr/
  base: process.env.GITHUB_PAGES === 'true' ? '/hhvr/' : '/simulatie-peilbeheer/',
  server: {
    fs: {
      allow: ['..']
    }
  }
})
