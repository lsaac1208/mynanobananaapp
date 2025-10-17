<template>
  <el-card class="mode-selector glass-card">
    <template #header>
      <div class="mode-header">
        <span>选择生成模式</span>
        <el-tag type="info" size="small">
          {{ modeDescription }}
        </el-tag>
      </div>
    </template>
    <el-radio-group v-model="selectedMode" size="large" @change="handleModeChange">
      <el-radio-button value="text-to-image">📝 文生图</el-radio-button>
      <el-radio-button value="image-to-image">🎨 图生图</el-radio-button>
    </el-radio-group>
  </el-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

// Props
const props = defineProps<{
  modelValue: 'text-to-image' | 'image-to-image'
}>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: 'text-to-image' | 'image-to-image']
}>()

// Local state
const selectedMode = ref(props.modelValue)

// Computed
const modeDescription = computed(() => {
  return selectedMode.value === 'text-to-image'
    ? '使用文字描述生成图片'
    : '使用参考图片+文字描述生成新图片'
})

// Methods
const handleModeChange = (value: 'text-to-image' | 'image-to-image') => {
  emit('update:modelValue', value)
}
</script>

<style scoped>
.mode-selector {
  margin-bottom: var(--spacing-lg);
}

.mode-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-radio-group {
  width: 100%;
  display: flex;
  gap: var(--spacing-md);
}

.el-radio-button {
  flex: 1;
}

:deep(.el-radio-button__inner) {
  width: 100%;
  padding: 12px 20px;
  font-size: 16px;
}

@media (max-width: 768px) {
  .el-radio-group {
    flex-direction: column;
  }
  
  :deep(.el-radio-button__inner) {
    min-height: 44px;
  }
}
</style>

