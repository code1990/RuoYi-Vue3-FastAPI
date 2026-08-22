<template>
  <div class="stat-page">
    <el-alert title="当前为模拟数据，仅用于确认统计图表口径；暂未读取后端数据。" type="info" :closable="false" show-icon />
    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :lg="14"><el-card header="5日达标率：按DDE强度与时段"><div ref="rateChart" class="chart" /></el-card></el-col>
      <el-col :xs="24" :lg="10"><el-card header="样本数量：避免小样本高胜率"><div ref="countChart" class="chart" /></el-card></el-col>
    </el-row>
    <el-card header="交易日 × DDE强度：5日达标率热力图" class="chart-row"><div ref="heatmapChart" class="heatmap" /></el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'

const rateChart = ref()
const countChart = ref()
const heatmapChart = ref()
const strengthBins = ['<1%', '1–3%', '3–5%', '5–8%', '8–12%', '≥12%']
const tradeDates = ['08-12', '08-13', '08-14', '08-15', '08-18', '08-19', '08-20', '08-21']
const chartInstances = []

function createChart(element, option) {
  const chart = echarts.init(element)
  chart.setOption(option)
  chartInstances.push(chart)
}

function initCharts() {
  createChart(rateChart.value, {
    tooltip: { trigger: 'axis', valueFormatter: value => `${value}%` },
    legend: { data: ['早盘', '午盘', '尾盘'] },
    grid: { left: 48, right: 20, top: 45, bottom: 45 },
    xAxis: { type: 'category', data: strengthBins, name: 'DDE强度' },
    yAxis: { type: 'value', name: '5日达标率', min: 0, max: 100, axisLabel: { formatter: '{value}%' } },
    series: [
      { name: '早盘', type: 'line', smooth: true, data: [31, 42, 51, 60, 66, 58] },
      { name: '午盘', type: 'line', smooth: true, data: [28, 39, 48, 55, 61, 54] },
      { name: '尾盘', type: 'line', smooth: true, data: [35, 47, 59, 68, 72, 63] }
    ]
  })
  createChart(countChart.value, {
    tooltip: { trigger: 'axis' },
    grid: { left: 42, right: 15, top: 25, bottom: 45 },
    xAxis: { type: 'category', data: strengthBins },
    yAxis: { type: 'value', name: '股票数' },
    series: [{ type: 'bar', data: [286, 431, 362, 218, 96, 41], itemStyle: { color: '#409eff' } }]
  })
  createChart(heatmapChart.value, {
    tooltip: { position: 'top', formatter: params => `${tradeDates[params.value[0]]}<br>${strengthBins[params.value[1]]}<br>达标率：${params.value[2]}%` },
    grid: { left: 70, right: 35, top: 20, bottom: 70 },
    xAxis: { type: 'category', data: tradeDates, splitArea: { show: true } },
    yAxis: { type: 'category', data: strengthBins, splitArea: { show: true } },
    visualMap: { min: 20, max: 80, calculable: true, orient: 'horizontal', left: 'center', bottom: 5, inRange: { color: ['#e8f3ff', '#91cc75', '#f7ba2a', '#ee6666'] } },
    series: [{ type: 'heatmap', label: { show: true, formatter: params => `${params.value[2]}%` }, data: [
      [0, 0, 27], [1, 0, 31], [2, 0, 29], [3, 0, 35], [4, 0, 33], [5, 0, 36], [6, 0, 30], [7, 0, 38],
      [0, 1, 39], [1, 1, 42], [2, 1, 45], [3, 1, 41], [4, 1, 49], [5, 1, 46], [6, 1, 43], [7, 1, 51],
      [0, 2, 48], [1, 2, 52], [2, 2, 50], [3, 2, 56], [4, 2, 54], [5, 2, 58], [6, 2, 55], [7, 2, 61],
      [0, 3, 57], [1, 3, 62], [2, 3, 60], [3, 3, 66], [4, 3, 63], [5, 3, 69], [6, 3, 65], [7, 3, 71],
      [0, 4, 61], [1, 4, 68], [2, 4, 65], [3, 4, 72], [4, 4, 69], [5, 4, 75], [6, 4, 70], [7, 4, 74],
      [0, 5, 53], [1, 5, 60], [2, 5, 57], [3, 5, 64], [4, 5, 59], [5, 5, 67], [6, 5, 62], [7, 5, 66]
    ] }]
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
.chart { height: 340px; }
.heatmap { height: 430px; }
</style>
