<template>
  <div class="employee-list">
    <el-card>
      <div class="table-header">
        <span class="title">数字员工管理</span>
        <el-button type="primary">+ 新建数字员工</el-button>
      </div>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column prop="role_description" label="角色描述" min-width="250" show-overflow-tooltip />
        <el-table-column label="状态" width="80">
          <template #default="{ row }"><el-tag v-if="row.is_enabled" type="success" size="small">启用</el-tag><el-tag v-else type="info" size="small">停用</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button text type="primary" size="small">编辑</el-button>
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
  try { const res: any = await request.get('/api/v1/digital-employees'); list.value = res.data || res || [] }
  finally { loading.value = false }
}
async function handleDelete(id: number) {
  try { await request.delete(`/api/v1/digital-employees/${id}`); ElMessage.success('已删除'); load() }
  catch (err: any) { ElMessage.error(err.message) }
}
</script>
<style scoped>
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.table-header .title { 