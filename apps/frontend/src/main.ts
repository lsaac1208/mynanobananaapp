import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import { useAuthStore } from './stores/auth'
import { useTheme } from './composables/useTheme'

// 样式导入
import 'element-plus/dist/index.css'
// 设计系统 - Design Tokens & Utilities
import './styles/design-tokens.css'
import './styles/animations.css'
import './styles/utilities.css'
import './styles/glassmorphism.css'
import './styles/element-overrides.css' // Element Plus样式覆盖
import './styles/mobile-responsive.css' // 移动端响应式优化
import './styles/main.css'

// 移动端性能监控（仅开发环境）
import './utils/performance'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 初始化主题系统
const { initTheme } = useTheme()
initTheme()

// 初始化认证状态
const authStore = useAuthStore()
authStore.initAuth().then(() => {
  app.mount('#app')
})