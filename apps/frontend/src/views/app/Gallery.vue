<template>
  <div class="gallery-container">
    <!-- 动态渐变背景 -->
    <AnimatedBackground />
    
    <!-- 页面标题和统计信息 -->
    <div class="gallery-header">
      <h1 class="gallery-title">我的作品画廊</h1>
      <div class="stats-cards" v-if="stats">
        <el-card class="stat-card">
          <div class="stat-item">
            <span class="stat-value">{{ stats.total }}</span>
            <span class="stat-label">总作品</span>
          </div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-item">
            <span class="stat-value">{{ stats.favorites || 0 }}</span>
            <span class="stat-label">收藏</span>
          </div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-item">
            <span class="stat-value">{{ stats.recent_week || 0 }}</span>
            <span class="stat-label">本周新增</span>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 搜索和筛选栏 -->
    <div class="filter-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索作品..."
        clearable
        class="search-input"
        @input="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <div class="filter-controls">
        <el-select
          v-model="selectedCategory"
          placeholder="选择分类"
          clearable
          @change="handleFilter"
          class="category-select"
        >
          <el-option label="全部分类" value="all" />
          <el-option
            v-for="category in availableCategories"
            :key="category"
            :label="category"
            :value="category"
          />
        </el-select>

        <el-checkbox
          v-model="showFavoritesOnly"
          @change="handleFilter"
        >
          仅显示收藏
        </el-checkbox>
      </div>
    </div>

    <!-- 作品展示区域 -->
    <div class="gallery-content" ref="galleryContent" v-loading="loading">
      <div v-if="creations.length > 0" class="creation-grid">
        <div
          v-for="creation in creations"
          :key="creation.id"
          class="creation-card"
        >
          <el-card class="image-card" shadow="hover">
            <!-- 图片 -->
            <div class="image-container">
              <el-image
                :src="creation.image_url"
                fit="cover"
                class="creation-image"
                @click="viewImage(creation)"
                loading="lazy"
              >
                <template #placeholder>
                  <div class="image-skeleton">
                    <el-skeleton-item variant="image" style="width: 100%; height: 100%;" />
                  </div>
                </template>
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                    <span>图片加载失败</span>
                  </div>
                </template>
              </el-image>

              <!-- 操作按钮 -->
              <div class="image-overlay">
                <el-button
                  :type="creation.is_favorite ? 'danger' : 'info'"
                  :icon="creation.is_favorite ? StarFilled : Star"
                  circle
                  size="small"
                  @click.stop="toggleFavorite(creation)"
                />
                <el-button
                  type="success"
                  :icon="MagicStick"
                  circle
                  size="small"
                  @click.stop="reuseForImageToImage(creation)"
                  title="图生图复用"
                />
                <el-button
                  type="primary"
                  :icon="Download"
                  circle
                  size="small"
                  @click.stop="downloadImage(creation)"
                />
                <el-button
                  type="danger"
                  :icon="Delete"
                  circle
                  size="small"
                  @click.stop="deleteCreation(creation)"
                  title="删除作品"
                />
              </div>
            </div>

            <!-- 作品信息 -->
            <div class="card-content">
              <p class="prompt-text" :title="creation.prompt">
                {{ creation.prompt }}
              </p>
              <div class="creation-meta">
                <el-tag v-if="creation.model_used" size="small" type="info">
                  {{ creation.model_used }}
                </el-tag>
                <span class="creation-date">
                  {{ formatDate(creation.created_at) }}
                </span>
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty
        v-else-if="!loading"
        description="暂无作品"
        class="empty-state"
      >
        <el-button type="primary" @click="$router.push('/app')">
          开始创作
        </el-button>
      </el-empty>
    </div>

    <!-- 无限滚动加载提示 -->
    <div class="infinite-scroll-status" v-if="creations.length > 0">
      <div v-if="isLoadingMore" class="loading-more">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>正在加载更多...</span>
      </div>
      <div v-else-if="!hasMore" class="no-more">
        <span>已加载全部 {{ totalCount }} 张作品</span>
      </div>
    </div>

    <!-- 图片查看器 -->
    <el-dialog
      v-model="imageViewerVisible"
      :title="currentImage?.prompt"
      width="90%"
      top="5vh"
      center
      class="image-viewer-dialog"
    >
      <div class="image-viewer-content" v-if="currentImage">
        <div class="viewer-image-wrapper">
          <el-image
            :src="currentImage.image_url"
            fit="contain"
            class="viewer-image"
            :preview-src-list="[currentImage.image_url]"
            :initial-index="0"
            preview-teleported
          >
            <template #error>
              <div class="image-error">
                <el-icon><Picture /></el-icon>
                <span>图片加载失败</span>
              </div>
            </template>
          </el-image>
        </div>
        <div class="image-details">
          <div class="detail-item">
            <span class="label">提示词:</span>
            <span class="value">{{ currentImage.prompt }}</span>
          </div>
          <div class="detail-item">
            <span class="label">模型:</span>
            <span class="value">{{ currentImage.model_used }}</span>
          </div>
          <div class="detail-item">
            <span class="label">尺寸:</span>
            <span class="value">{{ currentImage.size }}</span>
          </div>
          <div class="detail-item">
            <span class="label">创建日期:</span>
            <span class="value">{{ formatDate(currentImage.created_at) }}</span>
          </div>
          <div class="detail-actions">
            <el-button type="primary" :icon="Download" @click="downloadImage(currentImage)">
              下载图片
            </el-button>
            <el-button type="success" :icon="MagicStick" @click="reuseForImageToImage(currentImage)">
              图生图复用
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Picture, Star, StarFilled, Download, MagicStick, Delete, Loading } from '@element-plus/icons-vue'
import { useInfiniteScroll } from '@vueuse/core'
import { galleryApi } from '@/services/api'
import type { Creation, GalleryStats, GalleryFilters } from '@shared/index'
import AnimatedBackground from '@/components/common/AnimatedBackground.vue'

// 路由
const router = useRouter()

// 响应式数据
const loading = ref(false)
const creations = ref<Creation[]>([])
const stats = ref<GalleryStats | null>(null)
const availableCategories = ref<string[]>([])

// 筛选和搜索
const searchKeyword = ref('')
const selectedCategory = ref<string>('all')
const showFavoritesOnly = ref(false)

// 分页（改为无限滚动模式）
const currentPage = ref(1)
const pageSize = ref(24) // 每次加载更多
const totalCount = ref(0)
const hasMore = ref(true) // 是否还有更多数据
const isLoadingMore = ref(false) // 是否正在加载更多

// 图片查看器
const imageViewerVisible = ref(false)
const currentImage = ref<Creation | null>(null)

// 防抖搜索
let searchTimeout: number | undefined

// 滚动容器引用（用于无限滚动）
const galleryContent = ref<HTMLElement | null>(null)

// 加载画廊数据（支持无限滚动）
const loadGallery = async (append: boolean = false) => {
  if (append) {
    isLoadingMore.value = true
  } else {
    loading.value = true
  }
  
  try {
    const filters: GalleryFilters = {
      page: currentPage.value,
      per_page: pageSize.value
    }

    if (searchKeyword.value.trim()) {
      filters.search = searchKeyword.value.trim()
    }

    if (selectedCategory.value && selectedCategory.value !== 'all') {
      filters.category = selectedCategory.value
    }

    if (showFavoritesOnly.value) {
      filters.is_favorite = true
    }

    const response = await galleryApi.getCreations(filters)

    if (response.success) {
      const newCreations = response.creations || []
      
      if (append) {
        // 无限滚动模式：追加数据
        creations.value.push(...newCreations)
      } else {
        // 初始加载或筛选：替换数据
        creations.value = newCreations
      }
      
      stats.value = response.stats
      totalCount.value = response.stats?.total || 0
      
      // 检查是否还有更多数据
      hasMore.value = creations.value.length < totalCount.value
    } else {
      ElMessage.error(response.error || '加载画廊失败')
    }
  } catch (error) {
    console.error('Load gallery error:', error)
    ElMessage.error('加载画廊失败')
  } finally {
    loading.value = false
    isLoadingMore.value = false
  }
}

// 加载更多数据（无限滚动）
const loadMore = async () => {
  if (isLoadingMore.value || loading.value || !hasMore.value) {
    return
  }
  
  currentPage.value++
  await loadGallery(true)
}

// 搜索处理
const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    creations.value = [] // 清空现有数据
    hasMore.value = true
    loadGallery()
  }, 500)
}

// 筛选处理
const handleFilter = () => {
  currentPage.value = 1
  creations.value = [] // 清空现有数据
  hasMore.value = true
  loadGallery()
}

// 切换收藏状态
const toggleFavorite = async (creation: Creation) => {
  try {
    const newFavoriteStatus = !creation.is_favorite
    
    // 直接调用API更新收藏状态
    const response = await galleryApi.updateFavorite(creation.id, newFavoriteStatus)
    
    if (response.success) {
      // 更新本地状态
      creation.is_favorite = newFavoriteStatus
      ElMessage.success(newFavoriteStatus ? '已添加到收藏' : '已取消收藏')
      
      // 更新统计数据
      if (stats.value) {
        if (newFavoriteStatus) {
          stats.value.favorites = (stats.value.favorites || 0) + 1
        } else {
          stats.value.favorites = Math.max(0, (stats.value.favorites || 0) - 1)
        }
      }
      
      // 如果当前在收藏筛选模式下，且取消收藏，则刷新列表
      if (showFavoritesOnly.value && !newFavoriteStatus) {
        await loadGallery()
      }
    } else {
      ElMessage.error(response.error || '收藏操作失败')
    }
  } catch (error) {
    console.error('Toggle favorite error:', error)
    ElMessage.error('操作失败，请稍后重试')
  }
}

// 查看图片
const viewImage = (creation: Creation) => {
  currentImage.value = creation
  imageViewerVisible.value = true
}

// 复用图片进行图生图
const reuseForImageToImage = async (creation: Creation) => {
  try {
    ElMessage.info('正在准备图生图模式...')

    // 跳转到生成页面，并传递参数
    router.push({
      path: '/app',
      query: {
        mode: 'image-to-image',
        referenceImage: creation.image_url,
        prompt: creation.prompt
      }
    })

    ElMessage.success('已切换到图生图模式，参考图片正在加载中...')
  } catch (error) {
    console.error('Reuse image error:', error)
    ElMessage.error('复用失败，请稍后重试')
  }
}

// 下载图片
const downloadImage = async (creation: Creation) => {
  try {
    const response = await fetch(creation.image_url)
    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)

    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `creation-${creation.id}-${Date.now()}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    window.URL.revokeObjectURL(downloadUrl)
    ElMessage.success('开始下载')
  } catch (error) {
    console.error('Download error:', error)
    ElMessage.error('下载失败')
  }
}

// 删除作品
const deleteCreation = async (creation: Creation) => {
  try {
    // 二次确认对话框
    await ElMessageBox.confirm(
      '确定要删除这张作品吗？此操作无法撤销。',
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    // 调用 API 删除作品
    const response = await galleryApi.deleteCreation(creation.id)

    if (response.success) {
      ElMessage.success('作品已删除')
      
      // 从本地状态移除作品
      const index = creations.value.findIndex(c => c.id === creation.id)
      if (index > -1) {
        creations.value.splice(index, 1)
      }
      
      // 更新统计数据
      if (stats.value) {
        stats.value.total--
        // 如果是收藏作品，同时减少收藏数
        if (creation.is_favorite && stats.value.favorites) {
          stats.value.favorites--
        }
      }
      
      // 如果删除后当前页面为空且不是第一页，返回上一页
      if (creations.value.length === 0 && currentPage.value > 1) {
        currentPage.value--
        await loadGallery()
      }
    } else {
      ElMessage.error(response.error || '删除失败，请稍后重试')
    }
  } catch (error) {
    // 用户取消删除操作，不做任何提示
    if (error !== 'cancel') {
      console.error('删除作品失败:', error)
      ElMessage.error('删除失败，请稍后重试')
    }
  }
}

// 格式化日期
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 组件挂载时加载数据并设置无限滚动
onMounted(() => {
  loadGallery()
  
  // 设置无限滚动
  if (galleryContent.value) {
    useInfiniteScroll(
      galleryContent.value,
      loadMore,
      { distance: 300 } // 距离底部 300px 时触发加载
    )
  }
})
</script>

<style scoped>
.gallery-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}

/* 页面标题和统计信息 */
.gallery-header {
  margin-bottom: 30px;
  text-align: center;
}

.gallery-title {
  font-size: 2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 20px 0;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
  max-width: 400px;
  margin: 0 auto;
}

.stat-card {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.stat-item {
  text-align: center;
  padding: 10px;
}

.stat-value {
  display: block;
  font-size: 1.8rem;
  font-weight: bold;
  color: #409eff;
  line-height: 1;
}

.stat-label {
  display: block;
  font-size: 0.875rem;
  color: #909399;
  margin-top: 5px;
}

/* 搜索和筛选栏 */
.filter-bar {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
  border: 1px solid #e9ecef;
}

.search-input {
  width: 100%;
  margin-bottom: 15px;
}

.filter-controls {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.category-select {
  min-width: 150px;
}

/* 作品展示区域 */
.gallery-content {
  min-height: 400px;
}

/* 瀑布流布局 - CSS Column实现 */
.creation-grid {
  column-count: 3;
  column-gap: var(--spacing-lg);
}

.creation-card {
  /* 防止卡片被拆分到多列 */
  break-inside: avoid;
  page-break-inside: avoid;
  -webkit-column-break-inside: avoid;
  margin-bottom: var(--spacing-lg);
  transition: transform 0.3s ease;
  display: inline-block;
  width: 100%;
}

.creation-card:hover {
  transform: translateY(-4px);
}

.image-card {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur) var(--glass-saturate);
  -webkit-backdrop-filter: var(--glass-blur) var(--glass-saturate);
  border: 1px solid var(--glass-border);
  box-shadow: 
    0 8px 32px 0 rgba(102, 126, 234, 0.12),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 渐变遮罩层 */
.image-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.1), 
    rgba(118, 75, 162, 0.1));
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 1;
  pointer-events: none;
}

.image-card:hover::before {
  opacity: 1;
}

.image-card:hover {
  transform: translateY(-12px) scale(1.02);
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.15),
    0 0 40px rgba(102, 126, 234, 0.2),
    0 0 0 1px rgba(255, 255, 255, 0.7) inset;
}

.image-container {
  position: relative;
  overflow: hidden;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 280px;
}

.creation-image {
  width: 100%;
  height: 100%;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  display: block;
  object-fit: cover;
  image-rendering: -webkit-optimize-contrast;
}

/* 图片加载淡入动画 */
.creation-image :deep(img) {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 骨架屏样式 */
.image-skeleton {
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    background-position: -100% 0;
  }
  100% {
    background-position: 100% 0;
  }
}

/* 图片悬停缩放和滤镜效果 */
.image-card:hover .creation-image {
  transform: scale(1.08);
  filter: brightness(1.05) contrast(1.05) saturate(1.15);
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  background: #f5f7fa;
  color: #909399;
}

.image-error .el-icon {
  font-size: 2rem;
  margin-bottom: 8px;
}

/* 毛玻璃操作栏 */
.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border-top: 1px solid rgba(255, 255, 255, 0.3);
  transform: translateY(100%);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 2;
}

.image-container:hover .image-overlay {
  transform: translateY(0);
}

.image-overlay .el-button {
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.9);
  border: none;
}

.image-overlay .el-button--success {
  background: rgba(103, 194, 58, 0.9);
  color: white;
}

.image-overlay .el-button--success:hover {
  background: rgba(103, 194, 58, 1);
  transform: scale(1.1);
}

/* 删除按钮样式 (danger) */
.image-overlay .el-button--danger {
  background: rgba(245, 108, 108, 0.9);
  color: white;
  border: none;
}

.image-overlay .el-button--danger:hover {
  background: rgba(245, 108, 108, 1);
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(245, 108, 108, 0.4);
}

/* 下载按钮样式 (primary) */
.image-overlay .el-button--primary {
  background: rgba(64, 158, 255, 0.9);
  color: white;
  border: none;
}

.image-overlay .el-button--primary:hover {
  background: rgba(64, 158, 255, 1);
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

/* 收藏按钮样式 (info) */
.image-overlay .el-button--info {
  background: rgba(144, 147, 153, 0.9);
  color: white;
  border: none;
}

.image-overlay .el-button--info:hover {
  background: rgba(144, 147, 153, 1);
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(144, 147, 153, 0.4);
}

.card-content {
  padding: 15px;
}

.prompt-text {
  font-size: 0.875rem;
  color: #2c3e50;
  line-height: 1.4;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  cursor: help;
}

.creation-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.creation-date {
  font-size: 0.75rem;
  color: #909399;
}

/* 空状态 */
.empty-state {
  margin: 60px 0;
}

/* 无限滚动状态 */
.infinite-scroll-status {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
  margin-top: 20px;
}

.loading-more {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #409eff;
  font-size: 14px;
  font-weight: 500;
}

.loading-more .el-icon {
  font-size: 18px;
}

.no-more {
  color: #909399;
  font-size: 14px;
  text-align: center;
  padding: 20px;
  border-top: 1px dashed #e4e7ed;
  width: 100%;
}

/* 图片查看器 */
.image-viewer-dialog :deep(.el-dialog__body) {
  padding: 20px;
  max-height: 85vh;
  overflow-y: auto;
}

.image-viewer-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.viewer-image-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
  min-height: 300px;
}

.viewer-image {
  max-width: 100%;
  max-height: 65vh;
  height: auto;
  width: auto;
  display: block;
  margin: 0 auto;
}

.viewer-image :deep(img) {
  max-width: 100%;
  max-height: 65vh;
  height: auto;
  width: auto;
  object-fit: contain;
}

.image-details {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.detail-item {
  display: flex;
  margin-bottom: 12px;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-item .label {
  font-weight: 600;
  color: #606266;
  min-width: 80px;
  margin-right: 10px;
}

.detail-item .value {
  color: #2c3e50;
  flex: 1;
  word-break: break-word;
}

.detail-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.detail-actions .el-button {
  flex: 1;
}

/* 触摸优化 */
.el-button,
.el-input,
.el-select,
.el-checkbox,
.creation-image {
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .gallery-container {
    padding: 16px;
  }

  .gallery-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
    margin-bottom: 20px;
  }

  .gallery-title {
    font-size: 24px;
    text-align: center;
    margin-bottom: 0;
  }

  .stats-cards {
    max-width: 100%;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }

  .stat-card {
    border-radius: 8px;
  }

  .stat-item {
    padding: 12px 8px;
  }

  .stat-value {
    font-size: 20px;
  }

  .stat-label {
    font-size: 12px;
  }

  .filter-bar {
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 20px;
  }

  .search-input {
    margin-bottom: 16px;
  }

  .search-input .el-input__wrapper {
    height: 44px;
    border-radius: 22px;
  }

  .filter-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .category-select {
    width: 100%;
  }

  .category-select .el-input__wrapper {
    height: 44px;
    border-radius: 22px;
  }

  .el-checkbox {
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: white;
    border: 1px solid #dcdfe6;
    border-radius: 22px;
    padding: 0 16px;
    font-size: 15px;
  }

  .creation-grid {
    column-count: 2;
    column-gap: var(--spacing-md);
  }

  .image-card {
    border-radius: 12px;
  }

  .image-container {
    height: 240px;
  }

  .viewer-image-wrapper {
    padding: 15px;
    min-height: 250px;
  }

  .viewer-image {
    max-height: 60vh;
  }

  .viewer-image :deep(img) {
    max-height: 60vh;
  }

  .detail-actions {
    flex-direction: column;
    gap: 10px;
  }

  .detail-actions .el-button {
    width: 100%;
  }

  .image-overlay {
    position: absolute;
    top: 8px;
    right: 8px;
    bottom: auto;
    left: auto;
    gap: 6px;
    transform: translateY(0) !important;
    flex-direction: column;
    padding: 8px;
    background: transparent;
    backdrop-filter: none;
    border: none;
  }

  .image-overlay .el-button {
    width: 36px;
    height: 36px;
    min-height: 36px;
    backdrop-filter: blur(8px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }

  .card-content {
    padding: 12px;
  }

  .prompt-text {
    font-size: 14px;
    margin-bottom: 8px;
  }

  .creation-meta .el-tag {
    font-size: 12px;
    height: 24px;
  }

  .creation-date {
    font-size: 11px;
  }

  .empty-state {
    margin: 40px 0;
  }

  .empty-state .el-button {
    height: 48px;
    font-size: 16px;
    border-radius: 24px;
    padding: 0 32px;
  }

  .infinite-scroll-status {
    padding: 30px 16px;
    margin-top: 16px;
  }
}

@media (max-width: 480px) {
  .gallery-container {
    padding: 12px;
  }

  .gallery-title {
    font-size: 22px;
  }

  .stats-cards {
    gap: 8px;
  }

  .stat-item {
    padding: 10px 6px;
  }

  .stat-value {
    font-size: 18px;
  }

  .stat-label {
    font-size: 11px;
  }

  .filter-bar {
    padding: 12px;
    margin-bottom: 16px;
  }

  .search-input {
    margin-bottom: 12px;
  }

  .filter-controls {
    gap: 10px;
  }

  .el-checkbox {
    height: 40px;
    font-size: 14px;
    padding: 0 12px;
  }

  .creation-grid {
    column-count: 1;
    column-gap: 0;
  }

  .image-container {
    height: 300px;
  }

  .image-overlay {
    top: 6px;
    right: 6px;
    gap: 4px;
    transform: translateY(0) !important;
  }

  .image-overlay .el-button {
    width: 32px;
    height: 32px;
    min-height: 32px;
    padding: 0;
  }

  .card-content {
    padding: 10px;
  }

  .prompt-text {
    font-size: 13px;
    line-height: 1.3;
  }

  .creation-meta .el-tag {
    font-size: 11px;
    height: 22px;
  }

  .creation-date {
    font-size: 10px;
  }

  .empty-state {
    margin: 30px 0;
  }

  .empty-state .el-button {
    height: 44px;
    font-size: 15px;
    border-radius: 22px;
  }

  .infinite-scroll-status {
    padding: 20px 12px;
    margin-top: 12px;
  }
}

@media (max-width: 360px) {
  .gallery-container {
    padding: 10px;
  }

  .gallery-title {
    font-size: 20px;
  }

  .stats-cards {
    gap: 6px;
  }

  .stat-item {
    padding: 8px 4px;
  }

  .stat-value {
    font-size: 16px;
  }

  .filter-bar {
    padding: 10px;
  }

  .image-container {
    height: 260px;
  }

  .card-content {
    padding: 8px;
  }

  .empty-state .el-button {
    height: 42px;
    font-size: 14px;
  }
}

/* 横屏模式优化 */
@media (max-height: 600px) and (orientation: landscape) {
  .gallery-container {
    padding: 8px;
  }

  .gallery-title {
    font-size: 18px;
    margin-bottom: 8px;
  }

  .stats-cards {
    margin-bottom: 12px;
  }

  .filter-bar {
    padding: 8px 12px;
    margin-bottom: 12px;
  }

  .search-input {
    margin-bottom: 8px;
  }

  .filter-controls {
    gap: 8px;
  }

  .creation-grid {
    column-count: 1;
    column-gap: 0;
  }

  .image-container {
    height: 180px;
  }

  .card-content {
    padding: 6px;
  }

  .empty-state {
    margin: 20px 0;
  }
}

/* 大屏幕优化 */
@media (min-width: 1200px) {
  .gallery-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 32px;
  }

  .creation-grid {
    column-count: 4;
    column-gap: var(--spacing-xl);
  }

  .image-container {
    height: 300px;
  }
}
</style>