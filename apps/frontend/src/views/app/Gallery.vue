<template>
  <div class="gallery-container">
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
    <div class="gallery-content" v-loading="loading">
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
                fit="contain"
                class="creation-image"
                @click="viewImage(creation)"
                loading="lazy"
              >
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

    <!-- 分页 -->
    <div class="pagination-container" v-if="creations.length > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 36, 48]"
        :total="totalCount"
        layout="total, sizes, prev, pager, next"
        @size-change="handlePageSizeChange"
        @current-change="handlePageChange"
      />
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Picture, Star, StarFilled, Download, MagicStick } from '@element-plus/icons-vue'
import { galleryApi } from '@/services/api'
import type { Creation, GalleryStats, GalleryFilters } from '@shared/index'

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

// 分页
const currentPage = ref(1)
const pageSize = ref(12)
const totalCount = ref(0)

// 图片查看器
const imageViewerVisible = ref(false)
const currentImage = ref<Creation | null>(null)

// 防抖搜索
let searchTimeout: NodeJS.Timeout

// 加载画廊数据
const loadGallery = async () => {
  loading.value = true
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
      creations.value = response.creations || []
      stats.value = response.stats
      totalCount.value = response.stats?.total || 0
    } else {
      ElMessage.error(response.error || '加载画廊失败')
    }
  } catch (error) {
    console.error('Load gallery error:', error)
    ElMessage.error('加载画廊失败')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadGallery()
  }, 500)
}

// 筛选处理
const handleFilter = () => {
  currentPage.value = 1
  loadGallery()
}

// 分页处理
const handlePageChange = (page: number) => {
  currentPage.value = page
  loadGallery()
}

const handlePageSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadGallery()
}

// 切换收藏状态
const toggleFavorite = async (creation: Creation) => {
  try {
    const newFavoriteStatus = !creation.is_favorite
    // 这里应该调用API更新收藏状态
    // const response = await galleryApi.updateFavorite(creation.id, newFavoriteStatus)

    // 临时更新本地状态
    creation.is_favorite = newFavoriteStatus
    ElMessage.success(newFavoriteStatus ? '已添加到收藏' : '已取消收藏')

    // 如果当前在收藏筛选模式下，且取消收藏，则从列表中移除
    if (showFavoritesOnly.value && !newFavoriteStatus) {
      loadGallery()
    }
  } catch (error) {
    console.error('Toggle favorite error:', error)
    ElMessage.error('操作失败')
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

// 组件挂载时加载数据
onMounted(() => {
  loadGallery()
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

.creation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.creation-card {
  transition: transform 0.3s ease;
}

.creation-card:hover {
  transform: translateY(-4px);
}

.image-card {
  border-radius: 12px;
  overflow: hidden;
}

.image-container {
  position: relative;
  overflow: hidden;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  max-height: 300px;
}

.creation-image {
  width: 100%;
  height: auto;
  max-height: 300px;
  cursor: pointer;
  transition: transform 0.3s ease;
  display: block;
}

.creation-image:hover {
  transform: scale(1.02);
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

.image-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-container:hover .image-overlay {
  opacity: 1;
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

/* 分页 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 40px;
  padding: 20px 0;
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
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
  }

  .image-card {
    border-radius: 12px;
  }

  .image-container {
    min-height: 180px;
    max-height: 280px;
  }

  .creation-image {
    max-height: 280px;
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
    top: 8px;
    right: 8px;
    gap: 6px;
  }

  .image-overlay .el-button {
    width: 36px;
    height: 36px;
    min-height: 36px;
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

  .pagination-container {
    margin-top: 30px;
    padding: 16px 0;
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
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .image-container {
    min-height: 200px;
    max-height: 320px;
  }

  .creation-image {
    max-height: 320px;
  }

  .image-overlay {
    top: 6px;
    right: 6px;
    gap: 4px;
  }

  .image-overlay .el-button {
    width: 32px;
    height: 32px;
    min-height: 32px;
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

  .pagination-container {
    margin-top: 20px;
    padding: 12px 0;
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
    min-height: 180px;
    max-height: 280px;
  }

  .creation-image {
    max-height: 280px;
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
    gap: 8px;
  }

  .image-container {
    min-height: 120px;
    max-height: 200px;
  }

  .creation-image {
    max-height: 200px;
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
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 24px;
  }

  .creation-image {
    height: 240px;
  }
}
</style>