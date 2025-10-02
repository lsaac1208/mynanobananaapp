<template>
  <div class="home">
    <el-container class="home-container">
      <el-header class="home-header">
        <div class="container">
          <div class="flex justify-between items-center">
            <h1 class="logo">
              <el-icon><PictureFilled /></el-icon>
              Nano-Banana AI
            </h1>
            <UserInfo />
          </div>
        </div>
      </el-header>

      <el-main class="home-main">
        <div class="container">
          <div class="hero-section text-center">
            <h1 class="hero-title">AI创意无限，灵感即刻生成</h1>
            <p class="hero-subtitle">
              使用先进的nano-banana模型，轻松将您的创意转化为精美图片
            </p>
            <div class="hero-buttons mt-8">
              <el-button
                type="primary"
                size="large"
                @click="handleStartCreate"
              >
                开始创作
              </el-button>
              <el-button
                v-if="!authStore.isLoggedIn"
                size="large"
                @click="$router.push('/login')"
              >
                立即登录
              </el-button>
              <el-button
                v-else
                size="large"
                @click="$router.push('/app')"
              >
                进入应用
              </el-button>
            </div>
          </div>

          <div class="features-section">
            <el-row :gutter="32">
              <el-col :xs="24" :md="8">
                <div class="feature-card">
                  <el-icon class="feature-icon"><EditPen /></el-icon>
                  <h3>文生图</h3>
                  <p>输入文字描述，AI为您生成精美图片</p>
                </div>
              </el-col>
              <el-col :xs="24" :md="8">
                <div class="feature-card">
                  <el-icon class="feature-icon"><Picture /></el-icon>
                  <h3>图生图</h3>
                  <p>上传参考图片，基于您的创意进行再创作</p>
                </div>
              </el-col>
              <el-col :xs="24" :md="8">
                <div class="feature-card">
                  <el-icon class="feature-icon"><FolderOpened /></el-icon>
                  <h3>个人画廊</h3>
                  <p>保存和管理您的所有创作作品</p>
                </div>
              </el-col>
            </el-row>
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { PictureFilled, EditPen, Picture, FolderOpened } from '@element-plus/icons-vue'
import UserInfo from '../components/UserInfo.vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 处理开始创作按钮点击
const handleStartCreate = () => {
  if (authStore.isLoggedIn) {
    // 已登录，直接跳转到应用页面
    router.push('/app')
  } else {
    // 未登录，跳转到注册页面
    router.push('/register')
  }
}

// 初始化认证状态
onMounted(async () => {
  await authStore.initAuth()
})
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.home-container {
  min-height: 100vh;
}

.home-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.auth-buttons {
  gap: 0.5rem;
}

.home-main {
  padding-top: 4rem;
}

.hero-section {
  margin-bottom: 6rem;
}

.hero-title {
  font-size: 3rem;
  margin-bottom: 1rem;
  font-weight: 700;
  background: linear-gradient(45deg, #fff, #f0f8ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.9;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-buttons {
  gap: 1rem;
}

.features-section {
  margin-top: 4rem;
}

.feature-card {
  text-align: center;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 1rem;
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #ffd700;
}

.feature-card h3 {
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.feature-card p {
  opacity: 0.9;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .auth-buttons {
    flex-direction: column;
  }
}
</style>