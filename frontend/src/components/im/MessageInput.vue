<template>
  <div class="message-input">
    <!-- 工具栏 -->
    <div class="input-toolbar">
      <el-button text @click="triggerImageUpload" :disabled="disabled">
        <el-icon><Picture /></el-icon>
      </el-button>
      <el-button text @click="triggerFileUpload" :disabled="disabled">
        <el-icon><Folder /></el-icon>
      </el-button>
      <input
        ref="imageInput"
        type="file"
        accept="image/*"
        style="display: none"
        @change="handleImageUpload"
      />
      <input
        ref="fileInput"
        type="file"
        style="display: none"
        @change="handleFileUpload"
      />
    </div>

    <!-- 输入框 -->
    <div class="input-area">
      <el-input
        v-model="content"
        type="textarea"
        :rows="3"
        :disabled="disabled"
        placeholder="输入消息，Enter 发送，Ctrl+Enter 换行"
        @keydown.enter.exact="sendMessage"
        @keydown.ctrl.enter="insertNewLine"
      />
    </div>

    <!-- 发送按钮 -->
    <div class="input-actions">
      <el-button
        type="primary"
        :disabled="!content.trim() || disabled"
        :loading="sending"
        @click="sendMessage"
      >
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Picture, Folder } from '@element-plus/icons-vue'

const emit = defineEmits<{
  send: [content: string, msgType: string]
  uploadImage: [file: File]
  uploadFile: [file: File]
}>()

const props = defineProps<{
  disabled?: boolean
}>()

const content = ref('')
const sending = ref(false)
const imageInput = ref<HTMLInputElement>()
const fileInput = ref<HTMLInputElement>()

function sendMessage() {
  const text = content.value.trim()
  if (!text || props.disabled) return

  sending.value = true
  emit('send', text, 'text')
  content.value = ''
  setTimeout(() => { sending.value = false }, 100)
}

function insertNewLine() {
  content.value += '\n'
}

function triggerImageUpload() {
  imageInput.value?.click()
}

function triggerFileUpload() {
  fileInput.value?.click()
}

function handleImageUpload(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    emit('uploadImage', target.files[0])
  }
  target.value = ''
}

function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    emit('uploadFile', target.files[0])
  }
  target.value = ''
}
</script>

<style scoped>
.message-input {
  border-top: 1px solid #e4e7ed;
  background: #fff;
  display: flex;
  flex-direction: column;
}

.input-toolbar {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  border-bottom: 1px solid #f2f3f5;
  gap: 4px;
}

.input-area {
  padding: 8px;
}

.input-area :deep(.el-textarea__inner) {
  border: none;
  resize: none;
  box-shadow: none;
  padding: 0;
  font-size: 14px;
  line-height: 1.5;
}

.input-area :deep(.el-textarea__inner:focus) {
  box-shadow: none;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  padding: 4px 8px 8px;
}
</style>