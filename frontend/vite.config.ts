import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: '0.0.0.0', // Required for Docker container port mapping
    port: 5173,
    // Removed `watch: { usePolling: true }` because Linux natively supports file system events (inotify) without high CPU overhead.
  },
});
