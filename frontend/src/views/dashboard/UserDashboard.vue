<template>
  <div class="user-dashboard">
    <!-- 欢迎区 -->
    <div class="welcome-section">
      <div>
        <h2 class="welcome-title">欢迎回来，{{ username }}</h2>
        <p class="welcome-sub">{{ today }} · {{ pendingCount }} 条待办事项</p>
      </div>
    </div>

    <!-- 快捷入口卡片 -->
    <div class="quick-actions">
      <div class="action-card" @click="router.push('/im')">
        <div class="action-icon" style="background:#EEF2FF">
          <ChatDotSquare style="color:#4F46E5" />
        </div>
        <div class="action-title">即时通讯</div>
        <div class="action-meta">
          <span class="badge" v-if="unreadCount > 0">{{ unreadCount }} 条未读</span>
          <span v-else>进入聊天</span>
        </div>
      </div>
      <div class="action-card" @click="router.push('/nl2sql')">
        <div class="action-icon" style="background:#ECFDF5">
          <DataAnalysis style="color:#10B981" />
        </div>
        <div class="action-title">智能问数</div>
        <div class="action-meta">用自然语言查询数据</div>
      </div>
      <div class="action-card" @click="router.push('/files')">
        <div class="action-icon" style="background:#FFFBEB">
          <Folder style="color:#F59E0B" />
        </div>
        <div class="action-title">文件管理</div>
        <div class="action-meta">上传、下载、分享文件</div>
      </div>
      <div class="action-card" @click="router.push('/notifications')">
        <div class="action-icon" style="background:#FEF2F2">
          <Bell style="color:#EF4444" />
        </div>
        <div class="action-title">通知中心</div>
        <div class="action-meta">查看系统通知</div>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="dashboard-grid">
      <!-- 最近会话 -->
      <div class="dashboard-card">
        <div class="card-header">
          <h3>最近会话</h3>
          <el-button text type="primary" size="small" @click="router.push('/im')">查看全部</el-button>
        </div>
        <div v-if="recentConversations.length === 0" class="empty-state">
          <el-empty description="暂无最近会话" :image-size="80" />
        </div>
        <div v-for="conv in recentConversations" :key="conv.id" class="conv-item" @click="router.push('/im')">
          <el-avatar :size="36" class="conv-avatar">{{ conv.name?.[0] }}</el-avatar>
          <div class="conv-body">
            <div class="conv-top">
              <span class="conv-name">{{ conv.name }}</span>
              <span class="conv-time">{{ conv.lastTime }}</span>
            </div>
            <div class="conv-msg">{{ conv.lastMessage }}</div>
          </div>
        </div>
      </div>

      <!-- 今日概览 -->
      <div class="dashboard-card">
        <div class="card-header">
          <h3>今日概览</h3>
        </div>
        <div class="stats-grid">
          <div class="stat-cell">
            <div class="stat-num" style="color:#4F46E5">{{ stats.messageCount }}</div>
            <div class="stat-lbl">消息数</div>
          </div>
          <div class="stat-cell">
            <div class="stat-num" style="color:#10B981">{{ stats.queryCount }}</div>
            <div class="stat-lbl">查询次数</div>
          </div>
          <div class="stat-cell">
            <div class="stat-num" style="color:#F59E0B">{{ stats.fileCount }}</div>
            <div class="stat-lbl">文件数</div>
          </div>
          <div class="stat-cell">
            <div class="stat-num" style="color:#6366F1">{{ stats.onlineDays }}</div>
            <div class="stat-lbl">在线天数</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ChatDotSquare, DataAnalysis, Folder, Bell } from '@element-plus/icons-vue'

const router = useRouter()
const username = ref(localStorage.getItem('username') || '用户')
const today = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })
const pendingCount = ref(0)
const unreadCount = ref(0)

const recentConversations = ref<Array<{ id: number; name: string; lastMessage: string; lastTime: string }>>([])

const stats = ref({
  messageCount: 0,
  queryCount: 0,
  fileCount: 0,
  onlineDays: 0,
})
</script>

<style scoped>
.user-dashboard {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Welcome */
.welcome-section {
  margin-bottom: 24px;
}
.welcome-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 4px;
  letter-spacing: -0.3px;
}
.welcome-sub {
  font-size: 14px;
  color: var(--color-text-muted);
  margin: 0;
}

/* Quick actions - Linear style cards */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.action-card {
  background: var(--color-bg-white);
  border-radius: var(--border-radius);
  padding: 20px;
  cursor: pointer;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s, transform 0.2s;
}
.action-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}
.action-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  margin-bottom: 12px;
}
.action-icon svg, .action-icon i {
  width: 20px;
  height: 20px;
}
.action-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}
.action-meta {
  font-size: 13px;
  color: var(--color-text-muted);
}
.badge {
  color: var(--color-primary);
  font-weight: 500;
}

/* Dashboard grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 16px;
}
.dashboard-card {
  background: var(--color-bg-white);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.card-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

/* Conversation list */
.conv-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  cursor: pointer;
  border-bottom: 1px solid var(--color-border-light);
}
.conv-item:last-child { border-bottom: none; }
.conv-item:hover { background: var(--color-bg-hover); margin: 0 -12px; padding: 10px 12px; border-radius: 6px; }
.conv-body { flex: 1; overflow: hidden; }
.conv-top { display: flex; justify-content: space-between; align-items: center; }
.conv-name { font-size: 14px; font-weight: 500; color: var(--color-text-primary); }
.conv-time { font-size: 12px; color: var(--color-text-placeholder); }
.conv-msg { font-size: 13px; color: var(--color-text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-top: 2px; }

/* Stats grid */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.stat-cell {
  text-align: center;
  padding: 20px 12px;
  background: var(--color-bg);
  border-radius: var(--border-radius);
}
.stat-num {
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.5px;
}
.stat-lbl {
  font-size: 13px;
  color