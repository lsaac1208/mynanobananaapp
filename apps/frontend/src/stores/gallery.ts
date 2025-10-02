/**
 * 画廊状态管理
 */
import { defineStore } from 'pinia'
import type { Creation, GalleryStats, GalleryFilters } from '@shared/index'
import { galleryApi } from '../services/api'

interface GalleryState {
  creations: Creation[]
  stats: GalleryStats | null
  loading: boolean
  currentPage: number
  perPage: number
  totalPages: number
  filters: GalleryFilters
  selectedCreation: Creation | null
}

export const useGalleryStore = defineStore('gallery', {
  state: (): GalleryState => ({
    creations: [],
    stats: null,
    loading: false,
    currentPage: 1,
    perPage: 20,
    totalPages: 1,
    filters: {},
    selectedCreation: null
  }),

  getters: {
    // 获取收藏的作品
    favoriteCreations: (state) => state.creations.filter(c => c.is_favorite),

    // 按分类分组
    creationsByCategory: (state) => {
      const grouped: Record<string, Creation[]> = {}
      state.creations.forEach(creation => {
        if (!grouped[creation.category]) {
          grouped[creation.category] = []
        }
        grouped[creation.category].push(creation)
      })
      return grouped
    },

    // 获取所有分类
    availableCategories: (state) => {
      const categories = new Set(state.creations.map(c => c.category))
      return Array.from(categories).sort()
    },

    // 获取所有标签
    availableTags: (state) => {
      const tags = new Set<string>()
      state.creations.forEach(creation => {
        if (creation.tags) {
          creation.tags.split(',').forEach(tag => tags.add(tag.trim()))
        }
      })
      return Array.from(tags).sort()
    },

    // 是否有更多页面
    hasMorePages: (state) => state.currentPage < state.totalPages,

    // 是否为空画廊
    isEmpty: (state) => state.creations.length === 0 && !state.loading
  },

  actions: {
    // 获取画廊作品
    async fetchCreations(filters: GalleryFilters = {}, append = false) {
      this.loading = true

      try {
        const queryFilters = { ...this.filters, ...filters }
        const response = await galleryApi.getCreations(queryFilters)

        if (response.success) {
          if (append) {
            this.creations.push(...response.creations)
          } else {
            this.creations = response.creations
          }

          this.stats = response.stats
          this.currentPage = response.page
          this.perPage = response.per_page
          this.totalPages = Math.ceil(response.stats.total / response.per_page)
          this.filters = queryFilters
        }

        return response
      } catch (error: any) {
        console.error('获取画廊作品失败:', error)
        return {
          success: false,
          error: error.response?.data?.error || '获取作品失败'
        }
      } finally {
        this.loading = false
      }
    },

    // 加载更多作品（分页）
    async loadMore() {
      if (!this.hasMorePages || this.loading) {
        return
      }

      const nextPageFilters = {
        ...this.filters,
        page: this.currentPage + 1
      }

      return this.fetchCreations(nextPageFilters, true)
    },

    // 刷新画廊
    async refresh() {
      return this.fetchCreations(this.filters, false)
    },

    // 搜索作品
    async searchCreations(searchQuery: string) {
      const searchFilters = {
        ...this.filters,
        search: searchQuery,
        page: 1
      }
      return this.fetchCreations(searchFilters, false)
    },

    // 按分类筛选
    async filterByCategory(category: string | null) {
      const categoryFilters = {
        ...this.filters,
        category: category || undefined,
        page: 1
      }
      return this.fetchCreations(categoryFilters, false)
    },

    // 按收藏筛选
    async filterByFavorite(isFavorite: boolean | null) {
      const favoriteFilters = {
        ...this.filters,
        is_favorite: isFavorite === null ? undefined : isFavorite,
        page: 1
      }
      return this.fetchCreations(favoriteFilters, false)
    },

    // 清除筛选
    async clearFilters() {
      this.filters = {}
      return this.fetchCreations({}, false)
    },

    // 删除作品
    async deleteCreation(creationId: number) {
      try {
        const response = await galleryApi.deleteCreation(creationId)

        if (response.success) {
          // 从本地状态中移除
          const index = this.creations.findIndex(c => c.id === creationId)
          if (index > -1) {
            this.creations.splice(index, 1)
          }

          // 更新统计信息
          if (this.stats) {
            this.stats.total--
          }
        }

        return response
      } catch (error: any) {
        console.error('删除作品失败:', error)
        return {
          success: false,
          error: error.response?.data?.error || '删除作品失败'
        }
      }
    },

    // 更新收藏状态
    async toggleFavorite(creationId: number) {
      const creation = this.creations.find(c => c.id === creationId)
      if (!creation) {
        return { success: false, error: '作品未找到' }
      }

      const newFavoriteStatus = !creation.is_favorite

      try {
        const response = await galleryApi.updateFavorite(creationId, newFavoriteStatus)

        if (response.success) {
          // 更新本地状态
          creation.is_favorite = newFavoriteStatus

          // 更新统计信息
          if (this.stats) {
            if (newFavoriteStatus) {
              this.stats.favorites++
            } else {
              this.stats.favorites--
            }
          }
        }

        return response
      } catch (error: any) {
        console.error('更新收藏状态失败:', error)
        return {
          success: false,
          error: error.response?.data?.error || '更新收藏状态失败'
        }
      }
    },

    // 更新标签
    async updateTags(creationId: number, tags: string) {
      const creation = this.creations.find(c => c.id === creationId)
      if (!creation) {
        return { success: false, error: '作品未找到' }
      }

      try {
        const response = await galleryApi.updateTags(creationId, tags)

        if (response.success) {
          // 更新本地状态
          creation.tags = tags
          creation.updated_at = new Date().toISOString()
        }

        return response
      } catch (error: any) {
        console.error('更新标签失败:', error)
        return {
          success: false,
          error: error.response?.data?.error || '更新标签失败'
        }
      }
    },

    // 更新分类
    async updateCategory(creationId: number, category: string) {
      const creation = this.creations.find(c => c.id === creationId)
      if (!creation) {
        return { success: false, error: '作品未找到' }
      }

      try {
        const response = await galleryApi.updateCategory(creationId, category)

        if (response.success) {
          // 更新本地状态
          creation.category = category
          creation.updated_at = new Date().toISOString()
        }

        return response
      } catch (error: any) {
        console.error('更新分类失败:', error)
        return {
          success: false,
          error: error.response?.data?.error || '更新分类失败'
        }
      }
    },

    // 设置选中的作品
    setSelectedCreation(creation: Creation | null) {
      this.selectedCreation = creation
    },

    // 添加新作品到画廊（用于生成完成后）
    addCreation(creation: Creation) {
      this.creations.unshift(creation)

      // 更新统计信息
      if (this.stats) {
        this.stats.total++
        this.stats.recent_week++
      }
    },

    // 重置状态
    reset() {
      this.creations = []
      this.stats = null
      this.loading = false
      this.currentPage = 1
      this.totalPages = 1
      this.filters = {}
      this.selectedCreation = null
    }
  }
})