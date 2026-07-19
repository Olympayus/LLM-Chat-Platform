<template>
  <div class="crawler-list">
    <el-card>
      <div class="table-header">
        <span class="title">爬虫任务管理</span>
        <el-button type="primary">+ 新建任务</el-button>
      </div>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="任务名称" min-width="180" />
        <el-table-column prop="request_url" label="请求地址" min-width="250" show-overflow-tooltip />
        <el-table-column label="调度" width="120">
          <template #default="{ row }"><el-tag v-if="row.schedule_cron" size="small">{{ row.schedule_cron }}</el-tag><span v-else style="color:#909399">手动</span></template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }"><el-tag v-if="row.is_enabled" type="success" size="small">启用</el-tag><el-tag v-else type="info" size="small">停用</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button text type="primary" size="small">编辑</el-button>
            <el-button text type="success" size="small" @click="handleRun(row.id)">执行</el-button>
            <el-button text type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../../api/request'

const loading = ref(false)
const list = ref<any[]>([])
onMounted(() => load())

async function load() {
  loading.value = true
  try { const res: any = await request.get('/api/v1/crawlers'); list.value = res.data?.items || res.data || res || [] }
  finally { loading.value = false }
}
async function handleRun(id: number) {
  try { await request.post(`/api/v1/crawlers/${id}/run`); ElMessage.success('已触发执行') }
  catch (err: any) { ElMessage.error(err.message) }
}
async function handleDelete(id: number) {
  try { await request.delete(`/api/v1/crawlers/${id}`); ElMessage.success('已删除'); load() }
  catch (err: any) { ElMessage.error(err.message) }
}
</script>
<style scoped>
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.table-header 