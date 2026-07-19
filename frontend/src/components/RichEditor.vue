<template>
  <div class="rich-editor">
    <div class="editor-toolbar">
      <slot name="toolbar" />
    </div>
    <div ref="editorRef" class="editor-content" contenteditable="true" @input="onInput" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const props = defineProps<{ modelValue?: string }>()
const emit = defineEmits(['update:modelValue'])
const editorRef = ref<HTMLElement>()

function onInput() {
  if (editorRef.value) emit('update:modelValue', editorRef.value.innerTe