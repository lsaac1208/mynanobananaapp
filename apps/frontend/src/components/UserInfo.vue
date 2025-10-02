<template>
  <div class="user-info">
    <div v-if="authStore.isLoggedIn" class="user-profile">
      <div class="user-avatar">
        <el-avatar :size="40" src="" :icon="UserFilled" />
      </div>
      <div class="user-details">
        <div class="user-email">{{ authStore.user?.email }}</div>
        <div class="user-credits">
          <el-icon class="credits-icon"><CoinIcon /></el-icon>
          <span>剩余次数: {{ authStore.user?.credits || 0 }}</span>
        </div>
      </div>
      <div class="user-actions">
        <el-dropdown trigger="click" @command="handleCommand">
          <el-button type="text" :icon="Setting" circle />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item command="gallery">我的画廊</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <div v-else class="login-prompt">
      <el-button type="primary" @click="goToLogin">登录 / 注册</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UserFilled, Setting, Coin as CoinIcon } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 导航到登录页
const goToLogin = () => {
  router.push('/login')
}

// 处理下拉菜单命令
const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/app/profile')
      break

    case 'gallery':
      router.push('/app/gallery')
      break

    case 'logout':
      try {
        await ElMessageBox.confirm(
          '确定要退出登录吗？',
          '确认退出',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        await authStore.logout()
        ElMessage.success('已成功退出登录')
        router.push('/login')
      } catch (error) {
        // 用户取消操作
      }
      break
  }
}
</script>

<style scoped>
.user-info {
  display: flex;
  align-items: center;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.user-avatar {
  flex-shrink: 0;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-email {
  font-size: 14px;
  font-weight: 500;
  color: #2c3e50;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
}

.user-credits {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #6c757d;
  margin-top: 2px;
}

.credits-icon {
  color: #f39c12;
  font-size: 14px;
}

.user-actions {
  flex-shrink: 0;
}

.login-prompt {
  padding: 8px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-profile {
    padding: 6px 12px;
    gap: 8px;
  }

  .user-email {
    max-width: 120px;
    font-size: 13px;
  }

  .user-credits {
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .user-email {
    max-width: 100px;
  }

  .user-profile {
    padding: 4px 8px;
  }
}
</style>