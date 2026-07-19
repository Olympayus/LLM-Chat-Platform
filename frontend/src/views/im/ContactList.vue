<template>
  <div class="contact-list">
    <!-- 搜索框 -->
    <div class="search-box">
      <el-input
        v-model="searchQuery"
        placeholder="搜索联系人..."
        size="small"
        clearable
        prefix-icon="Search"
        @input="handleSearch"
      />
    </div>

    <!-- 联系人列表 -->
    <div class="list-content">
      <div v-if="filteredContacts.length === 0" class="empty-tip">
        暂无联系人
      </div>

      <div
        v-for="contact in filteredContacts"
        :key="contact.id"
        class="contact-item"
        :class="{ active: selectedId === contact.id }"
        @click="selectContact(contact)"
      >
        <div class="avatar">
          <el-avatar :size="36">{{ contact.alias?.[0] || contact.username?.[0] || '?' }}</el-avatar>
          <span class="online-dot" :class="{ online: contact.isOnline }" />
        </div>

        <div class="contact-info">
          <div class="contact-name">
            <span class="name">{{ contact.alias || contact.username || `用户${contact.userId}` }}</span>
          </div>
          <div class="contact-status">
            {{ contact.isOnline ? '在线' : '离线' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Contact {
  id: number
  userId: number
  username?: string
  alias?: string
  isOnline: boolean
}

const props = defineProps<{
  contacts: Contact[]
  selectedId?: number
}>()

const emit = defineEmits<{
  select: [contact: Contact]
}>()

const searchQuery = ref('')

const filteredContacts = computed(() => {
  if (!searchQuery.value) return props.contacts

  const q = searchQuery.value.toLowerCase()
  return props.contacts.filter(
    c =>
      (c.username && c.username.toLowerCase().includes(q)) ||
      (c.alias && c.alias.toLowerCase().includes(q))
  )
})

function handleSearch() {
  // 搜索过滤由 computed 自动处理
}

function selectContact(contact: Contact) {
  emit('select', contact)
}
</script>

<style scoped>
.contact-list {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.search-box {
  padding: 8px 12px;
  border-bottom: 1px solid #f2f3f5;
}

.list-content {
  flex: 1;
  overflow-y: auto;
}

.empty-tip {
  text-align: center;
  color: #999;
  padding: 40px 0;
  font-size: 14px;
}

.contact-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.contact-item:hover {
  background-color: #f5f5f5;
}

.contact-item.active {
  background-color: #e6f0ff;
}

.avatar {
  position: relative;
  flex-shrink: 0;
  margin-right: 10px;
}

.online-dot {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #ccc;
  border: 2px solid #fff;
}

.online-dot.online {
  background-color: #67c23a;
}

.contact-info {
  flex: 1;
  min-width: 0;
}

.contact-name {
  display: flex;
  align-items: center;
  gap