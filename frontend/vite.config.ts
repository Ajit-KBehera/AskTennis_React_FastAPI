import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig(() => {
  const isAppwriteBuild = process.env.APPWRITE_BUILD === 'true'

  return {
    // This ensures assets are linked relatively, crucial for Appwrite hosting
    base: './', 
    plugins: [
      react(),
      tailwindcss(),
    ],
    build: {
      // Explicitly set the output directory to match your Appwrite settings
      outDir: 'dist',
      // Keep your optimizations
      minify: isAppwriteBuild ? false : 'esbuild',
      cssMinify: !isAppwriteBuild,
      reportCompressedSize: !isAppwriteBuild,
      // Optional: Helps if the build is still timing out
      sourcemap: false, 
    },
  }
})