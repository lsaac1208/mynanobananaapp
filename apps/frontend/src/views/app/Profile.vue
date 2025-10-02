<template>
  <div class="profile-container">
    <!-- 现代化头像区域 - 渐变背景卡片 -->
    <div class="profile-header-card">
      <div class="gradient-background"></div>
      <div class="header-content">
        <div class="avatar-wrapper">
          <el-avatar :size="100" class="user-avatar">
            <el-icon :size="50"><User /></el-icon>
          </el-avatar>
          <div class="avatar-ring"></div>
        </div>
        <div class="user-basic-info">
          <h2 class="user-email">{{ userStore.user?.email || '未设置' }}</h2>
          <div class="credits-badge">
            <el-icon class="credits-icon"><Trophy /></el-icon>
            <span class="credits-number">{{ userStore.user?.credits || 0 }}</span>
            <span class="credits-text">次可用</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 用户详细信息卡片 -->
    <el-card class="user-details-card" shadow="hover">
      <div class="detail-item">
        <div class="detail-icon">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="detail-content">
          <div class="detail-label">注册时间</div>
          <div class="detail-value">{{ formatDate(userStore.user?.created_at) }}</div>
        </div>
      </div>

      <div class="detail-item">
        <div class="detail-icon">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="detail-content">
          <div class="detail-label">最后登录</div>
          <div class="detail-value">{{ formatDate(userStore.user?.last_login_at) }}</div>
        </div>
      </div>
    </el-card>

    <!-- 账户操作卡片 - 卡片式面板 -->
    <el-card class="actions-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon"><Setting /></el-icon>
          <span>账户操作</span>
        </div>
      </template>

      <div class="actions-grid">
        <!-- 刷新信息 -->
        <div class="action-item" @click="refreshUserInfo" :class="{ loading: refreshing }">
          <div class="action-icon refresh-icon">
            <el-icon><Refresh /></el-icon>
          </div>
          <div class="action-content">
            <div class="action-title">刷新信息</div>
            <div class="action-desc">更新账户数据</div>
          </div>
        </div>

        <!-- 修改密码 -->
        <div class="action-item" @click="showChangePasswordDialog">
          <div class="action-icon password-icon">
            <el-icon><Lock /></el-icon>
          </div>
          <div class="action-content">
            <div class="action-title">修改密码</div>
            <div class="action-desc">安全设置</div>
          </div>
        </div>

        <!-- 退出登录 -->
        <div class="action-item" @click="handleLogout">
          <div class="action-icon logout-icon">
            <el-icon><SwitchButton /></el-icon>
          </div>
          <div class="action-content">
            <div class="action-title">退出登录</div>
            <div class="action-desc">安全退出</div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 使用统计卡片 -->
    <el-card class="stats-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon"><DataLine /></el-icon>
          <span>使用统计</span>
        </div>
      </template>

      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-icon">
            <el-icon><PictureFilled /></el-icon>
          </div>
          <div class="stat-number">{{ stats.totalGenerations }}</div>
          <div class="stat-label">总生成次数</div>
        </div>

        <div class="stat-item">
          <div class="stat-icon">
            <el-icon><Calendar /></el-icon>
          </div>
          <div class="stat-number">{{ stats.thisMonthGenerations }}</div>
          <div class="stat-label">本月生成</div>
        </div>

        <div class="stat-item">
          <div class="stat-icon">
            <el-icon><Star /></el-icon>
          </div>
          <div class="stat-number">{{ stats.favoriteModel }}</div>
          <div class="stat-label">常用模型</div>
        </div>

        <div class="stat-item">
          <div class="stat-icon">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="stat-number">{{ stats.averageGenerationTime }}s</div>
          <div class="stat-label">平均生成时间</div>
        </div>
      </div>
    </el-card>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="changePasswordVisible" title="修改密码" width="400px">
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="当前密码" prop="currentPassword">
          <el-input
            v-model="passwordForm.currentPassword"
            type="password"
            placeholder="请输入当前密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            placeholder="请确认新密码"
            show-password
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="changePasswordVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="changingPassword"
            @click="handleChangePassword"
          >
            确认修改
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  User, Refresh, Lock, SwitchButton, Trophy, Calendar, Clock,
  Setting, DataLine, PictureFilled, Star, Timer
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { galleryApi } from '@/services/api'

const router = useRouter()
const userStore = useAuthStore()

// 响应式数据
const refreshing = ref(false)
const changePasswordVisible = ref(false)
const changingPassword = ref(false)

// 使用统计数据
const stats = reactive({
  totalGenerations: 0,
  thisMonthGenerations: 0,
  favoriteModel: 'nano-banana',
  averageGenerationTime: 2.5
})

// 修改密码表单
const passwordFormRef = ref<FormInstance>()
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 密码验证规则
const passwordValidator = (rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 8) {
    callback(new Error('密码长度至少8位'))
  } else if (!/[A-Za-z]/.test(value)) {
    callback(new Error('密码必须包含字母'))
  } else if (!/\d/.test(value)) {
    callback(new Error('密码必须包含数字'))
  } else {
    callback()
  }
}

const confirmPasswordValidator = (rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请确认密码'))
  } else if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules: FormRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { validator: passwordValidator, trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: confirmPasswordValidator, trigger: 'blur' }
  ]
}

// 方法
const formatDate = (dateString?: string) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleString('zh-CN')
}

const refreshUserInfo = async () => {
  refreshing.value = true
  try {
    await userStore.getUserInfo()
    ElMessage.success('信息刷新成功')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    refreshing.value = false
  }
}

const showChangePasswordDialog = () => {
  passwordForm.currentPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  changePasswordVisible.value = true
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return

  try {
    const valid = await passwordFormRef.value.validate()
    if (!valid) return

    changingPassword.value = true

    // TODO: 实现修改密码API
    // await authApi.changePassword(passwordForm)

    ElMessage.success('密码修改成功，请重新登录')
    changePasswordVisible.value = false
    await handleLogout()
  } catch (error) {
    ElMessage.error('密码修改失败')
  } finally {
    changingPassword.value = false
  }
}

const handleLogout = async () => {
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

    await userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch (error) {
    // 用户取消
  }
}

const loadUserStats = async () => {
  try {
    const response = await galleryApi.getCreations()
    if (response.success && response.creations) {
      stats.totalGenerations = response.stats.total

      // 计算本月生成次数
      const currentMonth = new Date().getMonth()
      const currentYear = new Date().getFullYear()

      stats.thisMonthGenerations = response.creations.filter(creation => {
        const creationDate = new Date(creation.created_at)
        return creationDate.getMonth() === currentMonth &&
               creationDate.getFullYear() === currentYear
      }).length

      // 计算最常用模型
      const modelCounts = response.creations.reduce((acc, creation) => {
        acc[creation.model_used] = (acc[creation.model_used] || 0) + 1
        return acc
      }, {} as Record<string, number>)

      stats.favoriteModel = Object.keys(modelCounts).reduce((a, b) =>
        modelCounts[a] > modelCounts[b] ? a : b, 'nano-banana')

      // 计算平均生成时间
      const totalTime = response.creations.reduce((sum, creation) =>
        sum + (creation.generation_time || 0), 0)
      stats.averageGenerationTime = Number((totalTime / response.creations.length).toFixed(1))
    }
  } catch (error: any) {
    console.error('加载用户统计失败:', error)
    ElMessage.error(error.response?.data?.error || '加载用户统计失败，请稍后重试')
  }
}

// 生命周期
onMounted(async () => {
  // 确保用户信息已加载
  if (!userStore.user) {
    await userStore.getUserInfo()
  }
  await loadUserStats()
})
</script>

<style scoped>
.profile-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

/* 现代化头像区域 */
.profile-header-card {
  position: relative;
  margin-bottom: 24px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
}

.gradient-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 180px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header-content {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 24px 24px;
  background: white;
  margin-top: 120px;
}

.avatar-wrapper {
  position: relative;
  margin-top: -80px;
  margin-bottom: 16px;
}

.user-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: 4px solid white;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.avatar-ring {
  position: absolute;
  top: -8px;
  left: -8px;
  right: -8px;
  bottom: -8px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.5;
  }
}

.user-basic-info {
  text-align: center;
}

.user-email {
  margin: 0 0 12px;
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
}

.credits-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  border-radius: 24px;
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
}

.credits-icon {
  font-size: 20px;
  color: #d4af37;
}

.credits-number {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
}

.credits-text {
  font-size: 14px;
  color: #666;
}

/* 用户详细信息卡片 */
.user-details-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f2f5;
  transition: background 0.3s;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item:hover {
  background: #f8f9fa;
}

.detail-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  margin-right: 16px;
}

.detail-icon .el-icon {
  font-size: 20px;
  color: white;
}

.detail-content {
  flex: 1;
}

.detail-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.detail-value {
  font-size: 15px;
  color: #2c3e50;
  font-weight: 500;
}

/* 账户操作卡片 */
.actions-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #2c3e50;
  font-size: 16px;
}

.header-icon {
  font-size: 18px;
  color: #667eea;
}

/* 卡片式操作面板 */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-radius: 12px;
  border: 2px solid #e9ecef;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.action-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.action-item:hover::before {
  opacity: 1;
}

.action-item:hover {
  transform: translateY(-6px);
  border-color: #667eea;
  box-shadow: 0 12px 28px rgba(102, 126, 234, 0.2);
}

.action-item:active {
  transform: translateY(-2px);
}

.action-item.loading {
  pointer-events: none;
  opacity: 0.7;
}

.action-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
}

.action-item:hover .action-icon {
  transform: scale(1.1) rotate(5deg);
}

.action-icon .el-icon {
  font-size: 28px;
  color: white;
}

.refresh-icon {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
}

.password-icon {
  background: linear-gradient(135deg, #e6a23c 0%, #f0c78a 100%);
}

.logout-icon {
  background: linear-gradient(135deg, #f56c6c 0%, #f89898 100%);
}

.action-content {
  text-align: center;
  position: relative;
  z-index: 1;
}

.action-title {
  font-size: 15px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.action-desc {
  font-size: 12px;
  color: #909399;
}

/* 使用统计卡片 */
.stats-card {
  border-radius: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 24px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-radius: 12px;
  border: 1px solid #e9ecef;
  transition: all 0.3s;
}

.stat-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  border-color: #667eea;
}

.stat-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.stat-icon .el-icon {
  font-size: 24px;
  color: white;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  font-weight: 500;
}

.dialog-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .profile-container {
    padding: 16px;
    padding-bottom: calc(60px + 16px); /* 为底部标签栏留空间 */
  }

  .profile-header-card {
    border-radius: 12px;
    margin-bottom: 16px;
  }

  .gradient-background {
    height: 140px;
  }

  .header-content {
    padding: 24px 16px 20px;
    margin-top: 90px;
  }

  .avatar-wrapper {
    margin-top: -60px;
  }

  .user-email {
    font-size: 18px;
  }

  .credits-number {
    font-size: 20px;
  }

  .user-details-card,
  .actions-card,
  .stats-card {
    margin-bottom: 16px;
  }

  .detail-item {
    padding: 14px;
  }

  .detail-icon {
    width: 36px;
    height: 36px;
    margin-right: 12px;
  }

  .detail-icon .el-icon {
    font-size: 18px;
  }

  /* 移动端卡片式操作面板 */
  .actions-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .action-item {
    padding: 20px 16px;
  }

  .action-icon {
    width: 48px;
    height: 48px;
  }

  .action-icon .el-icon {
    font-size: 24px;
  }

  .action-title {
    font-size: 14px;
  }

  .action-desc {
    font-size: 11px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .stat-item {
    padding: 20px 12px;
  }

  .stat-icon {
    width: 40px;
    height: 40px;
    margin-bottom: 10px;
  }

  .stat-icon .el-icon {
    font-size: 20px;
  }

  .stat-number {
    font-size: 28px;
  }

  .stat-label {
    font-size: 12px;
  }
}
</style>