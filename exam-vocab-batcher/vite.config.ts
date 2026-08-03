import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

const appBase = process.env.VITE_BASE_PATH ?? '/'

export default defineConfig({
  base: appBase,
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico'],
      manifest: {
        name: '會考單字練習',
        short_name: '會考單字',
        description: '國中會考英文單字練習 App',
        theme_color: '#3c83f6',
        background_color: '#f5f7f8',
        display: 'standalone',
        orientation: 'portrait',
        start_url: appBase,
        scope: appBase,
        icons: [
          { src: 'icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,json}'],
        navigateFallbackDenylist: [/^\/__\/auth\//, /^\/__\/firebase\//],
        runtimeCaching: [
          {
            urlPattern: /\/data\/vocab\.cleaned\.json$/,
            handler: 'CacheFirst',
            options: { cacheName: 'vocab-data' },
          },
        ],
      },
    }),
  ],
})
