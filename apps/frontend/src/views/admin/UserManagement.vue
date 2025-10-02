<template>
  <div class="user-management">
    <!-- 页面标题 -->
    <div class="management-header">
      <h1 class="management-title">用户管理</h1>
      <div class="header-actions">
        <el-button type="primary" :icon="Refresh" @click="refreshData" :loading="refreshing">
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 用户搜索 -->
    <el-card class="search-card">
      <template #header>
        <div class="card-header">
          <span>用户搜索</span>
          <el-icon><Search /></el-icon>
        </div>
      </template>
      <div class="search-section">
        <el-input
          v-model="searchQuery"
          placeholder="输入用户邮箱进行搜索..."
          :prefix-icon="Search"
          clearable
          @input="onSearchInput"
          @clear="clearSearch"
          class="search-input"
        />
        <div v-if="searching" class="search-loading">
          <el-icon class="loading-icon"><Loading /></el-icon>
          <span>搜索中...</span>
        </div>
      </div>

      <!-- 搜索结果 -->
      <div v-if="searchResults.length > 0" class="search-results">
        <h3>搜索结果 ({{ searchResults.length }}个用户)</h3>
        <div class="users-list">
          <div
            v-for="user in searchResults"
            :key="user.id"
            class="user-item"
            @click="selectUser(user)"
            :class="{ active: selectedUser?.id === user.id }"
          >
            <div class="user-info">
              <div class="user-email">{{ user.email }}</div>
              <div class="user-meta">
                <el-tag size="small" :type="user.is_active ? 'success' : 'danger'">
                  {{ user.is_active ? '活跃' : '禁用' }}
                </el-tag>
                <span class="user-credits">剩余次数: {{ user.credits }}</span>
                <span class="user-date">注册时间: {{ formatDate(user.created_at) }}</span>
              </div>
            </div>
            <div class="user-actions">
              <el-button
                type="primary"
                size="small"
                @click.stop="openAddCreditsDialog(user)"
              >
                充值
              </el-button>
              <el-button
                type="info"
                size="small"
                @click.stop="viewUserDetails(user)"
              >
                详情
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click.stop="confirmDeleteUser(user)"
                :disabled="user.id === 1"
              >
                删除
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 搜索提示 -->
      <div v-else-if="searchQuery && !searching" class="no-results">
        <el-empty description="未找到匹配的用户" />
      </div>
    </el-card>

    <!-- 所有用户列表 -->
    <el-card v-if="!searchQuery" class="users-card">
      <template #header>
        <div class="card-header">
          <span>所有用户 ({{ allUsers.length }}个)</span>
          <el-icon><User /></el-icon>
        </div>
      </template>

      <div v-loading="loadingAllUsers" class="all-users-section">
        <div v-if="allUsers.length > 0" class="users-list">
          <div
            v-for="user in allUsers"
            :key="user.id"
            class="user-item"
            @click="selectUser(user)"
            :class="{ active: selectedUser?.id === user.id }"
          >
            <div class="user-info">
              <div class="user-email">{{ user.email }}</div>
              <div class="user-meta">
                <el-tag size="small" :type="user.is_active ? 'success' : 'danger'">
                  {{ user.is_active ? '活跃' : '禁用' }}
                </el-tag>
                <span class="user-credits">剩余次数: {{ user.credits }}</span>
                <span class="user-date">注册时间: {{ formatDate(user.created_at) }}</span>
              </div>
            </div>
            <div class="user-actions">
              <el-button
                type="primary"
                size="small"
                @click.stop="openAddCreditsDialog(user)"
              >
                充值
              </el-button>
              <el-button
                type="info"
                size="small"
                @click.stop="viewUserDetails(user)"
              >
                详情
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click.stop="confirmDeleteUser(user)"
                :disabled="user.id === 1"
              >
                删除
              </el-button>
            </div>
          </div>
        </div>

        <div v-else-if="!loadingAllUsers" class="no-users">
          <el-empty description="暂无用户数据" />
        </div>
      </div>
    </el-card>

    <!-- 用户详情 -->
    <el-card v-if="selectedUser" class="user-details-card">
      <template #header>
        <div class="card-header">
          <span>用户详情</span>
          <el-icon><User /></el-icon>
        </div>
      </template>

      <div class="user-details" v-loading="loadingUserDetails">
        <div class="details-grid">
          <div class="detail-item">
            <label>用户ID:</label>
            <span>{{ selectedUser.id }}</span>
          </div>
          <div class="detail-item">
            <label>邮箱:</label>
            <span>{{ selectedUser.email }}</span>
          </div>
          <div class="detail-item">
            <label>剩余次数:</label>
            <span class="credits-value">{{ selectedUser.credits }}</span>
          </div>
          <div class="detail-item">
            <label>账户状态:</label>
            <el-tag :type="selectedUser.is_active ? 'success' : 'danger'">
              {{ selectedUser.is_active ? '活跃' : '禁用' }}
            </el-tag>
          </div>
          <div class="detail-item">
            <label>注册时间:</label>
            <span>{{ formatDateTime(selectedUser.created_at) }}</span>
          </div>
          <div class="detail-item">
            <label>最后登录:</label>
            <span>{{ selectedUser.last_login_at ? formatDateTime(selectedUser.last_login_at) : '从未登录' }}</span>
          </div>
        </div>

        <!-- 用户统计信息 -->
        <div v-if="userStats" class="user-stats">
          <h3>创作统计</h3>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-number">{{ userStats.total || 0 }}</div>
              <div class="stat-label">总作品数</div>
            </div>
            <div class="stat-card">
              <div class="stat-number">{{ userStats.recent_week || 0 }}</div>
              <div class="stat-label">本周创作</div>
            </div>
            <div class="stat-card">
              <div class="stat-number">{{ userStats.favorites || 0 }}</div>
              <div class="stat-label">收藏作品</div>
            </div>
          </div>

          <!-- 分类统计 -->
          <div v-if="userStats.categories && userStats.categories.length > 0" class="categories-stats">
            <h4>作品分类分布</h4>
            <div class="categories-list">
              <div
                v-for="category in userStats.categories"
                :key="category.category"
                class="category-item"
              >
                <span class="category-name">{{ category.category }}</span>
                <span class="category-count">{{ category.count }}个</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 用户生成的图片展示 -->
        <div v-if="userCreations && userCreations.length > 0" class="user-creations">
          <h3>用户作品 ({{ userCreations.length }})</h3>
          <div class="creations-grid">
            <div
              v-for="creation in userCreations"
              :key="creation.id"
              class="creation-card"
            >
              <div class="creation-image">
                <img :src="creation.image_url" :alt="creation.prompt" />
              </div>
              <div class="creation-info">
                <div class="creation-prompt">{{ creation.prompt }}</div>
                <div class="creation-meta">
                  <el-tag size="small">{{ creation.model_used }}</el-tag>
                  <span class="creation-date">{{ formatDate(creation.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else-if="loadingUserCreations" class="loading-creations">
          <el-icon class="loading-icon"><Loading /></el-icon>
          <span>加载作品中...</span>
        </div>
        <div v-else class="no-creations">
          <el-empty description="该用户暂无作品" :image-size="100" />
        </div>
      </div>
    </el-card>

    <!-- 次数充值对话框 -->
    <el-dialog
      v-model="addCreditsDialogVisible"
      title="为用户充值次数"
      width="500px"
      :before-close="handleDialogClose"
    >
      <div v-if="targetUser" class="add-credits-form">
        <div class="user-info-display">
          <div class="info-item">
            <label>目标用户:</label>
            <span class="user-email">{{ targetUser.email }}</span>
          </div>
          <div class="info-item">
            <label>当前次数:</label>
            <span class="current-credits">{{ targetUser.credits }}</span>
          </div>
        </div>

        <el-form :model="creditsForm" :rules="creditsRules" ref="creditsFormRef" label-width="120px">
          <el-form-item label="充值次数" prop="credits">
            <el-input-number
              v-model="creditsForm.credits"
              :min="1"
              :max="1000"
              placeholder="输入充值次数"
              style="width: 100%"
            />
            <div class="form-help">
              单次充值范围: 1-1000次
            </div>
          </el-form-item>

          <el-form-item label="充值说明" prop="description">
            <el-input
              v-model="creditsForm.description"
              type="textarea"
              :rows="3"
              placeholder="可选：输入充值说明或备注"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>
        </el-form>

        <div class="credits-preview">
          <div class="preview-item">
            <label>充值后次数:</label>
            <span class="new-credits">{{ targetUser.credits + (creditsForm.credits || 0) }}</span>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addCreditsDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            @click="confirmAddCredits"
            :loading="addingCredits"
            :disabled="!creditsForm.credits || creditsForm.credits <= 0"
          >
            确认充值
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 用户详情对话框 -->
    <el-dialog
      v-model="userDetailsDialogVisible"
      title="用户详细信息"
      width="600px"
    >
      <div v-if="detailUser" class="user-detail-content" v-loading="loadingDetailUser">
        <div class="user-basic-info">
          <h3>基本信息</h3>
          <div class="info-grid">
            <div class="info-item">
              <label>用户ID:</label>
              <span>{{ detailUser.id }}</span>
            </div>
            <div class="info-item">
              <label>邮箱:</label>
              <span>{{ detailUser.email }}</span>
            </div>
            <div class="info-item">
              <label>剩余次数:</label>
              <span class="credits-highlight">{{ detailUser.credits }}</span>
            </div>
            <div class="info-item">
              <label>账户状态:</label>
              <el-tag :type="detailUser.is_active ? 'success' : 'danger'">
                {{ detailUser.is_active ? '活跃' : '禁用' }}
              </el-tag>
            </div>
            <div class="info-item">
              <label>注册时间:</label>
              <span>{{ formatDateTime(detailUser.created_at) }}</span>
            </div>
            <div class="info-item">
              <label>最后登录:</label>
              <span>{{ detailUser.last_login_at ? formatDateTime(detailUser.last_login_at) : '从未登录' }}</span>
            </div>
          </div>
        </div>

        <div v-if="detailUserStats" class="user-stats-detail">
          <h3>创作统计</h3>
          <div class="stats-overview">
            <div class="stat-item">
              <span class="stat-label">总作品数:</span>
              <span class="stat-value">{{ detailUserStats.total || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">本周创作:</span>
              <span class="stat-value">{{ detailUserStats.recent_week || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">收藏作品:</span>
              <span class="stat-value">{{ detailUserStats.favorites || 0 }}</span>
            </div>
          </div>

          <div v-if="detailUserStats.categories && detailUserStats.categories.length > 0" class="categories-detail">
            <h4>作品分类分布</h4>
            <div class="categories-chart">
              <div
                v-for="category in detailUserStats.categories"
                :key="category.category"
                class="category-bar"
              >
                <div class="category-info">
                  <span class="category-name">{{ category.category }}</span>
                  <span class="category-count">{{ category.count }}</span>
                </div>
                <div class="progress-bar">
                  <div
                    class="progress-fill"
                    :style="{ width: `${(category.count / detailUserStats.total) * 100}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Refresh,
  Search,
  Loading,
  User
} from '@element-plus/icons-vue'
import { adminApi } from '@/services/api'

// 响应式数据
const refreshing = ref(false)
const searching = ref(false)
const searchQuery = ref('')
const searchResults = ref([])
const allUsers = ref([])
const loadingAllUsers = ref(false)
const selectedUser = ref(null)
const userStats = ref(null)
const loadingUserDetails = ref(false)
const userCreations = ref([])
const loadingUserCreations = ref(false)

// 充值相关
const addCreditsDialogVisible = ref(false)
const targetUser = ref(null)
const addingCredits = ref(false)
const creditsFormRef = ref<FormInstance>()

// 用户详情对话框
const userDetailsDialogVisible = ref(false)
const detailUser = ref(null)
const detailUserStats = ref(null)
const loadingDetailUser = ref(false)

// 表单数据
const creditsForm = reactive({
  credits: null,
  description: ''
})

const creditsRules: FormRules = {
  credits: [
    { required: true, message: '请输入充值次数', trigger: 'blur' },
    { type: 'number', min: 1, max: 1000, message: '充值次数必须在1-1000之间', trigger: 'blur' }
  ]
}

// 搜索防抖定时器
let searchDebounceTimer: NodeJS.Timeout | null = null

// 初始化组件
onMounted(() => {
  loadAllUsers()
})

// 方法
const loadAllUsers = async () => {
  loadingAllUsers.value = true
  try {
    // 使用空搜索来获取所有用户（或者后端提供专门的API）
    const response = await adminApi.searchUsers('')
    if (response.success) {
      allUsers.value = response.users || []
    } else {
      console.error('加载用户列表失败:', response.error)
      // 不显示错误消息，避免干扰用户
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
    // 不显示错误消息，避免干扰用户
  } finally {
    loadingAllUsers.value = false
  }
}

const refreshData = async () => {
  refreshing.value = true
  try {
    // 重新加载所有用户
    await loadAllUsers()

    // 如果有选中的用户，重新加载其详情
    if (selectedUser.value) {
      await loadUserDetails(selectedUser.value.id)
    }
    ElMessage.success('数据刷新成功')
  } catch (error) {
    console.error('数据刷新失败:', error)
    ElMessage.error('数据刷新失败')
  } finally {
    refreshing.value = false
  }
}

const onSearchInput = () => {
  // 清除之前的定时器
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }

  // 如果搜索内容为空，清空结果
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    return
  }

  // 设置防抖延迟
  searchDebounceTimer = setTimeout(() => {
    performSearch()
  }, 500)
}

const performSearch = async () => {
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    return
  }

  searching.value = true
  try {
    const response = await adminApi.searchUsers(searchQuery.value.trim())
    if (response.success) {
      searchResults.value = response.users || []
      if (searchResults.value.length === 0) {
        ElMessage.info('未找到匹配的用户')
      }
    } else {
      ElMessage.error(response.error || '搜索失败')
      searchResults.value = []
    }
  } catch (error) {
    console.error('搜索用户失败:', error)
    ElMessage.error('搜索失败，请稍后重试')
    searchResults.value = []
  } finally {
    searching.value = false
  }
}

const clearSearch = () => {
  searchResults.value = []
  selectedUser.value = null
  userStats.value = null
}

const selectUser = async (user: any) => {
  selectedUser.value = user
  await loadUserDetails(user.id)
}

const loadUserDetails = async (userId: number) => {
  loadingUserDetails.value = true
  try {
    const response = await adminApi.getUserDetails(userId)
    if (response.success) {
      // 更新选中用户的信息
      if (selectedUser.value && selectedUser.value.id === userId) {
        selectedUser.value = response.user
      }
      userStats.value = response.stats
    } else {
      ElMessage.error(response.error || '获取用户详情失败')
    }
  } catch (error) {
    console.error('获取用户详情失败:', error)
    ElMessage.error('获取用户详情失败')
  } finally {
    loadingUserDetails.value = false
  }

  // 加载用户作品
  await loadUserCreations(userId)
}

const loadUserCreations = async (userId: number) => {
  loadingUserCreations.value = true
  try {
    const response = await adminApi.getUserCreations(userId)
    if (response.success) {
      userCreations.value = response.creations || []
    } else {
      console.error('获取用户作品失败:', response.error)
      userCreations.value = []
    }
  } catch (error) {
    console.error('获取用户作品失败:', error)
    userCreations.value = []
  } finally {
    loadingUserCreations.value = false
  }
}

const openAddCreditsDialog = (user: any) => {
  targetUser.value = user
  creditsForm.credits = null
  creditsForm.description = ''
  addCreditsDialogVisible.value = true
}

const handleDialogClose = () => {
  // 重置表单
  creditsForm.credits = null
  creditsForm.description = ''
  if (creditsFormRef.value) {
    creditsFormRef.value.resetFields()
  }
}

const confirmAddCredits = async () => {
  if (!creditsFormRef.value) return

  const valid = await creditsFormRef.value.validate()
  if (!valid) return

  try {
    // 确认对话框
    await ElMessageBox.confirm(
      `确认为用户 ${targetUser.value.email} 充值 ${creditsForm.credits} 次数吗？`,
      '确认充值',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    addingCredits.value = true

    const response = await adminApi.addCredits(targetUser.value.email, creditsForm.credits)

    if (response.success) {
      ElNotification({
        title: '充值成功',
        message: `成功为用户 ${targetUser.value.email} 充值 ${creditsForm.credits} 次数`,
        type: 'success'
      })

      // 更新用户信息
      if (selectedUser.value && selectedUser.value.id === targetUser.value.id) {
        selectedUser.value.credits = response.data.new_credits
      }

      // 更新搜索结果中的用户信息
      const searchUserIndex = searchResults.value.findIndex(u => u.id === targetUser.value.id)
      if (searchUserIndex !== -1) {
        searchResults.value[searchUserIndex].credits = response.data.new_credits
      }

      // 更新所有用户列表中的用户信息
      const allUserIndex = allUsers.value.findIndex(u => u.id === targetUser.value.id)
      if (allUserIndex !== -1) {
        allUsers.value[allUserIndex].credits = response.data.new_credits
      }

      addCreditsDialogVisible.value = false
    } else {
      ElMessage.error(response.error || '充值失败')
    }
  } catch (error) {
    if (error === 'cancel') {
      // 用户取消操作
      return
    }
    console.error('充值失败:', error)
    ElMessage.error('充值失败，请稍后重试')
  } finally {
    addingCredits.value = false
  }
}

const viewUserDetails = async (user: any) => {
  detailUser.value = user
  userDetailsDialogVisible.value = true

  // 加载详细信息
  loadingDetailUser.value = true
  try {
    const response = await adminApi.getUserDetails(user.id)
    if (response.success) {
      detailUser.value = response.user
      detailUserStats.value = response.stats
    } else {
      ElMessage.error(response.error || '获取用户详情失败')
    }
  } catch (error) {
    console.error('获取用户详情失败:', error)
    ElMessage.error('获取用户详情失败')
  } finally {
    loadingDetailUser.value = false
  }
}

// 删除用户相关
const confirmDeleteUser = async (user: any) => {
  // 防止删除管理员自己
  if (user.id === 1) {
    ElMessage.warning('不能删除主管理员账户')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确认永久删除用户 ${user.email} 吗？此操作不可撤销！\n\n删除后：\n- 用户账户将被永久删除\n- 用户的作品将保留但标记为孤儿\n- 所有用户数据（会话、行为记录等）将被清除`,
      '确认删除用户',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
        distinguishCancelAndClose: true,
        confirmButtonClass: 'el-button--danger'
      }
    )

    // 询问删除原因
    const reason = await ElMessageBox.prompt(
      '请输入删除原因（可选）',
      '删除原因',
      {
        inputPlaceholder: '例如：违规用户、测试账号等',
        confirmButtonText: '确认',
        cancelButtonText: '跳过'
      }
    ).catch(() => ({ value: '' }))

    // 执行删除
    const response = await adminApi.deleteUser(user.id, reason.value || '')

    if (response.success) {
      ElNotification({
        title: '删除成功',
        message: `已删除用户 ${user.email}。${response.impact ? `孤儿作品: ${response.impact.creations_orphaned}个` : ''}`,
        type: 'success',
        duration: 5000
      })

      // 清除选中状态
      if (selectedUser.value && selectedUser.value.id === user.id) {
        selectedUser.value = null
        userStats.value = null
        userCreations.value = []
      }

      // 刷新列表
      await refreshData()
    } else {
      ElMessage.error(response.error || '删除用户失败')
    }
  } catch (error: any) {
    if (error !== 'cancel' && error !== 'close') {
      console.error('删除用户失败:', error)
      ElMessage.error('删除用户失败')
    }
  }
}

// 辅助方法
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const formatDateTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.user-management {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.management-title {
  margin: 0;
  color: #2c3e50;
  font-size: 28px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-card,
.users-card {
  margin-bottom: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.all-users-section {
  min-height: 200px;
}

.no-users {
  text-align: center;
  padding: 40px 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.search-section {
  margin-bottom: 16px;
}

.search-input {
  width: 100%;
  max-width: 500px;
}

.search-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  color: #909399;
  font-size: 14px;
}

.loading-icon {
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.search-results h3 {
  margin: 20px 0 16px 0;
  color: #2c3e50;
  font-size: 18px;
}

.users-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 2px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-item:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.user-item.active {
  border-color: #409eff;
  background-color: #e6f7ff;
}

.user-info {
  flex: 1;
}

.user-email {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #606266;
}

.user-credits {
  font-weight: 500;
  color: #409eff;
}

.user-actions {
  display: flex;
  gap: 8px;
}

.no-results {
  text-align: center;
  padding: 40px 20px;
}

.user-details-card {
  margin-bottom: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.user-details {
  min-height: 200px;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item label {
  font-weight: 600;
  color: #606266;
  font-size: 14px;
}

.detail-item span {
  color: #2c3e50;
  font-size: 16px;
}

.credits-value {
  font-weight: 600;
  color: #409eff;
  font-size: 18px;
}

.user-stats h3 {
  margin: 24px 0 16px 0;
  color: #2c3e50;
  font-size: 18px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.categories-stats h4 {
  margin: 20px 0 12px 0;
  color: #2c3e50;
  font-size: 16px;
}

.categories-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
}

.category-name {
  color: #0369a1;
  font-weight: 500;
}

.category-count {
  color: #0284c7;
  font-weight: 600;
  background: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

/* 用户作品展示样式 */
.user-creations {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
}

.user-creations h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #1f2937;
  font-weight: 600;
}

.creations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.creation-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
}

.creation-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.creation-image {
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: #f3f4f6;
}

.creation-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.creation-info {
  padding: 12px;
}

.creation-prompt {
  font-size: 13px;
  color: #374151;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.4;
}

.creation-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: #6b7280;
}

.creation-date {
  font-size: 11px;
}

.loading-creations,
.no-creations {
  margin-top: 24px;
  padding: 40px;
  text-align: center;
  color: #6b7280;
}

.loading-creations {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.loading-icon {
  font-size: 24px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 充值对话框样式 */
.add-credits-form {
  padding: 16px 0;
}

.user-info-display {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item label {
  font-weight: 600;
  color: #606266;
  width: 80px;
  margin-right: 12px;
}

.user-email {
  color: #409eff;
  font-weight: 600;
}

.current-credits {
  color: #67c23a;
  font-weight: 600;
}

.form-help {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.credits-preview {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
}

.preview-item {
  display: flex;
  align-items: center;
}

.preview-item label {
  font-weight: 600;
  color: #0369a1;
  margin-right: 12px;
}

.new-credits {
  color: #059669;
  font-weight: 700;
  font-size: 18px;
}

/* 用户详情对话框样式 */
.user-detail-content {
  padding: 16px 0;
}

.user-basic-info h3 {
  margin: 0 0 16px 0;
  color: #2c3e50;
  font-size: 18px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.credits-highlight {
  color: #409eff;
  font-weight: 700;
  font-size: 18px;
}

.user-stats-detail h3 {
  margin: 24px 0 16px 0;
  color: #2c3e50;
  font-size: 18px;
}

.stats-overview {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #409eff;
}

.categories-detail h4 {
  margin: 20px 0 12px 0;
  color: #2c3e50;
  font-size: 16px;
}

.categories-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.category-bar {
  padding: 8px 0;
}

.category-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.category-name {
  color: #2c3e50;
  font-weight: 500;
}

.category-count {
  color: #409eff;
  font-weight: 600;
}

.progress-bar {
  height: 8px;
  background: #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #409eff, #67c23a);
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* 触摸优化 */
.el-button,
.el-input,
.el-input-number,
.user-item,
.stat-card {
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-management {
    padding: 16px;
    max-width: 100%;
  }

  .management-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
    margin-bottom: 20px;
  }

  .management-title {
    font-size: 24px;
    text-align: center;
    margin: 0;
  }

  .header-actions {
    justify-content: center;
  }

  .header-actions .el-button {
    height: 48px;
    font-size: 16px;
    font-weight: 600;
    border-radius: 24px;
    padding: 0 24px;
  }

  /* 搜索卡片优化 */
  .search-card,
  .users-card,
  .user-details-card {
    margin-bottom: 20px;
    border-radius: 12px;
  }

  .search-input {
    max-width: 100%;
  }

  .search-input .el-input__wrapper {
    height: 48px;
    border-radius: 24px;
  }

  .search-loading {
    font-size: 15px;
    margin-top: 16px;
  }

  .search-results h3 {
    font-size: 18px;
    margin: 16px 0 12px 0;
  }

  /* 用户列表优化 */
  .user-item {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    padding: 16px;
    border-radius: 12px;
    min-height: auto;
  }

  .user-info {
    text-align: left;
  }

  .user-email {
    font-size: 16px;
    margin-bottom: 10px;
  }

  .user-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    font-size: 14px;
  }

  .user-meta .el-tag {
    align-self: flex-start;
  }

  .user-actions {
    justify-content: stretch;
    gap: 12px;
  }

  .user-actions .el-button {
    flex: 1;
    height: 44px;
    font-size: 15px;
    font-weight: 600;
    border-radius: 22px;
  }

  /* 详情网格优化 */
  .details-grid,
  .info-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .detail-item {
    padding: 12px;
    background: #f8f9fa;
    border-radius: 8px;
  }

  .detail-item label {
    font-size: 13px;
    margin-bottom: 6px;
  }

  .detail-item span {
    font-size: 15px;
  }

  .credits-value {
    font-size: 18px;
  }

  /* 统计卡片优化 */
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 12px;
    margin-bottom: 16px;
  }

  .stat-card {
    padding: 16px;
    border-radius: 10px;
  }

  .stat-number {
    font-size: 24px;
    margin-bottom: 6px;
  }

  .stat-label {
    font-size: 13px;
  }

  .stats-overview {
    flex-direction: column;
    gap: 16px;
    margin-bottom: 16px;
  }

  .stat-item {
    padding: 12px;
    background: #f8f9fa;
    border-radius: 8px;
  }

  .stat-label {
    font-size: 13px;
  }

  .stat-value {
    font-size: 20px;
  }

  /* 分类列表优化 */
  .categories-list {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .category-item {
    padding: 12px 14px;
    border-radius: 8px;
  }

  .category-name {
    font-size: 14px;
  }

  .category-count {
    font-size: 12px;
    padding: 3px 6px;
  }

  /* 对话框优化 */
  .el-dialog {
    width: 95% !important;
    margin: 5vh auto;
    border-radius: 12px;
  }

  .add-credits-form {
    padding: 12px 0;
  }

  .user-info-display {
    padding: 12px;
    margin-bottom: 16px;
    border-radius: 8px;
  }

  .info-item {
    margin-bottom: 10px;
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .info-item label {
    width: auto;
    margin-right: 0;
    font-size: 13px;
  }

  .user-email {
    font-size: 16px;
  }

  .current-credits {
    font-size: 16px;
  }

  .el-form-item__label {
    font-size: 14px;
    font-weight: 600;
  }

  .el-input-number {
    width: 100%;
  }

  .el-input-number .el-input__inner {
    height: 48px;
    font-size: 16px;
  }

  .el-textarea__inner {
    min-height: 80px !important;
    font-size: 14px;
    line-height: 1.5;
  }

  .form-help {
    font-size: 12px;
    margin-top: 6px;
  }

  .credits-preview {
    padding: 12px;
    margin-top: 12px;
    border-radius: 8px;
  }

  .preview-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .preview-item label {
    font-size: 14px;
    margin-right: 0;
  }

  .new-credits {
    font-size: 20px;
  }

  .dialog-footer {
    text-align: center;
    gap: 12px;
  }

  .dialog-footer .el-button {
    flex: 1;
    height: 48px;
    font-size: 16px;
    font-weight: 600;
    border-radius: 24px;
  }

  /* 用户详情对话框优化 */
  .user-detail-content {
    padding: 12px 0;
  }

  .user-basic-info h3,
  .user-stats-detail h3 {
    font-size: 18px;
    margin: 16px 0 12px 0;
  }

  .categories-detail h4 {
    font-size: 16px;
    margin: 16px 0 10px 0;
  }

  .credits-highlight {
    font-size: 18px;
  }

  .categories-chart {
    gap: 10px;
  }

  .category-bar {
    padding: 6px 0;
  }

  .category-info {
    margin-bottom: 6px;
  }

  .category-name {
    font-size: 14px;
  }

  .category-count {
    font-size: 14px;
  }

  .progress-bar {
    height: 6px;
  }
}

@media (max-width: 480px) {
  .user-management {
    padding: 12px;
  }

  .management-title {
    font-size: 22px;
  }

  .header-actions .el-button {
    height: 44px;
    font-size: 15px;
    padding: 0 20px;
  }

  .search-input .el-input__wrapper {
    height: 44px;
  }

  .search-results h3 {
    font-size: 16px;
  }

  .user-item {
    padding: 12px;
  }

  .user-email {
    font-size: 15px;
  }

  .user-meta {
    font-size: 13px;
  }

  .user-actions .el-button {
    height: 40px;
    font-size: 14px;
  }

  .detail-item {
    padding: 10px;
  }

  .detail-item label {
    font-size: 12px;
  }

  .detail-item span {
    font-size: 14px;
  }

  .stat-card {
    padding: 14px;
  }

  .stat-number {
    font-size: 22px;
  }

  .stat-label {
    font-size: 12px;
  }

  .stat-value {
    font-size: 18px;
  }

  .category-item {
    padding: 10px 12px;
  }

  .category-name {
    font-size: 13px;
  }

  .category-count {
    font-size: 11px;
  }

  .el-dialog {
    margin: 2vh auto;
  }

  .user-info-display {
    padding: 10px;
  }

  .info-item label {
    font-size: 12px;
  }

  .user-email {
    font-size: 15px;
  }

  .current-credits {
    font-size: 15px;
  }

  .el-input-number .el-input__inner {
    height: 44px;
    font-size: 15px;
  }

  .el-textarea__inner {
    min-height: 76px !important;
    font-size: 13px;
  }

  .credits-preview {
    padding: 10px;
  }

  .new-credits {
    font-size: 18px;
  }

  .dialog-footer .el-button {
    height: 44px;
    font-size: 15px;
  }

  .user-basic-info h3,
  .user-stats-detail h3 {
    font-size: 16px;
  }

  .categories-detail h4 {
    font-size: 15px;
  }

  .credits-highlight {
    font-size: 16px;
  }
}

@media (max-width: 360px) {
  .user-management {
    padding: 10px;
  }

  .management-title {
    font-size: 20px;
  }

  .header-actions .el-button {
    height: 42px;
    font-size: 14px;
    padding: 0 16px;
  }

  .user-item {
    padding: 10px;
  }

  .user-email {
    font-size: 14px;
  }

  .user-actions .el-button {
    height: 38px;
    font-size: 13px;
  }

  .stat-card {
    padding: 12px;
  }

  .stat-number {
    font-size: 20px;
  }

  .dialog-footer .el-button {
    height: 42px;
    font-size: 14px;
  }
}

/* 横屏模式优化 */
@media (max-height: 600px) and (orientation: landscape) {
  .user-management {
    padding: 8px 12px;
  }

  .management-header {
    margin-bottom: 12px;
  }

  .management-title {
    font-size: 20px;
  }

  .search-card,
  .users-card,
  .user-details-card {
    margin-bottom: 12px;
  }

  .user-item {
    padding: 8px 12px;
    gap: 8px;
  }

  .user-actions .el-button {
    height: 36px;
    font-size: 13px;
  }

  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .stat-card {
    padding: 10px;
  }

  .stat-number {
    font-size: 18px;
    margin-bottom: 4px;
  }

  .stat-label {
    font-size: 11px;
  }

  .el-dialog {
    margin: 1vh auto;
  }
}
</style>