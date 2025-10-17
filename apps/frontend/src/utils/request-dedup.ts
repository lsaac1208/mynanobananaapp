/**
 * 请求去重和并发控制
 * 防止快速重复点击导致的重复请求
 */

export class RequestDeduplicator {
  private pendingRequests: Map<string, Promise<any>> = new Map()

  /**
   * 去重执行请求
   * 如果已有相同key的请求正在进行，则返回该请求的Promise
   * 
   * @param key 请求的唯一标识
   * @param requestFn 实际的请求函数
   * @returns Promise<T>
   */
  async deduplicate<T>(
    key: string,
    requestFn: () => Promise<T>
  ): Promise<T> {
    // 如果已有相同请求正在进行，直接返回该请求
    if (this.pendingRequests.has(key)) {
      return this.pendingRequests.get(key)!
    }

    // 创建新请求
    const promise = requestFn()
    this.pendingRequests.set(key, promise)

    try {
      const result = await promise
      return result
    } finally {
      // 请求完成后，无论成功失败都清理
      this.pendingRequests.delete(key)
    }
  }

  /**
   * 检查指定key的请求是否正在进行
   */
  isPending(key: string): boolean {
    return this.pendingRequests.has(key)
  }

  /**
   * 取消指定key的请求
   * 注意：这只是从映射中移除，并不会真正取消HTTP请求
   */
  cancel(key: string): void {
    this.pendingRequests.delete(key)
  }

  /**
   * 清空所有待处理的请求
   */
  clearAll(): void {
    this.pendingRequests.clear()
  }

  /**
   * 获取当前待处理的请求数量
   */
  get pendingCount(): number {
    return this.pendingRequests.size
  }
}

// 导出单例实例
export const requestDeduplicator = new RequestDeduplicator()

/**
 * 用于API调用的装饰器风格辅助函数
 * 
 * @example
 * ```typescript
 * const result = await withDedup('user-login', () => api.post('/login', data))
 * ```
 */
export async function withDedup<T>(
  key: string,
  requestFn: () => Promise<T>
): Promise<T> {
  return requestDeduplicator.deduplicate(key, requestFn)
}

/**
 * 基于参数生成去重key的辅助函数
 * 
 * @example
 * ```typescript
 * const key = generateDedupKey('text-to-image', { prompt: 'cat', model: 'dall-e-3' })
 * // 返回: 'text-to-image:{"prompt":"cat","model":"dall-e-3"}'
 * ```
 */
export function generateDedupKey(prefix: string, params?: Record<string, any>): string {
  if (!params) {
    return prefix
  }
  
  // 对参数进行排序，确保相同参数生成相同的key
  const sortedParams = Object.keys(params)
    .sort()
    .reduce((acc, key) => {
      acc[key] = params[key]
      return acc
    }, {} as Record<string, any>)
  
  return `${prefix}:${JSON.stringify(sortedParams)}`
}

/**
 * 防抖去重组合
 * 结合了防抖和去重功能，适用于搜索等场景
 */
export class DebouncedDeduplicator {
  private deduplicator: RequestDeduplicator
  private timeoutId: number | null = null

  constructor(private delay: number = 300) {
    this.deduplicator = new RequestDeduplicator()
  }

  /**
   * 防抖去重执行
   */
  async execute<T>(
    key: string,
    requestFn: () => Promise<T>
  ): Promise<T> {
    return new Promise((resolve, reject) => {
      // 清除之前的定时器
      if (this.timeoutId !== null) {
        clearTimeout(this.timeoutId)
      }

      // 设置新的定时器
      this.timeoutId = window.setTimeout(async () => {
        try {
          const result = await this.deduplicator.deduplicate(key, requestFn)
          resolve(result)
        } catch (error) {
          reject(error)
        }
      }, this.delay)
    })
  }

  /**
   * 立即执行（跳过防抖）
   */
  async immediate<T>(
    key: string,
    requestFn: () => Promise<T>
  ): Promise<T> {
    if (this.timeoutId !== null) {
      clearTimeout(this.timeoutId)
      this.timeoutId = null
    }
    return this.deduplicator.deduplicate(key, requestFn)
  }
}

