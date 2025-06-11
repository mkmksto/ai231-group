import { svelte } from "@sveltejs/vite-plugin-svelte";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [svelte()],
  server: {
    proxy: {
      // "/api": "http://localhost:8000",
      "/api": "http://backend:8002",
    },
    allowedHosts: ["231group.207.148.67.31.sslip.io", "diag.miketest.site"],
  },
});
