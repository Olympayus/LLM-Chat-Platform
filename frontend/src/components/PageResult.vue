<template>
  <div class="page-result">
    <el-result :icon="iconType" :title="title" :sub-title="subTitle">
      <template #extra>
        <el-button v-if="type === 'error'" type="primary" @click="$emit('retry')">Retry</el-button>
        <el-button v-if="type === 'empty'" type="primary" @click="$emit('create')">Create</el-button>
      </template>
    </el-result>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ type: 'loading' | 'empty' | 'error'; title?: string; subTitle?: string }>()
const iconType = computed(() => props.type === 'loading' ? 'Loading' : props.type === 'empty' ? 'Warning' : 'error