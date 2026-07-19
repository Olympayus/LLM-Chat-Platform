<template>
  <div class="audit-log-list">
    <el-card>
      <div class="table-header">
        <span class="title">审计日志</span>
        <el-button @click="loadLogs">刷新</el-button>
      </div>

      <el-form :model="searchForm" inline class="search-bar">
        <el-form-item label="操作类型">
          <el-input v-model="searchForm.action" placeholder="如 recall/delete" style="width:150px" clearable />
        </el-form-item>
        <el-form-item label="资源类型">
          <el-input v-model="searchForm.resource" placeholder="如 message/user" style="width:150px" clearable />
        </el-form-item>
        <el-form-item label="操作人ID">
          <el-input v-model="searchForm.user_id" placeholder="用户ID" style="width:120px" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="logList" v-loading="loading" stripe style="width:100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user_id" label="操作人ID" width="100" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="action" label="操作类型" width="120" />
        <el-table-column prop="resource" label="资源" width="120" />
        <el-table-column prop="detail" label="详情" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="IP" width="140" />
        <el-table-column prop="created_at" label="操作时间" width="180" />
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadLogs"
          @current-change="loadLogs"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import request from '../../api/request'

const loading = ref(false)
const logList = ref<any[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const searchForm = reactive({
  action: '', resource: '', user_id: '',
})

onMounted(() => loadLogs())

async function loadLogs() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (searchForm.action) params.action = searchForm.action
    if (searchForm.resource) params.resource = searchForm.resource
    if (searchForm.user_id) params.user_id = parseInt(searchForm.user_id)
    const res: any = await request.get('/api/v1/admin/audit-logs', { params })
    logList.value = res.data?.items || res.items || []
    total.value = res.data?.total || res.total || 0
  } finally { loading.value = false }
}

function handleSearch() { page.value = 1; loadLogs() }
</script>

<style scoped>