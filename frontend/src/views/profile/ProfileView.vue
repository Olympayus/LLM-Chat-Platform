<template>
  <div class="profile-view" style="max-width:800px;margin:20px auto;padding:0 20px">
    <el-card>
      <template #header><span>个人中心</span></template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="用户名">{{ userInfo.username }}</el-descriptions-item>
        <el-descriptions-item label="真实姓名">{{ userInfo.real_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ userInfo.email || '-' }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ userInfo.mobile || '-' }}</el-descriptions-item>
        <el-descriptions-item label="最后登录">{{ userInfo.last_login_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ userInfo.created_at || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
    <el-card style="margin-top:16px">
      <template #header><span>修改密码</span></template>
      <el-form :model="pwdForm" style="max-width:400px">
        <el-form-item label="旧密码"><el-input v-model="pwdForm.old_password" type="password" show-password /></el-form-item>
        <el-form-item label="新密码"><el-input v-model="pwdForm.new_password" type="password" show-password /></el-form-item>
        <el-form-item><el-button type="primary" @click="handleChangePwd">修改密码</el-button></el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCurrentUser, changePassword } from '../../api/auth'

const userInfo = ref<any>({})
const pwdForm = reactive({ old_password: '', new_password: '' })

onMounted(async () => {
  try {
    const res: any = await getCurrentUser()
    userInfo.value = res.data || res
  } catch { /* ignore */ }
})

async function handleChangePwd() {
  try {
    await changePassword(pwdForm)
    ElMessage.success('密码修改成功')
    pwdForm.old_password = ''
    pwdForm.new_password = ''
  } catch (err: any) {
    ElMessage.error(