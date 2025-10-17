/**
 * 性能监控工具
 * 监控Core Web Vitals和自定义性能指标
 */

interface PerformanceMetric {
  name: string
  value: number
  timestamp: number
  url?: string
  userAgent?: string
}

class PerformanceMonitor {
  private metrics = new Map<string, number>()
  private batchQueue: PerformanceMetric[] = []
  private batchSize = 10
  private batchTimeout = 5000 // 5秒
  private batchTimer: number | null = null

  constructor() {
    this.initCoreWebVitals()
  }

  /**
   * 开始性能测量
   */
  startMeasure(name: string) {
    this.metrics.set(name, performance.now())
  }

  /**
   * 结束性能测量
   */
  endMeasure(name: string) {
    const start = this.metrics.get(name)
    if (!start) {
      console.warn(`No start time found for metric: ${name}`)
      return
    }

    const duration = performance.now() - start
    this.metrics.delete(name)

    // 记录性能指标
    this.recordMetric(name, duration)

    // 超过阈值警告
    const thresholds: Record<string, number> = {
      'api-request': 1000,      // API请求 < 1秒
      'page-load': 3000,        // 页面加载 < 3秒
      'image-generation': 30000, // 图像生成 < 30秒
      'component-render': 100   // 组件渲染 < 100ms
    }

    const threshold = thresholds[name] || 1000
    if (duration > threshold) {
      console.warn(`⚠️ Performance warning: ${name} took ${duration.toFixed(2)}ms (threshold: ${threshold}ms)`)
    }

    return duration
  }

  /**
   * 记录性能指标
   */
  private recordMetric(name: string, value: number) {
    const metric: PerformanceMetric = {
      name,
      value,
      timestamp: Date.now(),
      url: window.location.pathname,
      userAgent: navigator.userAgent
    }

    this.batchQueue.push(metric)

    // 检查是否需要发送批次
    if (this.batchQueue.length >= this.batchSize) {
      this.flushBatch()
    } else if (!this.batchTimer) {
      // 设置定时器批量发送
      this.batchTimer = window.setTimeout(() => {
        this.flushBatch()
      }, this.batchTimeout)
    }
  }

  /**
   * 批量发送性能指标
   */
  private flushBatch() {
    if (this.batchQueue.length === 0) return

    const batch = [...this.batchQueue]
    this.batchQueue = []

    if (this.batchTimer) {
      clearTimeout(this.batchTimer)
      this.batchTimer = null
    }

    // 使用 sendBeacon 发送数据（不阻塞页面）
    if (navigator.sendBeacon) {
      const blob = new Blob([JSON.stringify(batch)], { type: 'application/json' })
      navigator.sendBeacon('/api/metrics', blob)
    } else {
      // 降级方案：使用fetch，但不等待响应
      fetch('/api/metrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(batch),
        keepalive: true
      }).catch(err => console.error('Failed to send metrics:', err))
    }
  }

  /**
   * 初始化Core Web Vitals监控
   */
  private initCoreWebVitals() {
    // LCP - Largest Contentful Paint (最大内容绘制)
    this.observeLCP()

    // FID - First Input Delay (首次输入延迟)
    this.observeFID()

    // CLS - Cumulative Layout Shift (累积布局偏移)
    this.observeCLS()

    // FCP - First Contentful Paint (首次内容绘制)
    this.observeFCP()

    // TTFB - Time to First Byte (首字节时间)
    this.observeTTFB()
  }

  /**
   * 监控LCP - Largest Contentful Paint
   * 目标: < 2.5s
   */
  private observeLCP() {
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          const lcp = entry as PerformanceEntry
          this.recordMetric('web-vitals-lcp', lcp.startTime)
          
          if (lcp.startTime > 2500) {
            console.warn(`⚠️ LCP is ${lcp.startTime.toFixed(0)}ms (should be < 2500ms)`)
          }
        }
      })
      observer.observe({ entryTypes: ['largest-contentful-paint'] })
    } catch (error) {
      console.error('LCP observation failed:', error)
    }
  }

  /**
   * 监控FID - First Input Delay
   * 目标: < 100ms
   */
  private observeFID() {
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          const fidEntry = entry as PerformanceEventTiming
          const fid = fidEntry.processingStart - fidEntry.startTime
          this.recordMetric('web-vitals-fid', fid)
          
          if (fid > 100) {
            console.warn(`⚠️ FID is ${fid.toFixed(0)}ms (should be < 100ms)`)
          }
        }
      })
      observer.observe({ entryTypes: ['first-input'] })
    } catch (error) {
      console.error('FID observation failed:', error)
    }
  }

  /**
   * 监控CLS - Cumulative Layout Shift
   * 目标: < 0.1
   */
  private observeCLS() {
    try {
      let clsValue = 0
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          const layoutShift = entry as LayoutShift
          if (!layoutShift.hadRecentInput) {
            clsValue += layoutShift.value
          }
        }
        
        this.recordMetric('web-vitals-cls', clsValue)
        
        if (clsValue > 0.1) {
          console.warn(`⚠️ CLS is ${clsValue.toFixed(3)} (should be < 0.1)`)
        }
      })
      observer.observe({ entryTypes: ['layout-shift'] })
    } catch (error) {
      console.error('CLS observation failed:', error)
    }
  }

  /**
   * 监控FCP - First Contentful Paint
   * 目标: < 1.8s
   */
  private observeFCP() {
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          const fcp = entry as PerformancePaintTiming
          this.recordMetric('web-vitals-fcp', fcp.startTime)
          
          if (fcp.startTime > 1800) {
            console.warn(`⚠️ FCP is ${fcp.startTime.toFixed(0)}ms (should be < 1800ms)`)
          }
        }
      })
      observer.observe({ entryTypes: ['paint'] })
    } catch (error) {
      console.error('FCP observation failed:', error)
    }
  }

  /**
   * 监控TTFB - Time to First Byte
   * 目标: < 600ms
   */
  private observeTTFB() {
    try {
      window.addEventListener('load', () => {
        const navTiming = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
        if (navTiming) {
          const ttfb = navTiming.responseStart - navTiming.requestStart
          this.recordMetric('web-vitals-ttfb', ttfb)
          
          if (ttfb > 600) {
            console.warn(`⚠️ TTFB is ${ttfb.toFixed(0)}ms (should be < 600ms)`)
          }
        }
      })
    } catch (error) {
      console.error('TTFB observation failed:', error)
    }
  }

  /**
   * 记录长任务（Long Task）
   * 任务超过50ms被认为是长任务
   */
  observeLongTasks() {
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          const longTask = entry as PerformanceEntry
          console.warn(`⚠️ Long task detected: ${longTask.duration.toFixed(0)}ms`)
          this.recordMetric('long-task', longTask.duration)
        }
      })
      observer.observe({ entryTypes: ['longtask'] })
    } catch (error) {
      console.error('Long task observation not supported:', error)
    }
  }

  /**
   * 记录自定义用户时间
   */
  mark(name: string) {
    try {
      performance.mark(name)
    } catch (error) {
      console.error(`Failed to mark ${name}:`, error)
    }
  }

  /**
   * 测量两个标记之间的时间
   */
  measure(name: string, startMark: string, endMark: string) {
    try {
      performance.measure(name, startMark, endMark)
      const measures = performance.getEntriesByName(name, 'measure')
      if (measures.length > 0) {
        const duration = measures[measures.length - 1].duration
        this.recordMetric(name, duration)
        return duration
      }
    } catch (error) {
      console.error(`Failed to measure ${name}:`, error)
    }
    return null
  }

  /**
   * 获取页面性能摘要
   */
  getPerformanceSummary() {
    const navTiming = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
    
    if (!navTiming) {
      console.warn('Navigation timing not available')
      return null
    }

    return {
      dns: navTiming.domainLookupEnd - navTiming.domainLookupStart,
      tcp: navTiming.connectEnd - navTiming.connectStart,
      ttfb: navTiming.responseStart - navTiming.requestStart,
      download: navTiming.responseEnd - navTiming.responseStart,
      domParse: navTiming.domInteractive - navTiming.responseEnd,
      domContentLoaded: navTiming.domContentLoadedEventEnd - navTiming.domContentLoadedEventStart,
      loadComplete: navTiming.loadEventEnd - navTiming.loadEventStart,
      total: navTiming.loadEventEnd - navTiming.fetchStart
    }
  }

  /**
   * 清理所有性能条目
   */
  clearPerformance() {
    if (performance.clearMarks) {
      performance.clearMarks()
    }
    if (performance.clearMeasures) {
      performance.clearMeasures()
    }
  }
}

// 导出单例
export const perfMonitor = new PerformanceMonitor()

// 导出类型
export type { PerformanceMetric }

// 全局错误处理
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error)
  perfMonitor.recordMetric('error', 1)
})

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason)
  perfMonitor.recordMetric('promise-rejection', 1)
})

// 页面卸载时发送剩余指标
window.addEventListener('beforeunload', () => {
  perfMonitor['flushBatch']()
})

