<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1 class="title">Nano-Banana AI</h1>
        <p class="subtitle">AI绘图平台</p>
      </div>

      <div class="tab-container">
        <div class="tabs">
          <button
            class="tab-button"
            :class="{ active: activeTab === 'login' }"
            @click="activeTab = 'login'"
          >
            登录
          </button>
          <button
            class="tab-button"
            :class="{ active: activeTab === 'register' }"
            @click="activeTab = 'register'"
          >
            注册
          </button>
        </div>

        <!-- 登录表单 -->
        <div v-if="activeTab === 'login'" class="form-container">
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            label-width="0"
            size="large"
            @submit.prevent="handleLogin"
          >
            <el-form-item prop="email">
              <el-input
                v-model="loginForm.email"
                placeholder="邮箱地址"
                prefix-icon="User"
                type="email"
                autocomplete="email"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                placeholder="密码"
                prefix-icon="Lock"
                type="password"
                autocomplete="current-password"
                show-password
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                class="login-button"
                :loading="authStore.loading"
                @click="handleLogin"
              >
                {{ authStore.loading ? '登录中...' : '登录' }}
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 注册表单 -->
        <div v-if="activeTab === 'register'" class="form-container">
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            label-width="0"
            size="large"
            @submit.prevent="handleRegister"
          >
            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="邮箱地址"
                prefix-icon="User"
                type="email"
                autocomplete="email"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                placeholder="密码 (至少8位，包含字母和数字)"
                prefix-icon="Lock"
                type="password"
                autocomplete="new-password"
                show-password
              />
            </el-form-item>

            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                placeholder="确认密码"
                prefix-icon="Lock"
                type="password"
                autocomplete="new-password"
                show-password
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                class="login-button"
                :loading="authStore.loading"
                @click="handleRegister"
              >
                {{ authStore.loading ? '注册中...' : '注册账号' }}
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>

      <div class="login-footer">
        <p class="footer-text">注册即可获得 3 次免费生成机会</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import type { UserLoginRequest, UserCreateRequest } from '@shared/index'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 表单引用
const loginFormRef = ref<FormInstance>()
const registerFormRef = ref<FormInstance>()

// 活动标签
const activeTab = ref<'login' | 'register'>('login')

// 根据路由设置默认标签
onMounted(() => {
  if (route.path === '/register') {
    activeTab.value = 'register'
  }
})

// 登录表单
const loginForm = reactive<UserLoginRequest>({
  email: '',
  password: ''
})

// 注册表单
const registerForm = reactive<UserCreateRequest & { confirmPassword: string }>({
  email: '',
  password: '',
  confirmPassword: ''
})

// 邮箱验证规则
const emailValidator = (rule: any, value: string, callback: any) => {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  if (!value) {
    callback(new Error('请输入邮箱地址'))
  } else if (!emailRegex.test(value)) {
    callback(new Error('请输入有效的邮箱地址'))
  } else {
    callback()
  }
}

// 密码验证规则
const passwordValidator = (rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 8) {
    callback(new Error('密码长度至少8位'))
  } else if (!/[A-Za-z]/.test(value)) {
    callback(new Error('密码必须包含字母'))
  } else if (!/\d/.test(value)) {
    callback(new Error('密码必须包含数字'))
  } else {
    callback()
  }
}

// 确认密码验证规则
const confirmPasswordValidator = (rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请确认密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

// 登录表单验证规则
const loginRules: FormRules = {
  email: [{ validator: emailValidator, trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// 注册表单验证规则
const registerRules: FormRules = {
  email: [{ validator: emailValidator, trigger: 'blur' }],
  password: [{ validator: passwordValidator, trigger: 'blur' }],
  confirmPassword: [{ validator: confirmPasswordValidator, trigger: 'blur' }]
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    const valid = await loginFormRef.value.validate()
    if (!valid) return

    const result = await authStore.login(loginForm)

    if (result.success) {
      ElMessage.success(result.message)
      // 确保认证状态已更新后再跳转
      await new Promise(resolve => setTimeout(resolve, 100))

      // 智能跳转逻辑：检查保存的重定向路径或基于角色跳转
      const savedRedirect = localStorage.getItem('redirectAfterLogin')
      if (savedRedirect) {
        localStorage.removeItem('redirectAfterLogin')
        router.push(savedRedirect)
      } else if (authStore.isAdmin) {
        router.push('/admin')
      } else {
        router.push('/app')
      }
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('Login validation error:', error)
  }
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return

  try {
    const valid = await registerFormRef.value.validate()
    if (!valid) return

    const result = await authStore.register({
      email: registerForm.email,
      password: registerForm.password
    })

    if (result.success) {
      ElMessage.success(result.message)
      // 确保认证状态已更新后再跳转
      await new Promise(resolve => setTimeout(resolve, 100))

      // 智能跳转逻辑：检查保存的重定向路径或基于角色跳转
      const savedRedirect = localStorage.getItem('redirectAfterLogin')
      if (savedRedirect) {
        localStorage.removeItem('redirectAfterLogin')
        router.push(savedRedirect)
      } else if (authStore.isAdmin) {
        router.push('/admin')
      } else {
        router.push('/app')
      }
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('Register validation error:', error)
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  padding: 40px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.title {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 16px;
  color: #7f8c8d;
  margin: 0;
}

.tab-container {
  margin-bottom: 20px;
}

.tabs {
  display: flex;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 4px;
  margin-bottom: 24px;
}

.tab-button {
  flex: 1;
  padding: 12px;
  border: none;
  background: transparent;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-button.active {
  background: white;
  color: #495057;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-container {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
}

.login-footer {
  text-align: center;
  margin-top: 24px;
}

.footer-text {
  font-size: 14px;
  color: #6c757d;
  margin: 0;
}

/* Element Plus 样式覆盖 */
:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #e1e8ed;
  transition: all 0.2s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #409eff;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-button--primary) {
  background-color: #667eea;
  border-color: #667eea;
}

:deep(.el-button--primary:hover) {
  background-color: #5a6fd8;
  border-color: #5a6fd8;
}

/* 触摸优化 */
.tab-button,
.login-button {
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    padding: 15px;
    min-height: 100vh;
    min-height: 100svh; /* 支持移动端视窗 */
  }

  .login-card {
    max-width: 100%;
    min-width: 320px;
    padding: 32px 24px;
    margin: 0 auto;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  }

  .title {
    font-size: 26px;
  }

  .subtitle {
    font-size: 15px;
  }

  .tab-button {
    min-height: 44px; /* iOS推荐的最小点击区域 */
    font-size: 15px;
    padding: 12px 16px;
  }

  .login-button {
    height: 52px; /* 增加移动端按钮高度 */
    font-size: 17px;
  }
}

@media (max-width: 480px) {
  .login-container {
    padding: 12px;
  }

  .login-card {
    padding: 28px 20px;
    border-radius: 12px;
  }

  .title {
    font-size: 24px;
  }

  .subtitle {
    font-size: 14px;
  }

  .login-header {
    margin-bottom: 24px;
  }

  .tab-container {
    margin-bottom: 16px;
  }

  .tabs {
    margin-bottom: 20px;
  }

  .tab-button {
    min-height: 48px; /* 小屏幕更大的点击区域 */
    font-size: 14px;
    font-weight: 600;
  }

  .form-container {
    margin-bottom: 16px;
  }

  .login-button {
    height: 50px;
    font-size: 16px;
    font-weight: 700;
  }

  .footer-text {
    font-size: 13px;
    line-height: 1.4;
  }
}

@media (max-width: 360px) {
  .login-container {
    padding: 8px;
  }

  .login-card {
    padding: 24px 16px;
    min-width: 280px;
  }

  .title {
    font-size: 22px;
  }

  .tab-button {
    padding: 10px 12px;
    font-size: 13px;
  }

  .login-button {
    height: 48px;
    font-size: 15px;
  }
}

/* 横屏适配 */
@media (max-height: 600px) and (orientation: landscape) {
  .login-container {
    padding: 10px;
    align-items: flex-start;
    padding-top: 20px;
  }

  .login-card {
    margin-top: 0;
    padding: 20px 24px;
  }

  .login-header {
    margin-bottom: 20px;
  }

  .title {
    font-size: 22px;
  }

  .subtitle {
    font-size: 14px;
  }
}
</style>