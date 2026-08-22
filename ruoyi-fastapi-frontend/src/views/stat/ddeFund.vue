<template>
  <div class="stat-page">
    <el-alert title="模拟数据：每个交易日的三根柱固定按早盘、午盘、尾盘顺序排列。" type="info" :closable="false" show-icon />
    <el-card header="DDE强度、时段与5日结果" class="chart-row"><div ref="chartRef" class="chart" /></el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'

const chartRef = ref()
const tradeDates = ['07-13', '07-14', '07-15', '07-16', '07-17', '07-20', '07-21', '07-22', '07-23', '07-24', '07-27', '07-28', '07-29', '07-30', '07-31', '08-03', '08-04', '08-05', '08-06', '08-07', '08-10', '08-11', '08-12', '08-13', '08-14', '08-17', '08-18', '08-19', '08-20', '08-21']
const periods = ['早盘', '午盘', '尾盘']
function mockValues(base, phase) { return tradeDates.map((_, index) => Math.max(1, base + ((index * 5 + phase) % 7) - 3)) }
const source = {
  '0–5%': { success: [mockValues(6, 0), mockValues(5, 1), mockValues(7, 2)], failure: [mockValues(8, 3), mockValues(9, 4), mockValues(7, 5)] },
  '5–15%': { success: [mockValues(12, 1), mockValues(9, 2), mockValues(15, 3)], failure: [mockValues(5, 4), mockValues(6, 5), mockValues(4, 6)] },
  '15%+': { success: [mockValues(4, 2), mockValues(3, 3), mockValues(5, 4)], failure: [mockValues(3, 5), mockValues(4, 6), mockValues(2, 0)] }
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
