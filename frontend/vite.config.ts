import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig(() => {
  const isAppwriteBuild = process.env.APPWRITE_BUILD === 'true'

  return {
    plugins: [
      react(),
      tailwindcss(),
    ],
    build: {
      // Appwrite build containers can be CPU/memory constrained.
      // Disable minification/compressed-size reporting there to reduce
      // build pressure and make deployments more reliable.
      minify: isAppwriteBuild ? false : 'esbuild',
      cssMinify: !isAppwriteBuild,
      reportCompressedSize: !isAppwriteBuild,
    },
  }
})

