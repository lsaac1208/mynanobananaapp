<template>
  <div class="system-settings">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="header-icon"><Setting /></el-icon>
            <span class="header-title">API配置管理</span>
          </div>
          <el-button type="primary" :icon="Plus" @click="handleAdd">
            新增配置
          </el-button>
        </div>
      </template>

      <!-- 配置组列表表格 -->
      <el-table :data="configGroups" stripe style="width: 100%">
        <el-table-column prop="name" label="配置名称" width="200" />
        <el-table-column prop="description" label="说明" min-width="200" />
        <el-table-column label="Base URL" min-width="250">
          <template #default="{ row }">
            {{ row.settings.openai_hk_base_url || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="API Key" width="150">
          <template #default="{ row }">
            <span class="masked-value">{{ row.settings.openai_hk_api_key || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              @change="handleToggle(row)"
              :disabled="row.is_active"
            />
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">{{ formatDate(row.updated_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :icon="Edit"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              @click="handleDelete(row)"
              :disabled="row.is_active"
              :title="row.is_active ? '已启用的配置不能删除' : '删除配置'"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- API连接测试 -->
    <el-card class="test-card">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon"><Link /></el-icon>
          <span class="header-title">API连接测试</span>
        </div>
      </template>
      <el-button
        type="success"
        :icon="Promotion"
        :loading="testLoading"
        @click="handleTestConnection"
      >
        测试当前激活的API配置
      </el-button>
    </el-card>

    <!-- 使用说明 -->
    <el-card class="info-card">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon"><InfoFilled /></el-icon>
          <span class="header-title">使用说明</span>
        </div>
      </template>
      <el-alert type="info" :closable="false">
        <template #default>
          <ul class="info-list">
            <li>✅ 每个配置包含 Base URL 和 API Key 两部分</li>
            <li>🔐 API Key使用加密存储，保证安全性</li>
            <li>⚡ 同一时间只能启用一个配置</li>
            <li>⚠️ 已启用的配置不能删除，请先禁用</li>
            <li>💡 修改后立即生效，无需重启服务</li>
          </ul>
        </template>
      </el-alert>
    </el-card>

    <!-- 新增配置对话框 -->
    <el-dialog
      v-model="addDialogVisible"
      title="新增API配置"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="addFormRef"
        :model="addForm"
        :rules="addFormRules"
        label-width="120px"
      >
        <el-form-item label="配置名称" prop="name">
          <el-input
            v-model="addForm.name"
            placeholder="例如：nano-banana-备用"
            clearable
          />
        </el-form-item>
        <el-form-item label="说明" prop="description">
          <el-input
            v-model="addForm.description"
            placeholder="配置用途说明"
            clearable
          />
        </el-form-item>
        <el-form-item label="Base URL" prop="base_url">
          <el-input
            v-model="addForm.base_url"
            placeholder="https://api.openai-hk.com"
            clearable
          />
        </el-form-item>
        <el-form-item label="API Key" prop="api_key">
          <el-input
            v-model="addForm.api_key"
            type="password"
            show-password
            placeholder="请输入API Key"
            clearable
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitAdd" :loading="addLoading">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑配置对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="`编辑配置: ${currentGroup?.name}`"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editFormRules"
        label-width="120px"
      >
        <el-form-item label="Base URL" prop="base_url">
          <el-input
            v-model="editForm.base_url"
            placeholder="https://api.openai-hk.com"
            clearable
          />
        </el-form-item>
        <el-form-item label="API Key" prop="api_key">
          <el-input
            v-model="editForm.api_key"
            type="password"
            show-password
            placeholder="留空则不修改"
            clearable
          />
          <span class="form-tip">提示：留空则不修改原API Key</span>
        </el-form-item>
        <el-form-item label="说明">
          <el-input
            v-model="editForm.description"
            placeholder="配置用途说明"
            clearable
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEdit" :loading="editLoading">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Setting,
  Edit,
  Delete,
  Link,
  InfoFilled,
  Promotion,
  Plus
} from '@element-plus/icons-vue'
import { adminApi } from '@/services/api'

// 配置组列表数据
const configGroups = ref<any[]>([])
const testLoading = ref(false)

// 新增配置
const addDialogVisible = ref(false)
const addFormRef = ref<FormInstance>()
const addLoading = ref(false)
const addForm = reactive({
  name: '',
  description: '',
  base_url: '',
  api_key: ''
})

const addFormRules: FormRules = {
  name: [
    { required: true, message: '请输入配置名称', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z0-9_\u4e00-\u9fa5-]+$/,
      message: '名称只能包含字母、数字、中文、下划线和连字符',
      trigger: 'blur'
    }
  ],
  base_url: [
    { required: true, message: '请输入Base URL', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ],
  api_key: [{ required: true, message: '请输入API Key', trigger: 'blur' }]
}

// 编辑配置
const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editLoading = ref(false)
const currentGroup = ref<any>(null)
const editForm = reactive({
  base_url: '',
  api_key: '',
  description: ''
})

const editFormRules: FormRules = {
  base_url: [
    { required: true, message: '请输入Base URL', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ]
}

// 加载所有配置组
const loadAllConfigGroups = async () => {
  try {
    const response = await adminApi.getAllConfigGroups()
    if (response.success && response.groups) {
      configGroups.value = response.groups
    } else {
      ElMessage.error(response.error || '加载配置列表失败')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载配置列表失败')
  }
}

// 打开新增对话框
const handleAdd = () => {
  addForm.name = ''
  addForm.description = ''
  addForm.base_url = ''
  addForm.api_key = ''
  addDialogVisible.value = true
}

// 提交新增
const submitAdd = async () => {
  if (!addFormRef.value) return

  await addFormRef.value.validate(async (valid) => {
    if (!valid) return

    addLoading.value = true
    try {
      const response = await adminApi.createConfigGroup(
        addForm.name,
        addForm.description,
        addForm.base_url,
        addForm.api_key
      )

      if (response.success) {
        ElMessage.success(response.message || '配置创建成功')
        addDialogVisible.value = false
        await loadAllConfigGroups()
      } else {
        ElMessage.error(response.error || '配置创建失败')
      }
    } catch (error: any) {
      ElMessage.error(error.message || '配置创建失败')
    } finally {
      addLoading.value = false
    }
  })
}

// 打开编辑对话框
const handleEdit = (row: any) => {
  currentGroup.value = row
  editForm.base_url = row.settings.openai_hk_base_url || ''
  editForm.api_key = ''
  editForm.description = row.description
  editDialogVisible.value = true
}

// 提交编辑
const submitEdit = async () => {
  if (!editFormRef.value) return

  await editFormRef.value.validate(async (valid) => {
    if (!valid) return

    editLoading.value = true
    try {
      const updateData: any = {
        base_url: editForm.base_url,
        description: editForm.description
      }

      // 只有输入了新密钥才更新
      if (editForm.api_key) {
        updateData.api_key = editForm.api_key
      }

      const response = await adminApi.updateConfigGroup(
        currentGroup.value.id,
        updateData
      )

      if (response.success) {
        ElMessage.success(response.message || '配置更新成功')
        editDialogVisible.value = false
        await loadAllConfigGroups()
      } else {
        ElMessage.error(response.error || '配置更新失败')
      }
    } catch (error: any) {
      ElMessage.error(error.message || '配置更新失败')
    } finally {
      editLoading.value = false
    }
  })
}

// 切换启用/禁用
const handleToggle = async (row: any) => {
  const action = row.is_active ? '禁用' : '启用'

  try {
    await ElMessageBox.confirm(
      `确定要${action}配置 "${row.name}" 吗？${!row.is_active ? '启用后将自动禁用其他配置。' : ''}`,
      `${action}确认`,
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await adminApi.toggleConfigGroup(row.id)
    if (response.success) {
      ElMessage.success(response.message || `配置${action}成功`)
      await loadAllConfigGroups()
    } else {
      ElMessage.error(response.error || `配置${action}失败`)
      // 恢复原状态
      row.is_active = !row.is_active
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || `配置${action}失败`)
    }
    // 恢复原状态
    row.is_active = !row.is_active
  }
}

// 删除配置
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除配置 "${row.name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await adminApi.deleteConfigGroup(row.id)
    if (response.success) {
      ElMessage.success(response.message || '配置删除成功')
      await loadAllConfigGroups()
    } else {
      ElMessage.error(response.error || '配置删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '配置删除失败')
    }
  }
}

// 测试API连接
const handleTestConnection = async () => {
  testLoading.value = true
  try {
    const response = await adminApi.testApiConnection()
    if (response.success) {
      ElMessage.success(response.message || 'API连接测试成功')
    } else {
      ElMessage.error(response.error || 'API连接测试失败')
    }
  } catch (error: any) {
    ElMessage.error(error.message || 'API连接测试失败')
  } finally {
    testLoading.value = false
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 页面加载时获取配置列表
onMounted(() => {
  loadAllConfigGroups()
})
</script>

<style scoped>
.system-settings {
  padding: 20px;
}

.settings-card,
.test-card,
.info-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  font-size: 20px;
}

.header-title {
  font-size: 16px;
  font-weight: 500;
}

.masked-value {
  color: #909399;
  font-family: monospace;
}

.info-list {
  margin: 0;
  padding-left: 20px;
  line-height: 2;
}

.form-tip {
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}
</style>