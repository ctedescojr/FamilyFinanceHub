import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: '0.0.0.0', // Required for Docker container port mapping
    port: 5173,
    watch: {
      usePolling: true, // Helps with file change detection in some Docker setups
    },
  },
});
