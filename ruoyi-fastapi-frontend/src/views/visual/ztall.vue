<template>
  <div class="visual-page">
    <el-card>
      <el-form inline @submit.prevent>
        <el-form-item label="交易日"><el-date-picker v-model="tradeDate" type="date" value-format="YYYY-MM-DD" :clearable="false" /></el-form-item>
        <el-button type="primary" :loading="loading" @click="loadChart">查询</el-button>
      </el-form>
      <el-alert :title="`展示 ${displayDate} 涨停题材前15，按涨停家数排序。`" type="info" :closable="false" show-icon />
      <div ref="chartRef" v-loading="loading" class="chart" />
    </el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { getLimitUpThemeTop15 } from '@/api/stock/limitUp'

const chartRef = ref()
const tradeDate = ref('')
const displayDate = ref('-')
const loading = ref(false)
let chart

function renderChart(rows) {
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 140, right: 42, top: 28, bottom: 24 },
    xAxis: { type: 'value', name: '涨停家数', minInterval: 1 },
    yAxis: { type: 'category', inverse: true, data: rows.map(row => `${row.rankNo}. ${row.themeName}`) },
    series: [{ type: 'bar', data: rows.map(row => row.limitUpCount), itemStyle: { color: '#f56c6c' }, label: { show: true, position: 'right' } }]
  }, true)
}

async function loadChart() {
  loading.value = true
  try {
    const response = await getLimitUpThemeTop15({ tradeDate: tradeDate.value || undefined })
    displayDate.value = response.data.tradeDate || '-'
    tradeDate.value = response.data.tradeDate || ''
    renderChart(response.data.rows)
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
