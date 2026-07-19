<template>
  <div class="group-list">
    <!-- 搜索框 -->
    <div class="search-box">
      <el-input
        v-model="searchQuery"
        placeholder="搜索群组..."
        size="small"
        clearable
        prefix-icon="Search"
        @input="handleSearch"
      />
    </div>

    <!-- 群组列表 -->
    <div class="list-content">
      <div v-if="filteredGroups.length === 0" class="empty-tip">
        暂无群组
      </div>

      <div
        v-for="group in filteredGroups"
        :key="group.id"
        class="group-item"
        :class="{ active: selectedId === group.id }"
        @click="selectGroup(group)"
      >
        <div class="avatar">
          <el-avatar :size="36" shape="square">
            {{ group.groupName?.[0] || '群' }}
          </el-avatar>
        </div>

        <div class="group-info">
          <div class="group-name">
            <span class="name">{{ group.groupName || `群聊(${group.id})` }}</span>
            <span class="member-count">{{ group.memberCount }}人</span>
          </div>
          <div class="group-notice" v-if="group.lastMessage">
            {{ group.lastMessage }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Group {
  id: number
  groupName: string
  memberCount: number
  lastMessage?: string
}

const props = defineProps<{
  groups: Group[]
  selectedId?: number
}>()

const emit = defineEmits<{
  select: [group: Group]
}>()

const searchQuery = ref('')

const filteredGroups = computed(() => {
  if (!searchQuery.value) return props.groups

  const q = searchQuery.value.toLowerCase()
  return props.groups.filter(g => g.groupName.toLowerCase().includes(q))
})

function handleSearch() {
  // 搜索过滤由 computed 自动处理
}

function selectGroup(group: Group) {
  emit('select', group)
}
</script>

<style scoped>
.group-list {
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

.group-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.group-item:hover {
  background-color: #f5f5f5;
}

.group-item.active {
  background-color: #e6f0ff;
}

.avatar {
  flex-shrink: 0;
  margin-right: 10px;
}

.group-info {
  flex: 1;
  min-width: 0;
}

.group-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.member-count {
  font-size: 12px;
  color: #999;
}
