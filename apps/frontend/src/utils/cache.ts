/**
 * 移动端性能优化 - HTTP缓存工具
 * 实现简单的内存缓存策略，减少重复API请求
 */

interface CacheItem<T> {
  data: T
  timestamp: number
  expiresIn: number
}

class CacheManager {
  private cache: Map<string, CacheItem<any>>
  private maxSize: number

  constructor(maxSize = 50) {
    this.cache = new Map()
    this.maxSize = maxSize
  }

  /**
   * 设置缓存
   * @param key 缓存键
   * @param data 缓存数据
   * @param expiresIn 过期时间（毫秒），默认5分钟
   */
  set<T>(key: string, data: T, expiresIn = 5 * 60 * 1000): void {
    // 如果缓存已满，删除最早的项
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value
      this.cache.delete(firstKey)
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      expiresIn
    })
  }

  /**
   * 获取缓存
   * @param key 缓存键
   * @returns 缓存数据，如果不存在或已过期返回null
   */
  get<T>(key: string): T | null {
    const item = this.cache.get(key)

    if (!item) {
      return null
    }

    const now = Date.now()
    const isExpired = now - item.timestamp > item.expiresIn

    if (isExpired) {
      this.cache.delete(key)
      return null
    }

    return item.data as T
  }

  /**
   * 检查缓存是否存在且有效
   * @param key 缓存键
   */
  has(key: string): boolean {
    return this.get(key) !== null
  }

  /**
   * 删除指定缓存
   * @param key 缓存键
   */
  delete(key: string): void {
    this.cache.delete(key)
  }

  /**
   * 清空所有缓存
   */
  clear(): void {
    this.cache.clear()
  }

  /**
   * 删除匹配模式的缓存
   * @param pattern 匹配模式（正则表达式或字符串前缀）
   */
  deletePattern(pattern: string | RegExp): void {
    const regex = typeof pattern === 'string'
      ? new RegExp(`^${pattern}`)
      : pattern

    const keysToDelete: string[] = []

    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        keysToDelete.push(key)
      }
    }

    keysToDelete.forEach(key => this.cache.delete(key))
  }

  /**
   * 获取缓存统计信息
   */
  getStats() {
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      keys: Array.from(this.cache.keys())
    }
  }
}

// 创建全局缓存实例
export const apiCache = new CacheManager(50)

/**
 * 生成缓存键的辅助函数
 * @param endpoint API端点
 * @param params 请求参数
 */
export function generateCacheKey(endpoint: string, params?: Record<string, any>): string {
  if (!params || Object.keys(params).length === 0) {
    return endpoint
  }

  const sortedParams = Object.keys(params)
    .sort()
    .map(key => `${key}=${JSON.stringify(params[key])}`)
    .join('&')

  return `${endpoint}?${sortedParams}`
}

/**
 * 装饰器模式：为API请求添加缓存功能
 * @param fetchFn 原始的fetch函数
 * @param cacheKey 缓存键
 * @param expiresIn 过期时间（毫秒）
 */
export async function withCache<T>(
  fetchFn: () => Promise<T>,
  cacheKey: string,
  expiresIn = 5 * 60 * 1000
): Promise<T> {
  // 尝试从缓存获取
  const cachedData = apiCache.get<T>(cacheKey)

  if (cachedData !== null) {
    console.log(`[Cache Hit] ${cacheKey}`)
    return cachedData
  }

  // 缓存未命中，执行实际请求
  console.log(`[Cache Miss] ${cacheKey}`)
  const data = await fetchFn()

  // 存入缓存
  apiCache.set(cacheKey, data, expiresIn)

  return data
}

export default apiCache