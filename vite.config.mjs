import {resolve } from 'path'
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  base: "/static/",
  
  resolve: {
    alias: {
        '@': resolve('./static'),
    }},
  build: {
    manifest: "manifest.json",
    cssCodeSplit: false,
    outDir: resolve("./assets"),
    assetsDir: "django-assets",
    rollupOptions: {
      input: {
        test: resolve("./static/js/main.js"),
      }
    }
  },
  plugins:  [ tailwindcss()]
})
