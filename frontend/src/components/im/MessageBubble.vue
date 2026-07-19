<template>
  <div
    class="message-bubble"
    :class="[
      `message-${message.senderType}`,
      message.isRecalled ? 'message-recalled' : '',
      isOwn ? 'message-own' : 'message-other',
    ]"
  >
    <!-- 头像 -->
    <div class="message-avatar">
      <el-avatar :size="36">{{ message.senderName?.[0] || '?' }}</el-avatar>
    </div>

    <!-- 消息内容 -->
    <div class="message-body">
      <!-- 发送者名称 -->
      <div v-if="!isOwn && message.senderName" class="message-sender">
        {{ message.senderName }}
      </div>

      <!-- 撤回消息 -->
      <div v-if="message.isRecalled" class="recalled-notice">
        <el-tag type="danger" size="small" effect="dark" disable-transitions>
          ⚠️ 该消息因{{ message.recallReason || '违规' }}已被管理员撤回
        </el-tag>
      </div>

      <!-- 文本消息 -->
      <div v-else-if="message.msgType === 'text'" class="message-text">
        {{ message.content }}
      </div>

      <!-- 图片消息 -->
      <div v-else-if="message.msgType === 'image'" class="message-image">
        <el-image
          :src="message.content"
          :preview-src-list="[message.content]"
          fit="cover"
          style="max-width: 240px; max-height: 180px; border-radius: 8px;"
        />
      </div>

      <!-- 文件消息 -->
      <div v-else-if="message.msgType === 'file'" class="message-file">
        <el-button text type="primary" @click="downloadFile">
          <el-icon><Document /></el-icon>
          下载文件
        </el-button>
      </div>

      <!-- 系统消息 -->
      <div v-else-if="message.msgType === 'system'" class="message-system">
        <el-tag type="warning" size="small" effect="plain">
          {{ message.content }}
        </el-tag>
      </div>

      <!-- 时间 -->
      <div class="message-time">
        {{ formatTime(message.createdAt) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Message } from '../../types/im'
import { Document } from '@element-plus/icons-vue'

const props = defineProps<{
  message: Message
  isOwn: boolean
}>()

function formatTime(timeStr: string): string {
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  // 今天: 显示时分
  if (diff < 86400000 && date.getDate() === now.getDate()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  // 昨天
  const yesterday = new Date(now.getTime() - 86400000)
  if (date.getDate() === yesterday.getDate()) {
    return `昨天 ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`
  }

  // 更早
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function downloadFile() {
  // 文件下载逻辑
  window.open(props.message.content, '_blank')
}
</script>

<style scoped>
.message-bubble {
  display: flex;
  gap: 8px;
  padding: 8px 16px;
  transition: background-color 0.2s;
}

.message-bubble:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.message-own {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.message-body {
  max-width: 60%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-own .message-body {
  align-items: flex-end;
}

.message-sender {
  font-size: 12px;
  color: #909399;
  margin-bottom: 2px;
}

.message-text {
  background-color: #f0f2f5;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
  white-space: pre-wrap;
}

.message-own .message-text {
  background-color: #409eff;
  color: white;
}

.message-time {
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 2px;
}

.recalled-notice {
  padding: 8px 0;
}

.message-system {
  text-align: center;
  padding: 8px 0;
}

.message-file {
  background-color: #f0f2f5;
  padding: 10px 14px;
  border-radius: 12px;
}
</style>