<template>
  <div class="role-list">
    <el-card>
      <div class="table-header">
        <span class="title">角色管理</span>
        <el-button type="primary" @click="showCreateDialog">+ 新增角色</el-button>
      </div>

      <el-table :data="roleList" v-loading="loading" stripe style="width:100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="角色名称" min-width="150" />
        <el-table-column prop="code" label="角色编码" min-width="150" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="showEdit(row)">编辑</el-button>
            <el-popconfirm title="确定删除此角色？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button text type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑角色' : '新增角色'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input v-model="form.code" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
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
import { getRoleList, createRole, updateRole, deleteRole } from '../../../api/user'

const loading = ref(false)
const saving = ref(false)
const roleList = ref<any[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const form = reactive({ name: '', code: '', description: '' })
const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }],
}

onMounted(() => loadRoles())

async function loadRoles() {
  loading.value = true
  try {
    const res: any = await getRoleList()
    roleList.value = res.data || res || []
  } finally { loading.value = false }
}

function showCreateDialog() {
  isEdit.value = false; editId.value = null
  form.name = ''; form.code = ''; form.description = ''
  dialogVisible.value = true
}

function showEdit(row: any) {
  isEdit.value = true; editId.value = row.id
  form.name = row.name; form.code = row.code; form.description = row.description || ''
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value && editId.value) {
      await updateRole(editId.value, { name: form.name, description: form.description })
      ElMessage.success('更新成功')
    } else {
      await createRole({ name: form.name, code: form.code, description: form.description })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false; loadRoles()
  } catch (err: any) { ElMessage.error(err.message) }
  finally { saving.value = false }
}

async function handleDelete(id: number) {
  try { await deleteRole(id); ElMessage.success('删除成功'); loadRoles() }
  catch (err: any) { ElMessage.error(err.message) }
}
</script>

<style scoped>
.table-header { display: flex; justify-content: space-between; 