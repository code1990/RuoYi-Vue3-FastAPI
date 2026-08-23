<template>
  <div class="stat-page">
    <el-alert :title="`仅展示当前热度榜前30名股票；统计区间：${rangeText}。横向堆叠为早盘、午盘、尾盘的DDE出现次数。`" type="info" :closable="false" show-icon />
    <el-card header="DDE热度前30股票" class="chart-row"><div ref="chartRef" v-loading="loading" class="chart" /></el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { listDdeHotRank } from '@/api/stock/ddeFund'

const chartRef = ref()
const loading = ref(false)
const rangeText = ref('-')
let chart

function renderChart(rows) {
  const names = rows.map(row => `${row.rankNo}. ${row.stockCode} ${row.stockName}`)
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { top: 0 },
    grid: { left: 130, right: 30, top: 50, bottom: 20 },
    xAxis: { type: 'value', name: 'DDE出现次数', minInterval: 1 },
    yAxis: { type: 'category', inverse: true, data: names, axisLabel: { fontSize: 12 } },
    series: [
      { name: '早盘', type: 'bar', stack: 'count', data: rows.map(row => row.morningCount), itemStyle: { color: '#67c23a' } },
      { name: '午盘', type: 'bar', stack: 'count', data: rows.map(row => row.noonCount), itemStyle: { color: '#e6a23c' } },
      { name: '尾盘', type: 'bar', stack: 'count', data: rows.map(row => row.closeCount), itemStyle: { color: '#f56c6c' } }
    ]
  }, true)
}

async function getStatistics() {
  loading.value = true
  try {
    const response = await listDdeHotRank({ pageNum: 1, pageSize: 30 })
    const data = response.data
    rangeText.value = data.statStartDate ? `${data.statStartDate} 至 ${data.statEndDate}` : '-'
    renderChart(data.rows)
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
.chart { height: 900px; }
</style>
