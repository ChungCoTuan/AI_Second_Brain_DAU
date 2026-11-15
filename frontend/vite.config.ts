import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Cho phép hostname Tailscale (Vite mặc định chặn host lạ).
    allowedHosts: ['.ts.net'],
    // Bind mọi interface để Tailscale Funnel (và Cloudflare Tunnel) proxy tới được.
    // Mặc định Vite chỉ listen trên ::1/127.0.0.1 nên bị 502 khi public ra ngoài.
    host: '0.0.0.0',
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
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
