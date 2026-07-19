<template>
  <div class="nl2sql-view">
    <el-row :gutter="16">
      <!-- 左侧：问数区域 -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>智能问数</span>
          </template>

          <!-- 对话区域 -->
          <div class="chat-area" ref="chatArea">
            <div v-for="(item, idx) in chatHistory" :key="idx" class="chat-item">
              <!-- 用户问题 -->
              <div class="question">
                <el-avatar :size="32" style="background:#409eff">我</el-avatar>
                <div class="bubble question-bubble">{{ item.question }}</div>
              </div>
              <!-- AI 回答 -->
              <div class="answer" v-if="item.answer">
                <el-avatar :size="32" style="background:#67c23a">AI</el-avatar>
                <div class="bubble answer-bubble">
                  <div v-if="item.sql" class="sql-block">
                    <div class="sql-label">生成的 SQL：</div>
                    <pre class="sql-code">{{ item.sql }}</pre>
                  </div>
                  <div v-if="item.data" class="result-table">
                    <el-table :data="item.data" stripe border max-height="300" size="small" v-if="item.data.length > 0">
                      <el-table-column v-for="col in item.columns" :key="col" :prop="col" :label="col" min-width="100" show-overflow-tooltip />
                    </el-table>
                    <div v-else class="empty-result">无查询结果</div>
                  </div>
                  <div class="answer-text">{{ item.answer }}</div>
                </div>
              </div>
            </div>
            <div v-if="loading" class="loading-tip">
              <el-icon class="is-loading"><Loading /></el-icon> AI 正在思考...
            </div>
          </div>

          <!-- 输入框 -->
          <div class="input-area">
            <el-input
              v-model="question"
              type="textarea"
              :rows="3"
              placeholder="输入你的数据查询问题，例如：查询上个月每个部门的销售额"
              :disabled="loading"
              @keydown.ctrl.enter="handleAsk"
            />
            <div class="input-actions">
              <el-button type="primary" :loading="loading" :disabled="!question.trim()" @click="handleAsk">
                {{ loading ? '查询中...' : '发送' }}
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：历史记录 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>历史查询</span>
          </template>
          <div v-if="historyList.length === 0" class="empty-tip">暂无查询记录</div>
          <div v-for="item in historyList" :key="item.id" class="history-item" @click="loadHistory(item)">
            <div class="history-question">{{ item.question }}</div>
            <div class="history-time">{{ item.created_at }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import request from '../../api/request'

const question = ref('')
const loading = ref(false)
const chatArea = ref<HTMLElement>()
const chatHistory = ref<Array<{ question: string; sql?: string; data?: any[]; columns?: string[]; answer?: string }>>([])
const historyList = ref<Array<{ id: number; question: string; created_at: string }>>([])

onMounted(() => loadHistoryList())

async function loadHistoryList() {
  try {
    const res: any = await request.get('/api/v1/nl2sql/history', { params: { page: 1, page_size: 20 } })
    historyList.value = res.data?.items || res.items || []
  } catch { /* ignore */ }
}

async function handleAsk() {
  const text = question.value.trim()
  if (!text || loading.value) return

  chatHistory.value.push({ question: text })
  question.value = ''
  loading.value = true

  try {
    const res: any = await request.post('/api/v1/nl2sql/ask', { question: text })
    const data = res.data || res
    const last = chatHistory.value[chatHistory.value.length - 1]
    last.sql = data.generated_sql || data.sql || ''
    last.data = data.result || data.data || []
    last.columns = data.columns || (last.data.length > 0 ? Object.keys(last.data[0]) : [])
    last.answer = data.interpretation || data.answer || '查询完成'
  } catch (err: any) {
    const last = chatHistory.value[chatHistory.value.length - 1]
    last.answer = err.message || '查询失败，请重试'
  } finally {
    loading.value = false
    setTimeout(() => {
      chatArea.value?.scrollTo({ top: chatArea.value.scrollHeight, behavior: 'smooth' })
    }, 100)
  }
}

function loadHistory(item: any) {
  question.value = item.question
}
</script>

<style scoped>
.nl2sql-view { padding: 20px; }

.chat-area {
  height: 400px;
  overflow-y: auto;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 16px;
}

.chat-item { margin-bottom: 20px; }
.question, .answer { display: flex; gap: 10px; margin-bottom: 8px; }
.question { flex-direction: row-reverse; }
.bubble {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
}
.question-bubble { background: #409eff; color: white; }
.answer-bubble { background: white; border: 1px solid #e4e7ed; }

.sql-block {
  background: #f5f7fa;
  padding: 8px;
  border-radius: 6px;
  margin-bottom: 8px;
}
.sql-label { font-size: 12px; color: #909399; margin-bottom: 4px; }
.sql-code {
  margin: 0;
  font-size: 13px;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-all;
}

.answer-text { margin-top: 8px; color: #606266; }

.empty-result { text-align: center; color: #c0c4cc; padding: 20px; font-size: 14px; }

.loading-tip {
  text-align: center;
  color: #909399;
  padding: 16px;
}

.input-area {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.input-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.empty-tip { text-align: center; color: #c0c4cc; padding: 32px; font-size: 14px; }

.history-item {
  padding: 10px 0;
  cursor: pointer;
  border-bottom: 1px solid #f2f3f5;
}
.history-item:last-child { border-bottom: none; }
.hist