<template>
  <div class="app-layout">
    <!-- 顶部导航栏 -->
    <el-header class="app-header">
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
      <el-aside class="app-sidebar" :width="sidebarWidth">
        <!-- 移动端菜单按钮 -->
        <div class="mobile-menu-toggle" @click="toggleMobileSidebar">
          <el-icon><Menu /></el-icon>
        </div>

        <!-- 侧边栏抽屉 (移动端) -->
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
            <el-menu
              :default-active="currentRoute"
              class="mobile-sidebar-menu"
              router
              @select="handleMobileMenuSelect"
            >
              <el-menu-item index="/app">
                <el-icon><EditPen /></el-icon>
                <span>AI生成</span>
              </el-menu-item>
              <el-menu-item index="/app/gallery">
                <el-icon><FolderOpened /></el-icon>
                <span>我的画廊</span>
              </el-menu-item>
              <el-menu-item index="/app/profile">
                <el-icon><User /></el-icon>
                <span>个人中心</span>
              </el-menu-item>
            </el-menu>

            <!-- 管理员区域 -->
            <div class="mobile-admin-section" v-if="authStore.user?.id === 1">
              <el-divider content-position="center">
                <span class="section-title">管理员</span>
              </el-divider>
              <el-menu
                :default-active="currentRoute"
                class="mobile-admin-menu"
                router
                @select="handleMobileMenuSelect"
              >
                <el-menu-item index="/admin" class="admin-menu-item">
                  <el-icon><DataAnalysis /></el-icon>
                  <span>数据仪表板</span>
                </el-menu-item>
              </el-menu>
            </div>
          </div>
        </el-drawer>

        <!-- 桌面端侧边栏 -->
        <div class="desktop-sidebar-content" v-show="!isMobile">
          <el-menu
            :default-active="currentRoute"
            class="sidebar-menu"
            router
            @select="handleMenuSelect"
          >
            <el-menu-item index="/app">
              <el-icon><EditPen /></el-icon>
              <span>AI生成</span>
            </el-menu-item>
            <el-menu-item index="/app/gallery">
              <el-icon><FolderOpened /></el-icon>
              <span>我的画廊</span>
            </el-menu-item>
            <el-menu-item index="/app/profile">
              <el-icon><User /></el-icon>
              <span>个人中心</span>
            </el-menu-item>
          </el-menu>

          <!-- 管理员区域 -->
          <div class="admin-section" v-if="authStore.user?.id === 1">
            <el-divider content-position="center">
              <span class="section-title">管理员</span>
            </el-divider>
            <el-menu
              :default-active="currentRoute"
              class="admin-menu"
              router
              @select="handleMenuSelect"
            >
              <el-menu-item index="/admin" class="admin-menu-item">
                <el-icon><DataAnalysis /></el-icon>
                <span>数据仪表板</span>
              </el-menu-item>
            </el-menu>
          </div>
        </div>
      </el-aside>

      <!-- 主内容 -->
      <el-main class="app-content">
        <router-view />
      </el-main>
    </el-container>

    <!-- 移动端底部标签栏导航 -->
    <div v-if="isMobile" class="mobile-bottom-tabbar">
      <div
        class="tabbar-item"
        :class="{ active: currentRoute === '/app' }"
        @click="navigateTo('/app')"
      >
        <el-icon class="tabbar-icon"><EditPen /></el-icon>
        <span class="tabbar-label">AI生成</span>
      </div>
      <div
        class="tabbar-item"
        :class="{ active: currentRoute === '/app/gallery' }"
        @click="navigateTo('/app/gallery')"
      >
        <el-icon class="tabbar-icon"><FolderOpened /></el-icon>
        <span class="tabbar-label">画廊</span>
      </div>
      <div
        class="tabbar-item"
        :class="{ active: currentRoute === '/app/profile' }"
        @click="navigateTo('/app/profile')"
      >
        <el-icon class="tabbar-icon"><User /></el-icon>
        <span class="tabbar-label">我的</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { PictureFilled, EditPen, FolderOpened, User, Menu, DataAnalysis } from '@element-plus/icons-vue'
import UserInfo from '@/components/UserInfo.vue'
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
.app-layout {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.app-header {
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

.app-sidebar {
  background: white;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.sidebar-menu {
  border-right: none;
  padding: 16px 0;
}

:deep(.el-menu-item) {
  margin: 4px 12px;
  border-radius: 8px;
  height: 48px;
  line-height: 48px;
  display: flex;
  align-items: center;
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

:deep(.el-menu-item:hover) {
  background-color: #f0f2f5;
}

:deep(.el-menu-item.is-active:hover) {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}

:deep(.el-menu-item .el-icon) {
  margin-right: 8px;
  font-size: 18px;
}

.app-content {
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

.mobile-sidebar-menu,
.mobile-admin-menu {
  border-right: none;
  flex: 1;
}

.mobile-sidebar-menu {
  padding: 16px 0;
}

.mobile-admin-section {
  margin-top: auto;
  padding: 16px 0 20px;
  border-top: 1px solid #f0f2f5;
}

.mobile-admin-section .section-title {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.mobile-admin-menu {
  padding: 8px 0 0;
}

/* 桌面端侧边栏 */
.desktop-sidebar-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.admin-section {
  margin-top: auto;
  padding: 16px 0 20px;
  border-top: 1px solid #f0f2f5;
}

.admin-section .section-title {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.admin-menu {
  padding: 8px 0 0;
}

.admin-menu-item {
  color: #67c23a !important;
}

.admin-menu-item.is-active {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%) !important;
  color: white !important;
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
  .app-content {
    padding-bottom: calc(60px + env(safe-area-inset-bottom)) !important;
  }

  .header-content {
    padding: 0 16px;
  }

  .app-title {
    font-size: 18px;
  }

  .app-content {
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

  .app-content {
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