<template>
  <div class="admin-dashboard">
    <!-- 页面标题 -->
    <div class="dashboard-header">
      <h1 class="dashboard-title">管理员仪表板</h1>
      <div class="refresh-controls">
        <el-button type="primary" :icon="Refresh" @click="refreshAllData" :loading="refreshing">
          刷新数据
        </el-button>
        <el-select v-model="timeRange" @change="onTimeRangeChange" style="width: 150px; margin-left: 12px;">
          <el-option label="最近24小时" value="24" />
          <el-option label="最近7天" value="168" />
          <el-option label="最近30天" value="720" />
        </el-select>
      </div>
    </div>

    <!-- 系统健康状态卡片 -->
    <div class="health-overview">
      <el-card class="health-card" :class="getHealthCardClass()">
        <template #header>
          <div class="card-header">
            <span>系统健康状态</span>
            <el-tag :type="getHealthTagType()" size="large">
              {{ systemInsights.overall_health === 'good' ? '良好' : '警告' }}
            </el-tag>
          </div>
        </template>
        <div class="health-metrics">
          <div class="metric-item">
            <div class="metric-label">平均生成时间</div>
            <div class="metric-value">{{ systemInsights.performance?.avg_generation_time_24h || 0 }}s</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">错误率</div>
            <div class="metric-value" :class="getErrorRateClass()">
              {{ systemInsights.performance?.error_rate_24h || 0 }}%
            </div>
          </div>
          <div class="metric-item">
            <div class="metric-label">活跃会话</div>
            <div class="metric-value">{{ systemInsights.performance?.active_sessions || 0 }}</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">峰值负载</div>
            <div class="metric-value" :class="getLoadClass()">
              {{ Math.round((systemInsights.performance?.peak_load_24h || 0) * 100) }}%
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 洞察和建议 -->
    <div class="insights-section" v-if="systemInsights.insights && systemInsights.insights.length > 0">
      <el-card>
        <template #header>
          <span>系统洞察和建议</span>
        </template>
        <div class="insights-list">
          <div
            v-for="(insight, index) in systemInsights.insights"
            :key="index"
            class="insight-item"
            :class="insight.priority"
          >
            <el-icon class="insight-icon">
              <component :is="getInsightIcon(insight.type)" />
            </el-icon>
            <div class="insight-content">
              <div class="insight-message">{{ insight.message }}</div>
              <div class="insight-meta">
                <el-tag size="small" :type="getInsightTagType(insight.type)">
                  {{ getInsightTypeText(insight.type) }}
                </el-tag>
                <el-tag size="small" :type="getPriorityTagType(insight.priority)">
                  {{ getPriorityText(insight.priority) }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 数据分析网格 -->
    <div class="analytics-grid">
      <!-- 性能分析 -->
      <el-card class="analytics-card">
        <template #header>
          <div class="card-header">
            <span>性能分析</span>
            <el-icon><TrendCharts /></el-icon>
          </div>
        </template>
        <div class="analytics-content" v-loading="loadingPerformance">
          <div class="metric-row">
            <div class="metric-label">平均生成时间</div>
            <div class="metric-value primary">
              {{ performanceData.avg_generation_time || 0 }}s
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-label">错误率</div>
            <div class="metric-value" :class="getErrorRateClass()">
              {{ performanceData.error_rate || 0 }}%
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-label">峰值服务器负载</div>
            <div class="metric-value" :class="getLoadClass()">
              {{ Math.round((performanceData.peak_server_load || 0) * 100) }}%
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-label">时间范围</div>
            <div class="metric-value">{{ performanceData.time_range_hours || 0 }}小时</div>
          </div>
        </div>
      </el-card>

      <!-- 用户行为分析 -->
      <el-card class="analytics-card">
        <template #header>
          <div class="card-header">
            <span>用户行为分析</span>
            <el-icon><User /></el-icon>
          </div>
        </template>
        <div class="analytics-content" v-loading="loadingUserBehavior">
          <div class="metric-row">
            <div class="metric-label">偏好模型</div>
            <div class="metric-value">{{ userBehaviorData.preferred_model || '暂无数据' }}</div>
          </div>
          <div class="metric-row">
            <div class="metric-label">最活跃时段</div>
            <div class="metric-value">
              {{ userBehaviorData.most_active_hour !== null ? `${userBehaviorData.most_active_hour}:00` : '暂无数据' }}
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-label">平均会话时长</div>
            <div class="metric-value">{{ Math.round(userBehaviorData.avg_session_duration || 0) }}秒</div>
          </div>
          <div class="metric-row">
            <div class="metric-label">当前活跃会话</div>
            <div class="metric-value">{{ userBehaviorData.current_active_sessions || 0 }}</div>
          </div>
        </div>
      </el-card>

      <!-- 热门操作 -->
      <el-card class="analytics-card">
        <template #header>
          <div class="card-header">
            <span>热门操作统计</span>
            <el-icon><DataAnalysis /></el-icon>
          </div>
        </template>
        <div class="analytics-content" v-loading="loadingPopularActions">
          <div class="popular-actions-list">
            <div
              v-for="(action, index) in popularActions"
              :key="index"
              class="action-item"
            >
              <div class="action-name">{{ getActionDisplayName(action.action_type) }}</div>
              <div class="action-count">{{ action.count }}次</div>
            </div>
            <div v-if="popularActions.length === 0" class="no-data">
              暂无数据
            </div>
          </div>
        </div>
      </el-card>

      <!-- 每日统计 -->
      <el-card class="analytics-card">
        <template #header>
          <div class="card-header">
            <span>每日统计</span>
            <el-icon><Calendar /></el-icon>
          </div>
        </template>
        <div class="analytics-content" v-loading="loadingDailyStats">
          <div class="daily-stats-list">
            <div
              v-for="(stat, index) in dailyStats.slice(0, 5)"
              :key="index"
              class="stat-item"
            >
              <div class="stat-date">{{ formatDate(stat.date) }}</div>
              <div class="stat-details">
                <span class="stat-value">活跃用户: {{ stat.active_users }}</span>
                <span class="stat-value">生成次数: {{ stat.total_generations }}</span>
              </div>
            </div>
            <div v-if="dailyStats.length === 0" class="no-data">
              暂无数据
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 用户统计详情 -->
    <div class="user-stats-section" v-if="systemInsights.user_stats">
      <el-card>
        <template #header>
          <span>用户统计详情</span>
        </template>
        <div class="user-stats-grid">
          <div class="stat-card">
            <div class="stat-number">{{ systemInsights.user_stats.total || 0 }}</div>
            <div class="stat-label">总用户数</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ systemInsights.user_stats.favorites || 0 }}</div>
            <div class="stat-label">收藏作品数</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ systemInsights.user_stats.recent_week || 0 }}</div>
            <div class="stat-label">本周新增</div>
          </div>
        </div>

        <!-- 分类统计 -->
        <div class="categories-section" v-if="systemInsights.user_stats.categories && systemInsights.user_stats.categories.length > 0">
          <h3>作品分类分布</h3>
          <div class="categories-list">
            <div
              v-for="(category, index) in systemInsights.user_stats.categories"
              :key="index"
              class="category-item"
            >
              <span class="category-name">{{ category.category }}</span>
              <span class="category-count">{{ category.count }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  TrendCharts,
  User,
  DataAnalysis,
  Calendar,
  Warning,
  InfoFilled,
  CircleCheck
} from '@element-plus/icons-vue'
import { analyticsApi } from '@/services/api'

// 响应式数据
const refreshing = ref(false)
const timeRange = ref('24')
const loadingPerformance = ref(false)
const loadingUserBehavior = ref(false)
const loadingPopularActions = ref(false)
const loadingDailyStats = ref(false)

// 数据状态
const performanceData = reactive({
  avg_generation_time: 0,
  error_rate: 0,
  peak_server_load: 0,
  time_range_hours: 24,
  operation_type: 'all'
})

const userBehaviorData = reactive({
  preferred_model: null,
  most_active_hour: null,
  avg_session_duration: 0,
  current_active_sessions: 0
})

const popularActions = ref<any[]>([])
const dailyStats = ref<any[]>([])
const systemInsights = reactive<any>({
  performance: null,
  user_stats: null,
  insights: [],
  overall_health: 'good'
})

// 生命周期
onMounted(() => {
  refreshAllData()
})

// 方法
const refreshAllData = async () => {
  refreshing.value = true
  try {
    await Promise.all([
      loadPerformanceData(),
      loadUserBehaviorData(),
      loadPopularActions(),
      loadDailyStats(),
      loadSystemInsights()
    ])
    ElMessage.success('数据刷新成功')
  } catch (error) {
    console.error('数据刷新失败:', error)
    ElMessage.error('数据刷新失败')
  } finally {
    refreshing.value = false
  }
}

const loadPerformanceData = async () => {
  loadingPerformance.value = true
  try {
    const response = await analyticsApi.getPerformanceAnalytics(parseInt(timeRange.value))
    if (response.success && response.analytics) {
      Object.assign(performanceData, response.analytics)
    }
  } catch (error) {
    console.error('加载性能数据失败:', error)
  } finally {
    loadingPerformance.value = false
  }
}

const loadUserBehaviorData = async () => {
  loadingUserBehavior.value = true
  try {
    const response = await analyticsApi.getUserBehaviorAnalytics()
    if (response.success && response.user_analytics) {
      Object.assign(userBehaviorData, response.user_analytics)
    }
  } catch (error) {
    console.error('加载用户行为数据失败:', error)
  } finally {
    loadingUserBehavior.value = false
  }
}

const loadPopularActions = async () => {
  loadingPopularActions.value = true
  try {
    const days = Math.round(parseInt(timeRange.value) / 24)
    const response = await analyticsApi.getPopularActions(days)
    if (response.success && response.popular_actions) {
      popularActions.value = response.popular_actions
    }
  } catch (error) {
    console.error('加载热门操作数据失败:', error)
  } finally {
    loadingPopularActions.value = false
  }
}

const loadDailyStats = async () => {
  loadingDailyStats.value = true
  try {
    const response = await analyticsApi.getDailyStats()
    if (response.success && response.daily_stats) {
      dailyStats.value = response.daily_stats
    }
  } catch (error) {
    console.error('加载每日统计数据失败:', error)
  } finally {
    loadingDailyStats.value = false
  }
}

const loadSystemInsights = async () => {
  try {
    const response = await analyticsApi.getSystemInsights()
    if (response.success && response.system_insights) {
      Object.assign(systemInsights, response.system_insights)
    }
  } catch (error) {
    console.error('加载系统洞察数据失败:', error)
  }
}

const onTimeRangeChange = () => {
  refreshAllData()
}

// 辅助方法
const getHealthCardClass = () => {
  return systemInsights.overall_health === 'good' ? 'health-good' : 'health-warning'
}

const getHealthTagType = () => {
  return systemInsights.overall_health === 'good' ? 'success' : 'warning'
}

const getErrorRateClass = () => {
  const rate = performanceData.error_rate || 0
  if (rate > 5) return 'error'
  if (rate > 2) return 'warning'
  return 'success'
}

const getLoadClass = () => {
  const load = (performanceData.peak_server_load || 0) * 100
  if (load > 80) return 'error'
  if (load > 60) return 'warning'
  return 'success'
}

const getInsightIcon = (type: string) => {
  switch (type) {
    case 'warning': return Warning
    case 'info': return InfoFilled
    case 'suggestion': return CircleCheck
    default: return InfoFilled
  }
}

const getInsightTagType = (type: string) => {
  switch (type) {
    case 'warning': return 'warning'
    case 'info': return 'info'
    case 'suggestion': return 'success'
    default: return 'info'
  }
}

const getInsightTypeText = (type: string) => {
  switch (type) {
    case 'warning': return '警告'
    case 'info': return '信息'
    case 'suggestion': return '建议'
    default: return '信息'
  }
}

const getPriorityTagType = (priority: string) => {
  switch (priority) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'info'
    default: return 'info'
  }
}

const getPriorityText = (priority: string) => {
  switch (priority) {
    case 'high': return '高优先级'
    case 'medium': return '中优先级'
    case 'low': return '低优先级'
    default: return '普通'
  }
}

const getActionDisplayName = (actionType: string) => {
  const actionNames: Record<string, string> = {
    'login': '用户登录',
    'generate': '图片生成',
    'view_gallery': '查看画廊',
    'download': '下载图片',
    'favorite': '收藏操作'
  }
  return actionNames[actionType] || actionType
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.admin-dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.dashboard-title {
  margin: 0;
  color: #2c3e50;
  font-size: 28px;
  font-weight: 600;
}

.refresh-controls {
  display: flex;
  align-items: center;
}

.health-overview {
  margin-bottom: 24px;
}

.health-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.health-card.health-good {
  border-left: 4px solid #67c23a;
}

.health-card.health-warning {
  border-left: 4px solid #e6a23c;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.health-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.metric-item {
  text-align: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.metric-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.metric-value.primary {
  color: #409eff;
}

.metric-value.success {
  color: #67c23a;
}

.metric-value.warning {
  color: #e6a23c;
}

.metric-value.error {
  color: #f56c6c;
}

.insights-section {
  margin-bottom: 24px;
}

.insights-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.insight-item {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #dcdfe6;
}

.insight-item.high {
  border-left-color: #f56c6c;
  background: #fef0f0;
}

.insight-item.medium {
  border-left-color: #e6a23c;
  background: #fdf6ec;
}

.insight-item.low {
  border-left-color: #909399;
  background: #f4f4f5;
}

.insight-icon {
  margin-right: 12px;
  margin-top: 2px;
  font-size: 18px;
}

.insight-content {
  flex: 1;
}

.insight-message {
  font-size: 16px;
  margin-bottom: 8px;
  color: #2c3e50;
}

.insight-meta {
  display: flex;
  gap: 8px;
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.analytics-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.analytics-content {
  min-height: 200px;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.metric-row:last-child {
  border-bottom: none;
}

.popular-actions-list,
.daily-stats-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-item,
.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.action-name,
.stat-date {
  font-weight: 500;
  color: #2c3e50;
}

.action-count {
  font-weight: 600;
  color: #409eff;
}

.stat-details {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.stat-value {
  font-size: 12px;
  color: #606266;
}

.no-data {
  text-align: center;
  color: #909399;
  padding: 20px;
}

.user-stats-section {
  margin-bottom: 24px;
}

.user-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.categories-section h3 {
  margin: 0 0 16px 0;
  color: #2c3e50;
  font-size: 18px;
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

/* 触摸优化 */
.refresh-controls .el-button,
.refresh-controls .el-select,
.insight-item,
.analytics-card,
.stat-card {
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-dashboard {
    padding: 16px;
    max-width: 100%;
  }

  .dashboard-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
    margin-bottom: 20px;
  }

  .dashboard-title {
    font-size: 24px;
    text-align: center;
    margin-bottom: 0;
  }

  .refresh-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .refresh-controls .el-button {
    height: 48px;
    font-size: 16px;
    border-radius: 24px;
  }

  .refresh-controls .el-select {
    width: 100% !important;
  }

  .refresh-controls .el-select .el-input__wrapper {
    height: 48px;
    border-radius: 24px;
  }

  /* 健康状态卡片优化 */
  .health-overview {
    margin-bottom: 20px;
  }

  .health-card {
    border-radius: 12px;
  }

  .health-metrics {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .metric-item {
    padding: 12px;
    min-height: 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  .metric-label {
    font-size: 12px;
    margin-bottom: 6px;
  }

  .metric-value {
    font-size: 18px;
  }

  /* 洞察部分优化 */
  .insights-section {
    margin-bottom: 20px;
  }

  .insight-item {
    padding: 12px;
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .insight-icon {
    align-self: flex-start;
    margin-right: 0;
    margin-bottom: 4px;
  }

  .insight-message {
    font-size: 14px;
    line-height: 1.4;
  }

  .insight-meta {
    flex-wrap: wrap;
    gap: 6px;
  }

  /* 分析网格优化 */
  .analytics-grid {
    grid-template-columns: 1fr;
    gap: 16px;
    margin-bottom: 20px;
  }

  .analytics-card {
    border-radius: 12px;
  }

  .analytics-content {
    min-height: auto;
    padding: 0;
  }

  .metric-row {
    padding: 10px 0;
  }

  .metric-row .metric-label {
    font-size: 13px;
    flex: 1;
  }

  .metric-row .metric-value {
    font-size: 16px;
    text-align: right;
  }

  .popular-actions-list,
  .daily-stats-list {
    gap: 8px;
  }

  .action-item,
  .stat-item {
    padding: 10px;
    flex-direction: column;
    align-items: stretch;
    gap: 6px;
  }

  .action-name,
  .stat-date {
    font-size: 14px;
  }

  .action-count {
    font-size: 16px;
    text-align: right;
  }

  .stat-details {
    align-items: stretch;
    flex-direction: column;
    gap: 2px;
  }

  .stat-value {
    font-size: 12px;
    text-align: left;
  }

  /* 用户统计优化 */
  .user-stats-section {
    margin-bottom: 20px;
  }

  .user-stats-grid {
    grid-template-columns: 1fr;
    gap: 12px;
    margin-bottom: 20px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-number {
    font-size: 28px;
    margin-bottom: 6px;
  }

  .stat-label {
    font-size: 13px;
  }

  .categories-section h3 {
    font-size: 16px;
    margin-bottom: 12px;
  }

  .categories-list {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .category-item {
    padding: 10px 12px;
  }

  .category-name {
    font-size: 14px;
  }

  .category-count {
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .admin-dashboard {
    padding: 12px;
  }

  .dashboard-title {
    font-size: 22px;
  }

  .refresh-controls .el-button {
    height: 44px;
    font-size: 15px;
  }

  .refresh-controls .el-select .el-input__wrapper {
    height: 44px;
  }

  .health-metrics {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .metric-item {
    min-height: 70px;
    padding: 10px;
  }

  .metric-value {
    font-size: 16px;
  }

  .insight-item {
    padding: 10px;
  }

  .insight-message {
    font-size: 13px;
  }

  .analytics-grid {
    gap: 12px;
  }

  .metric-row {
    flex-direction: column;
    align-items: stretch;
    gap: 4px;
    padding: 8px 0;
  }

  .metric-row .metric-value {
    text-align: left;
    font-size: 15px;
  }

  .stat-card {
    padding: 14px;
  }

  .stat-number {
    font-size: 24px;
  }

  .stat-label {
    font-size: 12px;
  }
}

@media (max-width: 360px) {
  .admin-dashboard {
    padding: 10px;
  }

  .dashboard-title {
    font-size: 20px;
  }

  .refresh-controls .el-button {
    height: 42px;
    font-size: 14px;
  }

  .metric-item {
    min-height: 65px;
    padding: 8px;
  }

  .metric-value {
    font-size: 15px;
  }

  .insight-message {
    font-size: 12px;
  }

  .stat-card {
    padding: 12px;
  }

  .stat-number {
    font-size: 22px;
  }
}

/* 横屏模式优化 */
@media (max-height: 600px) and (orientation: landscape) {
  .admin-dashboard {
    padding: 8px 12px;
  }

  .dashboard-header {
    margin-bottom: 12px;
  }

  .dashboard-title {
    font-size: 20px;
  }

  .health-overview,
  .insights-section,
  .analytics-grid,
  .user-stats-section {
    margin-bottom: 12px;
  }

  .health-metrics {
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }

  .metric-item {
    min-height: 60px;
    padding: 8px;
  }

  .metric-value {
    font-size: 14px;
  }

  .insight-item {
    padding: 8px;
  }

  .analytics-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }

  .user-stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .stat-card {
    padding: 10px;
  }

  .stat-number {
    font-size: 20px;
    margin-bottom: 4px;
  }

  .stat-label {
    font-size: 11px;
  }
}
</style>