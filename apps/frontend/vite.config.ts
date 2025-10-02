import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
      imports: [
        'vue',
        'vue-router',
        'pinia'
      ],
      dts: true
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: true
    })
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@shared': resolve(__dirname, '../../packages/shared-types/src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    // 移动端性能优化：启用代码压缩和优化
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // 生产环境移除console
        drop_debugger: true
      }
    },
    // 代码分割优化
    rollupOptions: {
      output: {
        // 更细粒度的代码分割策略
        manualChunks: (id) => {
          // Element Plus 组件库单独分包
          if (id.includes('element-plus')) {
            return 'element-plus'
          }
          // Vue 核心库分包
          if (id.includes('vue') || id.includes('vue-router') || id.includes('pinia')) {
            return 'vue-vendor'
          }
          // Axios HTTP 客户端分包
          if (id.includes('axios')) {
            return 'axios'
          }
          // node_modules 中的其他依赖分包
          if (id.includes('node_modules')) {
            return 'vendor'
          }
        },
        // 优化资源文件命名
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: '[ext]/[name]-[hash].[ext]'
      }
    },
    // 块大小警告阈值（KB）
    chunkSizeWarningLimit: 1000,
    // 优化依赖预构建
    commonjsOptions: {
      transformMixedEsModules: true
    }
  },
  test: {
    environment: 'jsdom',
    globals: true
  }
})