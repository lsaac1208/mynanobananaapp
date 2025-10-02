<template>
  <div class="dynamic-menu-wrapper">
    <!-- 用户功能菜单 -->
    <el-menu
      :default-active="currentRoute"
      :class="menuClass"
      router
      @select="handleSelect"
    >
      <el-menu-item
        v-for="item in userMenuItems"
        :key="item.path"
        :index="item.path"
      >
        <el-icon>
          <component :is="item.icon" />
        </el-icon>
        <span>{{ item.label }}</span>
      </el-menu-item>
    </el-menu>

    <!-- 管理员功能区域 -->
    <div v-if="authStore.isAdmin" :class="adminSectionClass">
      <el-divider content-position="center">
        <span class="section-title">
          <el-icon class="section-icon"><Star /></el-icon>
          管理员功能
        </span>
      </el-divider>
      <el-menu
        :default-active="currentRoute"
        :class="adminMenuClass"
        router
        @select="handleSelect"
      >
        <el-menu-item
          v-for="item in adminMenuItems"
          :key="item.path"
          :index="item.path"
          class="admin-menu-item"
        >
          <el-icon>
            <component :is="item.icon" />
          </el-icon>
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  EditPen,
  FolderOpened,
  User,
  DataAnalysis,
  UserFilled,
  Setting,
  Star
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

interface MenuItem {
  path: string
  label: string
  icon: any
  roles?: string[]
}

interface Props {
  isMobile?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isMobile: false
})

const emit = defineEmits<{
  (e: 'select', index: string): void
}>()

const route = useRoute()
const authStore = useAuthStore()

// 当前路由
const currentRoute = computed(() => route.path)

// 用户菜单项配置
const userMenuItems = computed<MenuItem[]>(() => [
  {
    path: '/app',
    label: 'AI生成',
    icon: EditPen
  },
  {
    path: '/app/gallery',
    label: '我的画廊',
    icon: FolderOpened
  },
  {
    path: '/app/profile',
    label: '个人中心',
    icon: User
  }
])

// 管理员菜单项配置
const adminMenuItems = computed<MenuItem[]>(() => [
  {
    path: '/admin',
    label: '数据仪表板',
    icon: DataAnalysis,
    roles: ['admin']
  },
  {
    path: '/admin/users',
    label: '用户管理',
    icon: UserFilled,
    roles: ['admin']
  },
  {
    path: '/admin/settings',
    label: '系统设置',
    icon: Setting,
    roles: ['admin']
  }
])

// 动态CSS类
const menuClass = computed(() => {
  return props.isMobile ? 'mobile-menu' : 'desktop-menu'
})

const adminSectionClass = computed(() => {
  return props.isMobile ? 'mobile-admin-section' : 'desktop-admin-section'
})

const adminMenuClass = computed(() => {
  return props.isMobile ? 'mobile-admin-menu' : 'desktop-admin-menu'
})

// 处理菜单选择
const handleSelect = (index: string) => {
  emit('select', index)
}
</script>

<style scoped>
.dynamic-menu-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 桌面端菜单样式 */
.desktop-menu {
  border-right: none;
  padding: 16px 0;
  flex: 1;
}

.desktop-menu :deep(.el-menu-item) {
  margin: 4px 12px;
  border-radius: 8px;
  height: 48px;
  line-height: 48px;
  display: flex;
  align-items: center;
}

.desktop-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.desktop-menu :deep(.el-menu-item:hover) {
  background-color: #f0f2f5;
}

.desktop-menu :deep(.el-menu-item.is-active:hover) {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}

.desktop-menu :deep(.el-menu-item .el-icon) {
  margin-right: 8px;
  font-size: 18px;
}

/* 移动端菜单样式 */
.mobile-menu {
  border-right: none;
  padding: 16px 0;
  flex: 1;
}

.mobile-menu :deep(.el-menu-item) {
  margin: 4px 12px;
  border-radius: 8px;
  height: 48px;
  line-height: 48px;
  display: flex;
  align-items: center;
}

.mobile-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.mobile-menu :deep(.el-menu-item:hover) {
  background-color: #f0f2f5;
}

.mobile-menu :deep(.el-menu-item .el-icon) {
  margin-right: 8px;
  font-size: 18px;
}

/* 管理员区域 - 桌面端 */
.desktop-admin-section {
  margin-top: auto;
  padding: 16px 0 20px;
  border-top: 1px solid #f0f2f5;
}

.desktop-admin-section .section-title {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.desktop-admin-section .section-icon {
  font-size: 14px;
  color: #67c23a;
}

.desktop-admin-menu {
  border-right: none;
  padding: 8px 0 0;
}

.desktop-admin-menu :deep(.el-menu-item) {
  margin: 4px 12px;
  border-radius: 8px;
  height: 48px;
  line-height: 48px;
}

.desktop-admin-menu :deep(.el-menu-item.admin-menu-item) {
  color: #67c23a;
}

.desktop-admin-menu :deep(.el-menu-item.admin-menu-item.is-active) {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  color: white;
}

.desktop-admin-menu :deep(.el-menu-item:hover) {
  background-color: #f0f9ff;
}

.desktop-admin-menu :deep(.el-menu-item.admin-menu-item.is-active:hover) {
  background: linear-gradient(135deg, #5eb830 0%, #7bc257 100%);
}

.desktop-admin-menu :deep(.el-menu-item .el-icon) {
  margin-right: 8px;
  font-size: 18px;
}

/* 管理员区域 - 移动端 */
.mobile-admin-section {
  margin-top: auto;
  padding: 16px 0 20px;
  border-top: 1px solid #f0f2f5;
}

.mobile-admin-section .section-title {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.mobile-admin-section .section-icon {
  font-size: 14px;
  color: #67c23a;
}

.mobile-admin-menu {
  border-right: none;
  padding: 8px 0 0;
}

.mobile-admin-menu :deep(.el-menu-item) {
  margin: 4px 12px;
  border-radius: 8px;
  height: 48px;
  line-height: 48px;
}

.mobile-admin-menu :deep(.el-menu-item.admin-menu-item) {
  color: #67c23a;
}

.mobile-admin-menu :deep(.el-menu-item.admin-menu-item.is-active) {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  color: white;
}

.mobile-admin-menu :deep(.el-menu-item:hover) {
  background-color: #f0f9ff;
}

.mobile-admin-menu :deep(.el-menu-item .el-icon) {
  margin-right: 8px;
  font-size: 18px;
}
</style>