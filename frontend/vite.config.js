import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Proxy API calls to Django during development
    // so the browser always talks to localhost:5173 and we avoid CORS issues
    proxy: {
      "/api": {
        target: process.env.VITE_API_TARGET || "http://web:8000",
        changeOrigin: true,
      },
    },
  },
});
