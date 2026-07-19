<template>
  <div ref="chartRef" class="chart-view" :style="{ height: height + 'px' }" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
const props = defineProps<{ option: any; height?: number }>()
const chartRef = ref<HTMLElement>()

onMounted(() => {
  if (chartRef.value && props.option) {
    // Chart rendering delegated to ECharts (loaded via CDN or npm)
    import('echarts').then(echarts => {
      const chart = echarts.init(chartRef.value!)
      chart.setOption(props.option)
      watch(() => props.option, v => chart.setOption(v))
    })
