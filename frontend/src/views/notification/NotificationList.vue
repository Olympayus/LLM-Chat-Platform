<template>
  <div class="notification-list" style="max-width:800px;margin:20px auto;padding:0 20px">
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>通知中心</span>
          <el-button text type="primary" @click="markAllRead">全部已读</el-button>
        </div>
      </template>
      <el-tabs v-model="tab">
        <el-tab-pane label="全部" name="all">
          <div v-for="item in list" :key="item.id" class="notif-item" :class="{ unread: !item.is_read }" @click="markRead(item.id)">
            <div class="notif-header">
              <el-tag v-if="item.type === 'system'" size="small">系统</el-tag>
              <el-tag v-else-if="item.type === 'announcement'" type="warning" size="small">公告</el-tag>
              <el-tag v-else type="info" size="small">通知</el-tag>
              <span class="notif-title">{{ item.title }}</span>
              <span class="notif-time">{{ item.created_at }}</span>
            </div>
            <div class="notif-content">{{ item.content }}</div>
          </div>
          <div v-if="list.length === 0" style="text-align:center;color:#c0c4cc;padding:40px">暂无通知</div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../../api/request'

const tab = ref('all')
const list = ref<any[]>([])

onMounted(() => load())
async function load() {
  try {
    const res: any = await request.get('/api/v1/notifications', { params: { page: 1, page_size: 50 } })
    list.value = res.data?.items || res.items || []
  } catch { /* ignore */ }
}
async function markRead(id: number) {
  try { await request.put(`/api/v1/notifications/${id}/read`) } catch { /* ignore */ }
}
async function markAllRead() {
  try { await request.put('/api/v1/notifications/read-all'); ElMessage.success('已全部标记已读'); load() }
  catch { /* ignore */ }
}
</script>

<style scoped>
.notif-item {
  padding: 12px 0;
  cursor: pointer;
  border-bottom: 1px solid #f2f3f5;
}
.notif-item.unread { background: #f5f7fa; margin: 0 -12px; padding: 12px; border-radius: 6px; }
.notif-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.notif-title { font-size: 14px; font-weight: 500; color: #303133; flex: 1; }
.notif-time { font-size: 12px; color: #c0c4cc; white-space: nowrap; }
.notif-content { 