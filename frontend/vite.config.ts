import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Cho phép hostname Tailscale (Vite mặc định chặn host lạ).
    allowedHosts: ['.ts.net'],
    // Dev: chuyển /api sang backend localhost, để trình duyệt chỉ nói chuyện
    // với một origin (không cần CORS, backend không phải mở ra LAN).
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  preview: {
    allowedHosts: ['.ts.net'],
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
