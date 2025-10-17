<template>
  <button 
    :class="buttonClasses"
    :disabled="disabled || loading"
    :type="htmlType"
    @click="handleClick"
  >
    <span v-if="loading" class="btn-spinner">
      <svg class="spinner-icon" viewBox="0 0 24 24">
        <circle class="spinner-circle" cx="12" cy="12" r="10" />
      </svg>
    </span>
    <span v-if="icon && !loading" class="btn-icon">
      {{ icon }}
    </span>
    <span class="btn-content">
      <slot />
    </span>
    <span v-if="arrow && !loading" class="btn-arrow">
      →
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'text'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  loading?: boolean
  block?: boolean
  round?: boolean
  icon?: string
  arrow?: boolean
  htmlType?: 'button' | 'submit' | 'reset'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'primary',
  size: 'medium',
  disabled: false,
  loading: false,
  block: false,
  round: false,
  arrow: false,
  htmlType: 'button'
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const buttonClasses = computed(() => [
  'btn',
  `btn-${props.type}`,
  `btn-${props.size}`,
  {
    'btn-block': props.block,
    'btn-round': props.round,
    'btn-loading': props.loading,
    'btn-disabled': props.disabled
  }
])

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped>
/* ========================================
 * 按钮基础样式
 * ======================================== */

.btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: var(--font-family-base);
  font-weight: 500;
  text-align: center;
  white-space: nowrap;
  cursor: pointer;
  user-select: none;
  border: none;
  outline: none;
  transition: all var(--transition-base);
  overflow: hidden;
}

.btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.2), 
    transparent);
  opacity: 0;
  transition: opacity var(--transition-fast);
  pointer-events: none;
}

.btn:hover::before {
  opacity: 1;
}

.btn:active {
  transform: scale(0.98);
}

/* ========================================
 * 尺寸变体
 * ======================================== */

.btn-small {
  height: 32px;
  padding: 0 16px;
  font-size: 14px;
  border-radius: var(--radius-sm);
}

.btn-medium {
  height: 40px;
  padding: 0 24px;
  font-size: 16px;
  border-radius: var(--radius-md);
}

.btn-large {
  height: 48px;
  padding: 0 32px;
  font-size: 18px;
  border-radius: var(--radius-lg);
}

/* 移动端触摸目标最小高度 */
@media (max-width: 768px) {
  .btn-small {
    height: 40px;
    font-size: 15px;
  }
  
  .btn-medium {
    height: 44px;
    font-size: 16px;
  }
  
  .btn-large {
    height: 52px;
    font-size: 18px;
  }
}

/* ========================================
 * 类型变体 - Primary
 * ======================================== */

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 
    0 4px 12px rgba(102, 126, 234, 0.3),
    0 0 0 0 rgba(102, 126, 234, 0.4);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 8px 24px rgba(102, 126, 234, 0.4),
    0 0 0 0 rgba(102, 126, 234, 0.6);
}

.btn-primary:active {
  transform: translateY(0);
  box-shadow: 
    0 2px 8px rgba(102, 126, 234, 0.3);
}

/* ========================================
 * 类型变体 - Secondary
 * ======================================== */

.btn-secondary {
  background: rgba(102, 126, 234, 0.1);
  color: var(--color-primary);
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.btn-secondary:hover {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.5);
  transform: translateY(-2px);
}

/* ========================================
 * 类型变体 - Success
 * ======================================== */

.btn-success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4);
}

/* ========================================
 * 类型变体 - Danger
 * ======================================== */

.btn-danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.btn-danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(239, 68, 68, 0.4);
}

/* ========================================
 * 类型变体 - Warning
 * ======================================== */

.btn-warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.btn-warning:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(245, 158, 11, 0.4);
}

/* ========================================
 * 类型变体 - Text
 * ======================================== */

.btn-text {
  background: transparent;
  color: var(--color-primary);
  box-shadow: none;
}

.btn-text:hover {
  background: rgba(102, 126, 234, 0.08);
  transform: none;
}

/* ========================================
 * 修饰符 - Block
 * ======================================== */

.btn-block {
  width: 100%;
  display: flex;
}

/* ========================================
 * 修饰符 - Round
 * ======================================== */

.btn-round {
  border-radius: 999px;
}

/* ========================================
 * 状态 - Loading
 * ======================================== */

.btn-loading {
  cursor: not-allowed;
  opacity: 0.8;
}

.btn-spinner {
  display: inline-flex;
  width: 16px;
  height: 16px;
}

.spinner-icon {
  width: 100%;
  height: 100%;
  animation: spin 0.8s linear infinite;
}

.spinner-circle {
  fill: none;
  stroke: currentColor;
  stroke-width: 3;
  stroke-linecap: round;
  stroke-dasharray: 60;
  stroke-dashoffset: 20;
  animation: spinner-dash 1.5s ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes spinner-dash {
  0% {
    stroke-dasharray: 1, 200;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 100, 200;
    stroke-dashoffset: -40;
  }
  100% {
    stroke-dasharray: 100, 200;
    stroke-dashoffset: -120;
  }
}

/* ========================================
 * 状态 - Disabled
 * ======================================== */

.btn-disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.btn-disabled:hover {
  transform: none;
  box-shadow: none;
}

.btn-disabled::before {
  display: none;
}

/* ========================================
 * 图标和箭头
 * ======================================== */

.btn-icon {
  display: inline-flex;
  font-size: 1.2em;
}

.btn-arrow {
  display: inline-flex;
  font-size: 1.1em;
  transition: transform var(--transition-fast);
}

.btn:hover .btn-arrow {
  transform: translateX(4px);
}

/* ========================================
 * 暗色模式适配
 * ======================================== */

[data-theme="dark"] .btn-secondary {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.4);
}

[data-theme="dark"] .btn-secondary:hover {
  background: rgba(102, 126, 234, 0.25);
  border-color: rgba(102, 126, 234, 0.6);
}

[data-theme="dark"] .btn-text {
  color: var(--color-primary-light);
}

[data-theme="dark"] .btn-text:hover {
  background: rgba(102, 126, 234, 0.12);
}

/* ========================================
 * 焦点可访问性
 * ======================================== */

.btn:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* ========================================
 * 触摸设备优化
 * ======================================== */

@media (hover: none) {
  .btn:hover {
    transform: none;
  }
  
  .btn:active {
    transform: scale(0.95);
  }
}
</style>

