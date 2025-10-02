<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <h1 class="register-title">
          <el-icon><UserFilled /></el-icon>
          创建账户
        </h1>
        <p class="register-subtitle">加入 Nano-Banana AI，开启创意之旅</p>
      </div>

      <el-form
        ref="registerForm"
        :model="form"
        :rules="rules"
        @submit.prevent="handleRegister"
        class="register-form"
      >
        <el-form-item prop="email">
          <el-input
            v-model="form.email"
            placeholder="请输入邮箱地址"
            size="large"
            :prefix-icon="Message"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码（至少6位）"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请确认密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleRegister"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="authStore.loading"
            @click="handleRegister"
            class="register-button"
          >
            {{ authStore.loading ? '注册中...' : '立即注册' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="register-footer">
        <p>
          已有账户？
          <router-link to="/login" class="login-link">
            立即登录
          </router-link>
        </p>
        <router-link to="/" class="back-home">
          返回首页
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { UserFilled, Message, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '../../stores/auth'
import type { UserCreateRequest } from '@shared/index'

const router = useRouter()
const authStore = useAuthStore()
const registerForm = ref<FormInstance>()

// 表单数据
const form = reactive({
  email: '',
  password: '',
  confirmPassword: ''
})

// 确认密码验证
const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

// 表单验证规则
const rules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
    { max: 128, message: '密码长度不能超过128位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 处理注册
const handleRegister = async () => {
  if (!registerForm.value) return

  try {
    await registerForm.value.validate()

    const userData: UserCreateRequest = {
      email: form.email,
      password: form.password
    }

    const result = await authStore.register(userData)

    if (result.success) {
      ElMessage.success(result.message)
      // 注册成功后跳转到应用主页
      router.push('/app')
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('注册验证失败:', error)
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.register-card {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 16px;
  padding: 2.5rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.register-header {
  text-align: center;
  margin-bottom: 2rem;
}

.register-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #303133;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.register-subtitle {
  color: #909399;
  margin: 0;
}

.register-form {
  margin-bottom: 1.5rem;
}

.register-form .el-form-item {
  margin-bottom: 1.5rem;
}

.register-button {
  width: 100%;
  height: 48px;
  font-size: 1rem;
  font-weight: 500;
}

.register-footer {
  text-align: center;
  color: #909399;
  font-size: 0.875rem;
}

.register-footer p {
  margin-bottom: 1rem;
}

.login-link {
  color: #409eff;
  text-decoration: none;
  font-weight: 500;
}

.login-link:hover {
  text-decoration: underline;
}

.back-home {
  color: #909399;
  text-decoration: none;
  transition: color 0.3s;
}

.back-home:hover {
  color: #409eff;
}

@media (max-width: 480px) {
  .register-container {
    padding: 1rem;
  }

  .register-card {
    padding: 2rem 1.5rem;
  }
}
</style>