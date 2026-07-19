<template>
  <div class="dept-tree">
    <el-card>
      <div class="table-header">
        <span class="title">部门管理</span>
        <el-button type="primary" @click="showCreateDialog">+ 新增部门</el-button>
      </div>

      <el-tree
        :data="deptTree"
        :props="treeProps"
        node-key="id"
        default-expand-all
        :expand-on-click-node="false"
      >
        <template #default="{ node, data }">
          <span class="tree-node">
            <span>{{ node.label }}</span>
            <span class="tree-actions">
              <el-button text type="primary" size="small" @click="showEdit(data)">编辑</el-button>
              <el-popconfirm title="确定删除此部门？" @confirm="handleDelete(data.id)">
                <template #reference>
                  <el-button text type="danger" size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </span>
          </span>
        </template>
      </el-tree>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑部门' : '新增部门'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="上级部门">
          <el-tree-select v-model="form.parent_id" :data="deptTree" :props="treeProps" placeholder="顶级部门" clearable allow-create filterable />
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
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { getDeptTree, createDept, updateDept, deleteDept } from '../../../api/user'

const loading = ref(false)
const saving = ref(false)
const deptTree = ref<any[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const treeProps = { children: 'children', label: 'name' }

const form = ref({ name: '', parent_id: null as number | null, sort_order: 0 })
const rules = { name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }] }

onMounted(() => loadTree())

async function loadTree() {
  loading.value = true
  try {
    const res: any = await getDeptTree()
    deptTree.value = res.data || res || []
  } finally {
    loading.value = false
  }
}

function showCreateDialog() {
  isEdit.value = false; editId.value = null
  form.value = { name: '', parent_id: null, sort_order: 0 }
  dialogVisible.value = true
}

function showEdit(data: any) {
  isEdit.value = true; editId.value = data.id
  form.value = { name: data.name, parent_id: data.parent_id || null, sort_order: data.sort_order || 0 }
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value && editId.value) {
      await updateDept(editId.value, form.value)
      ElMessage.success('更新成功')
    } else {
      await createDept(form.value)
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
    await deleteDept(id)
    ElMessage.success('删除成功'); loadTree()
  } catch (err: any) {
    ElMessage.error(err.message || '删除失败')
  }
}
</script>

<style scoped>
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.table-header .title { font-size: 16px; font-weight: 600; }
.tree-node { flex: 1; display: f