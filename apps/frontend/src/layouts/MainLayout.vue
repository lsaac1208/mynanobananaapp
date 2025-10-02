<template>
  <div class="main-layout">
    <!-- 顶部导航栏 -->
    <el-header class="main-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="app-title">
            <el-icon class="title-icon"><PictureFilled /></el-icon>
            Nano-Banana AI
          </h1>
        </div>
        <div class="header-right">
          <UserInfo />
        </div>
      </div>
    </el-header>

    <!-- 主内容区域 -->
    <el-container class="main-container">
      <!-- 侧边栏导航 -->
      <el-aside class="main-sidebar" :width="sidebarWidth">
        <!-- 移动端菜单按钮 -->
        <div class="mobile-menu-toggle" @click="toggleMobileSidebar">
          <el-icon><Menu /></el-icon>
        </div>

        <!-- 移动端侧边栏抽屉 -->
        <el-drawer
          v-model="mobileSidebarVisible"
          :with-header="false"
          direction="ltr"
          size="280px"
          class="mobile-sidebar-drawer"
        >
          <div class="mobile-sidebar-content">
            <div class="mobile-sidebar-header">
              <h2 class="mobile-app-title">
                <el-icon class="title-icon"><PictureFilled /></el-icon>
                Nano-Banana AI
              </h2>
            </div>

            <!-- 动态菜单组件 - 移动端 -->
            <DynamicMenu
              :is-mobile="true"
              @select="handleMobileMenuSelect"
            />
          </div>
        </el-drawer>

        <!-- 桌面端侧边栏 -->
        <div class="desktop-sidebar-content" v-show="!isMobile">
          <!-- 动态菜单组件 - 桌面端 -->
          <DynamicMenu
            :is-mobile="false"
            @select="handleMenuSelect"
          />
        </div>
      </el-aside>

      <!-- 主内容 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>

    <!-- 移动端底部标签栏导航 -->
    <div v-if="isMobile && showBottomTabbar" class="mobile-bottom-tabbar">
      <div
        v-for="tab in bottomTabs"
        :key="tab.path"
        class="tabbar-item"
        :class="{ active: isActiveTab(tab.path) }"
        @click="navigateTo(tab.path)"
      >
        <el-icon class="tabbar-icon">
          <component :is="tab.icon" />
        </el-icon>
        <span class="tabbar-label">{{ tab.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { PictureFilled, EditPen, FolderOpened, User, Menu } from '@element-plus/icons-vue'
import UserInfo from '@/components/UserInfo.vue'
import DynamicMenu from '@/components/DynamicMenu.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 移动端响应式状态
const isMobile = ref(false)
const mobileSidebarVisible = ref(false)

// 当前路由
const currentRoute = computed(() => route.path)

// 响应式侧边栏宽度
const sidebarWidth = computed(() => {
  return isMobile.value ? '0px' : '240px'
})

// 底部标签栏配置
const bottomTabs = computed(() => {
  const userTabs = [
    { path: '/app', icon: EditPen, label: 'AI生成' },
    { path: '/app/gallery', icon: FolderOpened, label: '画廊' },
    { path: '/app/profile', icon: User, label: '我的' }
  ]
  return userTabs
})

// 是否显示底部标签栏
const showBottomTabbar = computed(() => {
  // 非管理员页面显示底部标签栏
  return !route.path.startsWith('/admin')
})

// 检查是否为活跃标签
const isActiveTab = (path: string) => {
  return route.path === path || route.path.startsWith(path + '/')
}

// 检测屏幕大小
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
  // 桌面端时关闭移动端抽屉
  if (!isMobile.value) {
    mobileSidebarVisible.value = false
  }
}

// 切换移动端侧边栏
const toggleMobileSidebar = () => {
  mobileSidebarVisible.value = !mobileSidebarVisible.value
}

// 处理菜单选择
const handleMenuSelect = (index: string) => {
  router.push(index)
}

// 底部标签栏导航
const navigateTo = (path: string) => {
  router.push(path)
}

// 处理移动端菜单选择
const handleMobileMenuSelect = (index: string) => {
  router.push(index)
  // 选择后关闭抽屉
  mobileSidebarVisible.value = false
}

// 生命周期钩子
onMounted(async () => {
  // 初始化认证状态
  if (!authStore.isLoggedIn) {
    await authStore.initAuth()
    if (!authStore.isLoggedIn) {
      router.push('/login')
    }
  }

  // 初始化响应式检测
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.main-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  height: 64px;
  padding: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.app-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: white;
}

.title-icon {
  font-size: 24px;
  color: #ffd700;
}

.header-right {
  display: flex;
  align-items: center;
}

.main-container {
  height: calc(100vh - 64px);
}

.main-sidebar {
  background: white;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.main-content {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}

/* 移动端菜单按钮 */
.mobile-menu-toggle {
  display: none;
  position: fixed;
  top: 16px;
  left: 16px;
  z-index: 1001;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  padding: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.mobile-menu-toggle:hover {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.mobile-menu-toggle .el-icon {
  font-size: 20px;
  color: #409eff;
}

/* 移动端抽屉样式 */
.mobile-sidebar-drawer {
  z-index: 1000;
}

.mobile-sidebar-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
}

.mobile-sidebar-header {
  padding: 20px 16px 16px;
  border-bottom: 1px solid #ebeef5;
}

.mobile-app-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

/* 桌面端侧边栏 */
.desktop-sidebar-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 移动端底部标签栏导航 */
.mobile-bottom-tabbar {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: white;
  border-top: 1px solid #ebeef5;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.06);
  z-index: 1000;
  padding: 0 env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left);
}

.tabbar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.tabbar-item:active {
  background: rgba(64, 158, 255, 0.05);
}

.tabbar-icon {
  font-size: 22px;
  color: #909399;
  transition: all 0.3s ease;
}

.tabbar-label {
  font-size: 11px;
  color: #909399;
  font-weight: 500;
  transition: all 0.3s ease;
}

.tabbar-item.active .tabbar-icon {
  color: #409eff;
  transform: scale(1.1);
}

.tabbar-item.active .tabbar-label {
  color: #409eff;
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 768px) {
  /* 隐藏汉堡菜单按钮 - 使用底部标签栏代替 */
  .mobile-menu-toggle {
    display: none !important;
  }

  /* 显示底部标签栏 */
  .mobile-bottom-tabbar {
    display: flex;
  }

  /* 调整内容区域底部间距，为标签栏留出空间 */
  .main-content {
    padding-bottom: calc(60px + env(safe-area-inset-bottom)) !important;
  }

  .header-content {
    padding: 0 16px;
  }

  .app-title {
    font-size: 18px;
  }

  .main-content {
    padding: 16px;
  }

  /* 移动端时隐藏桌面侧边栏 */
  .desktop-sidebar-content {
    display: none;
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 0 50px 0 12px;
  }

  .app-title {
    font-size: 16px;
  }

  .main-content {
    padding: 12px;
  }

  .mobile-sidebar-header {
    padding: 16px 12px 12px;
  }

  .mobile-app-title {
    font-size: 16px;
  }
}
</style>