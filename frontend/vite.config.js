import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// React is built into Flask's static folder, and Flask serves it.
// - base: the URL prefix Flask serves the built files from
// - outDir: where the compiled files are written (inside the Flask app)
export default defineConfig({
  plugins: [react()],
  base: '/static/dashboard/',
  build: {
    outDir: '../app/static/dashboard',
    emptyOutDir: true,
  },
  // Only used if you run "npm run dev" for hot-reload during development.
  server: {
    proxy: {
      '/api': 'http://localhost:5000',
      '/login': 'http://localhost:5000',
      '/logout': 'http://localhost:5000',
    },
  },
})
