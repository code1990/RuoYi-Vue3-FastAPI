<template>
  <div class="visual-page">
    <el-card>
      <el-alert :title="`横轴为交易日；题材按 2026 年以来累计涨停家数取前15，纵向堆叠显示每日涨停家数。`" type="info" :closable="false" show-icon />
      <div ref="chartRef" v-loading="loading" class="chart" />
    </el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { getLimitUpThemeTop15 } from '@/api/stock/limitUp'

const chartRef = ref()
const loading = ref(false)
let chart

function renderChart(data) {
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { type: 'scroll', top: 0 },
    grid: { left: 60, right: 24, top: 62, bottom: 88 },
    xAxis: { type: 'category', data: data.tradeDates, axisLabel: { formatter: value => value.slice(5), rotate: 45 } },
    yAxis: { type: 'value', name: '涨停家数', minInterval: 1 },
    dataZoom: [{ type: 'inside' }, { type: 'slider', bottom: 18 }],
    series: data.rows.map(row => ({ name: `${row.rankNo}. ${row.themeName}`, type: 'bar', stack: 'theme', data: row.values }))
  }, true)
}

async function loadChart() {
  loading.value = true
  try {
    const response = await getLimitUpThemeTop15()
    renderChart(response.data)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  chart = echarts.init(chartRef.value)
  loadChart()
  window.addEventListener('resize', chart.resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', chart.resize)
  chart.dispose()
})
</script>

<style scoped>
.visual-page { padding: 20px; }
.chart { height: 720px; margin-top: 16px; }
</style>
