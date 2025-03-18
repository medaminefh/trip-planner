import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // run the dev server on port 3000
  server: {
    port:
      3000
  },
  build: {
    outDir: 'dist', // Ensure this matches the directory being copied
    assetsDir: 'assets', // Default Vite assets directory
  },
  base: '/', // Ensure base URL is correct for deployment
})
