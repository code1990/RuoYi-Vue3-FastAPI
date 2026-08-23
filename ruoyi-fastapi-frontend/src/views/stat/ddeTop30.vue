<template>
  <div class="stat-page">
    <el-alert title="仅统计DDE资金30列表：按早盘、午盘、尾盘分组；完整5日样本中，任一天最高收益≥1.8%为达标。" type="info" :closable="false" show-icon />
    <el-card header="DDE资金30时段与5日结果" class="chart-row"><div ref="chartRef" v-loading="loading" class="chart" /></el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { getDdeTop30Statistics } from '@/api/stock/ddeFund'

const chartRef = ref()
const loading = ref(false)
const periods = [{ key: 'morning', label: '早盘', colors: ['#67c23a', '#b3e19d'] }, { key: 'noon', label: '午盘', colors: ['#e6a23c', '#f3d19e'] }, { key: 'close', label: '尾盘', colors: ['#f56c6c', '#fab6b6'] }]
let chart

function renderChart(rows) {
  const tradeDates = [...new Set(rows.map(row => row.tradeDate))].sort().slice(-30)
  const values = new Map(rows.map(row => [`${row.tradeDate}:${row.signalSlot}`, row]))
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { top: 0 },
    grid: { left: 60, right: 20, top: 55, bottom: 72 },
    xAxis: { type: 'category', data: tradeDates, axisLabel: { interval: 0, formatter: value => `${value.slice(4, 6)}-${value.slice(6)}` } },
    yAxis: { type: 'value', name: '完整5日样本数', minInterval: 1 },
    series: periods.flatMap(period => [
      { name: `${period.label} 达标`, type: 'bar', stack: period.key, barWidth: 8, data: tradeDates.map(date => values.get(`${date}:${period.key}`)?.successCount || 0), itemStyle: { color: period.colors[0] } },
      { name: `${period.label} 未达标`, type: 'bar', stack: period.key, barWidth: 8, data: tradeDates.map(date => values.get(`${date}:${period.key}`)?.failureCount || 0), itemStyle: { color: period.colors[1] } }
    ])
  }, true)
}

async function getStatistics() {
  loading.value = true
  try {
    const response = await getDdeTop30Statistics({ targetReturnPct: 1.8 })
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
