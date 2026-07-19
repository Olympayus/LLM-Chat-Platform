<template>
  <el-container class="user-layout">
    <!-- 顶部导航 -->
    <el-header>
      <div class="header-left">
        <div class="logo" @click="router.push('/dashboard')">智能协同平台</div>
      </div>
      <div class="header-right">
        <el-menu mode="horizontal" :ellipsis="false" router>
          <el-menu-item index="/dashboard">控制台</el-menu-item>
          <el-menu-item index="/im">即时通讯</el-menu-item>
          <el-menu-item index="/nl2sql">智能问数</el-menu-item>
          <el-menu-item index="/files">文件管理</el-menu-item>
        </el-menu>
        <div class="user-area">
          <el-badge :value="unreadCount" :hidden="unreadCount === 0">
            <el-button text @click="router.push('/notifications')">
              <el-icon><Bell /></el-icon>
            </el-button>
          </el-badge>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="28">{{ username?.[0] || 'U' }}</el-avatar>
              <span class="username">{{ username || '用户' }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>

    <!-- 内容区 -->
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Bell } from '@element-plus/icons-vue'

const router = useRouter()
const unreadCount = ref(0)
const username = ref(localStorage.getItem('username') || '用户')

function handleCommand(command: string) {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    router.push('/login')
  }
}
</script>

<style scoped>
.user-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 16px;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
  cursor: pointer;
  margin-right: 24px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
  justify-content: space-between;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.username {
  font-size: 14px;
