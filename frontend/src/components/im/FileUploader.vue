<template>
  <div class="file-uploader">
    <el-upload
      :action="uploadUrl"
      :headers="headers"
      :on-success="handleSuccess"
      :on-error="handleError"
      :before-upload="beforeUpload"
      :show-file-list="false"
      :multiple="false"
    >
      <el-button :icon="Upload" :disabled="disabled">
        {{ buttonText }}
      </el-button>
    </el-upload>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Upload } from '@element-plus/icons-vue'
import { useIMStore } from '../../stores/im'

const props = defineProps<{
  accept?: string
  maxSize?: number // MB
  buttonText?: string
  disabled?: boolean
  action?: string // 上传地址
}>()

const emit = defineEmits<{
  success: [url: string]
  error: [message: string]
}>()

const store = useIMStore()

const uploadUrl = computed(() => {
  return props.action || '/api/v1/upload'
})

const headers = computed(() => ({
  Authorization: `Bearer ${store.token}`,
}))

function beforeUpload(file: File): boolean {
  const maxSize = (props.maxSize || 10) * 1024 * 1024 // 默认 10MB
  if (file.size > maxSize) {
    emit('error', `文件大小不能超过 ${props.maxSize || 10}MB`)
    return false
  }
  return true
}

function handleSuccess(response: any) {
  if (response.data?.url) {
    emit('success', response.data.url)
  } else {
    emit('error', '上传失败：未返回文件地址')
  }
}

function handleError(error: any) {
  emit('error', error.message || '上传失败')
}
</script>