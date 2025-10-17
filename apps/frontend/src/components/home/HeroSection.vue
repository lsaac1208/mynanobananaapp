<template>
  <section class="hero-section">
    <div class="hero-background">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
      <div class="mesh-pattern"></div>
    </div>
    
    <div class="hero-content">
      <div class="hero-badge" data-aos="fade-down">
        <span class="badge-icon">✨</span>
        <span class="badge-text">AI驱动的创意工具</span>
      </div>
      
      <h1 class="hero-title" data-aos="fade-up" data-aos-delay="100">
        <span class="title-gradient">Nano-Banana AI</span>
        <br />
        让想象成为现实
      </h1>
      
      <p class="hero-description" data-aos="fade-up" data-aos-delay="200">
        使用先进的AI技术，将您的创意瞬间转化为精美图像。
        <br />
        无需专业技能，人人都能成为数字艺术家。
      </p>
      
      <div class="hero-actions" data-aos="fade-up" data-aos-delay="300">
        <button class="btn-hero-primary" @click="handleStart">
          <span>立即开始创作</span>
          <span class="btn-arrow">→</span>
        </button>
        <button class="btn-hero-secondary" @click="handleExplore">
          <span class="btn-icon">🎨</span>
          <span>浏览示例作品</span>
        </button>
      </div>
      
      <div class="hero-stats" data-aos="fade-up" data-aos-delay="400">
        <div class="stat-item">
          <div class="stat-value">10,000+</div>
          <div class="stat-label">生成图像</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <div class="stat-value">1,000+</div>
          <div class="stat-label">活跃用户</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <div class="stat-value">99%</div>
          <div class="stat-label">满意度</div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const handleStart = () => {
  router.push('/app/generate')
}

const handleExplore = () => {
  const section = document.querySelector('.features-section')
  if (section) {
    section.scrollIntoView({ behavior: 'smooth' })
  }
}
</script>

<style scoped>
/* ========================================
 * 英雄区容器
 * ======================================== */

.hero-section {
  position: relative;
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: var(--spacing-3xl) var(--spacing-lg);
}

/* ========================================
 * 动态背景
 * ======================================== */

.hero-background {
  position: absolute;
  inset: 0;
  z-index: 0;
  background: linear-gradient(135deg,
    rgba(102, 126, 234, 0.05) 0%,
    rgba(118, 75, 162, 0.05) 100%);
  overflow: hidden;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.3;
  animation: float 20s ease-in-out infinite;
}

.orb-1 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.8), transparent);
  top: -250px;
  left: -250px;
  animation-delay: 0s;
}

.orb-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(118, 75, 162, 0.8), transparent);
  bottom: -200px;
  right: -200px;
  animation-delay: 5s;
}

.orb-3 {
  width: 350px;
  height: 350px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.6), transparent);
  top: 50%;
  right: 10%;
  animation-delay: 10s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -30px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}

.mesh-pattern {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(102, 126, 234, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(102, 126, 234, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  opacity: 0.5;
}

/* ========================================
 * 内容区域
 * ======================================== */

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 900px;
  text-align: center;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 999px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-primary);
  margin-bottom: var(--spacing-lg);
  animation: badge-pulse 2s ease-in-out infinite;
}

@keyframes badge-pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.4);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(102, 126, 234, 0);
  }
}

.badge-icon {
  animation: sparkle 1.5s ease-in-out infinite;
}

@keyframes sparkle {
  0%, 100% {
    transform: scale(1) rotate(0deg);
  }
  50% {
    transform: scale(1.2) rotate(180deg);
  }
}

/* ========================================
 * 标题
 * ======================================== */

.hero-title {
  font-size: 64px;
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: var(--spacing-lg);
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.title-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradient-shift 3s ease infinite;
}

@keyframes gradient-shift {
  0%, 100% {
    filter: hue-rotate(0deg);
  }
  50% {
    filter: hue-rotate(10deg);
  }
}

/* ========================================
 * 描述
 * ======================================== */

.hero-description {
  font-size: 20px;
  line-height: 1.7;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-2xl);
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
}

/* ========================================
 * 操作按钮
 * ======================================== */

.hero-actions {
  display: flex;
  gap: var(--spacing-lg);
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: var(--spacing-3xl);
}

.btn-hero-primary {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 16px 40px;
  font-size: 18px;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 10px 40px rgba(102, 126, 234, 0.3),
    0 0 0 0 rgba(102, 126, 234, 0.4);
}

.btn-hero-primary:hover {
  transform: translateY(-4px);
  box-shadow: 
    0 20px 60px rgba(102, 126, 234, 0.4),
    0 0 0 0 rgba(102, 126, 234, 0.6);
}

.btn-hero-primary .btn-arrow {
  transition: transform 0.3s ease;
}

.btn-hero-primary:hover .btn-arrow {
  transform: translateX(6px);
}

.btn-hero-secondary {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 16px 40px;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-primary);
  background: rgba(102, 126, 234, 0.1);
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-hero-secondary:hover {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.5);
  transform: translateY(-2px);
}

/* ========================================
 * 统计数据
 * ======================================== */

.hero-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2xl);
  flex-wrap: wrap;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-tertiary);
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: var(--border-color);
}

/* ========================================
 * 响应式设计
 * ======================================== */

@media (max-width: 768px) {
  .hero-section {
    min-height: auto;
    padding: var(--spacing-2xl) var(--spacing-md);
  }
  
  .hero-title {
    font-size: 40px;
  }
  
  .hero-description {
    font-size: 16px;
  }
  
  .hero-actions {
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  .btn-hero-primary,
  .btn-hero-secondary {
    width: 100%;
    justify-content: center;
    font-size: 16px;
    padding: 14px 32px;
  }
  
  .stat-value {
    font-size: 28px;
  }
  
  .stat-divider {
    display: none;
  }
}

/* ========================================
 * 暗色模式
 * ======================================== */

[data-theme="dark"] .hero-background {
  background: linear-gradient(135deg,
    rgba(102, 126, 234, 0.08) 0%,
    rgba(118, 75, 162, 0.08) 100%);
}

[data-theme="dark"] .hero-badge {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
}

[data-theme="dark"] .btn-hero-secondary {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.4);
}
</style>

