<template>
  <div class="chat-window">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <div class="chat-header-info">
        <span class="chat-title">{{ conversation?.name || '选择会话' }}</span>
        <span v-if="conversation?.isOnline === true" class="online-status">在线</span>
        <span v-else-if="conversation?.isOnline === false" class="offline-status">离线</span>
      </div>
    </div>

    <!-- 消息列表 -->
    <div ref="messageListRef" class="message-list">
      <div v-if="messages.length === 0" class="empty-messages">
        <el-empty description="暂无消息，开始聊天吧" />
      </div>
      <MessageBubble
        v-for="msg in messages"
        :key="msg.id"
        :message="msg"
        :is-own="msg.senderId === currentUserId"
      />
    </div>

    <!-- 消息输入 -->
    <div v-if="conversation" class="chat-input">
      <MessageInput
        :disabled="!isConnected || isMuted"
        @send="handleSend"
        @upload-image="handleUploadImage"
        @upload-file="handleUploadFile"
      />
    </div>

    <!-- 未选择会话 -->
    <div v-else class="no-conversation">
      <el-empty description="请选择一个会话" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import MessageBubble from '../../components/im/MessageBubble.vue'
import MessageInput from '../../components/im/MessageInput.vue'
import type { Conversation, Message } from '../../types/im'
import { useIMStore } from '../../stores/im'

const props = defineProps<{
  conversation: Conversation | null
  messages: Message[]
  isConnected: boolean
  isMuted?: boolean
  currentUserId: number
}>()

const emit = defineEmits<{
  sendMessage: [content: string, msgType: string]
  uploadImage: [file: File]
  uploadFile: [file: File]
}>()

const messageListRef = ref<HTMLDivElement>()

// 监听消息变化，自动滚到底部
watch(
  () => props.messages.length,
  async () => {
    await nextTick()
    scrollToBottom()
  }
)

function scrollToBottom() {
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

function handleSend(content: string, msgType: string) {
  emit('sendMessage', content, msgType)
}

function handleUploadImage(file: File) {
  emit('uploadImage', file)
}

function handleUploadFile(file: File) {
  emit('uploadFile', file)
}
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f5f7fa;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.chat-header-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.online-status {
  font-size: 12px;
  color: #67c23a;
}

.offline-status {
  font-size: 12px;
  color: #c0c4cc;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px 0;
}

.empty-messages {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.chat-input {
  flex-shrink: 0;
}

.no-conversation {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
</style>