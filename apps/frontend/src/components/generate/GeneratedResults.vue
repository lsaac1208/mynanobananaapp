<template>
  <el-card v-if="results.length > 0" class="results glass-card">
    <template #header>
      <div class="results-header">
        <span>生成结果 ({{ results.length }})</span>
        <div class="header-actions">
          <el-button size="small" @click="handleDownloadAll">
            <el-icon><Download /></el-icon>
            全部下载
          </el-button>
          <el-button size="small" @click="handleClear" text type="danger">
            清空
          </el-button>
        </div>
      </div>
    </template>

    <div class="results-grid">
      <div
        v-for="(image, index) in results"
        :key="index"
        class="result-item glass-card"
      >
        <div class="result-image-container">
          <img
            :src="image.url"
            :alt="`生成的图片 ${index + 1}`"
            class="result-image"
            @click="handlePreview(image)"
          />
          
          <!-- 操作栏 -->
          <div class="result-overlay">
            <el-button
              circle
              size="small"
              @click="handleDownload(image)"
            >
              <el-icon><Download /></el-icon>
            </el-button>
            <el-button
              circle
              size="small"
              @click="handleSaveToGallery(image)"
            >
              <el-icon><FolderAdd /></el-icon>
            </el-button>
            <el-button
              circle
              size="small"
              @click="handleRegenerate(image)"
            >
              <el-icon><Refresh /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 改进的提示词 -->
        <div v-if="image.revised_prompt" class="revised-prompt">
          <el-tag size="small" type="info">改进提示词</el-tag>
          <p>{{ image.revised_prompt }}</p>
        </div>
      </div>
    </div>

    <!-- 图片预览对话框 -->
    <el-dialog
      v-model="previewVisible"
      title="图片预览"
      width="90%"
      :style="{ maxWidth: '1000px' }"
    >
      <img
        v-if="previewImage"
        :src="previewImage.url"
        alt="预览"
        style="width: 100%; height: auto;"
      />
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Download, FolderAdd, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { GeneratedImage } from '@shared/index'

// Props
const props = defineProps<{
  results: GeneratedImage[]
}>()

// Emits
const emit = defineEmits<{
  download: [image: GeneratedImage]
  downloadAll: []
  save: [image: GeneratedImage]
  regenerate: [image: GeneratedImage]
  clear: []
}>()

// Local state
const previewVisible = ref(false)
const previewImage = ref<GeneratedImage | null>(null)

// Methods
const handlePreview = (image: GeneratedImage) => {
  previewImage.value = image
  previewVisible.value = true
}

const handleDownload = (image: GeneratedImage) => {
  emit('download', image)
  ElMessage.success('开始下载图片')
}

const handleDownloadAll = () => {
  emit('downloadAll')
  ElMessage.success(`开始下载 ${props.results.length} 张图片`)
}

const handleSaveToGallery = (image: GeneratedImage) => {
  emit('save', image)
}

const handleRegenerate = (image: GeneratedImage) => {
  emit('regenerate', image)
}

const handleClear = () => {
  emit('clear')
}
</script>

<style scoped>
.results {
  margin-top: var(--spacing-lg);
  animation: slideInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--spacing-lg);
}

.result-item {
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.result-item:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.result-image-container {
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-md);
}

.result-image {
  width: 100%;
  height: auto;
  display: block;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.result-item:hover .result-image {
  transform: scale(1.05);
}

/* 操作栏 */
.result-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  transform: translateY(100%);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.result-image-container:hover .result-overlay {
  transform: translateY(0);
}

/* 改进的提示词 */
.revised-prompt {
  padding: var(--spacing-md);
}

.revised-prompt p {
  margin-top: var(--spacing-xs);
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .results-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
  
  .results-header {
    flex-direction: column;
    gap: var(--spacing-sm);
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .result-overlay {
    transform: translateY(0);
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

