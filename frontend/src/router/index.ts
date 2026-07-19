/** Vue Router 路由配置 */

import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  // ===== 认证页（无需登录） =====
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/Login.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/auth/Register.vue'),
  },

  // ===== 用户端 =====
  {
    path: '/',
    component: () => import('../components/UserLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'UserDashboard',
        component: () => import('../views/dashboard/UserDashboard.vue'),
        meta: { title: '控制台' },
      },
      {
        path: 'im',
        name: 'Chat',
        component: () => import('../views/im/ChatView.vue'),
        meta: { title: '即时通讯' },
      },
      {
        path: 'nl2sql',
        name: 'Nl2sql',
        component: () => import('../views/nl2sql/Nl2sqlView.vue'),
        meta: { title: '智能问数' },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/profile/ProfileView.vue'),
        meta: { title: '个人中心' },
      },
      {
        path: 'notifications',
        name: 'Notifications',
        component: () => import('../views/notification/NotificationList.vue'),
        meta: { title: '通知中心' },
      },
      {
        path: 'files',
        name: 'Files',
        component: () => import('../views/files/FileList.vue'),
        meta: { title: '文件管理' },
      },
    ],
  },

  // ===== 管理端 =====
  {
    path: '/admin',
    component: () => import('../components/AppLayout.vue'),
    redirect: '/admin/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('../views/dashboard/AdminDashboard.vue'),
        meta: { title: '管理控制台' },
      },
      {
        path: 'users',
        name: 'UserManage',
        component: () => import('../views/admin/users/UserList.vue'),
        meta: { title: '用户管理' },
      },
      {
        path: 'depts',
        name: 'DeptManage',
        component: () => import('../views/admin/depts/DeptTree.vue'),
        meta: { title: '部门管理' },
      },
      {
        path: 'roles',
        name: 'RoleManage',
        component: () => import('../views/admin/roles/RoleList.vue'),
        meta: { title: '角色管理' },
      },
      {
        path: 'menus',
        name: 'MenuManage',
        component: () => import('../views/admin/menus/MenuTree.vue'),
        meta: { title: '菜单管理' },
      },
      {
        path: 'models',
        name: 'ModelManage',
        component: () => import('../views/model/ModelList.vue'),
        meta: { title: '模型管理' },
      },
      {
        path: 'skills',
        name: 'SkillManage',
        component: () => import('../views/skill/SkillList.vue'),
        meta: { title: '技能管理' },
      },
      {
        path: 'employees',
        name: 'EmployeeManage',
        component: () => import('../views/employee/EmployeeList.vue'),
        meta: { title: '数字员工管理' },
      },
      {
        path: 'crawlers',
        name: 'CrawlerManage',
        component: () => import('../views/crawler/CrawlerList.vue'),
        meta: { title: '爬虫任务管理' },
      },
      {
        path: 'compliance',
        name: 'Compliance',
        component: () => import('../views/compliance/ComplianceView.vue'),
        meta: { title: '合规审计' },
      },
      {
        path: 'audit-logs',
        name: 'AuditLogs',
        component: () => import('../views/audit/AuditLogList.vue'),
        meta: { title: '审计日志' },
      },
      {
        path: 'settings',
        name: 'SysSettings',
        component: () => import('../views/settings/SysSettings.vue'),
        meta: { title: '系统设置' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

// 路由守卫 — 检查登录状态
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const publicPages = ['Login'