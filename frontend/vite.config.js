import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  // Load env file from the current directory
  const env = loadEnv(mode, process.cwd(), '')
  const backendTarget = env.VITE_BACKEND_TARGET || 'http://localhost:8000'

  return {
    plugins: [react()],
    server: {
      port: 5173,
      host: true, // Needed for Docker access
      proxy: {
        '/api': {
          target: backendTarget,
          changeOrigin: true
        }
      }
    }
  }
})
