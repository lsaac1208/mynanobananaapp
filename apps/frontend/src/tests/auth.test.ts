/**
 * 前端认证功能测试
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../stores/auth'
import { authApi } from '../services/api'

// Mock API
vi.mock('../services/api', () => ({
  authApi: {
    register: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
    checkToken: vi.fn(),
    refreshToken: vi.fn()
  }
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
vi.stubGlobal('localStorage', localStorageMock)

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
  })

  describe('初始状态', () => {
    it('应该有正确的初始状态', () => {
      const authStore = useAuthStore()

      expect(authStore.user).toBeNull()
      expect(authStore.token).toBeNull()
      expect(authStore.refreshToken).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
      expect(authStore.loading).toBe(false)
      expect(authStore.isLoggedIn).toBe(false)
      expect(authStore.currentUser).toBeNull()
      expect(authStore.userCredits).toBe(0)
    })

    it('应该从localStorage恢复token', () => {
      localStorageMock.getItem
        .mockReturnValueOnce('access_token_value')
        .mockReturnValueOnce('refresh_token_value')

      const authStore = useAuthStore()

      expect(authStore.token).toBe('access_token_value')
      expect(authStore.refreshToken).toBe('refresh_token_value')
    })
  })

  describe('用户注册', () => {
    it('成功注册应该设置认证信息', async () => {
      const authStore = useAuthStore()
      const mockResponse = {
        message: '注册成功',
        access_token: 'new_access_token',
        refresh_token: 'new_refresh_token',
        user: {
          id: 1,
          email: 'test@example.com',
          credits: 3,
          is_active: true,
          last_login_at: null,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      }

      vi.mocked(authApi.register).mockResolvedValueOnce(mockResponse)

      const result = await authStore.register({
        email: 'test@example.com',
        password: 'Test123456'
      })

      expect(result.success).toBe(true)
      expect(result.message).toBe('注册成功')
      expect(authStore.user).toEqual(mockResponse.user)
      expect(authStore.token).toBe('new_access_token')
      expect(authStore.refreshToken).toBe('new_refresh_token')
      expect(authStore.isAuthenticated).toBe(true)
      expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'new_access_token')
      expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', 'new_refresh_token')
    })

    it('注册失败应该返回错误信息', async () => {
      const authStore = useAuthStore()
      const mockError = {
        response: {
          data: {
            error: '邮箱已被注册'
          }
        }
      }

      vi.mocked(authApi.register).mockRejectedValueOnce(mockError)

      const result = await authStore.register({
        email: 'test@example.com',
        password: 'Test123456'
      })

      expect(result.success).toBe(false)
      expect(result.message).toBe('邮箱已被注册')
      expect(authStore.isAuthenticated).toBe(false)
    })
  })

  describe('用户登录', () => {
    it('成功登录应该设置认证信息', async () => {
      const authStore = useAuthStore()
      const mockResponse = {
        message: '登录成功',
        access_token: 'access_token',
        refresh_token: 'refresh_token',
        user: {
          id: 1,
          email: 'test@example.com',
          credits: 5,
          is_active: true,
          last_login_at: '2024-01-01T12:00:00Z',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T12:00:00Z'
        }
      }

      vi.mocked(authApi.login).mockResolvedValueOnce(mockResponse)

      const result = await authStore.login({
        email: 'test@example.com',
        password: 'Test123456'
      })

      expect(result.success).toBe(true)
      expect(result.message).toBe('登录成功')
      expect(authStore.user).toEqual(mockResponse.user)
      expect(authStore.isAuthenticated).toBe(true)
      expect(authStore.isLoggedIn).toBe(true)
    })

    it('登录失败应该返回错误信息', async () => {
      const authStore = useAuthStore()
      const mockError = {
        response: {
          data: {
            error: '邮箱或密码错误'
          }
        }
      }

      vi.mocked(authApi.login).mockRejectedValueOnce(mockError)

      const result = await authStore.login({
        email: 'test@example.com',
        password: 'wrongpassword'
      })

      expect(result.success).toBe(false)
      expect(result.message).toBe('邮箱或密码错误')
    })
  })

  describe('用户登出', () => {
    it('应该清除认证信息', async () => {
      const authStore = useAuthStore()

      // 先设置认证状态
      authStore.setAuth({
        message: '登录成功',
        access_token: 'access_token',
        refresh_token: 'refresh_token',
        user: {
          id: 1,
          email: 'test@example.com',
          credits: 5,
          is_active: true,
          last_login_at: null,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      })

      vi.mocked(authApi.logout).mockResolvedValueOnce()

      await authStore.logout()

      expect(authStore.user).toBeNull()
      expect(authStore.token).toBeNull()
      expect(authStore.refreshToken).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token')
    })

    it('即使API调用失败也应该清除本地认证信息', async () => {
      const authStore = useAuthStore()

      // 先设置认证状态
      authStore.setAuth({
        message: '登录成功',
        access_token: 'access_token',
        refresh_token: 'refresh_token',
        user: {
          id: 1,
          email: 'test@example.com',
          credits: 5,
          is_active: true,
          last_login_at: null,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      })

      vi.mocked(authApi.logout).mockRejectedValueOnce(new Error('Network error'))

      await authStore.logout()

      expect(authStore.user).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
    })
  })

  describe('认证状态检查', () => {
    it('有效token应该通过验证', async () => {
      const authStore = useAuthStore()
      authStore.token = 'valid_token'

      const mockUser = {
        id: 1,
        email: 'test@example.com',
        credits: 5,
        is_active: true,
        last_login_at: null,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      }

      vi.mocked(authApi.checkToken).mockResolvedValueOnce({
        message: '令牌有效',
        user: mockUser
      })

      const result = await authStore.checkAuth()

      expect(result).toBe(true)
      expect(authStore.user).toEqual(mockUser)
      expect(authStore.isAuthenticated).toBe(true)
    })

    it('无效token应该清除认证信息', async () => {
      const authStore = useAuthStore()
      authStore.token = 'invalid_token'

      vi.mocked(authApi.checkToken).mockRejectedValueOnce(new Error('Invalid token'))

      const result = await authStore.checkAuth()

      expect(result).toBe(false)
      expect(authStore.user).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
    })

    it('没有token应该返回false', async () => {
      const authStore = useAuthStore()
      authStore.token = null

      const result = await authStore.checkAuth()

      expect(result).toBe(false)
      expect(authApi.checkToken).not.toHaveBeenCalled()
    })
  })

  describe('token刷新', () => {
    it('成功刷新应该更新access token', async () => {
      const authStore = useAuthStore()
      authStore.refreshToken = 'valid_refresh_token'

      vi.mocked(authApi.refreshToken).mockResolvedValueOnce({
        access_token: 'new_access_token'
      })

      const result = await authStore.refreshAccessToken()

      expect(result).toBe(true)
      expect(authStore.token).toBe('new_access_token')
      expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'new_access_token')
    })

    it('刷新失败应该清除认证信息', async () => {
      const authStore = useAuthStore()
      authStore.refreshToken = 'invalid_refresh_token'

      vi.mocked(authApi.refreshToken).mockRejectedValueOnce(new Error('Invalid refresh token'))

      const result = await authStore.refreshAccessToken()

      expect(result).toBe(false)
      expect(authStore.user).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
    })

    it('没有refresh token应该返回false', async () => {
      const authStore = useAuthStore()
      authStore.refreshToken = null

      const result = await authStore.refreshAccessToken()

      expect(result).toBe(false)
      expect(authApi.refreshToken).not.toHaveBeenCalled()
    })
  })

  describe('getters', () => {
    it('isLoggedIn应该正确计算', () => {
      const authStore = useAuthStore()

      // 未认证状态
      expect(authStore.isLoggedIn).toBe(false)

      // 有token但未认证
      authStore.token = 'some_token'
      expect(authStore.isLoggedIn).toBe(false)

      // 已认证但无token
      authStore.token = null
      authStore.isAuthenticated = true
      expect(authStore.isLoggedIn).toBe(false)

      // 已认证且有token
      authStore.token = 'some_token'
      authStore.isAuthenticated = true
      expect(authStore.isLoggedIn).toBe(true)
    })

    it('userCredits应该返回正确的次数', () => {
      const authStore = useAuthStore()

      // 无用户
      expect(authStore.userCredits).toBe(0)

      // 有用户
      authStore.user = {
        id: 1,
        email: 'test@example.com',
        credits: 10,
        is_active: true,
        last_login_at: null,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      }
      expect(authStore.userCredits).toBe(10)
    })
  })
})