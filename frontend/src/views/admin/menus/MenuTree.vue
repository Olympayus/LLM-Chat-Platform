<template>
  <div class="menu-tree">
    <el-card>
      <div class="table-header">
        <span class="title">菜单/权限管理</span>
        <el-button type="primary" @click="showCreateDialog">+ 新增菜单</el-button>
      </div>

      <el-table :data="menuTree" v-loading="loading" stripe row-key="id" default-expand-all :tree-props="{ children: 'children' }">
        <el-table-column prop="name" label="菜单名称" min-width="180" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.type === 1" size="small">目录</el-tag>
            <el-tag v-else-if="row.type === 2" type="primary" size="small">菜单</el-tag>
            <el-tag v-else type="warning" size="small">按钮</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="permission_code" label="权限标识" min-width="180" />
        <el-table-column prop="path" label="路由路径" min-width="180" />
        <el-table-column prop="icon" label="图标" width="80" />
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="showEdit(row)">编辑</el-button>
            <el-popconfirm title="确定删除此菜单？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button text type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑菜单' : '新增菜单'" width="550px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="菜单类型" prop="type">
          <el-radio-group v-model="form.type">
            <el-radio :value="1">目录</el-radio>
            <el-radio :value="2">菜单</el-radio>
            <el-radio :value="3">按钮</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="菜单名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="父级菜单">
          <el-tree-select v-model="form.parent_id" :data="menuTree" :props="{ label: 'name' }" placeholder="顶级菜单" clearable />
        </el-form-item>
        <el-form-item label="路由路径" v-if="form.type !== 3">
          <el-input v-model="form.path" placeholder="如 /admin/users" />
        </el-form-item>
        <el-form-item label="权限标识">
          <el-input v-model="form.permission_code" placeholder="如 sys:user:list" />
        </el-form-item>
        <el-form-item label="图标" v-if="form.type !== 3">
          <el-input v-model="form.icon" placeholder="Element Plus 图标名" />
        </el-form-item>
        <el-form-item label="排序号">
          <el-input-number v-model="form.sort_order" :min="0" />
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
import { getMenuTree, createMenu, updateMenu, deleteMenu } from '../../../api/user'

const loading = ref(false)
const saving = ref(false)
const menuTree = ref<any[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const form = reactive({
  name: '', type: 2, parent_id: null as number | null,
  path: '', permission_code: '', icon: '', sort_order: 0,
})
const rules = {
  name: [{ required: true, message: '请输入菜单名称', trigger: 'blur' }],
}

onMounted(() => loadTree())

async function loadTree() {
  loading.value = true
  try {
    const res: any = await getMenuTree()
    menuTree.value = res.data || res || []
  } finally {
    loading.value = false
  }
}

function showCreateDialog() {
  isEdit.value = false; editId.value = null
  form.name = ''; form.type = 2; form.parent_id = null
  form.path = ''; form.permission_code = ''; form.icon = ''; form.sort_order = 0
  dialogVisible.value = true
}

function showEdit(row: any) {
  isEdit.value = true; editId.value = row.id
  form.name = row.name; form.type = row.type; form.parent_id = row.parent_id || null
  form.path = row.path || ''; form.permission_code = row.permission_code || ''
  form.icon = row.icon || ''; form.sort_order = row.sort_order || 0
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value && editId.value) {
      await updateMenu(editId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createMenu(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false; loadTree()
  } catch (err: any) {
    ElMessage.error(err.message || '操作失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await deleteMenu(id)
    ElMessage.success('删除成功'); loadTree()
  } catch (err: any) {
    ElMessage.error(err.message || '删除失败')
  }
}
</script>

<style scoped>
.table-header {
  display: flex;