<template>
  <div class="model-list">
    <el-card>
      <div class="table-header">
        <span class="title">模型管理</span>
        <el-button type="primary" @click="showCreateDialog">+ 新增模型</el-button>
      </div>

      <el-table :data="modelList" v-loading="loading" stripe style="width:100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="display_name" label="展示名称" min-width="150" />
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag>{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="model_id" label="模型ID" min-width="180" />
        <el-table-column prop="base_url" label="API地址" min-width="200" show-overflow-tooltip />
        <el-table-column label="默认" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.is_default" type="success" size="small">默认</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.is_enabled" type="success" size="small">启用</el-tag>
            <el-tag v-else type="info" size="small">停用</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="showEdit(row)">编辑</el-button>
            <el-button text type="success" size="small" @click="handleSetDefault(row)" v-if="!row.is_default">设为默认</el-button>
            <el-popconfirm title="确定删除此模型？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button text type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑模型' : '新增模型'" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="展示名称" prop="display_name">
          <el-input v-model="form.display_name" />
        </el-form-item>
        <el-form-item label="模型分类" prop="category">
          <el-select v-model="form.category" style="width:100%">
            <el-option label="文本 (text)" value="text" />
            <el-option label="图片 (image)" value="image" />
            <el-option label="视频 (video)" value="video" />
            <el-option label="向量 (embedding)" value="embedding" />
          </el-select>
        </el-form-item>
        <el-form-item label="API地址" prop="base_url">
          <el-input v-model="form.base_url" placeholder="https://dashscope.aliyuncs.com/compatible-mode/v1" />
        </el-form-item>
        <el-form-item label="API Key" prop="api_key">
          <el-input v-model="form.api_key" type="password" show-password />
        </el-form-item>
        <el-form-item label="模型ID" prop="model_id">
          <el-input v-model="form.model_id" placeholder="qwen-plus" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="温度">
              <el-slider v-model="form.temperature" :min="0" :max="2" :step="0.01" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最大Token">
              <el-input-number v-model="form.max_tokens" :min="1" :max="128000" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="启用">
          <el-switch v-model="form.is_enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import request from '../../../api/request'

const loading = ref(false)
const saving = ref(false)
const modelList = ref<any[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const form = reactive({
  display_name: '', category: 'text', base_url: '', api_key: '',
  model_id: '', temperature: 0.7, max_tokens: 4096, is_enabled: true,
})
const rules = {
  display_name: [{ required: true, message: '请输入展示名称', trigger: 'blur' }],
  base_url: [{ required: true, message: '请输入API地址', trigger: 'blur' }],
  api_key: [{ required: true, message: '请输入API Key', trigger: 'blur' }],
  model_id: [{ required: true, message: '请输入模型ID', trigger: 'blur' }],
}

onMounted(() => loadModels())

async function loadModels() {
  loading.value = true
  try {
    const res: any = await request.get('/api/v1/models')
    modelList.value = res.data?.items || res.data || res || []
  } finally {
    loading.value = false
  }
}

function showCreateDialog() {
  isEdit.value = false; editId.value = null
  form.display_name = ''; form.category = 'text'; form.base_url = ''; form.api_key = ''
  form.model_id = ''; form.temperature = 0.7; form.max_tokens = 4096; form.is_enabled = true
  dialogVisible.value = true
}

function showEdit(row: any) {
  isEdit.value = true; editId.value = row.id
  form.display_name = row.display_name; form.category = row.category; form.base_url = row.base_url
  form.api_key = row.api_key || ''; form.model_id = row.model_id
  form.temperature = row.temperature ?? 0.7; form.max_tokens = row.max_tokens ?? 4096
  form.is_enabled = row.is_enabled !== 0
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value && editId.value) {
      await request.put(`/api/v1/models/${editId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await request.post('/api/v1/models', form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false; loadModels()
  } catch (err: any) {
    ElMessage.error(err.message || '操作失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await request.delete(`/api/v1/models/${id}`)
    ElMessage.success('删除成功'); loadModels()
  } catch (err: any) {
    ElMessage.error(err.message || '删除失败')
  }
}

async function handleSetDefault(row: any) {
  try {
    await request.put(`/api/v1/models/${row.id}/default`)
    ElMessage.success('已设为默认模型'); loadModels()
  } catch (err: any) {
    ElMessage.error(err.message || '操作失败')
  }
}
</script>

<style scoped>
.