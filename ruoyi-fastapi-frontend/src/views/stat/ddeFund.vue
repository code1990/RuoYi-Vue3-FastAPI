<template>
  <div class="stat-page">
    <el-alert title="模拟数据：每个交易日的三根柱固定按早盘、午盘、尾盘顺序排列。" type="info" :closable="false" show-icon />
    <el-card header="DDE强度、时段与5日结果" class="chart-row"><div ref="chartRef" class="chart" /></el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'

const chartRef = ref()
const tradeDates = ['08-12', '08-13', '08-14', '08-15', '08-18', '08-19', '08-20', '08-21']
const periods = ['早盘', '午盘', '尾盘']
const source = {
  '0–5%': { success: [[4, 5, 6, 7, 5, 8, 6, 9], [3, 4, 4, 5, 4, 5, 5, 6], [5, 6, 7, 8, 6, 9, 8, 10]], failure: [[8, 9, 7, 8, 9, 7, 8, 6], [9, 8, 10, 7, 9, 8, 9, 7], [7, 6, 8, 5, 7, 5, 6, 5]] },
  '5–15%': { success: [[7, 9, 11, 13, 10, 15, 12, 16], [5, 7, 8, 10, 8, 11, 9, 12], [8, 11, 14, 17, 14, 19, 16, 21]], failure: [[6, 5, 7, 4, 6, 3, 5, 3], [7, 6, 8, 5, 7, 4, 6, 4], [5, 4, 6, 3, 5, 2, 4, 2]] },
  '15%+': { success: [[1, 2, 3, 4, 3, 5, 4, 6], [1, 1, 2, 2, 1, 3, 2, 3], [2, 3, 4, 5, 4, 6, 5, 7]], failure: [[3, 3, 2, 3, 3, 2, 3, 2], [4, 3, 4, 3, 4, 3, 4, 3], [2, 2, 3, 2, 3, 2, 2, 1]] }
}
const colors = { '0–5%': ['#67c23a', '#b3e19d'], '5–15%': ['#e6a23c', '#f3d19e'], '15%+': ['#f56c6c', '#fab6b6'] }
let chart

function initChart() {
  chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { top: 0 },
    grid: { left: 60, right: 20, top: 55, bottom: 72 },
    xAxis: {
      type: 'category',
      data: tradeDates,
      axisLabel: { interval: 0 }
    },
    yAxis: { type: 'value', name: '完整5日样本数', minInterval: 1 },
    series: Object.entries(source).flatMap(([strength, result]) => periods.flatMap((period, periodIndex) => [
      { name: `${strength} 达标`, type: 'bar', stack: period, barWidth: 5, data: result.success[periodIndex], itemStyle: { color: colors[strength][0] } },
      { name: `${strength} 未达标`, type: 'bar', stack: period, barWidth: 5, data: result.failure[periodIndex], itemStyle: { color: colors[strength][1] } }
    ]))
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
.chart { height: 560px; }
</style>
