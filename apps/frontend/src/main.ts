import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import { useAuthStore } from './stores/auth'

// 样式导入
import 'element-plus/dist/index.css'
import './styles/main.css'

// 移动端性能监控（仅开发环境）
import './utils/performance'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 初始化认证状态
const authStore = useAuthStore()
authStore.initAuth().then(() => {
  app.mount('#app')
})