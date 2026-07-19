<template>
  <div class="common-table">
    <div class="table-toolbar" v-if="$slots.toolbar">
      <slot name="toolbar" />
    </div>
    <el-table :data="data" v-loading="loading" @sort-change="$emit('sort-change', $event)" @selection-change="$emit('selection-change', $event)">
      <el-table-column v-if="selectable" type="selection" width="50" />
      <slot />
    </el-table>
    <el-pagination
      v-if="pagination"
      v-model:current-page="currentPage"
      :page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next"
      @size-change="$emit('size-change', $event)"
      @current-change="$emit('page-change', $event)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
const props = defineProps<{
  data: any[]; loading?: boolean; total?: number; pageSize?: number; page?: number; selectable?: boolean
}>()
const emit = defineEmits(['page-change', 'size-change', 'sort-change', 'selection-change'])
const currentPage = ref(props.page || 1)
const pageSize = ref(props.pageSize || 20)
const pagination = props.