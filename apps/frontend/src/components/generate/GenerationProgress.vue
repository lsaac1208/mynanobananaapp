<template>
  <div v-if="visible" class="generation-overlay">
    <!-- 粒子背景 -->
    <div class="particles-background">
      <div v-for="n in 20" :key="n" class="particle" :style="getParticleStyle(n)" />
    </div>
    
    <!-- 进度卡片 -->
    <div class="progress-card glass-card">
      <!-- AI光晕 -->
      <div class="ai-glow"></div>
      
      <!-- SVG环形进度 -->
      <svg class="progress-ring" viewBox="0 0 200 200">
        <defs>
          <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#667eea"/>
            <stop offset="100%" stop-color="#764ba2"/>
          </linearGradient>
        </defs>
        <!-- 背景圆 -->
        <circle
          class="progress-ring-bg"
          cx="100"
          cy="100"
          r="80"
          fill="none"
          stroke="rgba(102, 126, 234, 0.1)"
          stroke-width="8"
        />
        <!-- 进度圆 -->
        <circle
          class="progress-ring-circle"
          cx="100"
          cy="100"
          r="80"
          fill="none"
          stroke="url(#progressGradient)"
          stroke-width="8"
          stroke-linecap="round"
          :stroke-dasharray="circumference"
          :stroke-dashoffset="strokeDashoffset"
        />
      </svg>
      
      <!-- 进度内容 -->
      <div class="progress-content">
        <div class="time-display">
          <span class="time-value">{{ remainingTime }}</span>
          <span class="time-unit">秒</span>
        </div>
        <div class="stage-text">{{ currentStage }}</div>
        <div class="progress-percentage">{{ progressPercentage }}%</div>
        
        <!-- 脉冲波纹 -->
        <div class="pulse-rings">
          <div class="pulse-ring" v-for="i in 3" :key="i" :style="{ animationDelay: `${i * 0.6}s` }" />
        </div>
      </div>
      
      <!-- 取消按钮 -->
      <el-button class="cancel-button" @click="handleCancel" text>
        取消生成
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

// Props
const props = defineProps<{
  visible: boolean
  progress?: number
  estimatedTime?: number
  elapsedTime?: number
  stage?: string
}>()

// Emits
const emit = defineEmits<{
  cancel: []
}>()

// Local state
const remainingTime = ref(props.estimatedTime || 30)
const currentStage = ref(props.stage || '正在生成中...')
let intervalId: number | null = null

// Computed
const circumference = 2 * Math.PI * 80
const progressPercentage = computed(() => Math.round(props.progress || 0))
const strokeDashoffset = computed(() => {
  const progress = props.progress || 0
  return circumference - (progress / 100) * circumference
})

// Methods
const getParticleStyle = (index: number) => {
  const delay = Math.random() * 5
  const duration = 5 + Math.random() * 5
  const left = Math.random() * 100
  return {
    left: `${left}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`
  }
}

const handleCancel = () => {
  emit('cancel')
}

const startTimer = () => {
  if (intervalId) return
  
  intervalId = window.setInterval(() => {
    if (remainingTime.value > 0) {
      remainingTime.value--
    }
  }, 1000)
}

const stopTimer = () => {
  if (intervalId) {
    clearInterval(intervalId)
    intervalId = null
  }
}

// Watchers
watch(() => props.visible, (newVal) => {
  if (newVal) {
    startTimer()
  } else {
    stopTimer()
  }
})

watch(() => props.estimatedTime, (newVal) => {
  if (newVal) {
    remainingTime.value = newVal
  }
})

watch(() => props.stage, (newVal) => {
  if (newVal) {
    currentStage.value = newVal
  }
})

// Lifecycle
onMounted(() => {
  if (props.visible) {
    startTimer()
  }
})

onUnmounted(() => {
  stopTimer()
})
</script>

<style scoped>
.generation-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.3s ease;
}

/* 粒子背景 */
.particles-background {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.particle {
  position: absolute;
  bottom: -10px;
  width: 4px;
  height: 4px;
  background: rgba(102, 126, 234, 0.6);
  border-radius: 50%;
  animation: particleFloat 8s linear infinite;
}

@keyframes particleFloat {
  0% {
    transform: translateY(0) scale(1);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) scale(0.5);
    opacity: 0;
  }
}

/* 进度卡片 */
.progress-card {
  position: relative;
  width: 400px;
  padding: var(--spacing-2xl);
  text-align: center;
  animation: slideInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* AI光晕 */
.ai-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.3), transparent 70%);
  animation: glowPulse 2s ease-in-out infinite;
  pointer-events: none;
}

@keyframes glowPulse {
  0%, 100% {
    opacity: 0.5;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 0.8;
    transform: translate(-50%, -50%) scale(1.1);
  }
}

/* SVG环形进度 */
.progress-ring {
  width: 200px;
  height: 200px;
  transform: rotate(-90deg);
  filter: drop-shadow(0 0 10px rgba(102, 126, 234, 0.5));
}

.progress-ring-circle {
  transition: stroke-dashoffset 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 进度内容 */
.progress-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 160px;
}

.time-display {
  font-size: 48px;
  font-weight: 700;
  background: var(--color-primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  margin-bottom: var(--spacing-sm);
}

.time-unit {
  font-size: 16px;
  margin-left: 4px;
}

.stage-text {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-xs);
}

.progress-percentage {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-primary);
}

/* 脉冲波纹 */
.pulse-rings {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.pulse-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100px;
  height: 100px;
  border: 2px solid var(--color-primary);
  border-radius: 50%;
  animation: pulseExpand 1.8s ease-out infinite;
  opacity: 0;
}

@keyframes pulseExpand {
  0% {
    transform: translate(-50%, -50%) scale(0.5);
    opacity: 0.8;
  }
  100% {
    transform: translate(-50%, -50%) scale(2);
    opacity: 0;
  }
}

/* 取消按钮 */
.cancel-button {
  margin-top: var(--spacing-xl);
  color: var(--text-tertiary);
}

.cancel-button:hover {
  color: var(--color-danger);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .progress-card {
    width: 90%;
    max-width: 350px;
    padding: var(--spacing-xl);
  }
  
  .progress-ring {
    width: 160px;
    height: 160px;
  }
  
  .progress-content {
    width: 130px;
  }
  
  .time-display {
    font-size: 36px;
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>

