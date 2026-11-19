import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// 개발 서버(5173)에서 /api 요청을 Spring(8080)으로 넘김 → 브라우저 입장에서는 같은 주소라 CORS 문제가 없음
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // 프로젝트가 /mnt/c(Windows 디스크)에 있으면 WSL에서 파일 변경 감지가 안 되므로 주기적으로 확인
    watch: { usePolling: true, interval: 500 },
    proxy: {
      '/api': 'http://localhost:8080',
    },
  },
})
