import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// 获取环境变量
const API_URL = process.env.VITE_API_URL || "http://localhost:5000";

export default defineConfig({
  plugins: [vue()],
  base: "/",
  build: {
    rollupOptions: {
      output: {
        manualChunks: undefined,
      },
    },
  },
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/api": {
        target: API_URL,
        changeOrigin: true,
      },
    },
  },
});
