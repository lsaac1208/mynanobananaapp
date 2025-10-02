/**
 * AI生成状态管理
 */
import { defineStore } from 'pinia'
import type {
  GenerateTextToImageRequest,
  GenerateImageToImageRequest,
  GeneratedImage,
  GenerateResponse
} from '@shared/index'
import { generateApi } from '../services/api'
import { useAuthStore } from './auth'
import { useGalleryStore } from './gallery'

type GenerateMode = 'text-to-image' | 'image-to-image'

interface GenerateState {
  // 生成模式
  mode: GenerateMode

  // 加载状态
  generating: boolean

  // 可用选项
  availableModels: string[]
  availableSizes: string[]

  // 生成结果
  generatedImages: GeneratedImage[]
  lastGenerationTime: number | null

  // 表单数据
  textToImageForm: GenerateTextToImageRequest
  imageToImageForm: Omit<GenerateImageToImageRequest, 'image'> & { image: File | null }

  // 错误信息
  error: string | null

  // 历史记录
  generationHistory: GenerateResponse[]
}

export const useGenerateStore = defineStore('generate', {
  state: (): GenerateState => ({
    mode: 'text-to-image',
    generating: false,
    availableModels: ['nano-banana', 'nano-banana-hd'],
    availableSizes: ['1x1', '3x4', '4x3', '16x9'],
    generatedImages: [],
    lastGenerationTime: null,
    textToImageForm: {
      prompt: '',
      model: 'nano-banana',
      size: '4x3',
      n: 1
    },
    imageToImageForm: {
      prompt: '',
      image: null,
      model: 'nano-banana',
      size: '4x3',
      n: 1
    },
    error: null,
    generationHistory: []
  }),

  getters: {
    // 当前模式是否为文生图
    isTextToImage: (state) => state.mode === 'text-to-image',

    // 当前模式是否为图生图
    isImageToImage: (state) => state.mode === 'image-to-image',

    // 是否可以生成（表单验证）
    canGenerate: (state) => {
      const authStore = useAuthStore()

      // 检查用户次数
      if (!authStore.user || authStore.user.credits <= 0) {
        return false
      }

      // 检查表单完整性
      if (state.mode === 'text-to-image') {
        return state.textToImageForm.prompt.trim().length > 0
      } else {
        return state.imageToImageForm.prompt.trim().length > 0 && state.imageToImageForm.image !== null
      }
    },

    // 获取当前表单数据
    currentForm: (state) => {
      return state.mode === 'text-to-image' ? state.textToImageForm : state.imageToImageForm
    },

    // 生成历史统计
    historyStats: (state) => {
      const total = state.generationHistory.length
      const successful = state.generationHistory.filter(h => h.success).length
      const failed = total - successful

      return { total, successful, failed }
    },

    // 最后一次生成信息
    lastGeneration: (state) => {
      return state.generationHistory[0] || null
    }
  },

  actions: {
    // 设置生成模式
    setMode(mode: GenerateMode) {
      this.mode = mode
      this.clearError()
    },

    // 加载可用模型和尺寸
    async loadAvailableOptions() {
      try {
        const response = await generateApi.getAvailableModels()
        if (response.success) {
          this.availableModels = response.models
          this.availableSizes = response.sizes
        }
      } catch (error) {
        console.error('加载可用选项失败:', error)
      }
    },

    // 文生图
    async generateTextToImage() {
      if (!this.canGenerate || this.generating) {
        return { success: false, error: '无法生成图片' }
      }

      this.generating = true
      this.clearError()

      try {
        const response = await generateApi.textToImage(this.textToImageForm)

        if (response.success && response.images) {
          this.generatedImages = response.images
          this.lastGenerationTime = response.generation_time || null

          // 更新用户次数
          const authStore = useAuthStore()
          if (authStore.user && response.remaining_credits !== undefined) {
            authStore.user.credits = response.remaining_credits
          }

          // 添加到历史记录
          this.addToHistory(response)

          // 如果有作品创建，添加到画廊
          if (response.images.length > 0) {
            this.addToGallery(response)
          }
        } else {
          this.error = response.error || '生成失败'
        }

        return response
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || '生成失败，请稍后重试'
        this.error = errorMessage

        return {
          success: false,
          error: errorMessage
        }
      } finally {
        this.generating = false
      }
    },

    // 图生图
    async generateImageToImage() {
      if (!this.canGenerate || this.generating || !this.imageToImageForm.image) {
        return { success: false, error: '无法生成图片' }
      }

      this.generating = true
      this.clearError()

      try {
        const requestData: GenerateImageToImageRequest = {
          prompt: this.imageToImageForm.prompt,
          image: this.imageToImageForm.image,
          model: this.imageToImageForm.model,
          size: this.imageToImageForm.size,
          n: this.imageToImageForm.n
        }

        const response = await generateApi.imageToImage(requestData)

        if (response.success && response.images) {
          this.generatedImages = response.images
          this.lastGenerationTime = response.generation_time || null

          // 更新用户次数
          const authStore = useAuthStore()
          if (authStore.user && response.remaining_credits !== undefined) {
            authStore.user.credits = response.remaining_credits
          }

          // 添加到历史记录
          this.addToHistory(response)

          // 如果有作品创建，添加到画廊
          if (response.images.length > 0) {
            this.addToGallery(response)
          }
        } else {
          this.error = response.error || '生成失败'
        }

        return response
      } catch (error: any) {
        const errorMessage = error.response?.data?.error || '生成失败，请稍后重试'
        this.error = errorMessage

        return {
          success: false,
          error: errorMessage
        }
      } finally {
        this.generating = false
      }
    },

    // 设置上传的图片
    setUploadedImage(file: File) {
      this.imageToImageForm.image = file
    },

    // 移除上传的图片
    removeUploadedImage() {
      this.imageToImageForm.image = null
    },

    // 更新文生图表单
    updateTextToImageForm(updates: Partial<GenerateTextToImageRequest>) {
      this.textToImageForm = { ...this.textToImageForm, ...updates }
    },

    // 更新图生图表单
    updateImageToImageForm(updates: Partial<Omit<GenerateImageToImageRequest, 'image'>>) {
      this.imageToImageForm = { ...this.imageToImageForm, ...updates }
    },

    // 重置表单
    resetForm() {
      this.textToImageForm = {
        prompt: '',
        model: 'nano-banana',
        size: '4x3',
        n: 1
      }

      this.imageToImageForm = {
        prompt: '',
        image: null,
        model: 'nano-banana',
        size: '4x3',
        n: 1
      }

      this.clearError()
    },

    // 清除错误
    clearError() {
      this.error = null
    },

    // 清除生成结果
    clearResults() {
      this.generatedImages = []
      this.lastGenerationTime = null
      this.clearError()
    },

    // 添加到历史记录
    addToHistory(response: GenerateResponse) {
      this.generationHistory.unshift(response)

      // 限制历史记录数量
      if (this.generationHistory.length > 50) {
        this.generationHistory = this.generationHistory.slice(0, 50)
      }
    },

    // 添加到画廊（模拟，实际由后端处理）
    addToGallery(response: GenerateResponse) {
      const galleryStore = useGalleryStore()

      // 这里只是通知画廊刷新，实际的作品添加由后端自动处理
      // 在真实场景中，生成成功后后端会自动保存到数据库
      setTimeout(() => {
        galleryStore.refresh()
      }, 1000)
    },

    // 下载图片
    async downloadImage(imageUrl: string, filename?: string) {
      try {
        const response = await fetch(imageUrl)
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)

        const link = document.createElement('a')
        link.href = url
        link.download = filename || `generated-image-${Date.now()}.png`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)

        window.URL.revokeObjectURL(url)

        return { success: true }
      } catch (error) {
        console.error('下载图片失败:', error)
        return { success: false, error: '下载失败' }
      }
    },

    // 重置状态
    reset() {
      this.mode = 'text-to-image'
      this.generating = false
      this.generatedImages = []
      this.lastGenerationTime = null
      this.error = null
      this.generationHistory = []
      this.resetForm()
    }
  }
})