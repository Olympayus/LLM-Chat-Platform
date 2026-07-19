<template>
  <div class="compliance-view">
    <el-tabs v-model="activeTab">
      <!-- 敏感词管理 -->
      <el-tab-pane label="敏感词管理" name="sensitiveWords">
        <el-card>
          <div class="table-header">
            <span class="title">敏感词列表</span>
            <div>
              <el-button type="primary" @click="showWordDialog('create')">+ 添加敏感词</el-button>
            </div>
          </div>
          <el-table :data="wordList" v-loading="loadingWords" stripe style="width:100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="word" label="敏感词" min-width="200" />
            <el-table-column prop="level" label="级别" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.level === 'block'" type="danger" size="small">阻断</el-tag>
                <el-tag v-else type="warning" size="small">审计</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="分类" width="120" />
            <el-table-column label="启用" width="80">
              <template #default="{ row }">
                <el-switch v-model="row.is_enabled" @change="toggleWord(row)" />
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button text type="primary" size="small" @click="showWordDialog('edit', row)">编辑</el-button>
                <el-popconfirm title="确定删除此敏感词？" @confirm="handleDeleteWord(row.id)">
                  <template #reference>
                    <el-button text type="danger" size="small">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 群组管理 -->
      <el-tab-pane label="群组管理" name="groups">
        <el-card>
          <el-table :data="groupList" v-loading="loadingGroups" stripe style="width:100%">
            <el-table-column prop="id" label="群ID" width="80" />
            <el-table-column prop="group_name" label="群名称" min-width="180" />
            <el-table-column prop="owner_id" label="群主ID" width="100" />
            <el-table-column prop="member_count" label="成员数" width="80" />
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag v-if="row.is_muted_all" type="warning" size="small">全员禁言</el-tag>
                <el-tag v-else type="success" size="small">正常</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button text type="primary" size="small" @click="router.push(`/admin/compliance?groupId=${row.id}`)">详情</el-button>
                <el-popconfirm title="确定解散此群？" @confirm="handleDismissGroup(row.id)">
                  <template #reference>
                    <el-button text type="danger" size="small">解散</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 消息检索 -->
      <el-tab-pane label="消息检索" name="messageSearch">
        <el-card>
          <el-form :model="searchForm" inline>
            <el-form-item label="关键词">
              <el-input v-model="searchForm.keyword" placeholder="搜索消息内容" clearable />
            </el-form-item>
            <el-form-item label="发送人">
              <el-input v-model="searchForm.sender_id" placeholder="用户ID" style="width:120px" />
            </el-form-item>
            <el-form-item label="群组">
              <el-input v-model="searchForm.group_id" placeholder="群ID" style="width:120px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSearchMessages">搜索</el-button>
            </el-form-item>
          </el-form>

          <el-table :data="messageList" v-loading="loadingMessages" stripe style="width:100%">
            <el-table-column prop="message_id" label="消息ID" width="80" />
            <el-table-column prop="sender_id" label="发送人" width="80" />
            <el-table-column prop="content" label="内容" min-width="300" show-overflow-tooltip />
            <el-table-column prop="msg_type" label="类型" width="80" />
            <el-table-column prop="created_at" label="时间" width="180" />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-popconfirm title="确定撤回此消息？" @confirm="handleRecallMessage(row.message_id)">
                  <template #reference>
                    <el-button text type="danger" size="small">撤回</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 敏感词编辑弹窗 -->
    <el-dialog v-model="wordDialogVisible" :title="wordIsEdit ? '编辑敏感词' : '添加敏感词'" width="450px">
      <el-form ref="wordFormRef" :model="wordForm" :rules="wordRules" label-width="80px">
        <el-form-item label="敏感词" prop="word">
          <el-input v-model="wordForm.word" />
        </el-form-item>
        <el-form-item label="级别" prop="level">
          <el-select v-model="wordForm.level" style="width:100%">
            <el-option label="阻断 (block)" value="block" />
            <el-option label="审计 (audit)" value="audit" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="wordForm.category" placeholder="如：政治/广告/色情" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="wordDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingWord" @click="handleSaveWord">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import request from '../../api/request'

const router = useRouter()
const activeTab = ref('sensitiveWords')

// ===== 敏感词管理 =====
const loadingWords = ref(false)
const wordList = ref<any[]>([])
const wordDialogVisible = ref(false)
const wordIsEdit = ref(false)
const wordEditId = ref<number | null>(null)
const savingWord = ref(false)
const wordFormRef = ref<FormInstance>()

const wordForm = reactive({ word: '', level: 'block', category: '' })
const wordRules = { word: [{ required: true, message: '请输入敏感词', trigger: 'blur' }] }

onMounted(() => { loadWords(); loadGroups() })

async function loadWords() {
  loadingWords.value = true
  try {
    const res: any = await request.get('/api/v1/admin/sensitive-words')
    wordList.value = res.data?.items || res.data || res || []
  } finally { loadingWords.value = false }
}

function showWordDialog(action: string, row?: any) {
  wordIsEdit.value = action === 'edit'
  wordEditId.value = row?.id || null
  wordForm.word = row?.word || ''
  wordForm.level = row?.level || 'block'
  wordForm.category = row?.category || ''
  wordDialogVisible.value = true
}

async function handleSaveWord() {
  const valid = await wordFormRef.value?.validate().catch(() => false)
  if (!valid) return
  savingWord.value = true
  try {
    if (wordIsEdit.value && wordEditId.value) {
      await request.put(`/api/v1/admin/sensitive-words/${wordEditId.value}`, wordForm)
    } else {
      await request.post('/api/v1/admin/sensitive-words', wordForm)
    }
    ElMessage.success('保存成功')
    wordDialogVisible.value = false; loadWords()
  } catch (err: any) { ElMessage.error(err.message) }
  finally { savingWord.value = false }
}

async function handleDeleteWord(id: number) {
  try {
    await request.delete(`/api/v1/admin/sensitive-words/${id}`)
    ElMessage.success('删除成功'); loadWords()
  } catch (err: any) { ElMessage.error(err.message) }
}

async function toggleWord(row: any) {
  try {
    await request.put(`/api/v1/admin/sensitive-words/${row.id}`, { is_enabled: row.is_enabled })
  } catch { row.is_enabled = !row.is_enabled }
}

// ===== 群组管理 =====
const loadingGroups = ref(false)
const groupList = ref<any[]>([])

async function loadGroups() {
  loadingGroups.value = true
  try {
    const res: any = await request.get('/api/v1/admin/groups')
    groupList.value = res.data?.items || res.data || res || []
  } finally { loadingGroups.value = false }
}

async function handleDismissGroup(id: number) {
  try {
    await request.delete(`/api/v1/admin/groups/${id}`)
    ElMessage.success('已解散'); loadGroups()
  } catch (err: any) { ElMessage.error(err.message) }
}

// ===== 消息检索 =====
const loadingMessages = ref(false)
const messageList = ref<any[]>([])
const searchForm = reactive({ keyword: '', sender_id: '', group_id: '' })

async function handleSearchMessages() {
  loadingMessages.value = true
  try {
    const params: any = { page: 1, page_size: 20 }
    if (searchForm.keyword) params.keyword = searchForm.keyword
    if (searchForm.sender_id) params.sender_id = parseInt(searchForm.sender_id)
    if (searchForm.group_id) params.group_id = parseInt(searchForm.group_id)
    const res: any = await request.get('/api/v1/admin/messages/search', { params })
    messageList.value = res.data?.items || res.data?.data || res.data || []
  } finally { loadingMessages.value = false }
}

async function handleRecallMessage(messageId: number) {
  try {
    await request.p