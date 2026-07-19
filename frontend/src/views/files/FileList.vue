<template>
  <div class="file-list" style="max-width:1000px;margin:20px auto;padding:0 20px">
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>文件管理</span>
          <el-upload :action="uploadUrl" :headers="headers" :on-success="handleUploadSuccess" :show-file-list="false" :multiple="true">
            <el-button type="primary">上传文件</el-button>
          </el-upload>
        </div>
      </template>

      <el-table :data="list" v-loading="loading" stripe style="width:100%">
        <el-table-column prop="original_name" label="文件名" min-width="250" show-overflow-tooltip />
        <el-table-column prop="file_size" label="大小" width="100">
          <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column prop="file_type" label="类型" width="100">
          <template #default="{ row }"><el-tag size="small">{{ row.file_type?.split('/')[0] || '未知' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="180" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="handleDownload(row)">下载</el-button>
            <el-popconfirm title="确定删除此文件？" @confirm="handleDelete(row.id)">
              <template #reference><el-button text type="danger" size="small">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" layout="prev, pager, next" @current-change="load" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../../api/request'

const loading = ref(false)
const list = ref<any[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const uploadUrl = '/api/v1/files/upload'
const headers = computed(() => ({ Authorization: `Bearer ${localStorage.getItem('token')}` }))

onMounted(() => load())

async function load() {
  loading.value = true
  try {
    const res: any = await request.get('/api/v1/files', { params: { page: page.value, page_size: pageSize.value } })
    list.value = res.data?.items || res.items || []
    total.value = res.data?.total || res.total || 0
  } finally { loading.value = false }
}

function formatSize(bytes: number) {
  if (!bytes) return '0B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  while (bytes >= 1024 && i < units.length - 1) { bytes /= 1024; i++ }
  return `${bytes.toFixed(1)} ${units[i]}`
}

function handleUploadSuccess(res: any) {
  if (res?.code === 0 || res?.data) { ElMessage.success('上传成功'); load() }
  else { ElMessage.error(res?.message || '上传失败') }
}

function handleDownload(row: any) {
  if (row.id) { window.open(`/api/v1/files/${row.id}/download`, '_blank') }
}

async function handleDelete(id: number) {
  try { await request.delete(`/api/v1/files/${id}`); ElMessage.success('已删除'); load() }
  catch (err: any) { ElMessage.error(err.message) }
}
</script>

<style scoped>