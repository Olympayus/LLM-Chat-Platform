<template>
  <div class="file-uploader">
    <el-upload
      :action="uploadUrl"
      :headers="headers"
      :multiple="multiple"
      :limit="limit"
      :accept="accept"
      :on-success="handleSuccess"
      :on-error="handleError"
      :before-upload="beforeUpload"
      drag
    >
      <el-icon><upload-filled /></el-icon>
      <div class="upload-text">Drag files here or click to upload</div>
    </el-upload>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  multiple?: boolean
  limit?: number
  accept?: string
  maxSizeMb?: number
}>()
const emit = defineEmits(['upload-success', 'upload-error'])

const uploadUrl = '/api/v1/files/upload'
const headers = computed(() => ({ Authorization: `Bearer ${localStorage.getItem('llm_access_token') || ''}` }))

function beforeUpload(file: File) {
  const max = (props.maxSizeMb || 50) * 1024 * 1024
  if (file.size > max) { ElMessage.error(`File exceeds ${props.maxSizeMb || 50}MB limit`); return false }
  return true
}
function handleSuccess(res: any) { ElMessage.success('Upload success'); emit('upload-success', res) }
function handleError() { ElMessage.error('Upload fai