/**
 * 移动端性能监控工具
 * 实时监控页面性能指标，优化用户体验
 */

interface PerformanceMetric {
  name: string
  value: number
  rating: 'good' | 'needs-improvement' | 'poor'
}

interface PageLoadMetrics {
  // 核心Web指标
  FCP?: PerformanceMetric  // First Contentful Paint
  LCP?: PerformanceMetric  // Largest Contentful Paint
  FID?: PerformanceMetric  // First Input Delay
  CLS?: PerformanceMetric  // Cumulative Layout Shift
  TTFB?: PerformanceMetric // Time to First Byte

  // 自定义指标
  pageLoadTime?: number
  domContentLoaded?: number
  resourcesLoaded?: number
}

class PerformanceMonitor {
  private metrics: PageLoadMetrics = {}

  /**
   * 初始化性能监控
   */
  init(): void {
    if (typeof window === 'undefined' || !window.performance) {
      console.warn('Performance API不可用')
      return
    }

    // 监听页面加载完成
    if (document.readyState === 'complete') {
      this.collectMetrics()
    } else {
      window.addEventListener('load', () => {
        this.collectMetrics()
      })
    }

    // 使用 PerformanceObserver 监控 Web Vitals
    this.observeWebVitals()
  }

  /**
   * 收集页面加载性能指标
   */
  private collectMetrics(): void {
    const perfData = window.performance.timing
    const now = Date.now()

    // 页面加载时间
    this.metrics.pageLoadTime = perfData.loadEventEnd - perfData.navigationStart

    // DOM内容加载时间
    this.metrics.domContentLoaded = perfData.domContentLoadedEventEnd - perfData.navigationStart

    // 资源加载时间
    this.metrics.resourcesLoaded = perfData.loadEventEnd - perfData.domContentLoadedEventEnd

    // TTFB - 首字节时间
    const ttfb = perfData.responseStart - perfData.requestStart
    this.metrics.TTFB = {
      name: 'TTFB',
      value: ttfb,
      rating: this.rateTTFB(ttfb)
    }

    console.log('[性能监控] 页面加载指标:', this.metrics)
  }

  /**
   * 使用 PerformanceObserver 监控 Web Vitals
   */
  private observeWebVitals(): void {
    try {
      // 监控 LCP (Largest Contentful Paint)
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        const lastEntry = entries[entries.length - 1] as any

        this.metrics.LCP = {
          name: 'LCP',
          value: lastEntry.renderTime || lastEntry.loadTime,
          rating: this.rateLCP(lastEntry.renderTime || lastEntry.loadTime)
        }
      })
      lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true })

      // 监控 FID (First Input Delay)
      const fidObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries() as any[]
        entries.forEach((entry) => {
          this.metrics.FID = {
            name: 'FID',
            value: entry.processingStart - entry.startTime,
            rating: this.rateFID(entry.processingStart - entry.startTime)
          }
        })
      })
      fidObserver.observe({ type: 'first-input', buffered: true })

      // 监控 CLS (Cumulative Layout Shift)
      let clsValue = 0
      const clsObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries() as any[]
        entries.forEach((entry) => {
          if (!entry.hadRecentInput) {
            clsValue += entry.value
          }
        })

        this.metrics.CLS = {
          name: 'CLS',
          value: clsValue,
          rating: this.rateCLS(clsValue)
        }
      })
      clsObserver.observe({ type: 'layout-shift', buffered: true })
    } catch (error) {
      console.warn('[性能监控] PerformanceObserver不可用:', error)
    }
  }

  /**
   * 评估 LCP (Largest Contentful Paint)
   * Good: < 2.5s, Needs Improvement: 2.5-4s, Poor: > 4s
   */
  private rateLCP(value: number): 'good' | 'needs-improvement' | 'poor' {
    if (value < 2500) return 'good'
    if (value < 4000) return 'needs-improvement'
    return 'poor'
  }

  /**
   * 评估 FID (First Input Delay)
   * Good: < 100ms, Needs Improvement: 100-300ms, Poor: > 300ms
   */
  private rateFID(value: number): 'good' | 'needs-improvement' | 'poor' {
    if (value < 100) return 'good'
    if (value < 300) return 'needs-improvement'
    return 'poor'
  }

  /**
   * 评估 CLS (Cumulative Layout Shift)
   * Good: < 0.1, Needs Improvement: 0.1-0.25, Poor: > 0.25
   */
  private rateCLS(value: number): 'good' | 'needs-improvement' | 'poor' {
    if (value < 0.1) return 'good'
    if (value < 0.25) return 'needs-improvement'
    return 'poor'
  }

  /**
   * 评估 TTFB (Time to First Byte)
   * Good: < 800ms, Needs Improvement: 800-1800ms, Poor: > 1800ms
   */
  private rateTTFB(value: number): 'good' | 'needs-improvement' | 'poor' {
    if (value < 800) return 'good'
    if (value < 1800) return 'needs-improvement'
    return 'poor'
  }

  /**
   * 获取所有性能指标
   */
  getMetrics(): PageLoadMetrics {
    return this.metrics
  }

  /**
   * 打印性能报告
   */
  printReport(): void {
    console.group('📊 移动端性能报告')

    if (this.metrics.LCP) {
      console.log(`🎯 LCP (最大内容绘制): ${this.metrics.LCP.value.toFixed(0)}ms - ${this.metrics.LCP.rating}`)
    }

    if (this.metrics.FID) {
      console.log(`⚡ FID (首次输入延迟): ${this.metrics.FID.value.toFixed(0)}ms - ${this.metrics.FID.rating}`)
    }

    if (this.metrics.CLS) {
      console.log(`📐 CLS (累积布局偏移): ${this.metrics.CLS.value.toFixed(3)} - ${this.metrics.CLS.rating}`)
    }

    if (this.metrics.TTFB) {
      console.log(`🚀 TTFB (首字节时间): ${this.metrics.TTFB.value.toFixed(0)}ms - ${this.metrics.TTFB.rating}`)
    }

    if (this.metrics.pageLoadTime) {
      console.log(`⏱️ 页面加载时间: ${this.metrics.pageLoadTime.toFixed(0)}ms`)
    }

    console.groupEnd()
  }

  /**
   * 测量自定义操作的执行时间
   */
  measure(name: string, fn: () => void | Promise<void>): void {
    const start = performance.now()

    const result = fn()

    if (result instanceof Promise) {
      result.then(() => {
        const duration = performance.now() - start
        console.log(`⏱️ [${name}] 执行时间: ${duration.toFixed(2)}ms`)
      })
    } else {
      const duration = performance.now() - start
      console.log(`⏱️ [${name}] 执行时间: ${duration.toFixed(2)}ms`)
    }
  }
}

// 创建全局性能监控实例
export const performanceMonitor = new PerformanceMonitor()

/**
 * 在开发环境中自动初始化性能监控
 */
if (import.meta.env.DEV) {
  performanceMonitor.init()

  // 5秒后打印性能报告
  setTimeout(() => {
    performanceMonitor.printReport()
  }, 5000)
}

export default performanceMonitor