/** 用户/部门/角色/菜单管理 API */

import request from './request'

// ===== 用户管理 =====
export interface UserItem {
  id: number
  username: string
  real_name: string
  email: string
  mobile: string
  dept_id: number
  dept_name: string
  status: number
  created_at: string
}

export function getUserList(params: { page: number; page_size: number; keyword?: string; status?: number }) {
  return request.get('/api/v1/users', { params })
}

export function getUserDetail(id: number) {
  return request.get(`/api/v1/users/${id}`)
}

export function createUser(data: any) {
  return request.post('/api/v1/users', data)
}

export function updateUser(id: number, data: any) {
  return request.put(`/api/v1/users/${id}`, data)
}

export function deleteUser(id: number) {
  return request.delete(`/api/v1/users/${id}`)
}

export function setUserStatus(id: number, status: number) {
  return request.put(`/api/v1/users/${id}/status`, { status })
}

// ===== 部门管理 =====
export function getDeptTree() {
  return request.get('/api/v1/depts')
}

export function createDept(data: any) {
  return request.post('/api/v1/depts', data)
}

export function updateDept(id: number, data: any) {
  return request.put(`/api/v1/depts/${id}`, data)
}

export function deleteDept(id: number) {
  return request.delete(`/api/v1/depts/${id}`)
}

// ===== 角色管理 =====
export function getRoleList() {
  return request.get('/api/v1/roles')
}

export function createRole(data: any) {
  return request.post('/api/v1/roles', data)
}

export function updateRole(id: number, data: any) {
  return request.put(`/api/v1/roles/${id}`, data)
}

export function deleteRole(id: number) {
  return request.delete(`/api/v1/roles/${id}`)
}

// ===== 菜单管理 =====
export function getMenuTree() {
  return request.get('/api/v1/menus')
}

export function createMenu(data: any) {
  return request.post('/api/v1/menus', data)
}

export function updateMenu(id: number, data: any) {
  return request.put(`/api/v1/menus/${id}`, data)
}

e