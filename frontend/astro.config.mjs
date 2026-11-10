import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  output: 'static',
  vite: {
    plugins: [tailwindcss()],
    // Keep dashboard scripts external for the local server's self-only CSP.
    build: { assetsInlineLimit: 0 },
  },
});
