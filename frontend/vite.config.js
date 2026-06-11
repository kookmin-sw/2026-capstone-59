import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  // GitHub Pages 서브경로(/2026-capstone-59/landing/)에 정적 랜딩 배포용 base.
  // dev(npm run dev)에서는 base 기본값 '/'를 쓰도록 command 로 분기.
  base: process.env.BUILD_TARGET === 'landing' ? '/2026-capstone-59/landing/' : '/',
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/ai': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ai/, ''),
      },
    },
  },
})