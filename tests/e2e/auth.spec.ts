/**
 * E2E认证功能测试
 */
import { test, expect } from '@playwright/test'

// 测试数据
const testUser = {
  email: 'e2e-test@example.com',
  password: 'Test123456'
}

test.describe('用户认证流程', () => {
  test.beforeEach(async ({ page }) => {
    // 每个测试前访问首页
    await page.goto('/')
  })

  test('用户注册流程', async ({ page }) => {
    // 点击登录按钮
    await page.click('text=登录 / 注册')

    // 应该跳转到登录页面
    await expect(page).toHaveURL('/login')

    // 切换到注册标签
    await page.click('text=注册')

    // 填写注册表单
    await page.fill('input[type="email"]', testUser.email)
    await page.fill('input[type="password"]', testUser.password)
    await page.fill('input[placeholder*="确认密码"]', testUser.password)

    // 提交注册表单
    await page.click('text=注册账号')

    // 应该显示成功消息并跳转到主页
    await expect(page.locator('.el-message--success')).toBeVisible()
    await expect(page).toHaveURL('/')

    // 应该显示用户信息
    await expect(page.locator('text=' + testUser.email)).toBeVisible()
    await expect(page.locator('text=剩余次数: 3')).toBeVisible()
  })

  test('用户登录流程', async ({ page }) => {
    // 假设用户已经注册
    // 点击登录按钮
    await page.click('text=登录 / 注册')

    // 应该在登录标签页
    await expect(page.locator('.tab-button.active')).toHaveText('登录')

    // 填写登录表单
    await page.fill('input[type="email"]', testUser.email)
    await page.fill('input[type="password"]', testUser.password)

    // 提交登录表单
    await page.click('text=登录')

    // 应该显示成功消息并跳转到主页
    await expect(page.locator('.el-message--success')).toBeVisible()
    await expect(page).toHaveURL('/')

    // 应该显示用户信息
    await expect(page.locator('text=' + testUser.email)).toBeVisible()
  })

  test('用户登出流程', async ({ page }) => {
    // 假设用户已经登录
    // 先进行登录
    await page.goto('/login')
    await page.fill('input[type="email"]', testUser.email)
    await page.fill('input[type="password"]', testUser.password)
    await page.click('text=登录')

    // 等待跳转到主页
    await expect(page).toHaveURL('/')

    // 点击用户设置按钮
    await page.click('.el-button.is-circle')

    // 点击退出登录
    await page.click('text=退出登录')

    // 确认退出
    await page.click('text=确定')

    // 应该显示成功消息
    await expect(page.locator('.el-message--success')).toBeVisible()

    // 应该跳转到登录页
    await expect(page).toHaveURL('/login')

    // 应该不再显示用户信息
    await page.goto('/')
    await expect(page.locator('text=登录 / 注册')).toBeVisible()
  })

  test('表单验证', async ({ page }) => {
    await page.goto('/login')

    // 测试注册表单验证
    await page.click('text=注册')

    // 空表单提交
    await page.click('text=注册账号')

    // 应该显示验证错误
    await expect(page.locator('.el-form-item__error')).toHaveCount(2)

    // 测试邮箱格式验证
    await page.fill('input[type="email"]', 'invalid-email')
    await page.click('input[type="password"]') // 触发blur事件

    await expect(page.locator('text=请输入有效的邮箱地址')).toBeVisible()

    // 测试密码强度验证
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', '123') // 弱密码
    await page.click('input[placeholder*="确认密码"]') // 触发blur事件

    await expect(page.locator('text=密码长度至少8位')).toBeVisible()

    // 测试密码必须包含字母和数字
    await page.fill('input[type="password"]', 'abcdefgh') // 只有字母
    await page.click('input[placeholder*="确认密码"]')

    await expect(page.locator('text=密码必须包含数字')).toBeVisible()

    await page.fill('input[type="password"]', '12345678') // 只有数字
    await page.click('input[placeholder*="确认密码"]')

    await expect(page.locator('text=密码必须包含字母')).toBeVisible()

    // 测试确认密码验证
    await page.fill('input[type="password"]', 'Test123456')
    await page.fill('input[placeholder*="确认密码"]', 'DifferentPassword123')
    await page.click('text=注册账号') // 触发blur事件

    await expect(page.locator('text=两次输入的密码不一致')).toBeVisible()
  })

  test('错误处理', async ({ page }) => {
    await page.goto('/login')

    // 测试登录错误
    await page.fill('input[type="email"]', 'nonexistent@example.com')
    await page.fill('input[type="password"]', 'wrongpassword')
    await page.click('text=登录')

    // 应该显示错误消息
    await expect(page.locator('.el-message--error')).toBeVisible()

    // 测试重复注册
    await page.click('text=注册')
    await page.fill('input[type="email"]', testUser.email) // 已存在的邮箱
    await page.fill('input[type="password"]', testUser.password)
    await page.fill('input[placeholder*="确认密码"]', testUser.password)
    await page.click('text=注册账号')

    // 应该显示邮箱已被注册的错误
    await expect(page.locator('.el-message--error')).toBeVisible()
  })

  test('响应式设计', async ({ page }) => {
    // 测试移动端视图
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/login')

    // 登录卡片应该适应小屏幕
    const loginCard = page.locator('.login-card')
    await expect(loginCard).toBeVisible()

    // 表单元素应该正确显示
    await expect(page.locator('input[type="email"]')).toBeVisible()
    await expect(page.locator('input[type="password"]')).toBeVisible()
    await expect(page.locator('.login-button')).toBeVisible()

    // 测试标签切换在移动端的表现
    await page.click('text=注册')
    await expect(page.locator('.tab-button.active')).toHaveText('注册')
  })

  test('自动跳转', async ({ page }) => {
    // 测试已登录用户访问登录页的重定向
    // 先登录
    await page.goto('/login')
    await page.fill('input[type="email"]', testUser.email)
    await page.fill('input[type="password"]', testUser.password)
    await page.click('text=登录')

    // 等待跳转到主页
    await expect(page).toHaveURL('/')

    // 再次访问登录页应该重定向
    await page.goto('/login')
    await expect(page).toHaveURL('/app') // 应该重定向到应用页面
  })

  test('token持久化', async ({ page }) => {
    // 登录
    await page.goto('/login')
    await page.fill('input[type="email"]', testUser.email)
    await page.fill('input[type="password"]', testUser.password)
    await page.click('text=登录')

    // 等待跳转
    await expect(page).toHaveURL('/')

    // 刷新页面
    await page.reload()

    // 应该保持登录状态
    await expect(page.locator('text=' + testUser.email)).toBeVisible()

    // 关闭页面重新打开
    await page.close()
    const newPage = await page.context().newPage()
    await newPage.goto('/')

    // 应该仍然保持登录状态
    await expect(newPage.locator('text=' + testUser.email)).toBeVisible()
  })
})

test.describe('受保护路由', () => {
  test('未登录用户访问受保护路由应该重定向', async ({ page }) => {
    // 直接访问应用页面
    await page.goto('/app')

    // 应该重定向到登录页面
    await expect(page).toHaveURL('/login?redirect=%2Fapp')

    // 登录后应该重定向回原页面
    await page.fill('input[type="email"]', testUser.email)
    await page.fill('input[type="password"]', testUser.password)
    await page.click('text=登录')

    // 应该跳转到原来要访问的页面
    await expect(page).toHaveURL('/app')
  })
})

test.describe('用户体验', () => {
  test('加载状态', async ({ page }) => {
    await page.goto('/login')

    // 监听网络请求
    await page.route('/api/login', async route => {
      // 延迟响应以测试加载状态
      await new Promise(resolve => setTimeout(resolve, 1000))
      await route.continue()
    })

    await page.fill('input[type="email"]', testUser.email)
    await page.fill('input[type="password"]', testUser.password)
    await page.click('text=登录')

    // 应该显示加载状态
    await expect(page.locator('text=登录中...')).toBeVisible()
  })

  test('记住用户选择', async ({ page }) => {
    await page.goto('/login')

    // 切换到注册标签
    await page.click('text=注册')

    // 刷新页面
    await page.reload()

    // 应该还在注册标签（如果实现了状态保持）
    // 这个测试取决于具体实现
  })
})