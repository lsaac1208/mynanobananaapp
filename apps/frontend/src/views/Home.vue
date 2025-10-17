<template>
  <div class="home">
    <!-- 导航头部 -->
    <header class="home-header">
      <div class="header-container">
        <div class="header-content">
            <h1 class="logo">
              <el-icon><PictureFilled /></el-icon>
            <span class="logo-text">Nano-Banana AI</span>
            </h1>
            <UserInfo />
          </div>
        </div>
    </header>

    <!-- 主要内容 -->
    <main class="home-main">
      <!-- 英雄区 -->
      <HeroSection />
      
      <!-- 功能展示区 -->
      <FeaturesSection />
      
      <!-- CTA区 -->
      <CTASection />
    </main>

    <!-- 页脚 -->
    <footer class="home-footer">
      <div class="footer-container">
        <div class="footer-content">
          <div class="footer-info">
            <h3 class="footer-logo">
              <el-icon><PictureFilled /></el-icon>
              Nano-Banana AI
            </h3>
            <p class="footer-description">
              让每个人都能轻松创造精美的AI艺术作品
            </p>
          </div>

          <div class="footer-links">
            <div class="link-group">
              <h4>产品</h4>
              <a href="/app/generate">文生图</a>
              <a href="/app/generate">图生图</a>
              <a href="/app/gallery">我的画廊</a>
                </div>
            
            <div class="link-group">
              <h4>支持</h4>
              <a href="#">帮助文档</a>
              <a href="#">API文档</a>
              <a href="#">常见问题</a>
                </div>
            
            <div class="link-group">
              <h4>关于</h4>
              <a href="#">关于我们</a>
              <a href="#">隐私政策</a>
              <a href="#">服务条款</a>
                </div>
          </div>
        </div>
        
        <div class="footer-bottom">
          <p>&copy; 2025 Nano-Banana AI. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { PictureFilled } from '@element-plus/icons-vue'
import UserInfo from '../components/UserInfo.vue'
import HeroSection from '../components/home/HeroSection.vue'
import FeaturesSection from '../components/home/FeaturesSection.vue'
import CTASection from '../components/home/CTASection.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 初始化认证状态
onMounted(async () => {
  await authStore.initAuth()
})
</script>

<style scoped>
/* ========================================
 * 页面容器
 * ======================================== */

.home {
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
}

/* ========================================
 * 导航头部
 * ======================================== */

.home-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 800;
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

.logo .el-icon {
  font-size: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* ========================================
 * 主内容区
 * ======================================== */

.home-main {
  position: relative;
}

/* ========================================
 * 页脚
 * ======================================== */

.home-footer {
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  padding: var(--spacing-3xl) var(--spacing-lg) var(--spacing-xl);
  margin-top: var(--spacing-4xl);
}

.footer-container {
  max-width: 1400px;
  margin: 0 auto;
}

.footer-content {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: var(--spacing-3xl);
  margin-bottom: var(--spacing-2xl);
}

.footer-info {
  max-width: 400px;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 700;
  margin-bottom: var(--spacing-md);
  color: var(--text-primary);
}

.footer-logo .el-icon {
  font-size: 28px;
  color: var(--color-primary);
}

.footer-description {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.footer-links {
  display: contents;
}

.link-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.link-group h4 {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: var(--spacing-sm);
  color: var(--text-primary);
}

.link-group a {
  font-size: 14px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s ease;
}

.link-group a:hover {
  color: var(--color-primary);
}

.footer-bottom {
  padding-top: var(--spacing-xl);
  border-top: 1px solid var(--border-color);
  text-align: center;
}

.footer-bottom p {
  font-size: 14px;
  color: var(--text-tertiary);
  margin: 0;
}

/* ========================================
 * 响应式设计
 * ======================================== */

@media (max-width: 1024px) {
  .footer-content {
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-2xl);
  }
  
  .footer-info {
    grid-column: 1 / -1;
  }
}

@media (max-width: 768px) {
  .header-content {
    height: 64px;
  }
  
  .logo {
    font-size: 20px;
  }
  
  .logo .el-icon {
    font-size: 28px;
  }
  
  .footer-content {
    grid-template-columns: 1fr;
    gap: var(--spacing-xl);
  }
  
  .footer-info {
    grid-column: 1;
  }
}

/* ========================================
 * 暗色模式
 * ======================================== */

[data-theme="dark"] .home-header {
  background: rgba(26, 26, 29, 0.9);
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

[data-theme="dark"] .home-footer {
  background: var(--bg-secondary);
  border-top-color: rgba(255, 255, 255, 0.1);
}

[data-theme="dark"] .footer-bottom {
  border-top-color: rgba(255, 255, 255, 0.1);
}
</style>
