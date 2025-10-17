<template>
  <section class="features-section">
    <div class="section-header" data-aos="fade-up">
      <h2 class="section-title">强大的AI能力</h2>
      <p class="section-description">
        利用最先进的AI技术，为您提供专业级的图像生成体验
      </p>
    </div>
    
    <div class="features-grid">
      <div 
        v-for="(feature, index) in features" 
        :key="index"
        class="feature-card"
        data-aos="fade-up"
        :data-aos-delay="index * 100"
      >
        <div class="feature-icon-wrapper">
          <div class="feature-icon-glow"></div>
          <div class="feature-icon">{{ feature.icon }}</div>
        </div>
        <h3 class="feature-title">{{ feature.title }}</h3>
        <p class="feature-description">{{ feature.description }}</p>
        <ul class="feature-highlights">
          <li v-for="(highlight, i) in feature.highlights" :key="i">
            <span class="highlight-icon">✓</span>
            <span>{{ highlight }}</span>
          </li>
        </ul>
      </div>
    </div>
    
    <div class="features-demo" data-aos="fade-up" data-aos-delay="400">
      <div class="demo-card glass-card">
        <div class="demo-header">
          <span class="demo-tag">实时演示</span>
          <h3>查看AI生成过程</h3>
        </div>
        <div class="demo-content">
          <div class="demo-prompt">
            <span class="prompt-label">输入提示词：</span>
            <span class="prompt-text">"一只在太空中漂浮的可爱橙色猫，数字艺术风格"</span>
          </div>
          <div class="demo-arrow">↓</div>
          <div class="demo-result">
            <div class="result-placeholder">
              <span class="result-icon">🎨</span>
              <span class="result-text">AI生成的精美图像</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
interface Feature {
  icon: string
  title: string
  description: string
  highlights: string[]
}

const features: Feature[] = [
  {
    icon: '🎨',
    title: '文生图',
    description: '仅需一句话描述，AI即可为您创作独特的视觉作品',
    highlights: [
      '多种艺术风格',
      '高分辨率输出',
      '快速生成（15秒内）'
    ]
  },
  {
    icon: '🖼️',
    title: '图生图',
    description: '上传参考图片，AI将基于您的图片进行创意再造',
    highlights: [
      '保持原图风格',
      '智能细节优化',
      '灵活调整强度'
    ]
  },
  {
    icon: '⚡',
    title: '极速生成',
    description: '先进的AI架构确保快速响应，无需长时间等待',
    highlights: [
      '平均15秒完成',
      '并发批量生成',
      '实时进度反馈'
    ]
  },
  {
    icon: '🎯',
    title: '精准控制',
    description: '多维度参数调节，让您完全掌控创作过程',
    highlights: [
      '模型自由选择',
      '尺寸任意调整',
      '负面提示词过滤'
    ]
  },
  {
    icon: '📚',
    title: '作品管理',
    description: '个人画廊自动保存，分类整理您的所有创作',
    highlights: [
      '无限云端存储',
      '智能分类标签',
      '一键收藏下载'
    ]
  },
  {
    icon: '🔐',
    title: '隐私保护',
    description: '企业级安全措施，您的创作和数据完全私密',
    highlights: [
      '数据加密传输',
      '私有作品保护',
      '账号安全保障'
    ]
  }
]
</script>

<style scoped>
/* ========================================
 * 功能区容器
 * ======================================== */

.features-section {
  padding: var(--spacing-4xl) var(--spacing-lg);
  background: var(--bg-primary);
  position: relative;
}

/* ========================================
 * 章节头部
 * ======================================== */

.section-header {
  text-align: center;
  max-width: 700px;
  margin: 0 auto var(--spacing-3xl);
}

.section-title {
  font-size: 48px;
  font-weight: 800;
  margin-bottom: var(--spacing-md);
  color: var(--text-primary);
}

.section-description {
  font-size: 18px;
  line-height: 1.7;
  color: var(--text-secondary);
}

/* ========================================
 * 功能卡片网格
 * ======================================== */

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: var(--spacing-xl);
  margin-bottom: var(--spacing-3xl);
}

.feature-card {
  padding: var(--spacing-2xl);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.08);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.05), 
    rgba(118, 75, 162, 0.05));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.feature-card:hover::before {
  opacity: 1;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 60px rgba(102, 126, 234, 0.15);
}

/* ========================================
 * 功能图标
 * ======================================== */

.feature-icon-wrapper {
  position: relative;
  width: 80px;
  height: 80px;
  margin-bottom: var(--spacing-lg);
}

.feature-icon-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.3), transparent);
  border-radius: 50%;
  filter: blur(20px);
  animation: glow-pulse 2s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.8;
  }
}

.feature-icon {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
  transition: transform 0.3s ease;
}

.feature-card:hover .feature-icon {
  transform: rotateY(360deg);
}

/* ========================================
 * 功能内容
 * ======================================== */

.feature-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: var(--spacing-sm);
  color: var(--text-primary);
}

.feature-description {
  font-size: 16px;
  line-height: 1.7;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-lg);
}

.feature-highlights {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-highlights li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.highlight-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: bold;
  flex-shrink: 0;
}

/* ========================================
 * 演示区域
 * ======================================== */

.features-demo {
  max-width: 900px;
  margin: 0 auto;
}

.demo-card {
  padding: var(--spacing-2xl);
}

.demo-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.demo-tag {
  display: inline-block;
  padding: 6px 16px;
  background: rgba(102, 126, 234, 0.1);
  color: var(--color-primary);
  border-radius: 999px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: var(--spacing-md);
}

.demo-header h3 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.demo-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.demo-prompt {
  padding: var(--spacing-lg);
  background: rgba(102, 126, 234, 0.05);
  border-radius: var(--radius-md);
  border: 1px dashed rgba(102, 126, 234, 0.3);
}

.prompt-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-tertiary);
  margin-bottom: 8px;
}

.prompt-text {
  font-size: 16px;
  color: var(--text-primary);
  font-style: italic;
}

.demo-arrow {
  text-align: center;
  font-size: 32px;
  color: var(--color-primary);
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(10px);
  }
}

.demo-result {
  padding: var(--spacing-2xl);
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.05), 
    rgba(118, 75, 162, 0.05));
  border-radius: var(--radius-lg);
  border: 2px solid rgba(102, 126, 234, 0.2);
}

.result-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-3xl);
}

.result-icon {
  font-size: 64px;
  animation: rotate 3s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.result-text {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-secondary);
}

/* ========================================
 * 响应式设计
 * ======================================== */

@media (max-width: 768px) {
  .features-section {
    padding: var(--spacing-2xl) var(--spacing-md);
  }
  
  .section-title {
    font-size: 32px;
  }
  
  .section-description {
    font-size: 16px;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
  }
  
  .demo-card {
    padding: var(--spacing-lg);
  }
  
  .demo-header h3 {
    font-size: 22px;
  }
}

/* ========================================
 * 暗色模式
 * ======================================== */

[data-theme="dark"] .feature-card {
  background: rgba(42, 42, 46, 0.8);
  border-color: rgba(255, 255, 255, 0.1);
}

[data-theme="dark"] .demo-prompt {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.4);
}

[data-theme="dark"] .demo-result {
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.1), 
    rgba(118, 75, 162, 0.1));
  border-color: rgba(102, 126, 234, 0.3);
}
</style>

