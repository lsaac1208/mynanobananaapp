/**
 * UI状态管理
 */
import { defineStore } from 'pinia'

interface UIState {
  // 主题
  theme: 'light' | 'dark' | 'auto'

  // 侧边栏
  sidebarCollapsed: boolean

  // 加载状态
  globalLoading: boolean

  // 通知和消息
  notifications: Notification[]

  // 模态框状态
  modals: Record<string, boolean>

  // 当前页面
  currentPage: string

  // 移动端状态
  isMobile: boolean

  // 网络状态
  isOnline: boolean

  // 画廊视图模式
  galleryViewMode: 'grid' | 'list'

  // 图片预览
  imagePreview: {
    visible: boolean
    url: string
    title?: string
  }
}

interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
  persistent?: boolean
  createdAt: number
}

export const useUIStore = defineStore('ui', {
  state: (): UIState => ({
    theme: 'auto',
    sidebarCollapsed: false,
    globalLoading: false,
    notifications: [],
    modals: {},
    currentPage: '',
    isMobile: window.innerWidth < 768,
    isOnline: navigator.onLine,
    galleryViewMode: 'grid',
    imagePreview: {
      visible: false,
      url: '',
      title: undefined
    }
  }),

  getters: {
    // 获取当前主题
    currentTheme: (state) => {
      if (state.theme === 'auto') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      }
      return state.theme
    },

    // 是否为暗色主题
    isDarkTheme(): boolean {
      return this.currentTheme === 'dark'
    },

    // 获取未读通知数量
    unreadNotificationsCount: (state) => {
      return state.notifications.length
    },

    // 获取持久化通知
    persistentNotifications: (state) => {
      return state.notifications.filter(n => n.persistent)
    },

    // 获取临时通知
    temporaryNotifications: (state) => {
      return state.notifications.filter(n => !n.persistent)
    },

    // 是否有模态框打开
    hasOpenModal: (state) => {
      return Object.values(state.modals).some(isOpen => isOpen)
    }
  },

  actions: {
    // 设置主题
    setTheme(theme: 'light' | 'dark' | 'auto') {
      this.theme = theme
      localStorage.setItem('theme', theme)
      this.applyTheme()
    },

    // 应用主题
    applyTheme() {
      const theme = this.currentTheme
      const html = document.documentElement

      if (theme === 'dark') {
        html.classList.add('dark')
      } else {
        html.classList.remove('dark')
      }
    },

    // 切换主题
    toggleTheme() {
      const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark'
      this.setTheme(newTheme)
    },

    // 设置侧边栏状态
    setSidebarCollapsed(collapsed: boolean) {
      this.sidebarCollapsed = collapsed
      localStorage.setItem('sidebarCollapsed', String(collapsed))
    },

    // 切换侧边栏
    toggleSidebar() {
      this.setSidebarCollapsed(!this.sidebarCollapsed)
    },

    // 设置全局加载状态
    setGlobalLoading(loading: boolean) {
      this.globalLoading = loading
    },

    // 添加通知
    addNotification(notification: Omit<Notification, 'id' | 'createdAt'>) {
      const id = Date.now().toString() + Math.random().toString(36).substr(2, 9)
      const newNotification: Notification = {
        ...notification,
        id,
        createdAt: Date.now(),
        duration: notification.duration || 5000
      }

      this.notifications.push(newNotification)

      // 自动移除非持久化通知
      if (!notification.persistent && newNotification.duration && newNotification.duration > 0) {
        setTimeout(() => {
          this.removeNotification(id)
        }, newNotification.duration)
      }

      return id
    },

    // 移除通知
    removeNotification(id: string) {
      const index = this.notifications.findIndex(n => n.id === id)
      if (index > -1) {
        this.notifications.splice(index, 1)
      }
    },

    // 清除所有通知
    clearNotifications() {
      this.notifications = []
    },

    // 显示成功消息
    showSuccess(title: string, message?: string, duration?: number) {
      return this.addNotification({
        type: 'success',
        title,
        message,
        duration
      })
    },

    // 显示错误消息
    showError(title: string, message?: string, persistent = false) {
      return this.addNotification({
        type: 'error',
        title,
        message,
        persistent,
        duration: persistent ? 0 : 8000
      })
    },

    // 显示警告消息
    showWarning(title: string, message?: string, duration?: number) {
      return this.addNotification({
        type: 'warning',
        title,
        message,
        duration
      })
    },

    // 显示信息消息
    showInfo(title: string, message?: string, duration?: number) {
      return this.addNotification({
        type: 'info',
        title,
        message,
        duration
      })
    },

    // 打开模态框
    openModal(modalName: string) {
      this.modals[modalName] = true
    },

    // 关闭模态框
    closeModal(modalName: string) {
      this.modals[modalName] = false
    },

    // 切换模态框
    toggleModal(modalName: string) {
      this.modals[modalName] = !this.modals[modalName]
    },

    // 关闭所有模态框
    closeAllModals() {
      Object.keys(this.modals).forEach(key => {
        this.modals[key] = false
      })
    },

    // 设置当前页面
    setCurrentPage(page: string) {
      this.currentPage = page
    },

    // 设置移动端状态
    setMobile(isMobile: boolean) {
      this.isMobile = isMobile
    },

    // 设置网络状态
    setOnlineStatus(isOnline: boolean) {
      this.isOnline = isOnline

      if (!isOnline) {
        this.showWarning('网络连接丢失', '请检查您的网络连接', 0)
      } else {
        this.showSuccess('网络连接已恢复')
      }
    },

    // 设置画廊视图模式
    setGalleryViewMode(mode: 'grid' | 'list') {
      this.galleryViewMode = mode
      localStorage.setItem('galleryViewMode', mode)
    },

    // 切换画廊视图模式
    toggleGalleryViewMode() {
      const newMode = this.galleryViewMode === 'grid' ? 'list' : 'grid'
      this.setGalleryViewMode(newMode)
    },

    // 显示图片预览
    showImagePreview(url: string, title?: string) {
      this.imagePreview = {
        visible: true,
        url,
        title
      }
    },

    // 隐藏图片预览
    hideImagePreview() {
      this.imagePreview = {
        visible: false,
        url: '',
        title: undefined
      }
    },

    // 初始化UI状态
    initializeUI() {
      // 加载保存的主题
      const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'auto'
      if (savedTheme) {
        this.theme = savedTheme
      }
      this.applyTheme()

      // 加载保存的侧边栏状态
      const savedSidebarState = localStorage.getItem('sidebarCollapsed')
      if (savedSidebarState) {
        this.sidebarCollapsed = savedSidebarState === 'true'
      }

      // 加载保存的画廊视图模式
      const savedViewMode = localStorage.getItem('galleryViewMode') as 'grid' | 'list'
      if (savedViewMode) {
        this.galleryViewMode = savedViewMode
      }

      // 监听窗口大小变化
      const handleResize = () => {
        this.setMobile(window.innerWidth < 768)
      }
      window.addEventListener('resize', handleResize)

      // 监听网络状态变化
      const handleOnline = () => this.setOnlineStatus(true)
      const handleOffline = () => this.setOnlineStatus(false)
      window.addEventListener('online', handleOnline)
      window.addEventListener('offline', handleOffline)

      // 监听主题变化
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      const handleThemeChange = () => {
        if (this.theme === 'auto') {
          this.applyTheme()
        }
      }
      mediaQuery.addEventListener('change', handleThemeChange)

      // 返回清理函数
      return () => {
        window.removeEventListener('resize', handleResize)
        window.removeEventListener('online', handleOnline)
        window.removeEventListener('offline', handleOffline)
        mediaQuery.removeEventListener('change', handleThemeChange)
      }
    },

    // 重置UI状态
    reset() {
      this.theme = 'auto'
      this.sidebarCollapsed = false
      this.globalLoading = false
      this.notifications = []
      this.modals = {}
      this.currentPage = ''
      this.galleryViewMode = 'grid'
      this.imagePreview = {
        visible: false,
        url: '',
        title: undefined
      }
    }
  }
})