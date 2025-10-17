import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { generateApi } from '@/services/api'

export interface GeneratedImage {
  url: string
  prompt: string
  model: string
  size: string
  createdAt: Date
}

export interface GenerationParams {
  prompt: string
  model: string
  size: string
  num_images?: number
  negative_prompt?: string
}

export interface ImageToImageParams extends GenerationParams {
  image: string
  strength?: number
}

export type GenerateMode = 'text-to-image' | 'image-to-image'

export const useGenerateStore = defineStore('generate', () => {
  // State
  const generateMode = ref<GenerateMode>('text-to-image')
  const generating = ref(false)
  const generationProgress = ref(0)
  const estimatedTime = ref(0)
  const elapsedTime = ref(0)
  const currentStage = ref('')
  const generatedImages = ref<GeneratedImage[]>([])
  const availableModels = ref<string[]>([])
  const availableSizes = ref<string[]>([])
  
  // Progress tracking
  let progressTimer: number | null = null
  let progressStartTime: number = 0

  // Computed
  const hasGeneratedImages = computed(() => generatedImages.value.length > 0)
  const remainingTime = computed(() => Math.max(0, estimatedTime.value - elapsedTime.value))
  const progressPercentage = computed(() => Math.min(100, generationProgress.value))

  // Actions
  const setMode = (mode: GenerateMode) => {
    generateMode.value = mode
  }

  const loadAvailableOptions = async () => {
    try {
      const response = await generateApi.getModels()
      if (response.data.success) {
        availableModels.value = response.data.models || []
        availableSizes.value = response.data.sizes || []
        }
      } catch (error) {
      console.error('Failed to load available options:', error)
    }
  }

  const startProgress = (mode: GenerateMode) => {
    generating.value = true
    generationProgress.value = 0
    elapsedTime.value = 0
    progressStartTime = Date.now()
    
    // Estimate time based on mode
    estimatedTime.value = mode === 'text-to-image' ? 15 : 20
    
    // Set initial stage
    currentStage.value = '正在连接AI服务...'
    
    // Start progress simulation
    progressTimer = window.setInterval(() => {
      elapsedTime.value = Math.floor((Date.now() - progressStartTime) / 1000)
      
      // Simulate progress
      if (generationProgress.value < 30) {
        generationProgress.value += 2
        currentStage.value = '正在处理提示词...'
      } else if (generationProgress.value < 60) {
        generationProgress.value += 1.5
        currentStage.value = '正在生成图像...'
      } else if (generationProgress.value < 90) {
        generationProgress.value += 1
        currentStage.value = '正在优化细节...'
      } else if (generationProgress.value < 95) {
        generationProgress.value += 0.5
        currentStage.value = '即将完成...'
      }
    }, 500)
  }

  const stopProgress = () => {
    if (progressTimer) {
      clearInterval(progressTimer)
      progressTimer = null
    }
    generationProgress.value = 100
    currentStage.value = '生成完成！'
    
    // Reset after a short delay
    setTimeout(() => {
      generating.value = false
      generationProgress.value = 0
      elapsedTime.value = 0
      currentStage.value = ''
    }, 1000)
  }

  const generateTextToImage = async (params: GenerationParams) => {
    startProgress('text-to-image')
    
    try {
      const response = await generateApi.textToImage(params)
      
      if (response.data.success && response.data.images) {
        const newImages: GeneratedImage[] = response.data.images.map((url: string) => ({
          url,
          prompt: params.prompt,
          model: params.model,
          size: params.size,
          createdAt: new Date()
        }))
        
        generatedImages.value = [...newImages, ...generatedImages.value]
        stopProgress()
        return response.data
        } else {
        throw new Error(response.data.error || '生成失败')
      }
    } catch (error) {
      stopProgress()
      throw error
    }
  }

  const generateImageToImage = async (params: ImageToImageParams) => {
    startProgress('image-to-image')
    
    try {
      const response = await generateApi.imageToImage(params)
      
      if (response.data.success && response.data.images) {
        const newImages: GeneratedImage[] = response.data.images.map((url: string) => ({
          url,
          prompt: params.prompt,
          model: params.model,
          size: params.size,
          createdAt: new Date()
        }))
        
        generatedImages.value = [...newImages, ...generatedImages.value]
        stopProgress()
        return response.data
      } else {
        throw new Error(response.data.error || '生成失败')
      }
      } catch (error) {
      stopProgress()
      throw error
    }
  }

  const clearGeneratedImages = () => {
    generatedImages.value = []
  }

  const removeGeneratedImage = (index: number) => {
    generatedImages.value.splice(index, 1)
  }

  const cancelGeneration = () => {
    stopProgress()
    currentStage.value = '已取消'
  }

  return {
    // State
    generateMode,
    generating,
    generationProgress,
    estimatedTime,
    elapsedTime,
    currentStage,
    generatedImages,
    availableModels,
    availableSizes,
    
    // Computed
    hasGeneratedImages,
    remainingTime,
    progressPercentage,
    
    // Actions
    setMode,
    loadAvailableOptions,
    generateTextToImage,
    generateImageToImage,
    clearGeneratedImages,
    removeGeneratedImage,
    cancelGeneration
  }
})
