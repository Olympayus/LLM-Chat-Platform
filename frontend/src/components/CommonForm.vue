<template>
  <el-form ref="formRef" :model="formData" :rules="rules" v-bind="$attrs">
    <slot />
  </el-form>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
const props = defineProps<{ formData: Record<string, any>; rules?: Record<string, any> }>()
const formRef = ref()
defineExpose({ validate: () => formRef.value?.validate(), reset: () => formRef.value?.resetFields() })
