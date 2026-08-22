<template>
  <div class="stat-page">
    <el-alert title="模拟数据：每根柱仅统计已完成5个交易日观察的信号；绿色为达标，红色为未达标。" type="info" :closable="false" show-icon />
    <el-card header="DDE强度 5%–8%：交易日 × 时段 5日结果" class="chart-row"><div ref="dateChart" class="chart" /></el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'

const dateChart = ref()
const tradeDates = ['08-12', '08-13', '08-14', '08-15', '08-18', '08-19', '08-20', '08-21']
const chartInstances = []

function createChart(element, option) {
  const chart = echarts.init(element)
  chart.setOption(option)
  chartInstances.push(chart)
}

function resultSeries(stack, success, failure) {
  const labels = { morning: '早盘', noon: '午盘', close: '尾盘' }
  return [
    { name: `${labels[stack]}达标`, type: 'bar', stack, data: success, itemStyle: { color: stack === 'morning' ? '#67c23a' : stack === 'noon' ? '#95d475' : '#c2e7b0' } },
    { name: `${labels[stack]}未达标`, type: 'bar', stack, data: failure, itemStyle: { color: stack === 'morning' ? '#f56c6c' : stack === 'noon' ? '#f89898' : '#fab6b6' } }
  ]
}

function initCharts() {
  createChart(dateChart.value, {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { top: 0 },
    grid: { left: 50, right: 20, top: 65, bottom: 45 },
    xAxis: { type: 'category', data: tradeDates, name: '交易日' },
    yAxis: { type: 'value', name: '完整5日样本数' },
    series: [
      ...resultSeries('morning', [7, 9, 11, 13, 10, 15, 12, 16], [9, 8, 10, 7, 9, 6, 8, 6]),
      ...resultSeries('noon', [5, 7, 8, 10, 8, 11, 9, 12], [10, 9, 11, 8, 10, 7, 9, 8]),
      ...resultSeries('close', [8, 11, 14, 17, 14, 19, 16, 21], [7, 6, 8, 5, 7, 5, 6, 5])
    ]
  })
}

function resizeCharts() { chartInstances.forEach(chart => chart.resize()) }

onMounted(() => {
  initCharts()
  window.addEventListener('resize', resizeCharts)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts)
  chartInstances.forEach(chart => chart.dispose())
})
</script>

<style scoped>
.stat-page { padding: 20px; }
.chart-row { margin-top: 16px; }
.chart { height: 400px; }
</style>
