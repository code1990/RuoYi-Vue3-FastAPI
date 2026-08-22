<template>
  <div class="stat-page">
    <el-alert title="DDE收益列表可视化：与量化回测 DDE资金列表一致；5日内最高收益≥1.8%为达标。" type="info" :closable="false" show-icon />
    <el-card header="DDE强度、时段与5日结果" class="chart-row"><div ref="chartRef" v-loading="loading" class="chart" /></el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { getDdeStatistics } from '@/api/stock/ddeFund'

const chartRef = ref()
const loading = ref(false)
const periods = [{ key: 'morning', label: '早盘' }, { key: 'noon', label: '午盘' }, { key: 'close', label: '尾盘' }]
const strengthBands = ['0-5%', '5-15%', '15%+']
const colors = { '0-5%': ['#67c23a', '#b3e19d'], '5-15%': ['#e6a23c', '#f3d19e'], '15%+': ['#f56c6c', '#fab6b6'] }
let chart

function renderChart(rows) {
  const tradeDates = [...new Set(rows.map(row => row.trade_date))].sort().slice(-30)
  const values = new Map(rows.map(row => [`${row.trade_date}:${row.signal_slot}:${row.strength_band}`, row]))
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { top: 0 },
    grid: { left: 60, right: 20, top: 55, bottom: 72 },
    xAxis: { type: 'category', data: tradeDates, axisLabel: { interval: 0, formatter: value => `${value.slice(4, 6)}-${value.slice(6)}` } },
    yAxis: { type: 'value', name: '完整5日样本数', minInterval: 1 },
    series: strengthBands.flatMap(strength => periods.flatMap(period => [
      { name: `${strength} 达标`, type: 'bar', stack: period.key, barWidth: 5, data: tradeDates.map(date => values.get(`${date}:${period.key}:${strength}`)?.success_count || 0), itemStyle: { color: colors[strength][0] } },
      { name: `${strength} 未达标`, type: 'bar', stack: period.key, barWidth: 5, data: tradeDates.map(date => values.get(`${date}:${period.key}:${strength}`)?.failure_count || 0), itemStyle: { color: colors[strength][1] } }
    ]))
  }, true)
}

async function getStatistics() {
  loading.value = true
  try {
    const response = await getDdeStatistics({ targetReturnPct: 1.8 })
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
