<template>
  <div class="admin-dashboard">
    <!-- 统计卡片 -->
    <div class="stat-cards">
      <div class="stat-card">
        <div class="stat-icon" style="background:#EEF2FF">
          <User style="color:#4F46E5" />
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.totalUsers }}</div>
          <div class="stat-label">总用户数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#ECFDF5">
          <ChatDotSquare style="color:#10B981" />
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.todayMessages }}</div>
          <div class="stat-label">今日消息</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#FFFBEB">
          <Avatar style="color:#F59E0B" />
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.onlineUsers }}</div>
          <div class="stat-label">当前在线</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#FEF2F2">
          <Connection style="color:#EF4444" />
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.activeGroups }}</div>
          <div class="stat-label">活跃群组</div>
        </div>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="dashboard-grid">
      <!-- 趋势图 -->
      <div class="grid-card">
        <div class="card-header">
          <h3>消息趋势（近7天）</h3>
        </div>
        <div class="chart-box">
          <el-empty description="图表组件待接入" :image-size="80" />
        </div>
      </div>

      <!-- 侧边栏 -->
      <div class="side-stack">
        <div class="grid-card">
          <div class="card-header">
            <h3>快速操作</h3>
          </div>
          <div class="quick-ops">
            <el-button class="ops-btn" @click="router.push('/admin/compliance')">
              <Shield style="margin-right:6px" />合规审计
            </el-button>
            <el-button class="ops-btn" type="primary" @click="router.push('/admin/users')">
              <User style="margin-right:6px" />用户管理
            </el-button>
            <el-button class="ops-btn" @click="router.push('/admin/models')">
              <Cpu style="margin-right:6px" />模型管理
            </el-button>
            <el-button class="ops-btn" @click="router.push('/admin/crawlers')">
              <Search style="margin-right:6px" />爬虫任务
            </el-button>
          </div>
        </div>

        <div class="grid-card">
          <div class="card-header">
            <h3>系统状态</h3>
          </div>
          <div class="sys-status">
            <div class="status-row"><span class="dot dot-green"></span>MySQL</div>
            <div class="status-row"><span class="dot dot-green"></span>Redis</div>
            <div class="status-row"><span class="dot dot-green"></span>Elasticsearch</div>
            <div class="status-row"><span class="dot dot-yellow"></span>存储使用 45%</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { User, ChatDotSquare, Avatar, Connection, Shield, Cpu, Search } from '@element-plus/icons-vue'

const router = useRouter()

const stats = ref({
  totalUsers: 0,
  todayMessages: 0,
  onlineUsers: 0,
  activeGroups: 0,
})
</script>

<style scoped>
.admin-dashboard {
  padding: 24px;
}

/* Stat cards - Linear style */
.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.stat-card {
  background: var(--color-bg-white);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: box-shadow 0.2s;
}
.stat-card:hover { box-shadow: var(--shadow-md); }
.stat-icon {
  width: 48px; height: 48px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 12px;
  flex-shrink: 0;
}
.stat-icon svg { width: 22px; height: 22px; }
.stat-body { flex: 1; }
.stat-value { font-size: 28px; font-weight: 700; color: var(--color-text-primary); line-height: 1.2; }
.stat-label { font-size: 13px; color: var(--color-text-muted); margin-top: 2px; }

/* Dashboard grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 16px;
}
.grid-card {
  background: var(--color-bg-white);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  padding: 20px;
}
.side-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.card-header h3 {
  font-size: 15px; font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

/* Chart */
.chart-box {
  height: 280px;
  display: flex; align-items: center; justify-content: center;
}

/* Quick ops */
.quick-ops { display: flex; flex-direction: column; gap: 8px; }
.ops-btn { width: 100%; justify-content: flex-start; font-size: 13px; }

/* System status */
.sys-status { display: flex; flex-direction: column; gap: 12px; }
.status-row {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; color: var(--color-text-secondary);
}
.dot {
  width: 8px; height: 8px; border-radius: 50%;
  flex-shrink: 0;
}
.dot-green { background: #10B981; }
.dot-yell