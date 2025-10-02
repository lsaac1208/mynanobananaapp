<template>
  <el-container class="admin-layout">
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
          <h2 class="mobile-admin-title">
            <el-icon class="title-icon"><Setting /></el-icon>
            管理员面板
          </h2>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="mobile-admin-menu"
          @select="handleMobileMenuSelect"
          router
        >
          <el-menu-item index="/admin">
            <el-icon><Odometer /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/settings">
            <el-icon><Tools /></el-icon>
            <span>系统设置</span>
          </el-menu-item>
        </el-menu>
      </div>
    </el-drawer>

    <!-- 桌面端管理员侧边栏 -->
    <el-aside width="240px" class="admin-sidebar desktop-sidebar">
      <div class="sidebar-header">
        <h2>管理员面板</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="admin-menu"
        @select="handleMenuSelect"
        router
      >
        <el-menu-item index="/admin">
          <el-icon><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/settings">
          <el-icon><Tools /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 管理员主内容区 -->
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header class="admin-header">
        <div class="header-left">
          <h1 class="page-title">{{ pageTitle }}</h1>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-dropdown">
              <el-avatar :size="32" class="user-avatar">
                {{ userStore.user?.email?.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="user-name">{{ userStore.user?.email }}</span>
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="app">
                  <el-icon><House /></el-icon>
                  返回应用
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主要内容区域 -->
      <el-main class="admin-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import {
  Odometer,
  User,
  House,
  SwitchButton,
  ArrowDown,
  Menu,
  Setting,
  Tools
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useAuthStore()

// 移动端响应式状态
const isMobile = ref(false)
const mobileSidebarVisible = ref(false)

// 计算当前激活的菜单项
const activeMenu = computed(() => {
  return route.path
})

// 计算页面标题
const pageTitle = computed(() => {
  switch (route.name) {
    case 'AdminDashboard':
      return '仪表盘'
    case 'AdminUsers':
      return '用户管理'
    default:
      return '管理员面板'
  }
})

// 处理菜单选择
const handleMenuSelect = (index: string) => {
  if (index !== route.path) {
    router.push(index)
  }
}

// 处理下拉菜单命令
const handleCommand = (command: string) => {
  switch (command) {
    case 'app':
      router.push('/app')
      break
    case 'logout':
      userStore.logout()
      router.push('/login')
      ElMessage.success('已退出登录')
      break
  }
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

// 处理移动端菜单选择
const handleMobileMenuSelect = (index: string) => {
  if (index !== route.path) {
    router.push(index)
  }
  // 选择后关闭抽屉
  mobileSidebarVisible.value = false
}

// 生命周期钩子
onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.admin-layout {
  height: 100vh;
  background-color: #f5f5f5;
}

.admin-sidebar {
  background: #fff;
  border-right: 1px solid #e6e6e6;
  box-shadow: 2px 0 6px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e6e6e6;
  background: #fafafa;
}

.sidebar-header h2 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.admin-menu {
  border-right: none;
}

.admin-menu .el-menu-item {
  border-radius: 0;
  margin: 0 8px;
  border-radius: 6px;
}

.admin-menu .el-menu-item:hover {
  background-color: #f0f9ff;
  color: #409eff;
}

.admin-menu .el-menu-item.is-active {
  background-color: #ecf5ff;
  color: #409eff;
  font-weight: 600;
}

.admin-header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header-left .page-title {
  margin: 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.user-dropdown:hover {
  background-color: #f0f9ff;
}

.user-avatar {
  margin-right: 8px;
  background-color: #409eff;
  color: white;
  font-weight: 600;
}

.user-name {
  color: #606266;
  font-size: 14px;
  margin-right: 4px;
}

.admin-main {
  padding: 20px;
  background-color: #f5f5f5;
  overflow-y: auto;
}

/* 移动端菜单按钮 */
.mobile-menu-toggle {
  display: none;
  position: fixed;
  top: 16px;
  left: 16px;
  z-index: 1001;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  padding: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.mobile-menu-toggle:hover {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
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
  background: #f8f9fa;
  padding: 0;
}

.mobile-sidebar-header {
  padding: 20px 16px 16px;
  border-bottom: 1px solid #e4e7ed;
  background: white;
}

.mobile-admin-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.mobile-admin-title .title-icon {
  font-size: 20px;
  color: #67c23a;
}

.mobile-admin-menu {
  flex: 1;
  border-right: none;
  background: transparent;
  padding: 16px 0;
}

.mobile-admin-menu .el-menu-item {
  margin: 4px 12px;
  border-radius: 8px;
  height: 48px;
  line-height: 48px;
  font-size: 15px;
  color: #606266;
  transition: all 0.3s ease;
}

.mobile-admin-menu .el-menu-item:hover {
  background-color: #f0f9ff;
  color: #409eff;
}

.mobile-admin-menu .el-menu-item.is-active {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  color: white;
  font-weight: 600;
}

.mobile-admin-menu .el-menu-item .el-icon {
  margin-right: 8px;
  font-size: 18px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .mobile-menu-toggle {
    display: block;
  }

  .admin-layout {
    padding-top: 0;
  }

  .admin-header {
    padding: 0 60px 0 16px;
  }

  .header-left .page-title {
    font-size: 18px;
  }

  .user-dropdown {
    padding: 6px 10px;
  }

  .user-name {
    display: none; /* 移动端隐藏用户名，只显示头像 */
  }

  .desktop-sidebar {
    display: none; /* 移动端隐藏桌面端侧边栏 */
  }

  .admin-main {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .mobile-menu-toggle {
    top: 12px;
    left: 12px;
    padding: 6px;
  }

  .mobile-menu-toggle .el-icon {
    font-size: 18px;
  }

  .admin-header {
    padding: 0 50px 0 12px;
  }

  .header-left .page-title {
    font-size: 16px;
  }

  .user-dropdown {
    padding: 4px 8px;
  }

  .user-avatar {
    width: 28px !important;
    height: 28px !important;
    font-size: 12px;
  }

  .admin-main {
    padding: 12px;
  }

  .mobile-sidebar-header {
    padding: 16px 12px 12px;
  }

  .mobile-admin-title {
    font-size: 16px;
  }

  .mobile-admin-menu .el-menu-item {
    margin: 3px 8px;
    height: 44px;
    line-height: 44px;
    font-size: 14px;
  }
}

@media (max-width: 360px) {
  .admin-header {
    padding: 0 48px 0 10px;
  }

  .header-left .page-title {
    font-size: 15px;
  }

  .admin-main {
    padding: 10px;
  }

  .mobile-admin-menu .el-menu-item {
    height: 42px;
    line-height: 42px;
    font-size: 13px;
    margin: 2px 6px;
  }
}

/* 横屏模式优化 */
@media (max-height: 600px) and (orientation: landscape) {
  .mobile-menu-toggle {
    top: 8px;
    left: 8px;
  }

  .admin-header {
    height: 50px;
    min-height: 50px;
  }

  .admin-main {
    padding: 8px 12px;
  }

  .mobile-sidebar-header {
    padding: 12px;
  }

  .mobile-admin-title {
    font-size: 16px;
  }

  .mobile-admin-menu .el-menu-item {
    height: 40px;
    line-height: 40px;
  }
}

/* 触摸优化 */
.mobile-menu-toggle,
.mobile-admin-menu .el-menu-item,
.user-dropdown {
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}
</style>