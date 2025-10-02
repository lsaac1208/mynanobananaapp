/**
 * 认证状态管理
 */
import { defineStore } from 'pinia'
import type { User, AuthResponse, UserLoginRequest, UserCreateRequest, Role } from '@shared/index'
import { authApi } from '../services/api'

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  loading: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: localStorage.getItem('access_token'),
    refreshToken: localStorage.getItem('refresh_token'),
    isAuthenticated: false,
    loading: false
  }),

  getters: {
    isLoggedIn: (state) => state.isAuthenticated && !!state.token,
    currentUser: (state) => state.user,
    userCredits: (state) => state.user?.credits || 0,

    // 角色相关 getters
    userRoles: (state): Role[] => state.user?.roles || [],

    // 检查用户是否拥有指定角色
    hasRole: (state) => (roleName: string): boolean => {
      return state.user?.roles?.some(role => role.name === roleName) || false
    },

    // 检查用户是否为管理员
    isAdmin: (state): boolean => {
      return state.user?.roles?.some(role => role.name === 'admin') || false
    },

    // 获取用户角色名称列表
    roleNames: (state): string[] => {
      return state.user?.roles?.map(role => role.name) || []
    }
  },

  actions: {
    // 设置认证信息
    setAuth(authData: AuthResponse) {
      this.user = authData.user
      this.token = authData.access_token
      this.refreshToken = authData.refresh_token
      this.isAuthenticated = true

      // 保存到localStorage
      localStorage.setItem('access_token', authData.access_token)
      localStorage.setItem('refresh_token', authData.refresh_token)
    },

    // 清除认证信息
    clearAuth() {
      this.user = null
      this.token = null
      this.refreshToken = null
      this.isAuthenticated = false

      // 清除localStorage
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    },

    // 用户注册
    async register(userData: UserCreateRequest) {
      this.loading = true
      try {
        const response = await authApi.register(userData)
        this.setAuth(response)
        return { success: true, message: '注册成功' }
      } catch (error: any) {
        return {
          success: false,
          message: error.response?.data?.error || '注册失败，请稍后重试'
        }
      } finally {
        this.loading = false
      }
    },

    // 用户登录
    async login(credentials: UserLoginRequest) {
      this.loading = true
      try {
        const response = await authApi.login(credentials)
        this.setAuth(response)
        return { success: true, message: '登录成功' }
      } catch (error: any) {
        return {
          success: false,
          message: error.response?.data?.error || '登录失败，请稍后重试'
        }
      } finally {
        this.loading = false
      }
    },

    // 用户登出
    async logout() {
      try {
        if (this.token) {
          await authApi.logout()
        }
      } catch (error) {
        console.error('登出请求失败:', error)
      } finally {
        this.clearAuth()
      }
    },

    // 检查登录状态
    async checkAuth() {
      if (!this.token) {
        return false
      }

      try {
        const response = await authApi.checkToken()
        this.user = response.user
        this.isAuthenticated = true
        return true
      } catch (error) {
        this.clearAuth()
        return false
      }
    },

    // 刷新令牌
    async refreshAccessToken() {
      if (!this.refreshToken) {
        return false
      }

      try {
        const response = await authApi.refreshToken()
        this.token = response.access_token
        localStorage.setItem('access_token', response.access_token)
        return true
      } catch (error) {
        this.clearAuth()
        return false
      }
    },

    // 获取用户信息
    async getUserInfo() {
      if (!this.token) {
        return false
      }

      try {
        const response = await authApi.checkToken()
        this.user = response.user
        this.isAuthenticated = true
        return true
      } catch (error) {
        console.error('获取用户信息失败:', error)
        return false
      }
    },

    // 更新用户次数
    updateUserCredits(newCredits: number) {
      if (this.user) {
        this.user.credits = newCredits
      }
    },

    // 初始化认证状态
    async initAuth() {
      if (this.token) {
        await this.checkAuth()
      }
    }
  }
})