/**
 * API服务层
 * 移动端性能优化：添加HTTP缓存支持 + 请求去重
 */
import axios from 'axios'
import type {
  User,
  AuthResponse,
  UserLoginRequest,
  UserCreateRequest,
  UserPermissionsResponse,
  RolesResponse,
  GenerateTextToImageRequest,
  GenerateImageToImageRequest,
  GeneratedImage,
  GenerateResponse,
  AvailableModelsResponse,
  Creation,
  GalleryStats,
  GalleryResponse,
  GalleryFilters
} from '@shared/index'
import { apiCache, generateCacheKey, withCache } from '../utils/cache'
import { withDedup, generateDedupKey } from '../utils/request-dedup'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000, // 增加超时时间到30秒，适应AI生成的处理时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加认证token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理token过期
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // 如果是401错误且不是刷新token的请求
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post('/api/refresh', {}, {
            headers: {
              Authorization: `Bearer ${refreshToken}`
            }
          })

          const newToken = response.data.access_token
          localStorage.setItem('access_token', newToken)

          // 重新发送原请求
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        // 刷新失败，清除tokens并重定向到登录页
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// 认证API
export const authApi = {
  // 用户注册
  register: async (userData: UserCreateRequest): Promise<AuthResponse> => {
    const response = await api.post('/register', userData)
    return response.data
  },

  // 用户登录
  login: async (credentials: UserLoginRequest): Promise<AuthResponse> => {
    const response = await api.post('/login', credentials)
    return response.data
  },

  // 用户登出
  logout: async (): Promise<void> => {
    await api.post('/logout')
  },

  // 检查token有效性
  checkToken: async (): Promise<{ message: string; user: User }> => {
    const response = await api.get('/check-token')
    return response.data
  },

  // 刷新token
  refreshToken: async (): Promise<{ access_token: string }> => {
    const refreshToken = localStorage.getItem('refresh_token')
    const response = await api.post('/refresh', {}, {
      headers: {
        Authorization: `Bearer ${refreshToken}`
      }
    })
    return response.data
  },

  // 获取当前用户权限
  getMyPermissions: async (): Promise<UserPermissionsResponse> => {
    const response = await api.get('/me/permissions')
    return response.data
  },

  // 获取所有角色（管理员）
  getAllRoles: async (): Promise<RolesResponse> => {
    const response = await api.get('/roles')
    return response.data
  }
}

// 用户API
export const userApi = {
  // 获取当前用户信息
  getCurrentUser: async (): Promise<{ user: User }> => {
    const response = await api.get('/users/me')
    return response.data
  }
}

// 生成API
export const generateApi = {
  // 文生图 - 带请求去重
  textToImage: async (params: GenerateTextToImageRequest): Promise<GenerateResponse> => {
    // 生成去重key，基于主要参数
    const dedupKey = generateDedupKey('text-to-image', {
      prompt: params.prompt,
      model: params.model,
      size: params.size
    })
    
    return withDedup(dedupKey, async () => {
      const response = await api.post('/generate/text-to-image', params, {
        timeout: 120000 // AI生成需要更长时间，设置120秒（2分钟）超时
      })
      return response.data
    })
  },

  // 图生图 - 带请求去重，支持多图
  imageToImage: async (params: GenerateImageToImageRequest): Promise<GenerateResponse> => {
    // 图生图的去重key使用prompt和文件大小总和
    const imageSizes = params.images?.reduce((sum, img) => sum + (img instanceof File ? img.size : 0), 0) || 0
    const dedupKey = generateDedupKey('image-to-image', {
      prompt: params.prompt,
      model: params.model,
      imageSizes
    })
    
    return withDedup(dedupKey, async () => {
      const formData = new FormData()
      formData.append('prompt', params.prompt)
      if (params.model) formData.append('model', params.model)
      
      // 支持多图上传
      if (params.images && params.images.length > 0) {
        params.images.forEach(image => {
          formData.append('images[]', image)
        })
      } else if (params.image) {
        // 向后兼容单图
        formData.append('images[]', params.image)
      }

      const response = await api.post('/generate/image-to-image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 120000 // AI生成需要更长时间，设置120秒（2分钟）超时
      })
      return response.data
    })
  },

  // 获取可用模型 - 带缓存
  getAvailableModels: async (): Promise<AvailableModelsResponse> => {
    return withCache(
      async () => {
        const response = await api.get('/generate/models')
        return response.data
      },
      '/generate/models',
      10 * 60 * 1000 // 模型列表缓存10分钟（变化不频繁）
    )
  }
}

// 画廊API - 移动端性能优化：添加缓存支持
export const galleryApi = {
  // 获取画廊作品（支持筛选）- 带缓存
  getCreations: async (filters: GalleryFilters = {}): Promise<GalleryResponse> => {
    const cacheKey = generateCacheKey('/gallery', filters)

    return withCache(
      async () => {
        const params = new URLSearchParams()

        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            params.append(key, value.toString())
          }
        })

        const response = await api.get(`/gallery?${params}`)
        return response.data
      },
      cacheKey,
      2 * 60 * 1000 // 画廊数据缓存2分钟
    )
  },

  // 删除作品 - 清理缓存
  deleteCreation: async (creationId: number): Promise<{ success: boolean; message?: string; error?: string }> => {
    const response = await api.delete(`/gallery/${creationId}`)
    // 删除操作后清理画廊相关缓存
    apiCache.deletePattern('/gallery')
    return response.data
  },

  // 更新收藏状态 - 清理缓存
  updateFavorite: async (creationId: number, isFavorite: boolean): Promise<{ success: boolean; message?: string; error?: string }> => {
    const response = await api.put(`/gallery/${creationId}/favorite`, { is_favorite: isFavorite })
    // 更新操作后清理画廊相关缓存
    apiCache.deletePattern('/gallery')
    return response.data
  },

  // 更新标签 - 清理缓存
  updateTags: async (creationId: number, tags: string): Promise<{ success: boolean; message?: string; error?: string }> => {
    const response = await api.put(`/gallery/${creationId}/tags`, { tags })
    apiCache.deletePattern('/gallery')
    return response.data
  },

  // 更新分类 - 清理缓存
  updateCategory: async (creationId: number, category: string): Promise<{ success: boolean; message?: string; error?: string }> => {
    const response = await api.put(`/gallery/${creationId}/category`, { category })
    apiCache.deletePattern('/gallery')
    return response.data
  },

  // 获取可用分类 - 带缓存
  getCategories: async (): Promise<{ success: boolean; categories: string[]; error?: string }> => {
    return withCache(
      async () => {
        const response = await api.get('/gallery/categories')
        return response.data
      },
      '/gallery/categories',
      5 * 60 * 1000 // 分类数据缓存5分钟
    )
  },

  // 获取常用标签 - 带缓存
  getTags: async (limit: number = 20): Promise<{ success: boolean; tags: string[]; error?: string }> => {
    const cacheKey = generateCacheKey('/gallery/tags', { limit })
    return withCache(
      async () => {
        const response = await api.get(`/gallery/tags?limit=${limit}`)
        return response.data
      },
      cacheKey,
      5 * 60 * 1000 // 标签数据缓存5分钟
    )
  },

  // 获取统计信息 - 带缓存
  getStats: async (): Promise<{ success: boolean; stats: GalleryStats; error?: string }> => {
    return withCache(
      async () => {
        const response = await api.get('/gallery/stats')
        return response.data
      },
      '/gallery/stats',
      1 * 60 * 1000 // 统计数据缓存1分钟
    )
  },

  // 图片代理 - 解决跨域问题
  proxyImage: async (imageUrl: string): Promise<{
    success: boolean;
    image_data?: string;
    content_type?: string;
    size?: number;
    error?: string
  }> => {
    const response = await api.post('/gallery/proxy-image', { image_url: imageUrl })
    return response.data
  }
}

// Phase 2: 性能分析API
export const analyticsApi = {
  // 获取系统性能分析数据
  getPerformanceAnalytics: async (hours: number = 24, operationType?: string): Promise<{
    success: boolean;
    analytics?: {
      avg_generation_time: number;
      error_rate: number;
      peak_server_load: number;
      time_range_hours: number;
      operation_type: string;
    };
    error?: string;
  }> => {
    const params = new URLSearchParams()
    params.append('hours', hours.toString())
    if (operationType) {
      params.append('operation_type', operationType)
    }

    const response = await api.get(`/analytics/performance?${params}`)
    return response.data
  },

  // 获取用户行为分析数据
  getUserBehaviorAnalytics: async (): Promise<{
    success: boolean;
    user_analytics?: {
      preferred_model: string | null;
      most_active_hour: number | null;
      avg_session_duration: number;
      current_active_sessions: number;
    };
    error?: string;
  }> => {
    const response = await api.get('/analytics/user-behavior')
    return response.data
  },

  // 获取热门操作统计
  getPopularActions: async (days: number = 7): Promise<{
    success: boolean;
    popular_actions?: Array<{
      action_type: string;
      count: number;
    }>;
    time_range_days?: number;
    error?: string;
  }> => {
    const params = new URLSearchParams()
    params.append('days', days.toString())

    const response = await api.get(`/analytics/popular-actions?${params}`)
    return response.data
  },

  // 获取每日统计数据
  getDailyStats: async (): Promise<{
    success: boolean;
    daily_stats?: Array<{
      date: string;
      total_users: number;
      active_users: number;
      new_registrations: number;
      total_generations: number;
      successful_generations: number;
      avg_generation_time: number;
      total_credits_consumed: number;
      peak_concurrent_users: number;
      error_rate: number;
      created_at: string;
    }>;
    error?: string;
  }> => {
    const response = await api.get('/analytics/daily-stats')
    return response.data
  },

  // 获取系统综合洞察
  getSystemInsights: async (): Promise<{
    success: boolean;
    system_insights?: {
      performance: {
        avg_generation_time_24h: number;
        avg_generation_time_7d: number;
        error_rate_24h: number;
        peak_load_24h: number;
        active_sessions: number;
      };
      user_stats: {
        total: number;
        favorites: number;
        recent_week: number;
        categories: Array<{
          category: string;
          count: number;
        }>;
      };
      insights: Array<{
        type: 'warning' | 'info' | 'suggestion';
        message: string;
        priority: 'high' | 'medium' | 'low';
      }>;
      overall_health: 'good' | 'warning';
    };
    error?: string;
  }> => {
    const response = await api.get('/analytics/system-insights')
    return response.data
  }
}

// 管理员API
export const adminApi = {
  // 为用户添加次数
  addCredits: async (userEmail: string, credits: number): Promise<{
    success: boolean;
    message?: string;
    data?: {
      user_email: string;
      user_id: number;
      credits_added: number;
      old_credits: number;
      new_credits: number;
    };
    error?: string;
  }> => {
    const response = await api.post('/admin/add-credits', {
      user_email: userEmail,
      credits: credits
    })
    return response.data
  },

  // 搜索用户
  searchUsers: async (query: string): Promise<{
    success: boolean;
    users?: Array<{
      id: number;
      email: string;
      credits: number;
      is_active: boolean;
      created_at: string;
      last_login_at: string | null;
    }>;
    count?: number;
    error?: string;
  }> => {
    const response = await api.get(`/admin/users/search?q=${encodeURIComponent(query)}`)
    return response.data
  },

  // 获取用户详细信息
  getUserDetails: async (userId: number): Promise<{
    success: boolean;
    user?: {
      id: number;
      email: string;
      credits: number;
      is_active: boolean;
      created_at: string;
      last_login_at: string | null;
    };
    stats?: {
      total: number;
      recent_week: number;
      favorites: number;
      categories: Array<{
        category: string;
        count: number;
      }>;
    };
    error?: string;
  }> => {
    const response = await api.get(`/admin/users/${userId}`)
    return response.data
  },

  // 获取系统配置
  getSettings: async (): Promise<{
    success: boolean;
    settings?: Array<{
      id: number;
      key: string;
      value: string;
      description: string;
      is_encrypted: number;
      is_masked: boolean;
      updated_by: number | null;
      updated_at: string;
    }>;
    error?: string;
  }> => {
    const response = await api.get('/admin/settings')
    return response.data
  },

  // 更新系统配置
  updateSettings: async (data: {
    settings: Array<{
      key: string;
      value: string;
    }>;
  }): Promise<{
    success: boolean;
    message?: string;
    updated_count?: number;
    failed_items?: Array<{
      key: string;
      reason: string;
    }>;
    error?: string;
  }> => {
    const response = await api.put('/admin/settings', data)
    return response.data
  },

  // 测试API连接
  testApiConnection: async (testData?: {
    base_url?: string;
    api_key?: string;
  }): Promise<{
    success: boolean;
    message?: string;
    status_code?: number;
    error_detail?: string;
    error?: string;
  }> => {
    const response = await api.post('/admin/test-api-connection', testData || {})
    return {
      success: response.data.status === 'success',
      message: response.data.message,
      status_code: response.data.data?.status_code,
      error_detail: response.data.data?.error_detail,
      error: response.data.message
    }
  },

  // 获取所有系统配置（包括隐藏的）
  getAllSettings: async (): Promise<{
    success: boolean;
    settings?: Array<{
      key: string;
      value: string;
      description: string;
      is_encrypted: number;
      is_active: number;
      updated_at: string;
      updated_by: number | null;
    }>;
    count?: number;
    active_key?: string;
    error?: string;
  }> => {
    const response = await api.get('/admin/settings/all')
    return response.data
  },

  // 创建新配置
  createSetting: async (
    key: string,
    value: string,
    description: string,
    is_encrypted: boolean
  ): Promise<{
    success: boolean;
    message?: string;
    error?: string;
  }> => {
    const response = await api.post('/admin/settings', {
      key,
      value,
      description,
      is_encrypted
    })
    return response.data
  },

  // 更新单个配置
  updateSingleSetting: async (key: string, value: string): Promise<{
    success: boolean;
    message?: string;
    error?: string;
  }> => {
    const response = await api.put(`/admin/settings/${key}`, { value })
    return response.data
  },

  // 切换配置启用/禁用状态
  toggleSetting: async (key: string): Promise<{
    success: boolean;
    message?: string;
    is_active?: boolean;
    error?: string;
  }> => {
    const response = await api.put(`/admin/settings/${key}/toggle`)
    return response.data
  },

  // 删除单个配置
  deleteSetting: async (key: string): Promise<{
    success: boolean;
    message?: string;
    error?: string;
  }> => {
    const response = await api.delete(`/admin/settings/${key}`)
    return response.data
  },

  // 配置组管理API
  // 获取所有配置组
  getAllConfigGroups: async (): Promise<{
    success: boolean;
    groups?: Array<{
      id: number;
      name: string;
      description: string;
      is_active: boolean;
      settings: {
        openai_hk_base_url?: string;
        openai_hk_api_key?: string;
      };
      created_at: string;
      updated_at: string;
    }>;
    count?: number;
    error?: string;
  }> => {
    const response = await api.get('/admin/config-groups')
    // 转换后端响应格式为前端期望格式
    return {
      success: response.data.status === 'success',
      groups: response.data.data,
      count: response.data.count,
      error: response.data.message
    }
  },

  // 创建配置组
  createConfigGroup: async (
    name: string,
    description: string,
    base_url: string,
    api_key: string
  ): Promise<{
    success: boolean;
    message?: string;
    group_id?: number;
    error?: string;
  }> => {
    const response = await api.post('/admin/config-groups', {
      name,
      description,
      openai_hk_base_url: base_url,
      openai_hk_api_key: api_key
    })
    // 转换后端响应格式
    return {
      success: response.data.status === 'success',
      message: response.data.message,
      group_id: response.data.data?.id,
      error: response.data.message
    }
  },

  // 更新配置组
  updateConfigGroup: async (
    groupId: number,
    data: {
      base_url?: string;
      api_key?: string;
      description?: string;
    }
  ): Promise<{
    success: boolean;
    message?: string;
    error?: string;
  }> => {
    // 转换前端字段名到后端期望的格式
    const backendData: any = {
      description: data.description
    }
    if (data.base_url) {
      backendData.openai_hk_base_url = data.base_url
    }
    if (data.api_key) {
      backendData.openai_hk_api_key = data.api_key
    }

    const response = await api.put(`/admin/config-groups/${groupId}`, backendData)
    return {
      success: response.data.status === 'success',
      message: response.data.message,
      error: response.data.message
    }
  },

  // 切换配置组启用状态
  toggleConfigGroup: async (groupId: number): Promise<{
    success: boolean;
    message?: string;
    is_active?: boolean;
    error?: string;
  }> => {
    const response = await api.post(`/admin/config-groups/${groupId}/toggle`)
    return {
      success: response.data.status === 'success',
      message: response.data.message,
      is_active: response.data.data?.is_active,
      error: response.data.message
    }
  },

  // 删除配置组
  deleteConfigGroup: async (groupId: number): Promise<{
    success: boolean;
    message?: string;
    error?: string;
  }> => {
    const response = await api.delete(`/admin/config-groups/${groupId}`)
    return {
      success: response.data.status === 'success',
      message: response.data.message,
      error: response.data.message
    }
  },

  // 删除用户
  deleteUser: async (userId: number, reason?: string): Promise<{
    success: boolean;
    message?: string;
    deleted_user?: {
      id: number;
      email: string;
      deleted_at: string;
    };
    impact?: {
      creations_orphaned: number;
      sessions_deleted: number;
      behaviors_deleted: number;
      preferences_deleted: number;
      performance_metrics_deleted: number;
    };
    error?: string;
  }> => {
    const url = reason
      ? `/admin/users/${userId}?reason=${encodeURIComponent(reason)}`
      : `/admin/users/${userId}`
    const response = await api.delete(url)
    return response.data
  },

  // 获取用户的生成作品
  getUserCreations: async (userId: number): Promise<{
    success: boolean;
    creations?: Array<{
      id: number;
      prompt: string;
      image_url: string;
      model_used: string;
      size: string;
      created_at: string;
    }>;
    error?: string;
  }> => {
    const response = await api.get(`/gallery?user_id=${userId}`)
    // 包装成统一格式
    if (response.data.success) {
      return {
        success: true,
        creations: response.data.creations || []
      }
    } else {
      return {
        success: false,
        error: response.data.error || '获取用户作品失败'
      }
    }
  }
}

export default api