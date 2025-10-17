<template>
  <section class="cta-section">
    <div class="cta-background">
      <div class="cta-gradient"></div>
    </div>
    
    <div class="cta-content" data-aos="zoom-in">
      <h2 class="cta-title">准备好释放创造力了吗？</h2>
      <p class="cta-description">
        加入数千位创作者，开启您的AI艺术之旅
      </p>
      
      <div class="cta-actions">
        <button class="btn-cta-primary" @click="handleGetStarted">
          <span>免费开始创作</span>
          <span class="btn-icon">✨</span>
        </button>
        <button class="btn-cta-secondary" @click="handleLearnMore">
          了解更多
        </button>
      </div>
      
      <div class="cta-features">
        <div class="cta-feature-item">
          <span class="feature-check">✓</span>
          <span>无需信用卡</span>
        </div>
        <div class="cta-feature-item">
          <span class="feature-check">✓</span>
          <span>即刻开始使用</span>
        </div>
        <div class="cta-feature-item">
          <span class="feature-check">✓</span>
          <span>专业级品质</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const handleGetStarted = () => {
  router.push('/register')
}

const handleLearnMore = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<style scoped>
/* ========================================
 * CTA区容器
 * ======================================== */

.cta-section {
  position: relative;
  padding: var(--spacing-4xl) var(--spacing-lg);
  overflow: hidden;
}

/* ========================================
 * 背景效果
 * ======================================== */

.cta-background {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.cta-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.15) 0%, 
    rgba(118, 75, 162, 0.15) 100%);
}

/* ========================================
 * 内容区域
 * ======================================== */

.cta-content {
  position: relative;
  z-index: 1;
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
  padding: var(--spacing-3xl);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: var(--radius-2xl);
  box-shadow: 
    0 20px 60px rgba(102, 126, 234, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
}

.cta-title {
  font-size: 48px;
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: var(--spacing-lg);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.cta-description {
  font-size: 20px;
  line-height: 1.7;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-2xl);
}

/* ========================================
 * CTA按钮
 * ======================================== */

.cta-actions {
  display: flex;
  gap: var(--spacing-lg);
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: var(--spacing-2xl);
}

.btn-cta-primary {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 18px 48px;
  font-size: 18px;
  font-weight: 700;
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 10px 40px rgba(102, 126, 234, 0.4),
    0 0 0 0 rgba(102, 126, 234, 0.5);
  position: relative;
  overflow: hidden;
}

.btn-cta-primary::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.3), 
    transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.btn-cta-primary:hover::before {
  opacity: 1;
}

.btn-cta-primary:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: 
    0 20px 60px rgba(102, 126, 234, 0.5),
    0 0 0 0 rgba(102, 126, 234, 0.7);
}

.btn-cta-primary .btn-icon {
  font-size: 20px;
  animation: sparkle-cta 2s ease-in-out infinite;
}

@keyframes sparkle-cta {
  0%, 100% {
    transform: scale(1) rotate(0deg);
  }
  50% {
    transform: scale(1.3) rotate(180deg);
  }
}

.btn-cta-secondary {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 18px 48px;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-primary);
  background: transparent;
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cta-secondary:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.5);
  transform: translateY(-2px);
}

/* ========================================
 * 特性列表
 * ======================================== */

.cta-features {
  display: flex;
  justify-content: center;
  gap: var(--spacing-xl);
  flex-wrap: wrap;
}

.cta-feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  color: var(--text-secondary);
}

.feature-check {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border-radius: 50%;
  font-size: 14px;
  font-weight: bold;
}

/* ========================================
 * 响应式设计
 * ======================================== */

@media (max-width: 768px) {
  .cta-section {
    padding: var(--spacing-2xl) var(--spacing-md);
  }
  
  .cta-content {
    padding: var(--spacing-xl);
  }
  
  .cta-title {
    font-size: 32px;
  }
  
  .cta-description {
    font-size: 16px;
  }
  
  .cta-actions {
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  .btn-cta-primary,
  .btn-cta-secondary {
    width: 100%;
    justify-content: center;
    font-size: 16px;
    padding: 16px 32px;
  }
  
  .cta-features {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
}

/* ========================================
 * 暗色模式
 * ======================================== */

[data-theme="dark"] .cta-gradient {
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.2) 0%, 
    rgba(118, 75, 162, 0.2) 100%);
}

[data-theme="dark"] .cta-content {
  background: rgba(42, 42, 46, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
}

[data-theme="dark"] .btn-cta-secondary {
  border-color: rgba(102, 126, 234, 0.4);
}

[data-theme="dark"] .btn-cta-secondary:hover {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.6);
}
</style>

