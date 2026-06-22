import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  root: './', // Явно указываем корень
  server: {
    port: 3000,
    fs: {
      strict: true,
      allow: ['..'] // Ограничиваем доступ только текущей папкой и выше по необходимости, но аккуратно
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  }
})
