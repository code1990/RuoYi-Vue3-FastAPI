<template>
  <div class="algorithm-page">
    <el-alert title="二分法首个条件：DDE资金强度是否达到15%；5日内最高收益≥1.8%为达标，不含涨停样本。" type="info" :closable="false" show-icon />
    <el-card header="DDE强度二分结果" class="chart-row"><div ref="chartRef" v-loading="loading" class="chart" /></el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { getDdeStatistics } from '@/api/stock/ddeFund'

const chartRef = ref()
const loading = ref(false)
const slots = [{ key: 'morning', label: '早盘' }, { key: 'noon', label: '午盘' }, { key: 'close', label: '尾盘' }]
let chart

function renderChart(rows) {
  const values = new Map()
  slots.forEach(({ key }) => {
    values.set(`${key}:低强度`, { success: 0, failure: 0 })
    values.set(`${key}:高强度`, { success: 0, failure: 0 })
  })
  rows.forEach(row => {
    const branch = row.strength_band === '15%+' ? '高强度' : '低强度'
    const value = values.get(`${row.signal_slot}:${branch}`)
    if (value) {
      value.success += row.success_count
      value.failure += row.failure_count
    }
  })
  const categories = slots.flatMap(({ label }) => [`${label}\n<15%`, `${label}\n≥15%`])
  const branches = slots.flatMap(({ key }) => [`${key}:低强度`, `${key}:高强度`])
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { top: 0 },
    grid: { left: 100, right: 24, top: 52, bottom: 24 },
    xAxis: { type: 'value', name: '完整5日样本数', minInterval: 1 },
    yAxis: { type: 'category', inverse: true, data: categories, axisLabel: { lineHeight: 18 } },
    series: [
      { name: '达标', type: 'bar', stack: 'sample', data: branches.map(key => values.get(key).success), itemStyle: { color: '#f56c6c' } },
      { name: '未达标', type: 'bar', stack: 'sample', data: branches.map(key => values.get(key).failure), itemStyle: { color: '#909399' } }
    ]
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
.algorithm-page { padding: 20px; }
.chart-row { margin-top: 16px; }
.chart { height: 560px; }
</style>
