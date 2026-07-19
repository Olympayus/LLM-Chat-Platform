<template>
  <div class="skill-list">
    <el-card>
      <div class="table-header">
        <span class="title">技能管理</span>
        <el-button type="primary" @click="showCreateDialog">+ 新建技能</el-button>
      </div>
      <el-table :data="skillList" v-loading="loading" stripe style="width:100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="技能名称" min-width="150" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.type === 'function_call' ? 'Function Call' : 'SKILL.md' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.is_enabled" type="success" size="small">启用</el-tag>
            <el-tag v-else type="info" size="small">停用</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
              <template #reference><el-button text type="danger" size="small">删除</el-button></template>
            </el-popconfirm>
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
const skillList = ref<any[]>([])

onMounted(() => loadSkills())

async function loadSkills() {
  loading.value = true
  try {
    const res: any = await request.get('/api/v1/skills')
    skillList.value = res.data?.items || res.data || res || []
  } finally { loading.value = false }
}

function showCreateDialog() { ElMessage.info('创建技能表单待完善') }
function handleEdit(row: any) { ElMessage.info('编辑技能表单待完善') }
async function handleDelete(id: number) {
  try { await request.delete(`/api/v1/skills/${id}`); ElMessage.success('已删除'); loadSkills() }
  catch (err: any) { ElMessage.error(err.message) }
}
</script>

<style scoped>
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.tab