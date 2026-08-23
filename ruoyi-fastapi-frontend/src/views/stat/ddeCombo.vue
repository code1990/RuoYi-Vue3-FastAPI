<template>
  <div class="stat-page">
    <el-alert title="仅统计2日DDE列表：昨日与今日DDE次数相加分组；完整5日样本中，任一天最高收益≥1.8%为达标。" type="info" :closable="false" show-icon />
    <el-card header="2日DDE次数与5日结果" class="chart-row"><div ref="chartRef" v-loading="loading" class="chart" /></el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { getDdeComboStatistics } from '@/api/stock/ddeFund'

const chartRef = ref()
const loading = ref(false)
const comboBands = ['2次', '3次', '4次+']
const colors = { '2次': ['#67c23a', '#b3e19d'], '3次': ['#e6a23c', '#f3d19e'], '4次+': ['#f56c6c', '#fab6b6'] }
let chart

function renderChart(rows) {
  const tradeDates = [...new Set(rows.map(row => row.signalDate))].sort().slice(-30)
  const values = new Map(rows.map(row => [`${row.signalDate}:${row.comboBand}`, row]))
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { top: 0 },
    grid: { left: 60, right: 20, top: 55, bottom: 72 },
    xAxis: { type: 'category', data: tradeDates, axisLabel: { interval: 0, formatter: value => `${value.slice(4, 6)}-${value.slice(6)}` } },
    yAxis: { type: 'value', name: '完整5日样本数', minInterval: 1 },
    series: comboBands.flatMap(band => [
      { name: `${band} 达标`, type: 'bar', stack: band, barWidth: 8, data: tradeDates.map(date => values.get(`${date}:${band}`)?.successCount || 0), itemStyle: { color: colors[band][0] } },
      { name: `${band} 未达标`, type: 'bar', stack: band, barWidth: 8, data: tradeDates.map(date => values.get(`${date}:${band}`)?.failureCount || 0), itemStyle: { color: colors[band][1] } }
    ])
  }, true)
}

async function getStatistics() {
  loading.value = true
  try {
    const response = await getDdeComboStatistics({ targetReturnPct: 1.8 })
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
