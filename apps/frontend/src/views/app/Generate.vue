<template>
  <div class="generate-container">
    <!-- 动态渐变背景 -->
    <AnimatedBackground />
    
    <!-- 主布局：左右分栏 -->
    <div class="main-layout">
      
      <!-- 左侧控制面板 -->
      <div class="control-panel">
        <!-- 面板头部 -->
        <div class="panel-header">
          <h3 class="panel-title">
            {{ generateMode === 'text-to-image' ? 'AI生图' : '图生图' }}
          </h3>
          <el-tag type="info" size="small">
            剩余: {{ userStore.user?.credits || 0 }}
        </el-tag>
      </div>

        <!-- 模式切换 -->
        <div class="mode-switcher">
          <el-radio-group v-model="generateMode" size="default" @change="onModeChange">
            <el-radio-button value="text-to-image">文生图</el-radio-button>
            <el-radio-button value="image-to-image">图生图</el-radio-button>
          </el-radio-group>
        </div>

        <!-- 控制表单 -->
        <div class="control-form">
          <!-- 尺寸选择 -->
          <div class="form-group">
            <label class="form-label">尺寸</label>
            <el-select 
              v-model="textForm.size" 
              size="default"
              placeholder="选择尺寸"
            >
              <el-option
                v-for="size in availableSizes"
                :key="size"
                :label="size"
                :value="size"
              />
            </el-select>
          </div>

          <!-- 画质 -->
          <div class="form-group">
            <label class="form-label">画质</label>
            <el-select v-model="imageQuality" size="default">
              <el-option label="标准" value="standard" />
              <el-option label="高清" value="hd" />
            </el-select>
          </div>

          <!-- 数量 -->
          <div class="form-group">
            <label class="form-label">数量</label>
            <el-input-number
              v-model="textForm.n"
              :min="1"
              :max="4"
              size="default"
              controls-position="right"
            />
          </div>

          <!-- 提示词 -->
          <div class="form-group">
            <label class="form-label">提示词</label>
            <el-input
              v-model="textForm.prompt"
              type="textarea"
              :rows="6"
              placeholder="描述你想要生成的图片..."
              maxlength="1000"
              show-word-limit
            />
          </div>

          <!-- 图生图：参考图片上传 -->
          <div v-if="generateMode === 'image-to-image'" class="form-group">
            <label class="form-label">参考图片</label>
            <div class="image-upload-area">
              <!-- 已上传的图片缩略图 -->
              <div v-if="imageFileList.length > 0" class="uploaded-images">
                <div 
                  v-for="(file, idx) in imageFileList" 
                  :key="idx"
                  class="uploaded-thumb"
                >
                  <img :src="file.url" alt="参考图" />
                  <el-icon class="remove-icon" @click="handleImageRemove(file)">
                    <Close />
                  </el-icon>
                </div>
              </div>
              
              <!-- 上传按钮 -->
              <el-upload
                v-if="imageFileList.length < 4"
                ref="uploadRef"
                :auto-upload="false"
                :file-list="imageFileList"
                :on-change="handleImageChange"
                accept="image/*"
                :show-file-list="false"
                :limit="4"
              >
                <el-button 
                  type="default" 
                  :icon="Plus" 
                  class="upload-btn"
                  :disabled="isLoadingReferenceImage"
                >
                  上传图片
                </el-button>
              </el-upload>

              <!-- 从画廊选择 -->
              <el-button 
                type="primary" 
                :icon="Picture" 
                @click="openGallerySelector"
                :disabled="imageFileList.length >= 4 || isLoadingReferenceImage"
                class="gallery-btn"
                size="default"
              >
                从画廊选择
              </el-button>
            </div>
          </div>

          <!-- 生成按钮 -->
          <el-button
            type="primary"
            size="large"
            :loading="generating"
            :disabled="isGenerateDisabled || userStore.user?.credits === 0"
            @click="handleGenerate"
            class="generate-btn"
          >
            <template v-if="!generating">
              <el-icon><MagicStick /></el-icon>
              <span>生成图片</span>
            </template>
            <template v-else>
              生成中...
            </template>
          </el-button>
        </div>
      </div>

      <!-- 右侧预览区 -->
      <div class="preview-area">
        <!-- 空状态 -->
        <div v-if="generatedImages.length === 0 && !generating" class="empty-preview">
          <el-icon class="empty-icon"><Picture /></el-icon>
          <p class="empty-text">生成的图片将在这里显示</p>
        </div>

        <!-- 生成中状态 -->
        <div v-if="generating" class="generating-preview">
          <el-progress 
            type="circle" 
            :percentage="generationProgress" 
            :width="160"
            :stroke-width="6"
            :color="getProgressColor()"
          >
            <template #default>
              <div class="progress-content">
                <div class="remaining-time">
                  <span class="time-value">{{ Math.max(0, estimatedTime - elapsedTime) }}</span>
                  <span class="time-unit">秒</span>
                </div>
              </div>
            </template>
          </el-progress>
          <p class="generating-text">{{ currentStage }}</p>
          <el-button text @click="cancelGeneration" class="cancel-btn">取消</el-button>
        </div>

        <!-- 主图展示 -->
        <div v-if="generatedImages.length > 0 && !generating" class="main-image-display">
          <img 
            :src="currentDisplayImageThumbnail" 
            alt="生成结果" 
            class="main-image"
            loading="lazy"
            decoding="async"
            @click="previewImage(currentDisplayImage)"
            :title="'点击查看高清原图'"
          />
          
          <!-- 操作栏 -->
          <div class="image-actions-bar">
            <div class="action-group">
              <el-button :icon="Download" @click="downloadImage(currentDisplayImage, selectedImageIndex)">
                下载
              </el-button>
              <el-button 
                type="success" 
                :icon="MagicStick" 
                @click="continueWithImageToImage(currentDisplayImage)"
                class="reuse-btn"
              >
                复用到图生图
              </el-button>
            </div>
            <div class="image-info">
              <span>{{ textForm.size }} • {{ lastGenerationTime }}s</span>
            </div>
          </div>
        </div>

        <!-- 底部历史缩略图 -->
        <div v-if="generatedImages.length > 1 && !generating" class="history-thumbnails">
          <div 
            v-for="(image, index) in generatedImages" 
            :key="index"
            class="history-thumb"
            :class="{ active: selectedImageIndex === index }"
            @click="selectImage(index)"
            :title="`图片 ${index + 1}`"
          >
            <img 
              :src="image.thumbnailUrl || image.url" 
              :alt="`图片 ${index + 1}`"
              loading="lazy"
              decoding="async"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 旧的部分暂时保留（后面会移除）-->
    <div style="display:none">
    <!-- 生成模式选择 -->
    <el-card class="mode-selector">
      <template #header>
        <div class="mode-header">
          <span>选择生成模式</span>
          <el-tag type="info" size="small">
            {{ generateMode === 'text-to-image' ? '使用文字描述生成图片' : '使用参考图片+文字描述生成新图片' }}
          </el-tag>
        </div>
      </template>
      <el-radio-group v-model="generateMode" size="large" @change="onModeChange">
        <el-radio-button label="text-to-image">📝 文生图</el-radio-button>
        <el-radio-button label="image-to-image">🎨 图生图</el-radio-button>
      </el-radio-group>
    </el-card>

    <!-- 文生图表单 -->
    <el-card v-if="generateMode === 'text-to-image'" class="generate-form">
      <template #header>
        <span>文生图设置</span>
      </template>

      <el-form ref="textFormRef" :model="textForm" :rules="textFormRules" label-width="80px">
        <el-form-item label="提示词" prop="prompt">
          <el-input
            v-model="textForm.prompt"
            type="textarea"
            :rows="4"
            placeholder="描述你想要生成的图片，例如：一只可爱的橙色小猫在花园里玩耍"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="画质">
              <el-select v-model="imageQuality" placeholder="选择画质">
                <el-option label="标准" value="standard" />
                <el-option label="高清" value="hd" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="尺寸">
              <el-select v-model="textForm.size" placeholder="选择尺寸">
                <el-option
                  v-for="size in availableSizes"
                  :key="size"
                  :label="size"
                  :value="size"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="数量">
              <el-input-number
                v-model="textForm.n"
                :min="1"
                :max="4"
                placeholder="1-4张"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button
            type="primary"
            :loading="generating"
            :disabled="!textForm.prompt || userStore.user?.credits === 0"
            @click="generateTextToImage"
          >
            {{ generating ? 'AI正在创作中，请耐心等待 (通常需要30-60秒)' : '生成图片' }}
          </el-button>

          <!-- 极简中心式进度指示器 -->
          <div v-if="generating" class="generation-progress-minimalist">
            <div class="progress-circle-container">
              <!-- 环形进度条 -->
              <el-progress
                type="circle"
                :percentage="generationProgress"
                :width="180"
                :stroke-width="6"
                :color="getProgressColor()"
                class="progress-circle"
              >
                <template #default>
                  <div class="progress-content">
                    <!-- 剩余时间 -->
                    <div class="remaining-time">
                      <span class="time-value">{{ Math.max(0, estimatedTime - elapsedTime) }}</span>
                      <span class="time-unit">秒</span>
                    </div>
                    <!-- 阶段指示 -->
                    <div class="stage-indicator">
                      <el-icon class="rotating-icon"><Loading /></el-icon>
                      <span class="stage-text">{{ currentStage }}</span>
                    </div>
                  </div>
                </template>
              </el-progress>

              <!-- 取消按钮 -->
              <el-button
                text
                size="small"
                class="cancel-button-minimalist"
                @click="cancelGeneration"
              >
                取消
              </el-button>
            </div>
          </div>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 图生图表单 -->
    <el-card v-if="generateMode === 'image-to-image'" class="generate-form">
      <template #header>
        <span>图生图设置</span>
      </template>

      <el-form ref="imageFormRef" :model="imageForm" :rules="imageFormRules" label-width="80px">
        <el-form-item label="参考图片">
          <div class="image-upload-container">
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :file-list="imageFileList"
              :on-change="handleImageChange"
              :on-remove="handleImageRemove"
              accept="image/*"
              list-type="picture-card"
              :limit="4"
              :disabled="isLoadingReferenceImage"
            >
              <div v-if="isLoadingReferenceImage" class="loading-area" v-loading="true">
                <div class="loading-text">正在加载参考图片...</div>
              </div>
              <div v-else class="upload-trigger">
                <el-icon class="upload-icon"><Plus /></el-icon>
                <div class="upload-text">点击上传</div>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 JPG、PNG、GIF、WEBP 格式，最多4张，每张最大 10MB
                  <br>
                  <span class="paste-hint">💡 提示：您也可以直接粘贴（Ctrl+V / ⌘+V）剪贴板中的图片</span>
                </div>
              </template>
            </el-upload>
            
            <!-- 从画廊选择按钮 -->
            <el-button 
              type="primary" 
              :icon="Picture" 
              @click="openGallerySelector"
              :disabled="imageFileList.length >= 4 || isLoadingReferenceImage"
              class="gallery-select-btn"
            >
              从画廊选择
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="提示词" prop="prompt">
          <el-input
            v-model="imageForm.prompt"
            type="textarea"
            :rows="4"
            placeholder="描述你想要对图片进行的修改或处理"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="画质">
          <el-select v-model="imageQuality" placeholder="选择画质">
            <el-option label="标准" value="standard" />
            <el-option label="高清" value="hd" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="generating"
            :disabled="!imageForm.prompt || !imageForm.images || imageForm.images.length === 0 || userStore.user?.credits === 0"
            @click="generateImageToImage"
          >
            {{ generating ? 'AI正在处理图片，请耐心等待 (图生图通常需要更长时间)' : '生成图片' }}
          </el-button>

          <!-- 极简中心式进度指示器 -->
          <div v-if="generating" class="generation-progress-minimalist">
            <div class="progress-circle-container">
              <!-- 环形进度条 -->
              <el-progress
                type="circle"
                :percentage="generationProgress"
                :width="180"
                :stroke-width="6"
                :color="getProgressColor()"
                class="progress-circle"
              >
                <template #default>
                  <div class="progress-content">
                    <!-- 剩余时间 -->
                    <div class="remaining-time">
                      <span class="time-value">{{ Math.max(0, estimatedTime - elapsedTime) }}</span>
                      <span class="time-unit">秒</span>
                    </div>
                    <!-- 阶段指示 -->
                    <div class="stage-indicator">
                      <el-icon class="rotating-icon"><Loading /></el-icon>
                      <span class="stage-text">{{ currentStage }}</span>
                    </div>
                  </div>
                </template>
              </el-progress>

              <!-- 取消按钮 -->
              <el-button
                text
                size="small"
                class="cancel-button-minimalist"
                @click="cancelGeneration"
              >
                取消
              </el-button>
            </div>
          </div>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 生成结果 -->
    <el-card v-if="generatedImages.length > 0" class="results">
      <template #header>
        <div class="results-header">
          <span>生成结果</span>
          <el-tag v-if="lastGenerationTime" type="success">
            生成耗时: {{ lastGenerationTime }}s
          </el-tag>
        </div>
      </template>

      <div class="image-grid">
        <div
          v-for="(image, index) in generatedImages"
          :key="index"
          class="image-item"
        >
          <img :src="image.url" :alt="`生成的图片 ${index + 1}`" @click="previewImage(image.url)" />
          <div class="image-actions">
            <el-button type="success" size="small" :icon="MagicStick" @click="continueWithImageToImage(image.url)">
              图生图
            </el-button>
            <el-button type="primary" size="small" @click="downloadImage(image.url, index)">
              下载
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    </div><!-- 关闭 display:none 的旧部分 -->

    <!-- 图片预览对话框 -->
    <el-dialog v-model="previewVisible" title="图片预览" width="85%" center>
      <div class="preview-container">
        <img :src="previewImageUrl" alt="预览图片" class="preview-image" />
      </div>
      <template #footer>
        <div class="preview-dialog-footer">
          <el-button :icon="Download" @click="downloadCurrentPreview">
            下载原图
          </el-button>
          <el-button 
            type="success" 
            :icon="MagicStick" 
            @click="continueWithImageToImageFromPreview"
          >
            复用到图生图
          </el-button>
          <el-button @click="previewVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 画廊选择器对话框 -->
    <el-dialog
      v-model="galleryDialogVisible"
      title="从画廊选择图片"
      width="80%"
      :close-on-click-modal="false"
      class="gallery-selector-dialog"
    >
      <div class="gallery-selector-content">
        <!-- 加载状态 -->
        <div v-if="loadingGallery" class="loading-container" v-loading="true">
          <p>加载中...</p>
        </div>
        
        <!-- 图片网格 -->
        <div v-else class="gallery-grid">
          <div
            v-for="creation in galleryCreations"
            :key="creation.id"
            class="gallery-item"
            :class="{ selected: isSelected(creation.id) }"
            @click="toggleSelection(creation)"
          >
            <img :src="creation.image_url" :alt="creation.prompt" />
            <div class="selection-indicator">
              <el-icon v-if="isSelected(creation.id)"><Check /></el-icon>
            </div>
            <div class="image-info">
              <p class="prompt">{{ creation.prompt }}</p>
            </div>
          </div>
        </div>
        
        <!-- 空状态 -->
        <el-empty v-if="!loadingGallery && galleryCreations.length === 0" description="画廊中还没有作品" />
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <span class="selection-count">已选择: {{ selectedCreations.length }} / {{ maxSelectable }}</span>
          <div>
            <el-button @click="galleryDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="confirmSelection" :disabled="selectedCreations.length === 0">
              确定选择 ({{ selectedCreations.length }})
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'
import { Plus, Delete, MagicStick, Loading, InfoFilled, CircleCheck, Close, Picture, Check, Download } from '@element-plus/icons-vue'
import type { FormInstance, FormRules, UploadFile } from 'element-plus'
import { generateApi, galleryApi } from '@/services/api'
import type { GeneratedImage, GenerateTextToImageRequest, GenerateImageToImageRequest, Creation } from '@shared/index'
import { useAuthStore } from '@/stores/auth'
import { useGalleryStore } from '@/stores/gallery'
import AnimatedBackground from '@/components/common/AnimatedBackground.vue'

// Store
const userStore = useAuthStore()
const galleryStore = useGalleryStore()

// 路由
const route = useRoute()

// 响应式数据
const generateMode = ref<'text-to-image' | 'image-to-image'>('text-to-image')
const generating = ref(false)
const availableModels = ref<string[]>([])
const availableSizes = ref<string[]>([])
const generatedImages = ref<GeneratedImage[]>([])
const lastGenerationTime = ref<number | null>(null)
const imageQuality = ref('standard') // 图片质量：standard 或 hd

// 画质到模型的映射
const qualityToModel: Record<string, string> = {
  'standard': 'nano-banana',
  'hd': 'nano-banana-hd'
}

// 进度指示器
const generationProgress = ref(0)
const estimatedTime = ref(0)
const elapsedTime = ref(0)
const progressInterval = ref<number | null>(null)

// 性能监控和用户体验增强 (Phase 1)
const currentStage = ref('')
const performanceInsight = ref('')
const systemLoad = ref(0)
const averageGenerationTime = ref(0)

// 图片预览
const previewVisible = ref(false)
const previewImageUrl = ref('')

// 当前显示的图片（用于大图展示）
const selectedImageIndex = ref(0)
const currentDisplayImage = computed(() => {
  if (generatedImages.value.length > 0 && generatedImages.value[selectedImageIndex.value]) {
    return generatedImages.value[selectedImageIndex.value].url
  }
  return ''
})

// 当前显示图片的缩略图（用于预览区，提升加载性能）
const currentDisplayImageThumbnail = computed(() => {
  if (generatedImages.value.length > 0 && generatedImages.value[selectedImageIndex.value]) {
    const img = generatedImages.value[selectedImageIndex.value]
    // 优先使用缩略图，如果没有则降级使用原图
    return img.thumbnailUrl || img.url
  }
  return ''
})

// 计算生成按钮是否应该禁用
const isGenerateDisabled = computed(() => {
  if (generateMode.value === 'text-to-image') {
    // 文生图模式：需要提示词
    return !textForm.prompt || textForm.prompt.trim() === ''
  } else {
    // 图生图模式：需要提示词 + 参考图片
    return !imageForm.prompt || 
           imageForm.prompt.trim() === '' || 
           imageFileList.value.length === 0
  }
})

// 文生图表单
const textFormRef = ref<FormInstance>()
const textForm = reactive<Omit<GenerateTextToImageRequest, 'model'>>({
  prompt: '',
  size: '4x3',
  n: 1
})

const textFormRules: FormRules = {
  prompt: [
    { required: true, message: '请输入提示词', trigger: 'blur' },
    { min: 5, message: '提示词至少5个字符', trigger: 'blur' }
  ]
}

// 图生图表单
const imageFormRef = ref<FormInstance>()
const imageForm = reactive({
  prompt: '',
  images: [] as File[]  // 改为数组支持多图
})

const imageFormRules: FormRules = {
  prompt: [
    { required: true, message: '请输入提示词', trigger: 'blur' },
    { min: 5, message: '提示词至少5个字符', trigger: 'blur' }
  ]
  // ✅ 移除 images 验证规则，改用手动检查 imageFileList.value
}

// 图片上传相关
const uploadRef = ref()
const imageFileList = ref<any[]>([])  // 用于显示文件列表
const imagePreview = ref<string[]>([])  // 改为数组存储多个预览URL

// 加载状态
const isLoadingReferenceImage = ref(false)

// 画廊选择器相关状态
const galleryDialogVisible = ref(false)
const loadingGallery = ref(false)
const galleryCreations = ref<Creation[]>([])
const selectedCreations = ref<Creation[]>([])

// 计算最大可选数量
const maxSelectable = computed(() => {
  return 4 - imageFileList.value.length
})

// 生命周期
onMounted(async () => {
  try {
    await loadAvailableModels()

    // 处理从画廊复用的参数
    const { mode, referenceImage, prompt } = route.query
    if (mode === 'image-to-image' && referenceImage) {
      console.log('🔄 检测到画廊复用参数')
      
      // 切换到图生图模式
      generateMode.value = 'image-to-image'

      // 设置提示词（确保不是undefined）
      if (prompt) {
        imageForm.prompt = String(prompt)
        console.log('📝 设置提示词:', imageForm.prompt)
      } else {
        imageForm.prompt = ''
        console.log('📝 提示词为空，用户需要填写')
      }

      // 显示加载状态并加载参考图片
      isLoadingReferenceImage.value = true
      try {
        await loadReferenceImage(String(referenceImage))
      } catch (error) {
        console.error('❌ onMounted 加载参考图片失败:', error)
        ElMessage.error('参考图片加载失败，请手动上传')
      } finally {
        isLoadingReferenceImage.value = false
      }
    }
  } catch (error) {
    console.error('❌ onMounted 初始化失败:', error)
  }
  
  // 添加粘贴事件监听
  window.addEventListener('paste', handlePasteImage)
})

// 组件卸载时清理定时器
onUnmounted(() => {
  if (progressInterval.value) {
    clearInterval(progressInterval.value)
    progressInterval.value = null
  }
  
  // 移除粘贴事件监听
  window.removeEventListener('paste', handlePasteImage)
})

// 方法
const loadAvailableModels = async () => {
  try {
    const response = await generateApi.getAvailableModels()
    if (response.success) {
      availableModels.value = response.models
      availableSizes.value = response.sizes
    }
  } catch (error) {
    console.error('加载可用模型失败:', error)
  }
}

/**
 * 使用Canvas生成图片缩略图
 * @param imageUrl 原图URL
 * @param maxWidth 缩略图最大宽度（默认600px，适合预览区）
 * @param quality JPEG压缩质量（0-1，默认0.7）
 * @returns 缩略图的base64 URL
 */
const generateThumbnail = async (
  imageUrl: string,
  maxWidth: number = 600,
  quality: number = 0.7
): Promise<string> => {
  return new Promise((resolve) => {
    const img = new Image()
    
    // 设置跨域属性（重要！否则canvas会污染）
    img.crossOrigin = 'anonymous'
    
    img.onload = () => {
      try {
        // 创建离屏canvas
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')
        
        if (!ctx) {
          console.warn('无法获取canvas context，使用原图')
          resolve(imageUrl)
          return
        }
        
        // 计算缩放比例（保持宽高比）
        const scale = Math.min(1, maxWidth / img.width)
        canvas.width = Math.floor(img.width * scale)
        canvas.height = Math.floor(img.height * scale)
        
        // 使用更好的缩放算法
        ctx.imageSmoothingEnabled = true
        ctx.imageSmoothingQuality = 'high'
        
        // 绘制缩略图
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
        
        // 转换为JPEG base64（体积更小）
        const thumbnailUrl = canvas.toDataURL('image/jpeg', quality)
        
        // 记录缩略图大小（用于调试）
        const thumbnailSize = (thumbnailUrl.length * 0.75 / 1024).toFixed(1)
        console.log(`✅ 缩略图生成成功: ${canvas.width}x${canvas.height}, 约${thumbnailSize}KB`)
        
        resolve(thumbnailUrl)
      } catch (error) {
        console.error('❌ 生成缩略图失败:', error)
        resolve(imageUrl) // 失败时降级使用原图
      }
    }
    
    img.onerror = (error) => {
      console.error('❌ 加载图片失败:', imageUrl, error)
      resolve(imageUrl) // 加载失败时降级使用原图
    }
    
    // 开始加载图片
    img.src = imageUrl
  })
}

/**
 * 批量生成缩略图
 * @param images 原始图片数组
 * @returns 包含缩略图的图片数组
 */
const generateThumbnailsForImages = async (
  images: GeneratedImage[]
): Promise<GeneratedImage[]> => {
  console.log(`🖼️ 开始为 ${images.length} 张图片生成缩略图...`)
  const startTime = Date.now()
  
  const results = await Promise.all(
    images.map(async (img) => {
      const thumbnailUrl = await generateThumbnail(img.url, 600, 0.7)
      return {
        ...img,
        thumbnailUrl
      }
    })
  )
  
  const duration = ((Date.now() - startTime) / 1000).toFixed(2)
  console.log(`✅ 缩略图生成完成，耗时: ${duration}秒`)
  
  return results
}

// Phase 1: 增强的进度控制函数
const startProgress = (mode: 'text-to-image' | 'image-to-image') => {
  generationProgress.value = 0
  elapsedTime.value = 0

  // 基于历史数据优化预估时间
  const baseTime = mode === 'text-to-image' ? 45 : 60
  estimatedTime.value = averageGenerationTime.value > 0 ?
    Math.round((averageGenerationTime.value + baseTime) / 2) : baseTime

  // 初始化阶段信息
  updateProgressStage('准备中...', '正在连接AI服务')

  progressInterval.value = setInterval(() => {
    elapsedTime.value += 1
    updateProgressStage()

    // 智能进度算法：结合系统负载动态调整
    const timeProgress = elapsedTime.value / estimatedTime.value
    const loadFactor = Math.max(0.8, 1 - systemLoad.value * 0.3) // 负载越高，进度越慢

    if (timeProgress < 0.3) {
      generationProgress.value = Math.min(25, timeProgress * 83.33 * loadFactor)
    } else if (timeProgress < 0.8) {
      generationProgress.value = Math.min(75, 25 + (timeProgress - 0.3) * 100 * loadFactor)
    } else {
      generationProgress.value = Math.min(95, 75 + (timeProgress - 0.8) * 100 * loadFactor)
    }

    // 超时处理
    if (elapsedTime.value > estimatedTime.value) {
      generationProgress.value = Math.min(98, generationProgress.value + 0.5)
      if (elapsedTime.value > estimatedTime.value * 1.5) {
        updateProgressStage('处理中...', '图片生成需要更多时间，请耐心等待')
      }
    }
  }, 1000)
}

// Phase 1: 更新进度阶段信息
const updateProgressStage = (stage?: string, insight?: string) => {
  if (stage) {
    currentStage.value = stage
  } else {
    // 根据进度自动更新阶段
    if (generationProgress.value < 10) {
      currentStage.value = '初始化请求...'
    } else if (generationProgress.value < 30) {
      currentStage.value = 'AI模型分析中...'
    } else if (generationProgress.value < 70) {
      currentStage.value = '正在生成图片...'
    } else if (generationProgress.value < 90) {
      currentStage.value = '优化图片质量...'
    } else {
      currentStage.value = '即将完成...'
    }
  }

  if (insight) {
    performanceInsight.value = insight
  }
}

// Phase 1: 进度条颜色动态调整
const getProgressColor = () => {
  if (systemLoad.value > 0.8) return '#f56c6c' // 高负载时红色
  if (elapsedTime.value > estimatedTime.value * 1.2) return '#e6a23c' // 超时时橙色
  return '#409eff' // 正常时蓝色
}

// Phase 1: 负载状态样式
const getLoadClass = () => {
  if (systemLoad.value > 0.8) return 'load-high'
  if (systemLoad.value > 0.6) return 'load-medium'
  return 'load-normal'
}

// 服务器负载颜色
const getLoadColor = () => {
  if (systemLoad.value > 0.8) return '#f56c6c' // 高负载红色
  if (systemLoad.value > 0.6) return '#e6a23c' // 中负载橙色
  return '#67c23a' // 正常绿色
}

// 取消生成功能
const cancelGeneration = () => {
  if (!generating.value) return

  ElMessageBox.confirm(
    '确定要取消当前的图片生成吗？已扣除的次数不会返还。',
    '确认取消',
    {
      confirmButtonText: '确定取消',
      cancelButtonText: '继续生成',
      type: 'warning'
    }
  ).then(() => {
    // 停止进度
    stopProgress()
    generating.value = false

    ElMessage.warning('已取消图片生成')
  }).catch(() => {
    // 用户点击了"继续生成"，不做任何操作
  })
}

const stopProgress = () => {
  if (progressInterval.value) {
    clearInterval(progressInterval.value)
    progressInterval.value = null
  }
  generationProgress.value = 100

  // Phase 1: 清理增强的状态信息
  setTimeout(() => {
    generationProgress.value = 0
    currentStage.value = ''
    performanceInsight.value = ''
    systemLoad.value = 0
  }, 1000)
}

const onModeChange = () => {
  // 清空生成结果
  generatedImages.value = []
  lastGenerationTime.value = null
}

// 生成按钮点击处理 - 统一错误捕获
const handleGenerate = async () => {
  try {
    console.log('🎯 点击生成按钮，模式:', generateMode.value)
    
    if (generateMode.value === 'text-to-image') {
      await generateTextToImage()
    } else {
      await generateImageToImage()
    }
  } catch (error: any) {
    console.error('❌ 生成失败（全局捕获）:', error)
    
    // 确保状态恢复
    generating.value = false
    stopProgress()
    
    // 显示错误提示
    const errorMessage = error?.message || error?.error || '生成失败，请稍后重试'
    ElMessage.error(errorMessage)
  }
}

// 处理图片上传
const handleImageChange = (file: any, fileList: any[]) => {
  imageFileList.value = fileList
  imageForm.images = fileList.map(f => f.raw).filter(Boolean)
}

// 移除图片 - 兼容手动调用和el-upload回调两种方式
const handleImageRemove = (file: any, fileList?: any[]) => {
  if (fileList && Array.isArray(fileList)) {
    // 方式1：手动调用，传递了fileList数组
    imageFileList.value = fileList
  } else {
    // 方式2：el-upload回调或手动调用（只传file）
    const index = imageFileList.value.findIndex((f: any) => f.uid === file.uid || f === file)
    if (index > -1) {
      imageFileList.value.splice(index, 1)
    }
  }
  
  // 同步更新imageForm.images
  imageForm.images = imageFileList.value.map((f: any) => f.raw).filter(Boolean) as File[]
  
  console.log('🗑️ 移除图片，剩余:', imageFileList.value.length, '张')
}

// 清空图片
const removeAllImages = () => {
  imageFileList.value = []
  imageForm.images = []
  imagePreview.value = []
}

// 从URL加载参考图片 - 快速加载优化版本
const loadReferenceImage = async (imageUrl: string) => {
  try {
    console.log('📥 快速加载参考图片:', imageUrl)
    
    // ⚡ 直接使用URL，立即显示（不下载整个文件）
    // 延迟下载到实际生成时，大幅提升加载速度
    imageFileList.value = [{
      name: 'reference-image.png',
      url: imageUrl,
      raw: null,  // 延迟加载，生成时才下载
      uid: Date.now()
    }]
    
    // 清空之前的File对象（会在生成时重新下载）
    imageForm.images = []
    
    ElMessage.success('参考图片已加载')
    console.log('✅ 参考图片显示完成（延迟下载模式）')

  } catch (error) {
    console.error('❌ 加载参考图片失败:', error)
    const errorMessage = error instanceof Error ? error.message : '未知错误'
    ElMessage.error(`加载参考图片失败: ${errorMessage}`)
  }
}

/**
 * 从URL下载图片并转换为File对象
 * 仅在提交图生图时调用，不阻塞预览显示
 */
const downloadAndConvertToFile = async (imageUrl: string): Promise<File> => {
  try {
    console.log('⬇️ 下载图片用于生成:', imageUrl)
    
    // 尝试直接下载
    try {
      const response = await fetch(imageUrl)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      const blob = await response.blob()
      
      // 检查文件类型
      if (!blob.type.startsWith('image/')) {
        throw new Error(`无效的图片类型: ${blob.type}`)
      }
      
      // 检查文件大小
      if (blob.size > 10 * 1024 * 1024) {
        throw new Error('图片文件过大（超过10MB）')
      }
      
      // 直接从blob创建File（更快，不需要base64转换）
      const file = new File(
        [blob], 
        'reference-image.png', 
        { type: blob.type || 'image/png' }
      )
      
      console.log('✅ 图片已准备好，大小:', (blob.size / 1024).toFixed(1), 'KB')
      return file
      
    } catch (directError) {
      console.log('❌ 直接下载失败，尝试代理:', directError)
      
      // 策略2: 使用后端代理
      const { galleryApi } = await import('@/services/api')
      const proxyResponse = await galleryApi.proxyImage(imageUrl)
      
      if (!proxyResponse.success) {
        throw new Error(proxyResponse.error || '代理获取图片失败')
      }
      
      // 从base64转换为File
      const base64Data = proxyResponse.image_data!.split(',')[1]
      const binaryData = atob(base64Data)
      const bytes = new Uint8Array(binaryData.length)
      
      for (let i = 0; i < binaryData.length; i++) {
        bytes[i] = binaryData.charCodeAt(i)
      }
      
      const file = new File(
        [bytes], 
        'reference-image.png', 
        { type: proxyResponse.content_type || 'image/png' }
      )
      
      console.log('✅ 代理下载成功，大小:', proxyResponse.size, 'bytes')
      return file
    }
    
  } catch (error) {
    console.error('❌ 下载图片失败:', error)
    throw new Error('图片下载失败，请重试')
  }
}

const generateTextToImage = async () => {
  if (!textFormRef.value) return

  const valid = await textFormRef.value.validate()
  if (!valid) return

  if (!userStore.user?.credits || userStore.user.credits <= 0) {
    ElMessage.error('生成次数不足，请联系管理员充值')
    return
  }

  generating.value = true
  startProgress('text-to-image')

  // Phase 1: 模拟系统负载监控
  systemLoad.value = 0.3 + Math.random() * 0.4 // 模拟 30-70% 负载

  try {
    const response: any = await generateApi.textToImage({
      prompt: textForm.prompt,
      model: qualityToModel[imageQuality.value],
      size: textForm.size,
      n: textForm.n
    })

    if (response.success && response.images) {
      // 🔥 生成缩略图以提升预览性能
      const imagesWithThumbnails = await generateThumbnailsForImages(response.images)
      
      generatedImages.value = imagesWithThumbnails
      selectedImageIndex.value = 0 // 重置到第一张图片
      lastGenerationTime.value = response.generation_time || null

      // Phase 1: 更新历史性能数据
      if (response.generation_time) {
        averageGenerationTime.value = averageGenerationTime.value > 0 ?
          (averageGenerationTime.value + response.generation_time) / 2 :
          response.generation_time

        updateProgressStage('完成', `生成耗时 ${response.generation_time}s，比预期快 ${Math.max(0, estimatedTime.value - response.generation_time)}s`)
      }

      // 更新用户次数
      if (response.remaining_credits !== undefined) {
        userStore.updateUserCredits(response.remaining_credits)
      }

      // 添加新作品到画廊
      if (response.creations && response.creations.length > 0) {
        response.creations.forEach((creation: any) => {
          galleryStore.addCreation(creation)
        })
      }

      ElNotification({
        title: '生成成功',
        message: `成功生成 ${response.images.length} 张图片`,
        type: 'success'
      })
    } else {
      ElMessage.error(response.error || '生成失败')
    }
  } catch (error: any) {
    console.error('文生图失败:', error)

    // 根据错误类型提供更精确的提示
    let errorMessage = '生成失败，请稍后重试'
    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
      errorMessage = 'AI生成时间较长，请耐心等待或稍后重试'
    } else if (error.response?.data?.error) {
      errorMessage = error.response.data.error
    } else if (error.message.includes('timeout')) {
      errorMessage = '请求超时，AI生成可能需要更多时间，请稍后重试'
    }

    ElMessage.error(errorMessage)
  } finally {
    generating.value = false
    stopProgress()
  }
}

const generateImageToImage = async () => {
  console.log('🎯 开始图生图生成流程')
  console.log('📋 imageForm.prompt:', imageForm.prompt)
  console.log('📋 imageForm.images 长度:', imageForm.images?.length || 0)
  console.log('📋 imageFileList.value 长度:', imageFileList.value.length)
  
  if (!imageFormRef.value) {
    console.error('❌ imageFormRef 未定义')
    return
  }

  const valid = await imageFormRef.value.validate()
  if (!valid) {
    console.log('⚠️ 表单验证失败')
    return
  }

  if (!userStore.user?.credits || userStore.user.credits <= 0) {
    ElMessage.error('生成次数不足，请联系管理员充值')
    return
  }

  // 检查是否有参考图片
  if (imageFileList.value.length === 0) {
    ElMessage.error('请先上传参考图片')
    return
  }

  generating.value = true
  startProgress('image-to-image')

  // Phase 1: 模拟系统负载监控
  systemLoad.value = 0.4 + Math.random() * 0.4 // 图生图负载稍高 40-80%

  try {
    // 🔥 新增：处理延迟下载的图片
    let processedImages: File[] = []
    
    console.log('🔍 检查图片状态...')
    console.log('   - imageForm.images:', imageForm.images?.length || 0)
    console.log('   - imageFileList.value:', imageFileList.value.length)
    
    // 如果 imageForm.images 为空，说明图片是从URL加载的，需要先下载
    if (!imageForm.images || imageForm.images.length === 0) {
      console.log('🔄 检测到延迟加载的图片，开始下载...')
      currentStage.value = '正在准备参考图片...'
      
      try {
        const downloadPromises = imageFileList.value.map(async (fileItem, index) => {
          console.log(`📥 处理图片 ${index + 1}/${imageFileList.value.length}`)
          
          if (fileItem.raw && fileItem.raw instanceof File) {
            console.log(`   ✅ 图片 ${index + 1} 已是File对象`)
            return fileItem.raw
          }
          
          // 从URL下载
          console.log(`   ⬇️ 图片 ${index + 1} 需要从URL下载:`, fileItem.url)
          const file = await downloadAndConvertToFile(fileItem.url)
          console.log(`   ✅ 图片 ${index + 1} 下载完成`)
          return file
        })
        
        processedImages = await Promise.all(downloadPromises)
        
        // 过滤掉可能的null/undefined值
        processedImages = processedImages.filter(img => img instanceof File)
        
        console.log(`✅ ${processedImages.length} 张参考图片准备完成`)
      } catch (downloadError: any) {
        console.error('❌ 下载参考图片失败:', downloadError)
        console.error('❌ 错误堆栈:', downloadError?.stack)
        generating.value = false
        stopProgress()
        ElMessage.error('参考图片加载失败，请重新选择图片')
        return
      }
    } else {
      console.log('✅ 使用已有的File对象')
      // 使用已有的File对象
      processedImages = imageForm.images.filter(img => img instanceof File)
    }
    
    if (processedImages.length === 0) {
      console.error('❌ 没有可用的参考图片')
      generating.value = false
      stopProgress()
      ElMessage.error('没有可用的参考图片，请重新上传')
      return
    }
    
    console.log(`🚀 开始提交图生图请求，图片数量: ${processedImages.length}`)

    const response: any = await generateApi.imageToImage({
      prompt: imageForm.prompt,
      images: processedImages,
      model: qualityToModel[imageQuality.value]
    })

    if (response.success && response.images) {
      // 🔥 生成缩略图以提升预览性能
      const imagesWithThumbnails = await generateThumbnailsForImages(response.images)
      
      generatedImages.value = imagesWithThumbnails
      selectedImageIndex.value = 0 // 重置到第一张图片
      lastGenerationTime.value = response.generation_time || null

      // Phase 1: 更新历史性能数据
      if (response.generation_time) {
        averageGenerationTime.value = averageGenerationTime.value > 0 ?
          (averageGenerationTime.value + response.generation_time) / 2 :
          response.generation_time

        updateProgressStage('完成', `图生图耗时 ${response.generation_time}s，图片处理已完成`)
      }

      // 更新用户次数
      if (response.remaining_credits !== undefined) {
        userStore.updateUserCredits(response.remaining_credits)
      }

      // 添加新作品到画廊
      if (response.creations && response.creations.length > 0) {
        response.creations.forEach((creation: any) => {
          galleryStore.addCreation(creation)
        })
      }

      ElNotification({
        title: '生成成功',
        message: `成功生成 ${response.images.length} 张图片`,
        type: 'success'
      })
    } else {
      ElMessage.error(response.error || '生成失败')
    }
  } catch (error: any) {
    console.error('图生图失败:', error)

    // 根据错误类型提供更精确的提示
    let errorMessage = '生成失败，请稍后重试'
    
    if (error.message?.includes('参考图片加载失败') || error.message?.includes('图片下载失败')) {
      errorMessage = '参考图片加载失败，请重新选择图片或检查网络连接'
    } else if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
      errorMessage = 'AI生成时间较长，请耐心等待或稍后重试'
    } else if (error.response?.data?.error) {
      errorMessage = error.response.data.error
    } else if (error.message.includes('timeout')) {
      errorMessage = '请求超时，AI生成可能需要更多时间，请稍后重试'
    } else if (error.message) {
      errorMessage = error.message
    }

    ElMessage.error(errorMessage)
  } finally {
    generating.value = false
    stopProgress()
  }
}

const previewImage = (url: string) => {
  previewImageUrl.value = url
  previewVisible.value = true
}

// 从预览对话框下载图片
const downloadCurrentPreview = async () => {
  if (previewImageUrl.value) {
    // 找到当前预览图片的索引
    const index = generatedImages.value.findIndex(img => img.url === previewImageUrl.value)
    await downloadImage(previewImageUrl.value, index >= 0 ? index : 0)
  }
}

// 从预览对话框复用到图生图
const continueWithImageToImageFromPreview = async () => {
  previewVisible.value = false
  if (previewImageUrl.value) {
    await continueWithImageToImage(previewImageUrl.value)
  }
}

// 切换显示的图片
const selectImage = (index: number) => {
  selectedImageIndex.value = index
}

// 继续使用生成的图片进行图生图
const continueWithImageToImage = async (imageUrl: string) => {
  try {
    // 切换到图生图模式
    generateMode.value = 'image-to-image'

    // 加载当前图片作为参考图片
    await loadReferenceImage(imageUrl)

    // 使用当前的提示词（如果是文生图生成的）
    if (textForm.prompt) {
      imageForm.prompt = textForm.prompt
    }

    ElMessage.success('已切换到图生图模式，可以继续创作！')

    // 滚动到图生图表单
    setTimeout(() => {
      document.querySelector('.generate-form')?.scrollIntoView({ behavior: 'smooth' })
    }, 100)
  } catch (error) {
    console.error('Continue with image-to-image error:', error)
    ElMessage.error('切换失败，请稍后重试')
  }
}

const downloadImage = async (url: string, index: number) => {
  try {
    const response = await fetch(url)
    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)

    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `generated-image-${Date.now()}-${index + 1}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    window.URL.revokeObjectURL(downloadUrl)
    ElMessage.success('图片下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败，请稍后重试')
  }
}

// 打开画廊选择器
const openGallerySelector = async () => {
  galleryDialogVisible.value = true
  selectedCreations.value = []
  
  // 加载画廊数据
  loadingGallery.value = true
  try {
    const response = await galleryApi.getCreations({
      page: 1,
      per_page: 50 // 显示最近50个作品
    })
    
    if (response.creations) {
      galleryCreations.value = response.creations
    }
  } catch (error) {
    console.error('加载画廊失败:', error)
    ElMessage.error('加载画廊失败，请稍后重试')
  } finally {
    loadingGallery.value = false
  }
}

// 判断是否已选中
const isSelected = (creationId: number) => {
  return selectedCreations.value.some(c => c.id === creationId)
}

// 切换选择状态
const toggleSelection = (creation: Creation) => {
  const index = selectedCreations.value.findIndex(c => c.id === creation.id)
  
  if (index > -1) {
    // 已选中，取消选择
    selectedCreations.value.splice(index, 1)
  } else {
    // 未选中，添加选择
    if (selectedCreations.value.length < maxSelectable.value) {
      selectedCreations.value.push(creation)
    } else {
      ElMessage.warning(`最多只能选择 ${maxSelectable.value} 张图片`)
    }
  }
}

// 确认选择
const confirmSelection = async () => {
  if (selectedCreations.value.length === 0) {
    return
  }
  
  isLoadingReferenceImage.value = true
  
  try {
    // 将选中的图片URL转换为File对象
    for (const creation of selectedCreations.value) {
      const response = await fetch(creation.image_url)
      const blob = await response.blob()
      
      // 从URL提取文件名或使用creation id
      const filename = `gallery-${creation.id}.png`
      const file = new File([blob], filename, { type: blob.type })
      
      // 添加到文件列表
      imageFileList.value.push({
        name: filename,
        url: creation.image_url,
        raw: file,
        uid: Date.now() + Math.random()
      })
      
      // 添加到表单数据
      imageForm.images.push(file)
    }
    
    ElMessage.success(`已添加 ${selectedCreations.value.length} 张图片`)
    galleryDialogVisible.value = false
    selectedCreations.value = []
  } catch (error) {
    console.error('添加图片失败:', error)
    ElMessage.error('添加图片失败，请稍后重试')
  } finally {
    isLoadingReferenceImage.value = false
  }
}

// 处理粘贴图片
const handlePasteImage = async (event: ClipboardEvent) => {
  // 只在图生图模式下处理
  if (generateMode.value !== 'image-to-image') {
    return
  }
  
  // 检查是否已达到上传限制
  if (imageFileList.value.length >= 4) {
    ElMessage.warning('最多只能上传4张图片')
    return
  }
  
  const items = event.clipboardData?.items
  if (!items || items.length === 0) {
    return
  }
  
  // 查找图片项
  let hasImage = false
  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    
    // 检查是否为图片类型
    if (item.type.startsWith('image/')) {
      event.preventDefault() // 阻止默认粘贴行为
      hasImage = true
      
      const file = item.getAsFile()
      if (!file) {
        continue
      }
      
      // 检查文件大小（最大10MB）
      const maxSize = 10 * 1024 * 1024
      if (file.size > maxSize) {
        ElMessage.warning('图片大小不能超过 10MB')
        continue
      }
      
      // 生成文件名
      const timestamp = Date.now()
      const extension = file.type.split('/')[1] || 'png'
      const filename = `pasted-image-${timestamp}.${extension}`
      
      // 创建新的File对象（使用更友好的文件名）
      const newFile = new File([file], filename, { type: file.type })
      
      // 添加到文件列表
      imageFileList.value.push({
        name: filename,
        url: URL.createObjectURL(newFile),
        raw: newFile,
        uid: timestamp + Math.random()
      })
      
      // 添加到表单数据
      imageForm.images.push(newFile)
      
      ElMessage.success('已添加粘贴的图片')
      
      // 如果已经达到4张，停止处理
      if (imageFileList.value.length >= 4) {
        break
      }
    }
  }
  
  // 如果没有找到图片，提示用户
  if (!hasImage && items.length > 0) {
    // 检查剪贴板中是否有文本
    const hasText = Array.from(items).some(item => item.type.startsWith('text/'))
    if (!hasText) {
      ElMessage.info('剪贴板中没有图片')
    }
  }
}
</script>

<style scoped>
/* ============================================
   主容器和布局
   ============================================ */
.generate-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  position: relative;
}

.main-layout {
  display: flex;
  height: 100vh;
  width: 100%;
}

/* ============================================
   左侧控制面板
   ============================================ */
.control-panel {
  width: 320px;
  margin: 20px;
  padding: 24px;
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur) var(--glass-saturate);
  -webkit-backdrop-filter: var(--glass-blur) var(--glass-saturate);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
  max-height: calc(100vh - 40px);  /* ✅ 限制最大高度 */
  box-shadow: 
    0 8px 32px 0 rgba(102, 126, 234, 0.12),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
  transition: all 0.3s ease;
}

.control-panel:hover {
  box-shadow: 
    0 12px 48px 0 rgba(102, 126, 234, 0.18),
    0 0 0 1px rgba(255, 255, 255, 0.7) inset;
}

/* 面板头部 */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.15);
}

.panel-title {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
  letter-spacing: 0.5px;
}

/* 模式切换 */
.mode-switcher {
  margin-bottom: 24px;
}

.mode-switcher :deep(.el-radio-group) {
  width: 100%;
  display: flex;
}

.mode-switcher :deep(.el-radio-button) {
  flex: 1;
}

.mode-switcher :deep(.el-radio-button__inner) {
  width: 100%;
  background: rgba(255, 255, 255, 0.6);
  border-color: rgba(102, 126, 234, 0.2);
  color: #606266;
  transition: all 0.3s;
}

.mode-switcher :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-color: #667eea;
  color: #fff;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
}

.mode-switcher :deep(.el-radio-button__inner:hover) {
  background: rgba(255, 255, 255, 0.8);
  color: #2c3e50;
}

/* 控制表单 */
.control-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex: 1;
  overflow-y: auto;           /* ✅ 内容区可滚动 */
  padding-bottom: 20px;       /* ✅ 底部留白 */
  min-height: 0;              /* ✅ 允许flex收缩 */
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
  letter-spacing: 0.3px;
}

/* Element Plus 玻璃态主题适配 */
.control-panel :deep(.el-select),
.control-panel :deep(.el-input),
.control-panel :deep(.el-input-number) {
  width: 100%;
}

.control-panel :deep(.el-select .el-input__wrapper),
.control-panel :deep(.el-input__wrapper),
.control-panel :deep(.el-textarea__inner) {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(102, 126, 234, 0.2);
  color: #2c3e50;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.control-panel :deep(.el-select .el-input__wrapper):hover,
.control-panel :deep(.el-input__wrapper):hover,
.control-panel :deep(.el-textarea__inner):hover {
  background: rgba(255, 255, 255, 1);
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.control-panel :deep(.el-select .el-input__wrapper.is-focus),
.control-panel :deep(.el-input__wrapper.is-focus),
.control-panel :deep(.el-textarea__inner:focus) {
  background: rgba(255, 255, 255, 1);
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
}

.control-panel :deep(.el-input__inner),
.control-panel :deep(.el-textarea__inner) {
  color: #2c3e50;
}

.control-panel :deep(.el-input__inner::placeholder),
.control-panel :deep(.el-textarea__inner::placeholder) {
  color: #a8abb2;
}

.control-panel :deep(.el-input__count) {
  background: transparent;
  color: #909399;
}

/* 图片上传区域 */
.image-upload-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.uploaded-images {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.uploaded-thumb {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid rgba(102, 126, 234, 0.2);
  cursor: pointer;
  transition: all 0.3s;
  background: rgba(255, 255, 255, 0.5);
}

.uploaded-thumb:hover {
  border-color: #667eea;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.uploaded-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-icon {
  position: absolute;
  top: 4px;
  right: 4px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  padding: 4px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.remove-icon:hover {
  background: #f56c6c;
  transform: scale(1.1);
}

.upload-btn,
.gallery-btn {
  width: 100%;
  background: rgba(255, 255, 255, 0.8);
  border-color: rgba(102, 126, 234, 0.25);
  color: #606266;
}

.upload-btn:hover,
.gallery-btn:hover {
  background: rgba(255, 255, 255, 1);
  border-color: rgba(102, 126, 234, 0.4);
  color: #2c3e50;
}

/* 生成按钮 */
.generate-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  margin-top: auto;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  color: #fff;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  transition: all 0.3s;
  flex-shrink: 0;            /* ✅ 防止被压缩 */
  display: flex !important;  /* ✅ 强制显示 */
  align-items: center;
  justify-content: center;
  visibility: visible !important;  /* ✅ 强制可见 */
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.generate-btn:active:not(:disabled) {
  transform: translateY(0);
}

.generate-btn:disabled {
  background: rgba(102, 126, 234, 0.3);
  color: rgba(255, 255, 255, 0.6);
  box-shadow: none;
  cursor: not-allowed;
  opacity: 0.7;  /* ✅ 禁用时半透明，但仍可见 */
}

/* ============================================
   右侧预览区
   ============================================ */
.preview-area {
  flex: 1;
  background: transparent;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  padding: 20px 20px 20px 0;
}

/* 空状态 */
.empty-preview {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: rgba(102, 126, 234, 0.3);
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  margin: 0 20px 20px 0;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
  opacity: 0.4;
  color: rgba(102, 126, 234, 0.5);
}

.empty-text {
  font-size: 16px;
  margin: 0;
  color: #909399;
}

/* 生成中状态 */
.generating-preview {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  margin: 0 20px 20px 0;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.12);
}

.progress-content {
  text-align: center;
}

.remaining-time {
  display: flex;
  align-items: baseline;
  gap: 6px;
  justify-content: center;
}

.time-value {
  font-size: 48px;
  font-weight: 600;
  color: #667eea;
  line-height: 1;
}

.time-unit {
  font-size: 16px;
  color: #909399;
}

.generating-text {
  font-size: 16px;
  color: #667eea;
  margin: 0;
}

.cancel-btn {
  color: #909399;
  transition: all 0.3s;
}

.cancel-btn:hover {
  color: #f56c6c;
}

/* 主图展示 */
.main-image-display {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 32px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  margin: 0 20px 0 0;
  box-shadow: 
    0 8px 32px 0 rgba(102, 126, 234, 0.12),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
}

.main-image {
  flex: 1;
  width: 100%;
  height: 100%;
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  cursor: zoom-in;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.3);
  animation: fadeIn 0.5s ease-in-out;
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 操作栏 */
.image-actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0 0;
  border-top: 1px solid rgba(102, 126, 234, 0.15);
  margin-top: 20px;
}

.action-group {
  display: flex;
  gap: 12px;
}

.action-group .el-button {
  background: rgba(255, 255, 255, 0.8);
  border-color: rgba(102, 126, 234, 0.25);
  color: #606266;
}

.action-group .el-button:hover {
  background: rgba(255, 255, 255, 1);
  border-color: rgba(102, 126, 234, 0.4);
  color: #2c3e50;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

/* 复用按钮特殊样式 */
.action-group .reuse-btn {
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.3);
}

.action-group .reuse-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.5);
}

.image-info {
  font-size: 13px;
  color: #909399;
}

/* 历史缩略图 */
.history-thumbnails {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 16px;
  overflow-x: auto;
  overflow-y: hidden;
  margin: 16px 20px 20px 0;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.08);
}

/* 隐藏滚动条但保持功能 */
.history-thumbnails::-webkit-scrollbar {
  height: 6px;
}

.history-thumbnails::-webkit-scrollbar-track {
  background: rgba(102, 126, 234, 0.05);
  border-radius: 3px;
}

.history-thumbnails::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 3px;
  transition: all 0.3s;
}

.history-thumbnails::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}

.history-thumb {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  border: 3px solid rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  background: rgba(255, 255, 255, 0.3);
}

.history-thumb:hover {
  border-color: rgba(102, 126, 234, 0.6);
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.history-thumb.active {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.25);
  transform: scale(1.05);
}

.history-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* ============================================
   响应式适配
   ============================================ */
/* 平板端（1024px 以下） */
@media (max-width: 1024px) {
  .main-layout {
    flex-direction: column;
  }
  
  .control-panel {
    width: 100%;
    height: auto;
    max-height: 45vh;
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding: 20px;
  }
  
  .preview-area {
    height: 55vh;
  }
  
  .main-image-display {
    padding: 20px;
  }
  
  .history-thumbnails {
    padding: 12px 20px;
  }
}

/* 移动端（768px 以下） */
@media (max-width: 768px) {
  .generate-container {
    height: auto;
    min-height: 100vh;
  }
  
  .main-layout {
    flex-direction: column;
    height: auto;
    min-height: calc(100vh - 124px); /* 减去header和bottom tabbar */
  }
  
  .control-panel {
    width: 100%;
    max-height: none;
    padding: 16px;
    margin: 12px;
    border-radius: 12px;
  }
  
  .panel-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .control-form {
    gap: 16px;
  }
  
  .form-label {
    font-size: 13px;
  }
  
  .generate-btn {
    height: 48px;
    font-size: 15px;
  }
  
  .preview-area {
    padding: 0;
    height: auto;
    min-height: 400px;
  }
  
  .main-image-display {
    padding: 16px;
    margin: 12px;
    border-radius: 12px;
  }
  
  .image-actions-bar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .action-group {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .action-group .el-button {
    flex: 1;
    min-width: 120px;
  }
  
  .image-info {
    text-align: center;
  }
  
  .history-thumbnails {
    padding: 12px 16px;
    gap: 8px;
    margin: 12px;
  }
  
  .history-thumb {
    width: 60px;
    height: 60px;
  }
  
  .empty-icon {
    font-size: 60px;
  }
  
  .empty-text {
    font-size: 14px;
  }
  
  .empty-preview {
    margin: 12px;
  }
  
  .generating-preview {
    margin: 12px;
  }
}

/* 小屏手机（480px 以下） */
@media (max-width: 480px) {
  .control-panel {
    padding: 12px;
    margin: 8px;
  }
  
  .panel-title {
    font-size: 18px;
  }
  
  .mode-switcher :deep(.el-radio-button__inner) {
    font-size: 13px;
    padding: 8px 12px;
  }
  
  .form-group {
    gap: 6px;
  }
  
  .control-panel :deep(.el-textarea__inner) {
    font-size: 14px;
    min-height: 80px;
  }
  
  .generate-btn {
    height: 46px;
    font-size: 14px;
  }
  
  .main-image-display {
    padding: 12px;
    margin: 8px;
  }
  
  .time-value {
    font-size: 36px;
  }
  
  .generating-text {
    font-size: 14px;
  }
  
  .history-thumbnails {
    padding: 8px 12px;
    margin: 8px;
  }
  
  .history-thumb {
    width: 50px;
    height: 50px;
  }
  
  .empty-preview {
    margin: 8px;
    min-height: 300px;
  }
  
  .generating-preview {
    margin: 8px;
    min-height: 300px;
  }
  
  .action-group .el-button {
    font-size: 13px;
    padding: 8px 12px;
  }
  
  /* 图片上传区域移动端优化 */
  .uploaded-images {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .uploaded-thumb {
    aspect-ratio: 1;
  }
  
  .upload-btn,
  .gallery-btn {
    width: 100%;
    height: 44px;
    font-size: 14px;
  }
  
  /* Element Plus组件移动端优化 */
  .control-panel :deep(.el-select),
  .control-panel :deep(.el-input-number) {
    width: 100%;
  }
  
  .control-panel :deep(.el-input-number .el-input__wrapper) {
    width: 100%;
  }
}

/* ============================================
   旧样式（保持兼容）
   ============================================ */
/* 应用玻璃态效果到卡片 */
.mode-selector {
  margin-bottom: 20px;
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur) var(--glass-saturate);
  -webkit-backdrop-filter: var(--glass-blur) var(--glass-saturate);
  border: 1px solid var(--glass-border);
  box-shadow: 
    0 8px 32px 0 rgba(102, 126, 234, 0.12),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
  transition: all var(--transition-base) var(--ease-in-out);
}

.mode-selector:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 12px 48px 0 rgba(102, 126, 234, 0.18),
    0 0 0 1px rgba(255, 255, 255, 0.7) inset;
}

.mode-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.generate-form {
  margin-bottom: 20px;
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur) var(--glass-saturate);
  -webkit-backdrop-filter: var(--glass-blur) var(--glass-saturate);
  border: 1px solid var(--glass-border);
  box-shadow: 
    0 8px 32px 0 rgba(102, 126, 234, 0.12),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
  transition: all var(--transition-base) var(--ease-in-out);
}

.generate-form:hover {
  box-shadow: 
    0 12px 48px 0 rgba(102, 126, 234, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.6) inset;
}

.image-upload {
  width: 100%;
}

.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  text-align: center;
  padding: 40px 20px;
  transition: border-color 0.3s;
}

.upload-area:hover {
  border-color: #409eff;
}

.upload-icon {
  font-size: 28px;
  color: #8c939d;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 16px;
  color: #606266;
  margin-bottom: 8px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
}

.image-preview {
  position: relative;
  width: 200px;
  height: 200px;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #dcdfe6;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.5);
  padding: 4px;
}

.results {
  margin-top: 20px;
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur) var(--glass-saturate);
  -webkit-backdrop-filter: var(--glass-blur) var(--glass-saturate);
  border: 1px solid var(--glass-border);
  box-shadow: 
    0 8px 32px 0 rgba(102, 126, 234, 0.12),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.image-item {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #ebeef5;
  transition: transform 0.3s, box-shadow 0.3s;
}

.image-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.image-item img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  cursor: pointer;
}

.image-actions {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  padding: 8px;
  opacity: 0;
  transition: opacity 0.3s;
}

.image-item:hover .image-actions {
  opacity: 1;
}

.image-actions .el-button--success {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  border: none;
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.3);
}

.image-actions .el-button--success:hover {
  background: linear-gradient(135deg, #85ce61, #67c23a);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.4);
}

.preview-container {
  text-align: center;
}

.preview-image {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
}

/* 预览对话框底部操作栏 */
.preview-dialog-footer {
  display: flex;
  gap: 12px;
  justify-content: center;
  align-items: center;
}

/* 移动端优化 */
/* 触摸优化 */
.el-radio-button,
.el-button,
.el-select,
.el-input-number {
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .generate-container {
    padding: 12px;
    max-width: 100%;
  }

  .header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    margin-bottom: 16px;
  }

  .title {
    font-size: 22px;
    text-align: center;
    margin: 0;
  }

  .credits-info {
    text-align: center;
  }

  .credits-info .el-tag {
    font-size: 15px;
    padding: 8px 16px;
    border-radius: 20px;
  }

  /* 模式选择器优化 */
  .mode-selector {
    margin-bottom: 16px;
  }

  .mode-header {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
    text-align: center;
  }

  .mode-header .el-tag {
    align-self: center;
  }

  .el-radio-group {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
  }

  .el-radio-button {
    flex: 1;
    min-width: 120px;
  }

  .el-radio-button .el-radio-button__inner {
    height: 48px;
    line-height: 48px;
    font-size: 15px;
    font-weight: 600;
    padding: 0 16px;
    border-radius: 24px;
  }

  /* 表单容器优化 - Material Design规范 */
  .generate-form {
    margin-bottom: 16px;
  }

  .generate-form .el-card__body {
    padding: 16px;
    box-sizing: border-box;
  }

  .el-form {
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
  }

  /* 强制el-row垂直堆叠 - 关键修复！ */
  .el-row {
    display: flex !important;
    flex-direction: column !important;
    width: 100% !important;
  }

  /* 强制el-col全宽 - 覆盖栅格系统 */
  .el-col {
    max-width: 100% !important;
    flex: 0 0 100% !important;
    width: 100% !important;
  }

  .el-form-item {
    margin-bottom: 20px;
    width: 100%;
    box-sizing: border-box;
  }

  .el-form-item__label {
    font-size: 14px;
    font-weight: 600;
    line-height: 1.5;
    padding-bottom: 8px;
  }

  .el-form-item__content {
    width: 100%;
    max-width: 100%;
  }

  /* 文本输入框优化 - 防止溢出，使用:deep()穿透 */
  .el-textarea {
    width: 100% !important;
    box-sizing: border-box;
  }

  :deep(.el-textarea__inner) {
    width: 100% !important;
    min-height: 120px !important;
    font-size: 16px !important;  /* 防止iOS自动缩放 */
    line-height: 1.6;
    padding: 12px;
    box-sizing: border-box;
    border-radius: 8px;
  }

  /* 选择器全宽优化 - 使用:deep()穿透Element Plus内部样式 */
  .el-select {
    width: 100% !important;
    box-sizing: border-box;
  }

  /* 深度修复el-select内部wrapper的flex收缩问题 */
  :deep(.el-select__wrapper) {
    width: 100% !important;
    min-width: 100% !important;
    flex: 1 1 100% !important;
    box-sizing: border-box;
  }

  :deep(.el-select__selection) {
    width: 100% !important;
    flex: 1 1 100% !important;
  }

  :deep(.el-select .el-input) {
    width: 100% !important;
  }

  :deep(.el-select .el-input__wrapper) {
    width: 100% !important;
    min-width: 100% !important;
    box-sizing: border-box;
  }

  :deep(.el-select .el-input__inner) {
    height: 48px;
    font-size: 16px;
    border-radius: 8px;
    width: 100%;
  }

  /* 数量选择器优化 - 深度修复内部结构 */
  .el-input-number {
    width: 100% !important;
    box-sizing: border-box;
  }

  :deep(.el-input-number .el-input__wrapper) {
    width: 100% !important;
    min-width: 100% !important;
    flex: 1 1 100% !important;
    box-sizing: border-box;
  }

  :deep(.el-input-number .el-input__inner) {
    height: 48px;
    font-size: 16px;
    text-align: center;
    width: 100%;
  }

  /* 按钮优化 - Material Design 触摸目标 */
  .el-form-item .el-button {
    width: 100%;
    height: 48px;
    min-height: 48px;
    font-size: 16px;
    font-weight: 600;
    border-radius: 24px;
    box-sizing: border-box;
    margin: 0;
  }

  /* 生成按钮特殊样式 */
  .el-button--primary {
    height: 52px;
    font-size: 17px;
    letter-spacing: 0.5px;
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
  }

  .el-button--primary:active {
    transform: scale(0.98);
  }

  /* 按钮行优化 */
  .button-row {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 24px;
    width: 100%;
  }

  .button-row .el-button {
    width: 100%;
    margin-left: 0 !important;
  }

  /* 图片网格优化 */
  .image-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  /* 上传区域优化 */
  .upload-area {
    padding: 24px 16px;
    min-height: 160px;
  }

  .upload-icon {
    font-size: 32px;
  }

  .upload-text {
    font-size: 15px;
  }

  .upload-tip {
    font-size: 12px;
    line-height: 1.4;
  }

  /* 图片预览优化 */
  .image-preview {
    width: 120px;
    height: 120px;
    margin: 0 auto;
  }

  /* 结果展示优化 */
  .results {
    margin-top: 16px;
  }

  .results-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    text-align: center;
  }

  .results-header h3 {
    margin: 0;
    font-size: 18px;
  }

  .stats-info {
    font-size: 13px;
  }

  /* 智能建议优化 */
  .smart-suggestions {
    margin-top: 12px;
    padding: 12px;
    border-radius: 8px;
  }

  .suggestions-header {
    margin-bottom: 12px;
  }

  .suggestion-item {
    padding: 12px;
    margin-bottom: 12px;
    border-radius: 6px;
  }

  .suggestion-header {
    flex-direction: column;
    align-items: stretch;
    gap: 6px;
    text-align: center;
  }

  .confidence {
    align-self: center;
  }

  .optimized-prompt,
  .recommended-value {
    font-size: 12px;
    padding: 8px;
    line-height: 1.5;
  }

  .apply-btn {
    width: 100%;
    margin-top: 12px;
    height: 40px;
    font-size: 14px;
    border-radius: 20px;
  }

  /* 触摸优化 - Material Design */
  .el-button,
  .el-select,
  .el-input-number,
  .el-radio-button {
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
  }

  /* 防止iOS双击缩放 */
  input,
  textarea,
  select,
  button {
    touch-action: manipulation;
  }
}

@media (max-width: 480px) {
  .generate-container {
    padding: 8px;
  }

  .title {
    font-size: 20px;
  }

  .credits-info .el-tag {
    font-size: 14px;
    padding: 6px 12px;
  }

  .el-radio-button .el-radio-button__inner {
    height: 44px;
    line-height: 44px;
    font-size: 14px;
    padding: 0 12px;
  }

  .el-textarea__inner {
    min-height: 80px !important;
    font-size: 13px;
  }

  .button-row .el-button {
    height: 44px;
    font-size: 15px;
  }

  .upload-area {
    padding: 20px 12px;
    min-height: 140px;
  }

  .upload-icon {
    font-size: 28px;
  }

  .upload-text {
    font-size: 14px;
  }

  .image-preview {
    width: 100px;
    height: 100px;
  }

  .results-header h3 {
    font-size: 16px;
  }

  .smart-suggestions {
    padding: 10px;
  }

  .suggestion-item {
    padding: 10px;
  }

  .apply-btn {
    height: 36px;
    font-size: 13px;
  }
}

/* 超小屏幕优化 */
@media (max-width: 360px) {
  .generate-container {
    padding: 6px;
  }

  .title {
    font-size: 18px;
  }

  .el-radio-button .el-radio-button__inner {
    font-size: 13px;
    padding: 0 8px;
  }

  .button-row .el-button {
    height: 42px;
    font-size: 14px;
  }

  .upload-area {
    padding: 16px 8px;
    min-height: 120px;
  }
}

/* 横屏模式优化 */
@media (max-height: 600px) and (orientation: landscape) {
  .generate-container {
    padding: 8px;
  }

  .title {
    font-size: 18px;
  }

  .upload-area {
    min-height: 100px;
    padding: 16px;
  }

  .image-preview {
    width: 80px;
    height: 80px;
  }

  .smart-suggestions {
    max-height: 200px;
    overflow-y: auto;
  }
}

/* 加载状态样式 */
.loading-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  background: #f8f9fa;
  border: 2px dashed #409eff;
  border-radius: 8px;
  color: #409eff;
  transition: all 0.3s ease;
}

.loading-text {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 8px;
}

.loading-tip {
  font-size: 12px;
  color: #909399;
}

.loading-area .el-loading-mask {
  border-radius: 8px;
}

/* 生成进度指示器样式 */
.generation-progress {
  margin-top: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.progress-bar {
  margin-bottom: 12px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
}

.elapsed-time {
  color: #409eff;
  font-weight: 500;
}

.estimated-time {
  color: #909399;
}

/* Phase 1: 增强的进度信息样式 */
.enhanced-progress-info {
  border-top: 1px solid #e4e7ed;
  padding-top: 12px;
  margin-top: 8px;
}

.current-stage {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409eff;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
}

.current-stage .el-icon {
  animation: rotate 2s linear infinite;
}

.performance-insight {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 13px;
  margin-bottom: 8px;
}

.system-status {
  display: flex;
  justify-content: flex-end;
}

.load-indicator {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.load-normal {
  background: #f0f9ff;
  color: #0084ff;
}

.load-medium {
  background: #fff7e6;
  color: #fa8c16;
}

.load-high {
  background: #fff2f0;
  color: #ff4d4f;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计优化 */
@media (max-width: 768px) {
  .generation-progress {
    margin-top: 12px;
    padding: 12px;
  }

  .progress-info {
    font-size: 12px;
  }
}

/* 极简中心式进度条样式 - 浮层模式 */
.generation-progress-minimalist {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 24px;
}

.progress-circle-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  background: #ffffff;
  padding: 48px 32px;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

.progress-circle {
  transition: all 0.3s ease;
}

.progress-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.remaining-time {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.time-value {
  font-size: 48px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
  letter-spacing: -0.5px;
}

.time-unit {
  font-size: 16px;
  color: #909399;
  font-weight: 400;
}

.stage-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f5f7fa;
  border-radius: 20px;
}

.rotating-icon {
  font-size: 14px;
  color: #409eff;
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.stage-text {
  font-size: 14px;
  color: #606266;
  font-weight: 400;
  white-space: nowrap;
}

.cancel-button-minimalist {
  margin-top: 8px;
  color: #909399;
  font-size: 14px;
  padding: 8px 20px;
  transition: all 0.2s ease;
}

.cancel-button-minimalist:hover {
  color: #f56c6c;
  background-color: #fef0f0;
}

/* 统一的响应式布局 - PC和移动端 */
@media (max-width: 768px) {
  .generation-progress-minimalist {
    padding: 20px;
  }

  .progress-circle-container {
    padding: 40px 28px;
    border-radius: 12px;
  }

  .progress-circle {
    width: 160px !important;
    height: 160px !important;
  }

  .time-value {
    font-size: 42px;
  }

  .time-unit {
    font-size: 14px;
  }

  .stage-indicator {
    padding: 6px 14px;
  }

  .stage-text {
    font-size: 13px;
  }

  .cancel-button-minimalist {
    font-size: 13px;
    padding: 6px 16px;
  }
}

@media (max-width: 480px) {
  .generation-progress-minimalist {
    padding: 16px;
  }

  .progress-circle-container {
    padding: 36px 24px;
    border-radius: 12px;
  }

  .progress-circle {
    width: 140px !important;
    height: 140px !important;
  }

  .time-value {
    font-size: 36px;
  }

  .time-unit {
    font-size: 13px;
  }

  .stage-indicator {
    padding: 6px 12px;
  }

  .stage-text {
    font-size: 12px;
  }

  .cancel-button-minimalist {
    font-size: 12px;
    padding: 5px 14px;
  }
}

/* 触摸优化 */
.cancel-button-minimalist {
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

/* 图片上传容器 */
.image-upload-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

.gallery-select-btn {
  align-self: flex-start;
}

/* 画廊选择器对话框 */
.gallery-selector-dialog {
  .gallery-selector-content {
    min-height: 400px;
    max-height: 600px;
    overflow-y: auto;
  }
  
  .loading-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 400px;
  }
  
  .gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
    padding: 8px;
  }
  
  .gallery-item {
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;
    border: 3px solid transparent;
    transition: all 0.3s ease;
    background: var(--el-fill-color-light);
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    &.selected {
      border-color: var(--el-color-primary);
      box-shadow: 0 0 0 2px var(--el-color-primary-light-5);
    }
    
    img {
      width: 100%;
      height: 200px;
      object-fit: cover;
      display: block;
      image-rendering: -webkit-optimize-contrast;
      transition: opacity 0.3s ease-in;
    }
    
    img[loading] {
      opacity: 0;
    }
    
    img:not([loading]) {
      opacity: 1;
    }
    
    .selection-indicator {
      position: absolute;
      top: 8px;
      right: 8px;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: white;
      border: 2px solid var(--el-border-color);
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s ease;
      
      .el-icon {
        font-size: 20px;
        color: var(--el-color-primary);
        font-weight: bold;
      }
    }
    
    &.selected .selection-indicator {
      background: var(--el-color-primary);
      border-color: var(--el-color-primary);
      
      .el-icon {
        color: white;
      }
    }
    
    .image-info {
      padding: 12px;
      background: white;
      
      .prompt {
        margin: 0;
        font-size: 12px;
        color: var(--el-text-color-regular);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }
  
  .dialog-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .selection-count {
      font-size: 14px;
      color: var(--el-text-color-regular);
      font-weight: 500;
    }
  }
}

/* 移动端响应式 */
@media (max-width: 768px) {
  .gallery-selector-dialog {
    .gallery-grid {
      grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
      gap: 12px;
    }
    
    .gallery-item {
      img {
        height: 150px;
      }
      
      .image-info {
        padding: 8px;
        
        .prompt {
          font-size: 11px;
        }
      }
    }
  }
}

/* 粘贴提示样式 */
.paste-hint {
  color: var(--el-color-primary);
  font-size: 12px;
  font-weight: 500;
  margin-top: 4px;
  display: inline-block;
}

.el-upload__tip {
  line-height: 1.6;
}
</style>