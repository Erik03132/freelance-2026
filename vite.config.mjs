import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/freelance-2026/',
  build: {
    outDir: 'dist'
  }
})
