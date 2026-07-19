<template>
  <div class="chat-view">
    <!-- 左侧：会话列表 -->
    <div class="sidebar" :class="{ collapsed: !showSidebar }">
      <div class="sidebar-tabs">
        <el-button
          :type="activeTab === 'conversations' ? 'primary' : 'text'"
          size="small"
          @click="activeTab = 'conversations'"
        >
          会话
        </el-button>
        <el-button
          :type="activeTab === 'contacts' ? 'primary' : 'text'"
          size="small"
          @click="activeTab = 'contacts'"
        >
          联系人
        </el-button>
      </div>

      <!-- 会话列表 -->
      <ConversationList
        v-show="activeTab === 'conversations'"
        :conversations="store.conversations"
        :current-conversation="store.currentConversation"
        @select="handleSelectConversation"
      />
    </div>

    <!-- 中间：聊天窗口 -->
    <div class="main-area">
      <!-- 连接状态 -->
      <div v-if="!ws.isConnected.value" class="connection-bar">
        <el-alert
          title="WebSocket 未连接，尝试重连中..."
          type="warning"
          :closable="false"
          show-icon
        />
      </div>

      <ChatWindow
        :conversation="store.currentConversation"
        :messages="store.currentMessages"
        :is-connected="ws.isConnected.value"
        :current-user-id="currentUserId"
        @send-message="handleSendMessage"
        @upload-image="handleUploadImage"
        @upload-file="handleUploadFile"
      />
    </div>

    <!-- 右侧：群信息面板 -->
    <div class="right-panel" v-if="store.currentGroup && store.currentConversation?.type === 'group'">
      <GroupInfoPanel :group="store.currentGroup" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ConversationList from './ConversationList.vue'
import ChatWindow from './ChatWindow.vue'
import GroupInfoPanel from '../../components/im/GroupInfoPanel.vue'
import type { Conversation } from '../../types/im'
import { useIMStore } from '../../stores/im'
import { useWebSocket } from '../../composables/useWebSocket'

const store = useIMStore()
const ws = useWebSocket()

const showSidebar = ref(true)
const activeTab = ref<'conversations' | 'contacts'>('conversations')
// [F-01/A] 从 JWT Token 中提取用户ID
// 等待成员A提供JWT解析中间件后替换
function getUserIdFromToken(): number {
  const token = localStorage.getItem('token')
  if (!token) return 0
  try {
    // JWT payload 是 base64 编码的，取中间部分
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.sub || payload.user_id || 0
  } catch {
    return 0
  }
}
const currentUserId = ref(getUserIdFromToken())

onMounted(async () => {
  // 初始化 Token
  store.initToken()

  // 如果有 Token，连接 WebSocket
  if (store.token) {
    ws.connect(store.token)
  }

  // 加载会话列表
  await store.loadConversations()
})

function handleSelectConversation(conv: Conversation) {
  store.selectConversation(conv)

  // 加载历史消息
  store.loadHistory(conv.id)
}

function handleSendMessage(content: string, msgType: string) {
  if (!store.currentConversation) return

  const receiverId = store.currentConversation.type === 'private'
    ? store.currentConversation.id
    : store.currentConversation.id

  ws.send(store.currentConversation.type, receiverId, content, msgType)
}

async function handleUploadImage(file: File) {
  try {
    // [F-FL/F] 调用成员F的文件上传API
    const formData = new FormData()
    formData.append('file', file)
    const res: any = await (await import('../../api/request')).default.post('/api/v1/files/upload', formData)
    const url = res.data?.url || ''
    if (url && store.currentConversation) {
      ws.send(store.currentConversation.type, store.currentConversation.id, url, 'image')
    }
  } catch (e) {
    console.error('Upload image failed:', e)
  }
}

async function handleUploadFile(file: File) {
  try {
    // [F-FL/F] 调用成员F的文件上传API
    const formData = new FormData()
    formData.append('file', file)
    const res: any = await (await import('../../api/request')).default.post('/api/v1/files/upload', formData)
    const url = res.data?.url || ''
    if (url && store.currentConversation) {
      ws.send(store.currentConversation.type, store.currentConversation.id, url, 'file')
    }
  } catch (e) {
    console.error('Upload file failed:', e)
  }
}
</script>

<style scoped>
.chat-view {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 280px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-right: 1px solid #e4e7ed;
}

.sidebar-tabs {
  display: flex;
  padding: 8px 12px;
  gap: 4px;
  border-bottom: 1px solid #f2f3f5;
}

.main-area 