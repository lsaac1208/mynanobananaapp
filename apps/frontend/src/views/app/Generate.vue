<template>
  <div class="generate-container">
    <!-- 标题区域 -->
    <div class="header">
      <h2 class="title">AI 图片生成</h2>
      <div class="credits-info">
        <el-tag type="info" size="large">
          剩余次数: {{ userStore.user?.credits || 0 }}
        </el-tag>
      </div>
    </div>

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
            <el-form-item label="模型">
              <el-select v-model="textForm.model" placeholder="选择模型">
                <el-option
                  v-for="model in availableModels"
                  :key="model"
                  :label="model"
                  :value="model"
                />
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
        <el-form-item label="参考图片" prop="image">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleImageChange"
            accept="image/*"
            class="image-upload"
            :disabled="isLoadingReferenceImage"
          >
            <div v-if="isLoadingReferenceImage" class="loading-area" v-loading="true">
              <div class="loading-text">正在加载参考图片...</div>
              <div class="loading-tip">请稍候，图片加载中</div>
            </div>
            <div v-else-if="!imagePreview" class="upload-area">
              <el-icon class="upload-icon"><Plus /></el-icon>
              <div class="upload-text">点击上传图片</div>
              <div class="upload-tip">支持 JPG、PNG、GIF、WEBP 格式，最大 10MB</div>
            </div>
            <div v-else class="image-preview">
              <img :src="imagePreview" alt="预览图片" />
              <div class="image-overlay">
                <el-button type="danger" circle @click="removeImage">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </el-upload>
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

        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="模型">
              <el-select v-model="imageForm.model" placeholder="选择模型">
                <el-option
                  v-for="model in availableModels"
                  :key="model"
                  :label="model"
                  :value="model"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="尺寸">
              <el-select v-model="imageForm.size" placeholder="选择尺寸">
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
                v-model="imageForm.n"
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
            :disabled="!imageForm.prompt || !imageForm.image || userStore.user?.credits === 0"
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

    <!-- 图片预览对话框 -->
    <el-dialog v-model="previewVisible" title="图片预览" width="80%" center>
      <div class="preview-container">
        <img :src="previewImageUrl" alt="预览图片" class="preview-image" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'
import { Plus, Delete, MagicStick, Loading, InfoFilled, CircleCheck, Close } from '@element-plus/icons-vue'
import type { FormInstance, FormRules, UploadFile } from 'element-plus'
import { generateApi } from '@/services/api'
import type { GeneratedImage, GenerateTextToImageRequest, GenerateImageToImageRequest } from '@shared/index'
import { useAuthStore } from '@/stores/auth'
import { useGalleryStore } from '@/stores/gallery'

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

// 进度指示器
const generationProgress = ref(0)
const estimatedTime = ref(0)
const elapsedTime = ref(0)
const progressInterval = ref<NodeJS.Timeout | null>(null)

// 性能监控和用户体验增强 (Phase 1)
const currentStage = ref('')
const performanceInsight = ref('')
const systemLoad = ref(0)
const averageGenerationTime = ref(0)

// 图片预览
const previewVisible = ref(false)
const previewImageUrl = ref('')

// 文生图表单
const textFormRef = ref<FormInstance>()
const textForm = reactive<GenerateTextToImageRequest>({
  prompt: '',
  model: 'nano-banana',
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
const imageForm = reactive<Omit<GenerateImageToImageRequest, 'image'> & { image: File | null }>({
  prompt: '',
  image: null,
  model: 'nano-banana',
  size: '4x3',
  n: 1
})

const imageFormRules: FormRules = {
  prompt: [
    { required: true, message: '请输入提示词', trigger: 'blur' },
    { min: 5, message: '提示词至少5个字符', trigger: 'blur' }
  ],
  image: [
    { required: true, message: '请上传参考图片', trigger: 'change' }
  ]
}

// 图片上传相关
const uploadRef = ref()
const imagePreview = ref('')

// 加载状态
const isLoadingReferenceImage = ref(false)

// 生命周期
onMounted(async () => {
  await loadAvailableModels()

  // 处理从画廊复用的参数
  const { mode, referenceImage, prompt } = route.query
  if (mode === 'image-to-image' && referenceImage && prompt) {
    // 切换到图生图模式
    generateMode.value = 'image-to-image'

    // 设置提示词
    imageForm.prompt = String(prompt)

    // 显示加载状态并加载参考图片
    isLoadingReferenceImage.value = true
    try {
      await loadReferenceImage(String(referenceImage))
    } finally {
      isLoadingReferenceImage.value = false
    }
  }
})

// 组件卸载时清理定时器
onUnmounted(() => {
  if (progressInterval.value) {
    clearInterval(progressInterval.value)
    progressInterval.value = null
  }
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

const handleImageChange = (file: UploadFile) => {
  if (!file.raw) return

  // 验证文件类型
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.raw.type)) {
    ElMessage.error('请上传有效的图片文件 (JPG, PNG, GIF, WEBP)')
    return
  }

  // 验证文件大小 (10MB)
  if (file.raw.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 10MB')
    return
  }

  imageForm.image = file.raw

  // 生成预览
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target?.result as string
  }
  reader.readAsDataURL(file.raw)
}

const removeImage = (event: Event) => {
  event.stopPropagation()
  imageForm.image = null
  imagePreview.value = ''
  uploadRef.value?.clearFiles()
}

// 从URL加载参考图片 - 智能加载策略
const loadReferenceImage = async (imageUrl: string, retryCount = 0) => {
  const maxRetries = 2

  try {
    // 策略1: 尝试直接获取图片 (可能遇到CORS)
    let imageData: string
    let contentType = 'image/png'

    try {
      console.log(`尝试直接加载图片: ${imageUrl}`)
      const response = await fetch(imageUrl)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const blob = await response.blob()
      contentType = blob.type || 'image/png'

      // 检查是否是有效的图片类型
      if (!contentType.startsWith('image/')) {
        throw new Error(`无效的图片类型: ${contentType}`)
      }

      // 检查文件大小
      if (blob.size > 10 * 1024 * 1024) {
        throw new Error('图片文件过大（超过10MB）')
      }

      // 转换为base64 data URL
      imageData = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result as string)
        reader.onerror = () => reject(new Error('文件读取失败'))
        reader.readAsDataURL(blob)
      })

      console.log('✅ 直接加载成功')

    } catch (directError) {
      console.log('❌ 直接加载失败:', directError)

      // 策略2: 使用后端代理获取图片
      console.log('🔄 切换到代理模式')

      const { galleryApi } = await import('@/services/api')
      const proxyResponse = await galleryApi.proxyImage(imageUrl)

      if (!proxyResponse.success) {
        throw new Error(proxyResponse.error || '代理获取图片失败')
      }

      imageData = proxyResponse.image_data!
      contentType = proxyResponse.content_type || 'image/png'

      console.log('✅ 代理加载成功, 大小:', proxyResponse.size, 'bytes')
    }

    // 将base64数据转换为File对象
    const base64Data = imageData.split(',')[1]
    const binaryData = atob(base64Data)
    const bytes = new Uint8Array(binaryData.length)

    for (let i = 0; i < binaryData.length; i++) {
      bytes[i] = binaryData.charCodeAt(i)
    }

    const file = new File([bytes], 'reference-image.png', { type: contentType })
    imageForm.image = file

    // 设置预览图片
    imagePreview.value = imageData

    ElMessage.success('参考图片已加载')

  } catch (error) {
    console.error('Load reference image error:', error)

    // 重试机制
    if (retryCount < maxRetries) {
      console.log(`🔄 第 ${retryCount + 1} 次重试...`)
      ElMessage.warning(`加载失败，正在重试... (${retryCount + 1}/${maxRetries})`)

      // 延迟重试
      await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1)))
      return loadReferenceImage(imageUrl, retryCount + 1)
    }

    // 所有重试都失败
    const errorMessage = error instanceof Error ? error.message : '未知错误'
    ElMessage.error(`加载参考图片失败: ${errorMessage}`)
    console.error('最终加载失败:', error)
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
    const response = await generateApi.textToImage({
      prompt: textForm.prompt,
      model: textForm.model,
      size: textForm.size,
      n: textForm.n
    })

    if (response.success && response.images) {
      generatedImages.value = response.images
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
        response.creations.forEach(creation => {
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
  if (!imageFormRef.value) return

  const valid = await imageFormRef.value.validate()
  if (!valid) return

  if (!userStore.user?.credits || userStore.user.credits <= 0) {
    ElMessage.error('生成次数不足，请联系管理员充值')
    return
  }

  if (!imageForm.image) {
    ElMessage.error('请先上传参考图片')
    return
  }

  generating.value = true
  startProgress('image-to-image')

  // Phase 1: 模拟系统负载监控
  systemLoad.value = 0.4 + Math.random() * 0.4 // 图生图负载稍高 40-80%

  try {
    const response = await generateApi.imageToImage({
      prompt: imageForm.prompt,
      image: imageForm.image,
      model: imageForm.model,
      size: imageForm.size,
      n: imageForm.n
    })

    if (response.success && response.images) {
      generatedImages.value = response.images
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
        response.creations.forEach(creation => {
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

const previewImage = (url: string) => {
  previewImageUrl.value = url
  previewVisible.value = true
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
</script>

<style scoped>
.generate-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.title {
  margin: 0;
  color: #2c3e50;
}

.credits-info {
  display: flex;
  align-items: center;
}

.mode-selector {
  margin-bottom: 20px;
}

.mode-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.generate-form {
  margin-bottom: 20px;
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
</style>