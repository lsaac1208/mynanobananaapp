/**
 * 主题管理Composable
 * 支持亮色/暗色模式切换，自动检测系统偏好
 */

import { ref, watch, onMounted } from 'vue'

export type Theme = 'light' | 'dark'

const THEME_STORAGE_KEY = 'app-theme'

// 全局主题状态（在所有组件间共享）
const theme = ref<Theme>('light')

export function useTheme() {
  /**
   * 切换主题
   */
  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
  }

  /**
   * 设置特定主题
   */
  const setTheme = (newTheme: Theme) => {
    theme.value = newTheme
  }

  /**
   * 初始化主题
   * 优先级: localStorage > 系统偏好 > 默认亮色
   */
  const initTheme = () => {
    // 1. 检查localStorage中的保存值
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) as Theme | null
    
    if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
      theme.value = savedTheme
    } else {
      // 2. 检测系统偏好
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      theme.value = prefersDark ? 'dark' : 'light'
    }
    
    // 应用主题到DOM
    applyTheme(theme.value)
    
    // 监听系统主题变化
    watchSystemTheme()
  }

  /**
   * 应用主题到DOM
   */
  const applyTheme = (newTheme: Theme) => {
    document.documentElement.setAttribute('data-theme', newTheme)
    
    // 同时更新body class（用于某些第三方组件）
    document.body.classList.remove('theme-light', 'theme-dark')
    document.body.classList.add(`theme-${newTheme}`)
    
    // 更新meta theme-color（移动端地址栏颜色）
    updateMetaThemeColor(newTheme)
  }

  /**
   * 更新移动端地址栏颜色
   */
  const updateMetaThemeColor = (newTheme: Theme) => {
    let metaThemeColor = document.querySelector('meta[name="theme-color"]')
    
    if (!metaThemeColor) {
      metaThemeColor = document.createElement('meta')
      metaThemeColor.setAttribute('name', 'theme-color')
      document.head.appendChild(metaThemeColor)
    }
    
    // 根据主题设置颜色
    const color = newTheme === 'dark' ? '#1a1a1d' : '#ffffff'
    metaThemeColor.setAttribute('content', color)
  }

  /**
   * 监听系统主题偏好变化
   */
  const watchSystemTheme = () => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    
    // 现代浏览器支持addEventListener
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', (e) => {
        // 只在没有手动设置主题时才跟随系统
        const savedTheme = localStorage.getItem(THEME_STORAGE_KEY)
        if (!savedTheme) {
          theme.value = e.matches ? 'dark' : 'light'
        }
      })
    } else {
      // 旧版浏览器使用addListener
      mediaQuery.addListener((e) => {
        const savedTheme = localStorage.getItem(THEME_STORAGE_KEY)
        if (!savedTheme) {
          theme.value = e.matches ? 'dark' : 'light'
        }
      })
    }
  }

  /**
   * 获取当前是否为暗色模式
   */
  const isDark = () => theme.value === 'dark'

  /**
   * 获取当前是否为亮色模式
   */
  const isLight = () => theme.value === 'light'

  // 监听theme变化，自动保存和应用
  watch(theme, (newTheme) => {
    // 保存到localStorage
    localStorage.setItem(THEME_STORAGE_KEY, newTheme)
    
    // 应用到DOM
    applyTheme(newTheme)
    
    // 触发自定义事件（其他组件可以监听）
    window.dispatchEvent(new CustomEvent('theme-changed', { detail: { theme: newTheme } }))
  })

  return {
    theme, // 当前主题（响应式）
    toggleTheme, // 切换主题
    setTheme, // 设置特定主题
    initTheme, // 初始化主题
    isDark, // 是否暗色模式
    isLight // 是否亮色模式
  }
}

/**
 * 主题切换动画
 * 在主题切换时添加过渡效果，避免突兀感
 */
export function useThemeTransition() {
  const enableTransition = () => {
    document.documentElement.classList.add('theme-transitioning')
    
    // 300ms后移除过渡类
    setTimeout(() => {
      document.documentElement.classList.remove('theme-transitioning')
    }, 300)
  }

  return {
    enableTransition
  }
}

