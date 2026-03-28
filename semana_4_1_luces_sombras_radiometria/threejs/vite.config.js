import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules/three') || id.includes('node_modules/@react-three')) {
            return 'three-vendor'
          }

          if (id.includes('node_modules/react')) {
            return 'react-vendor'
          }

          if (id.includes('node_modules/leva')) {
            return 'ui-vendor'
          }
        },
      },
    },
  },
})
