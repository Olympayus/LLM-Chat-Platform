<template>
  <div class="user-list">
    <!-- 搜索栏 - compact -->
    <div class="search-section">
      <el-form :model="searchForm" inline size="small">
        <el-form-item label="用户名">
          <el-input v-model="searchForm.keyword" placeholder="搜索..." clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable style="width:110px">
            <el-option label="正常" :value="1" />
            <el-option label="禁用" :value="0" />
            <el-option label="封号" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 表格 -->
    <div class="table-container">
      <div class="table-toolbar">
        <span class="toolbar-title">用户列表</span>
        <div class="toolbar-actions">
          <el-button size="small" @click="loadUsers">刷新</el-button>
          <el-button size="small" type="primary" @click="showCreateDialog">+ 新增</el-button>
        </div>
      </div>

      <el-table :data="userList" v-loading="loading" stripe style="width:100%" @selection-change="onSelectionChange">
        <el-table-column type="selection" width="40" />
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="real_name" label="姓名" width="120" show-overflow-tooltip />
        <el-table-column prop="email" label="邮箱" min-width="160" show-overflow-tooltip />
        <el-table-column prop="dept_name" label="部门" width="120" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <span class="status-badge" :class="`status-${row.status}`">
              <span class="status-dot"></span>
              {{ row.status === 1 ? '正常' : row.status === 0 ? '禁用' : '封号' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" @click="showEdit(row)">编辑</el-button>
            <el-button text size="small" :type="row.status === 1 ? 'warning' : 'success'" @click="handleToggleStatus(row)">
              {{ row.status === 1 ? '禁用' : '启用' }}
            </el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button text type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="table-footer">
        <span class="selected-info" v-if="selectedIds.length > 0">已选 {{ selectedIds.length }} 项</span>
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          small
          @size-change="loadUsers"
          @current-change="loadUsers"
        />
      </div>
    </div>

    <!-- 创建/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="500px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px" size="small">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="真实姓名">
          <el-input v-model="form.real_name" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role_ids" multiple style="width:100%">
            <el-option v-for="r in roleOptions" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
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
import { getUserList, createUser, updateUser, deleteUser, setUserStatus } from '../../../api/user'

const loading = ref(false)
const saving = ref(false)
const userList = ref<any[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const selectedIds = ref<number[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const roleOptions = ref<any[]>([])

const searchForm = reactive({ keyword: '', status: '' })
const form = reactive({ username: '', password: '', real_name: '', email: '', role_ids: [] as number[] })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

onMounted(() => loadUsers())

async function loadUsers() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (searchForm.keyword) params.keyword = searchForm.keyword
    if (searchForm.status !== '') params.status = searchForm.status
    const res: any = await getUserList(params)
    userList.value = res.data?.items || res.items || []
    total.value = res.data?.total || res.total || 0
  } finally { loading.value = false }
}

function onSelectionChange(rows: any[]) { selectedIds.value = rows.map((r: any) => r.id) }
function handleSearch() { page.value = 1; loadUsers() }
function resetSearch() { searchForm.keyword = ''; searchForm.status = ''; page.value = 1; loadUsers() }

function showCreateDialog() {
  isEdit.value = false; editId.value = null
  form.username = ''; form.password = ''; form.real_name = ''; form.email = ''; form.role_ids = []
  dialogVisible.value = true
}

function showEdit(row: any) {
  isEdit.value = true; editId.value = row.id
  form.username = row.username; form.password = ''; form.real_name = row.real_name || ''
  form.email = row.email || ''; form.role_ids = row.role_ids || []
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value && editId.value) {
      await updateUser(editId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createUser(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false; loadUsers()
  } catch (err: any) { ElMessage.error(err.message || '操作失败') }
  finally { saving.value = false }
}

async function handleDelete(id: number) {
  try { await deleteUser(id); ElMessage.success('删除成功'); loadUsers() }
  catch (err: any) { ElMessage.error(err.message) }
}

async function handleToggleStatus(row: any) {
  try {
    await setUserStatus(row.id, row.status === 1 ? 0 : 1)
    ElMessage.success('状态已更新'); loadUsers()
  } catch (err: any) { ElMessage.error(err.message) }
}
</script>

<style scoped>
.user-list { padding: 24px; }

/* Search - compact */
.search-section {
  background: var(--color-bg-white);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  padding: 16px 20px;
  margin-bottom: 16px;
}
.search-section :deep(.el-form-item) { margin-bottom: 0; }

/* Table container */
.table-container {
  background: var(--color-bg-white);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
}
.table-toolbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px 0;
}
.toolbar-title { font-size: 15px; font-weight: 600; color: var(--color-text-primary); }
.toolbar-actions { display: flex; gap: 8px; }

/* Status badge - dot style from Linear */
.status-badge {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 13px;
}
.status-dot {
  width: 7px; height: 7px; border-radius: 50%;
}
.status-1 .status-dot { background: #10B981; }
.status-0 .status-dot { background: #94A3B8; }
.status-2 .status-dot { background: #EF4444; }
.status-1 { color: #059669; }
.status-0 { color: #64748B; }
.status-2 { color: #DC2626; }

/* Footer */
.table-footer {
  display: flex; justify-content: space-between; align-items: