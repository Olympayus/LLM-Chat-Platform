<template>
  <div class="sys-settings" style="max-width:800px;margin:20px auto;padding:0 20px">
    <el-card>
      <template #header><span>系统设置</span></template>
      <el-tabs v-model="tab">
        <el-tab-pane label="站点信息" name="site">
          <el-form :model="siteForm" label-width="100px">
            <el-form-item label="站点名称"><el-input v-model="siteForm.site_name" /></el-form-item>
            <el-form-item label="站点 Logo"><el-input v-model="siteForm.logo_url" placeholder="输入Logo URL" /></el-form-item>
            <el-form-item label="备案号"><el-input v-model="siteForm.icp" /></el-form-item>
            <el-form-item label="系统公告"><el-input v-model="siteForm.announcement" type="textarea" :rows="4" /></el-form-item>
            <el-form-item><el-button type="primary" @click="handleSaveSite">保存</el-button></el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="存储配置" name="storage">
          <el-form label-width="120px">
            <el-form-item label="文件大小限制"><el-input-number :min="1" :max="100" v-model="storageForm.max_size" /> MB</el-form-item>
            <el-form-item label="允许类型"><el-input v-model="storageForm.allowed_types" placeholder="如：jpg,png,pdf,doc" /></el-form-item>
            <el-form-item><el-button type="primary" @click="handleSaveStorage">保存</el-button></el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../../api/request'

const tab = ref('site')
const siteForm = reactive({ site_name: '企业智能协同平台', logo_url: '', icp: '', announcement: '' })
const storageForm = reactive({ max_size: 10, allowed_types: 'jpg,png,pdf,doc,docx,xls,xlsx' })

async function handleSaveSite() {
  try {
    await request.put('/api/v1/sys-config', { category: 'site', config: siteForm })
    ElMessage.success('保存成功')
  } catch (err: any) { ElMessage.error(err.message) }
}

async function handleSaveStorage() {
  try {
    await request.put('/api/v1/sys-config', { category: 'storage', config: storageForm })
    ElMessage.success('保存成功')
  } catch (err: any