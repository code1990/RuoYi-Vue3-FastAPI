<template>
  <div class="stat-page">
    <el-alert title="仅统计DDE日内连续列表：按早午尾组合分组；完整5日样本中，任一天最高收益≥1.8%为达标。" type="info" :closable="false" show-icon />
    <el-card header="DDE日内连续与5日结果" class="chart-row"><div ref="chartRef" v-loading="loading" class="chart" /></el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { getDdeIntradayComboStatistics } from '@/api/stock/ddeFund'

const chartRef = ref()
const loading = ref(false)
const comboTypes = [
  { key: 'morning_noon', label: '早+午', colors: ['#67c23a', '#b3e19d'] },
  { key: 'noon_close', label: '午+尾', colors: ['#e6a23c', '#f3d19e'] },
  { key: 'morning_close', label: '早+尾', colors: ['#909399', '#c8c9cc'] },
  { key: 'morning_noon_close', label: '早+午+尾', colors: ['#f56c6c', '#fab6b6'] }
]
let chart

function renderChart(rows) {
  const tradeDates = [...new Set(rows.map(row => row.tradeDate))].sort().slice(-30)
  const values = new Map(rows.map(row => [`${row.tradeDate}:${row.comboType}`, row]))
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { top: 0 },
    grid: { left: 60, right: 20, top: 55, bottom: 72 },
    xAxis: { type: 'category', data: tradeDates, axisLabel: { interval: 0, formatter: value => `${value.slice(4, 6)}-${value.slice(6)}` } },
    yAxis: { type: 'value', name: '完整5日样本数', minInterval: 1 },
    series: comboTypes.flatMap(combo => [
      { name: `${combo.label} 达标`, type: 'bar', stack: combo.key, barWidth: 6, data: tradeDates.map(date => values.get(`${date}:${combo.key}`)?.successCount || 0), itemStyle: { color: combo.colors[0] } },
      { name: `${combo.label} 未达标`, type: 'bar', stack: combo.key, barWidth: 6, data: tradeDates.map(date => values.get(`${date}:${combo.key}`)?.failureCount || 0), itemStyle: { color: combo.colors[1] } }
    ])
  }, true)
}

async function getStatistics() {
  loading.value = true
  try {
    const response = await getDdeIntradayComboStatistics({ targetReturnPct: 1.8 })
    renderChart(response.data)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  chart = echarts.init(chartRef.value)
  getStatistics()
  window.addEventListener('resize', chart.resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', chart.resize)
  chart.dispose()
})
</script>

<style scoped>
.stat-page { padding: 20px; }
.chart-row { margin-top: 16px; }
.chart { height: 560px; }
</style>
