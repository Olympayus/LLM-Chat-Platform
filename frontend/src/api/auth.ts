/** 认证相关 API */

import request from './request'

export interface LoginParams {
  username: string
  password: string
}

export interface RegisterParams {
  username: string
  password: string
  email?: string
  mobile?: string
}

export interface LoginResult {
  access_token: string
  token_type: string
  expires_in: number
  user: {
    id: number
    username: string
    real_name: string
    avatar_url: string
  }
}

/** 登录 */
export function login(data: LoginParams) {
  return request.post('/api/v1/auth/login', data)
}

/** 注册 */
export function register(data: RegisterParams) {
  return request.post('/api/v1/auth/register', data)
}

/** 退出登录 */
export function logout() {
  return request.post('/api/v1/auth/logout')
}

/** 获取当前用户信息 */
export function getCurrentUser() {
  return request.get('/api/v1/auth/me')
}

/** 修改密码 */
export function changePassword(data: { old_password: string; new_password: string }) {
  r