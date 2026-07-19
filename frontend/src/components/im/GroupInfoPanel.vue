<template>
  <div class="group-info-panel">
    <div v-if="group" class="panel-content">
      <!-- 群信息 -->
      <div class="group-header">
        <el-avatar :size="56" class="group-avatar">
          {{ group.groupName[0] }}
        </el-avatar>
        <div class="group-name">{{ group.groupName }}</div>
      </div>

      <!-- 群公告 -->
      <div class="info-section">
        <div class="section-title">群公告</div>
        <div class="notice-content">
          <p v-if="group.notice">{{ group.notice }}</p>
          <p v-else class="no-notice">暂无公告</p>
        </div>
      </div>

      <!-- 群成员 -->
      <div class="info-section">
        <div class="section-title">
          群成员
          <span class="member-count">({{ group.memberCount }})</span>
        </div>
        <div class="member-list">
          <div v-for="member in group.members" :key="member.id" class="member-item">
            <el-avatar :size="32" class="member-avatar">
              {{ member.username?.[0] || '?' }}
            </el-avatar>
            <div class="member-info">
              <span class="member-name">{{ member.username || `用户${member.userId}` }}</span>
              <el-tag v-if="member.role === 'owner'" size="small" type="warning">群主</el-tag>
              <el-tag v-else-if="member.role === 'admin'" size="small" type="success">管理员</el-tag>
              <el-tag v-else-if="member.userType === 'bot'" size="small" type="info">AI</el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 无群组时 -->
    <div v-else class="no-group">
      <el-empty description="当前未选择群聊" :image-size="80" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { GroupInfo } from '../../types/im'

defineProps<{
  group: GroupInfo | null
}>()
</script>

<style scoped>
.group-info-panel {
  height: 100%;
  background: #fff;
  border-left: 1px solid #e4e7ed;
  overflow-y: auto;
}

.panel-content {
  padding: 16px;
}

.group-header {
  text-align: center;
  padding: 16px 0;
  border-bottom: 1px solid #f2f3f5;
  margin-bottom: 16px;
}

.group-avatar {
  background-color: #409eff;
  color: white;
  margin-bottom: 8px;
}

.group-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.info-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid #f2f3f5;
}

.member-count {
  font-weight: 400;
  color: #909399;
}

.notice-content p {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

.no-notice {
  color: #c0c4cc;
  font-style: italic;
}

.member-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.member-item:hover {
  background-color: #f5f7fa;
}

.member-avatar {
  flex-shrink: 0;
  background-color: #67c23a;
  color: white;
}

.member-info {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.member-name {
  font-size: 13px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.no-group {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
</style>