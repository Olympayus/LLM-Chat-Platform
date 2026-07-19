<template>
  <el-container class="app-layout">
    <el-aside :width="sidebarWidth" class="app-sidebar">
      <div class="logo-area">{{ siteName }}</div>
      <el-menu :default-active="activeRoute" router :collapse="collapsed">
        <slot name="menu" />
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="app-header">
        <slot name="header" />
      </el-header>
      <el-main class="app-main">
        <el-breadcrumb separator="/"><slot name="breadcrumb" /></el-breadcrumb>
        <slot />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
const props = withDefaults(defineProps<{
  collapsed?: boolean; activeRoute?: string; siteName?: string
}>(), { collapsed: false, activeRoute: '/', siteName: 'LLM Platform' })
const sidebarWidth = computed(() => props.collapsed ? '64