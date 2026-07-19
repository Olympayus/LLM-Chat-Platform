<template>
  <div class="conversation-list">
    <!-- 搜索框 -->
    <div class="search-box">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索联系人/群聊"
        :prefix-icon="Search"
        clearable
        size="small"
      />
    </div>

    <!-- 会话列表 -->
    <div class="list-items">
      <div
        v-for="conv in filteredConversations"
        :key="conv.id"
        class="conversation-item"
        :class="{ active: currentConversation?.id === conv.id && currentConversation?.type === conv.type }"
        @click="$emit('select', conv)"
      >
        <el-avatar :size="40" class="item-avatar">
          {{ conv.name[0] }}
        </el-avatar>

        <div class="item-content">
          <div class="item-header">
            <span class="item-name">{{ conv.name }}</span>
            <span class="item-time">{{ formatTime(conv.lastTime) }}</span>
          </div>
          <div class="item-message">
            <span class="item-preview">{{ conv.lastMessage || '暂无消息' }}</span>
            <el-badge v-if="conv.unreadCount > 0" :value="conv.unreadCount" :max="99" class="unread-badge" />
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="filteredConversations.length === 0" class="empty-list">
        <el-empty description="暂无会话" :image-size="80" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import type { Conversation } from '../../types/im'

const props = defineProps<{
  conversations: Conversation[]
  currentConversation: Conversation | null
}>()

defineEmits<{
  select: [conversation: Conversation]
}>()

const searchKeyword = ref('')

const filteredConversations = computed(() => {
  if (!searchKeyword.value) return props.conversations
  const keyword = searchKeyword.value.toLowerCase()
  return props.conversations.filter(
    conv => conv.name.toLowerCase().includes(keyword)
  )
})

function formatTime(timeStr?: string): string {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000 && date.getDate() === now.getDate()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  const yesterday = new Date(now.getTime() - 86400000)
  if (date.getDate() === yesterday.getDate()) return '昨天'

  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}
</script>

<style scoped>
.conversation-list {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-right: 1px solid #e4e7ed;
}

.search-box {
  padding: 12px;
  border-bottom: 1px solid #f2f3f5;
}

.list-items {
  flex: 1;
  overflow-y: auto;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.conversation-item:hover {
  background-color: #f5f7fa;
}

.conversation-item.active {
  background-color: #ecf5ff;
}

.item-avatar {
  flex-shrink: 0;
  background-color: #409eff;
  color: white;
}

.item-content {
  flex: 1;
  min-width: 0;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.item-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-time {
  font-size: 11px;
  color: #c0c4cc;
  flex-shrink: 0;
}

.item-message {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-preview {
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.unread-badge {
  flex-shrink: 0;
  margin-left: 4px;
}

.empty-list {
  padding: 40px 0;
}
</style>