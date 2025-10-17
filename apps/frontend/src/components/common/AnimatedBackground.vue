<template>
  <div class="animated-background">
    <!-- 渐变光球 -->
    <div class="gradient-orb orb-1"></div>
    <div class="gradient-orb orb-2"></div>
    <div class="gradient-orb orb-3"></div>
    
    <!-- 网格纹理 -->
    <div class="mesh-pattern"></div>
    
    <!-- 可选的粒子效果 -->
    <div v-if="particles" class="particles-container">
      <div v-for="n in particleCount" :key="n" class="particle" :style="getParticleStyle(n)"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  particles?: boolean
  particleCount?: number
  intensity?: 'light' | 'medium' | 'strong'
}

const props = withDefaults(defineProps<Props>(), {
  particles: false,
  particleCount: 20,
  intensity: 'medium'
})

const getParticleStyle = (index: number) => {
  // 为每个粒子生成随机位置和动画延迟
  const left = Math.random() * 100
  const animationDelay = Math.random() * 10
  const animationDuration = 15 + Math.random() * 10
  const size = 2 + Math.random() * 4
  
  return {
    left: `${left}%`,
    animationDelay: `${animationDelay}s`,
    animationDuration: `${animationDuration}s`,
    width: `${size}px`,
    height: `${size}px`
  }
}
</script>

<style scoped>
.animated-background {
  position: fixed;
  inset: 0;
  z-index: -1;
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.03) 0%, 
    rgba(118, 75, 162, 0.03) 100%);
  overflow: hidden;
  pointer-events: none;
}

/* 渐变光球 */
.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  will-change: transform;
}

.orb-1 {
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  top: -250px;
  left: -250px;
  animation: float 20s ease-in-out infinite;
}

.orb-2 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #f093fb, #f5576c);
  bottom: -200px;
  right: -200px;
  animation: float 25s ease-in-out infinite reverse;
}

.orb-3 {
  width: 350px;
  height: 350px;
  background: linear-gradient(135deg, #4facfe, #00f2fe);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: float 30s ease-in-out infinite;
  animation-delay: 5s;
}

/* 网格纹理 */
.mesh-pattern {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(102, 126, 234, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(102, 126, 234, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  opacity: 0.5;
}

/* 粒子容器 */
.particles-container {
  position: absolute;
  inset: 0;
}

.particle {
  position: absolute;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.8) 0%, transparent 70%);
  border-radius: 50%;
  animation: particleFloat linear infinite;
  bottom: -10px;
}

/* 动画定义 */
@keyframes float {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  33% {
    transform: translate(30px, -30px) rotate(120deg);
  }
  66% {
    transform: translate(-20px, 20px) rotate(240deg);
  }
}

@keyframes particleFloat {
  0% {
    transform: translateY(0) translateX(0) scale(0);
    opacity: 0;
  }
  10% {
    opacity: 0.6;
    transform: scale(1);
  }
  90% {
    opacity: 0.4;
  }
  100% {
    transform: translateY(-100vh) translateX(20px) scale(0.5);
    opacity: 0;
  }
}

/* 暗色模式适配 */
[data-theme="dark"] .animated-background {
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.08) 0%, 
    rgba(118, 75, 162, 0.08) 100%);
}

[data-theme="dark"] .gradient-orb {
  opacity: 0.2;
}

[data-theme="dark"] .mesh-pattern {
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
}

/* 响应式优化 */
@media (max-width: 768px) {
  /* 移动端减少光球大小和模糊效果以提升性能 */
  .orb-1 {
    width: 300px;
    height: 300px;
    filter: blur(60px);
  }
  
  .orb-2 {
    width: 250px;
    height: 250px;
    filter: blur(60px);
  }
  
  .orb-3 {
    width: 200px;
    height: 200px;
    filter: blur(60px);
  }
  
  .mesh-pattern {
    background-size: 30px 30px;
  }
  
  .particle {
    display: none; /* 移动端禁用粒子以提升性能 */
  }
}

/* 减少动画偏好设置 */
@media (prefers-reduced-motion: reduce) {
  .gradient-orb {
    animation: none;
  }
  
  .particle {
    animation: none;
    display: none;
  }
}

/* 性能优化 - 使用transform硬件加速 */
.gradient-orb,
.particle {
  transform: translateZ(0);
  backface-visibility: hidden;
}
</style>

