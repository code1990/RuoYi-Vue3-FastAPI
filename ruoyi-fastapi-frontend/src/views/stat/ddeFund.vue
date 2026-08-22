<template>
  <div class="stat-page">
    <el-alert title="模拟数据：仅统计信号后5个交易日内达到目标收益的股票。" type="info" :closable="false" show-icon />
    <el-card header="DDE强度 × 交易日：达标股票数" class="chart-row"><div ref="chartRef" class="chart" /></el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'

const chartRef = ref()
const tradeDates = ['08-12', '08-13', '08-14', '08-15', '08-18', '08-19', '08-20', '08-21']
const strengthLevels = [
  { name: '0–5%', morning: [4, 5, 6, 7, 5, 8, 6, 9], noon: [3, 4, 4, 5, 4, 5, 5, 6], close: [5, 6, 7, 8, 6, 9, 8, 10] },
  { name: '5–15%', morning: [7, 9, 11, 13, 10, 15, 12, 16], noon: [5, 7, 8, 10, 8, 11, 9, 12], close: [8, 11, 14, 17, 14, 19, 16, 21] },
  { name: '15%+', morning: [1, 2, 3, 4, 3, 5, 4, 6], noon: [1, 1, 2, 2, 1, 3, 2, 3], close: [2, 3, 4, 5, 4, 6, 5, 7] }
]
let chart

function initChart() {
  chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['早盘', '午盘', '尾盘'] },
    title: strengthLevels.map((level, index) => ({ text: level.name, left: 8, top: `${12 + index * 29}%`, textStyle: { fontSize: 13, fontWeight: 'normal' } })),
    grid: strengthLevels.map((_, index) => ({ left: 65, right: 20, top: `${8 + index * 31}%`, height: '20%' })),
    xAxis: strengthLevels.map((_, index) => ({ gridIndex: index, type: 'category', data: tradeDates, axisLabel: { show: index === 2 }, axisTick: { show: index === 2 }, axisLine: { show: index === 2 } })),
    yAxis: strengthLevels.map((_, index) => ({ gridIndex: index, type: 'value', name: '达标数', minInterval: 1 })),
    series: strengthLevels.flatMap((level, index) => [
      { name: '早盘', type: 'bar', stack: level.name, xAxisIndex: index, yAxisIndex: index, data: level.morning, itemStyle: { color: '#409eff' } },
      { name: '午盘', type: 'bar', stack: level.name, xAxisIndex: index, yAxisIndex: index, data: level.noon, itemStyle: { color: '#e6a23c' } },
      { name: '尾盘', type: 'bar', stack: level.name, xAxisIndex: index, yAxisIndex: index, data: level.close, itemStyle: { color: '#67c23a' } }
    ])
  })
}

onMounted(() => {
  initChart()
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
.chart { height: 760px; }
</style>
