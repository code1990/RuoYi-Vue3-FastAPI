<template>
  <div class="stat-page">
    <el-alert title="模拟数据：仅统计信号后5个交易日内达到目标收益的股票。" type="info" :closable="false" show-icon />
    <el-card v-for="level in strengthLevels" :key="level.name" :header="`${level.name} DDE强度：达标股票数`" class="chart-row">
      <div :ref="element => setChartRef(level.name, element)" class="chart" />
    </el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'

const tradeDates = ['08-12', '08-13', '08-14', '08-15', '08-18', '08-19', '08-20', '08-21']
const strengthLevels = [
  { name: '0–5%', morning: [4, 5, 6, 7, 5, 8, 6, 9], noon: [3, 4, 4, 5, 4, 5, 5, 6], close: [5, 6, 7, 8, 6, 9, 8, 10] },
  { name: '5–15%', morning: [7, 9, 11, 13, 10, 15, 12, 16], noon: [5, 7, 8, 10, 8, 11, 9, 12], close: [8, 11, 14, 17, 14, 19, 16, 21] },
  { name: '15%+', morning: [1, 2, 3, 4, 3, 5, 4, 6], noon: [1, 1, 2, 2, 1, 3, 2, 3], close: [2, 3, 4, 5, 4, 6, 5, 7] }
]
const chartRefs = {}
const chartInstances = []

function setChartRef(name, element) {
  if (element) chartRefs[name] = element
}

function initCharts() {
  strengthLevels.forEach(level => {
    const chart = echarts.init(chartRefs[level.name])
    chart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['早盘', '午盘', '尾盘'] },
      grid: { left: 50, right: 20, top: 45, bottom: 45 },
      xAxis: { type: 'category', data: tradeDates, name: '交易日' },
      yAxis: { type: 'value', name: '达标股票数', minInterval: 1 },
      series: [
        { name: '早盘', type: 'bar', stack: 'success', data: level.morning, itemStyle: { color: '#409eff' } },
        { name: '午盘', type: 'bar', stack: 'success', data: level.noon, itemStyle: { color: '#e6a23c' } },
        { name: '尾盘', type: 'bar', stack: 'success', data: level.close, itemStyle: { color: '#67c23a' } }
      ]
    })
    chartInstances.push(chart)
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
.chart { height: 300px; }
</style>
