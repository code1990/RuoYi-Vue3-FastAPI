<template><div class="stat-page"><el-alert title="仅统计融资融券列表：按融资参与度分组；完整5日样本中，任一天最高收益≥1.8%为达标。" type="info" :closable="false" show-icon /><el-card header="融资参与度与5日结果" class="chart-row"><div ref="chartRef" v-loading="loading" class="chart" /></el-card></div></template>
<script setup>
import * as echarts from 'echarts'
import { getMarginComboStatistics, getMarginLongStatistics } from '@/api/stock/marginTrading'
const chartRef = ref(); const loading = ref(false)
const route = useRoute(); const windowDays = computed(() => [2, 3, 5].includes(Number(route.query.windowDays)) ? Number(route.query.windowDays) : 0)
const bands = [{ key: '10%以下', colors: ['#67c23a', '#b3e19d'] }, { key: '10-20%', colors: ['#e6a23c', '#f3d19e'] }, { key: '20%+', colors: ['#f56c6c', '#fab6b6'] }]
let chart
function renderChart(rows) {
  const dates = [...new Set(rows.map(row => row.signalDate))].sort().slice(-30); const values = new Map(rows.map(row => [`${row.signalDate}:${row.participationBand}`, row]))
  chart.setOption({ tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } }, legend: { top: 0 }, grid: { left: 60, right: 20, top: 55, bottom: 72 }, xAxis: { type: 'category', data: dates, axisLabel: { interval: 0, formatter: value => `${value.slice(4, 6)}-${value.slice(6)}` } }, yAxis: { type: 'value', name: '完整5日样本数', minInterval: 1 }, series: bands.flatMap(band => [{ name: `${band.key} 达标`, type: 'bar', stack: band.key, barWidth: 8, data: dates.map(date => values.get(`${date}:${band.key}`)?.successCount || 0), itemStyle: { color: band.colors[0] } }, { name: `${band.key} 未达标`, type: 'bar', stack: band.key, barWidth: 8, data: dates.map(date => values.get(`${date}:${band.key}`)?.failureCount || 0), itemStyle: { color: band.colors[1] } }]) }, true)
}
async function getStatistics() { loading.value = true; try { const getStatistics = windowDays.value ? getMarginComboStatistics : getMarginLongStatistics; renderChart((await getStatistics({ targetReturnPct: 1.8, windowDays: windowDays.value || undefined })).data) } finally { loading.value = false } }
onMounted(() => { chart = echarts.init(chartRef.value); getStatistics(); window.addEventListener('resize', chart.resize) })
onBeforeUnmount(() => { window.removeEventListener('resize', chart.resize); chart.dispose() })
watch(windowDays, getStatistics)
</script>
<style scoped>.stat-page { padding: 20px; }.chart-row { margin-top: 16px; }.chart { height: 560px; }</style>
