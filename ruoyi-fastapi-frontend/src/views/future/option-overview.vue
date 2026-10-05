<template>
  <div class="app-container option-overview">
    <el-alert title="研究观察，非投资建议。日 K 在查询时更新；联动统计仅使用同交易日有效样本。" type="info" :closable="false" show-icon />
    <el-card shadow="never" class="toolbar"><el-form inline><el-form-item label="标的"><el-select v-model="underlyingCode" filterable class="code-input" @change="loadContracts"><el-option v-for="item in underlyings" :key="item.underlyingCode" :value="item.underlyingCode" :label="`${item.underlyingCode}｜${item.name || ''}`" /></el-select></el-form-item><el-form-item label="期权合约"><el-select v-model="thscode" filterable class="contract-select"><el-option v-for="item in contracts" :key="item.thscode" :value="item.thscode" :label="`${item.thscode}｜${item.name || ''}`" /></el-select></el-form-item><el-form-item><el-button :loading="loading" type="primary" @click="load">更新决策数据</el-button></el-form-item></el-form></el-card>
    <el-row :gutter="16" class="metrics"><el-col :xs="24" :sm="8"><el-card shadow="never"><el-statistic title="最新收盘" :value="latest.close_price ?? 0" :precision="3" /><small>{{ date(latest.timestamp) }}</small></el-card></el-col><el-col :xs="24" :sm="8"><el-card shadow="never"><el-statistic title="日内最新价" :value="intraday.price ?? 0" :precision="3" /><small>{{ time(intraday.timestamp) }}</small></el-card></el-col><el-col :xs="24" :sm="8"><el-card shadow="never"><el-statistic title="成交量" :value="latest.volume ?? 0" :precision="0" /><small>{{ latest.turnover ?? '-' }} 成交额</small></el-card></el-col></el-row>
    <el-card v-loading="loading" shadow="never" class="chart-card"><template #header>{{ thscode }} 日 K 与成交量</template><div ref="chartRef" class="chart" /><el-empty v-if="!loading && !bars.length" description="暂无日线数据" :image-size="70" /></el-card>
    <el-card shadow="never" class="summary-card"><template #header>期权—期货联动摘要</template><el-table :data="summary" size="small"><el-table-column prop="contractCode" label="标的期货" /><el-table-column prop="lastPx" label="最新价" /><el-table-column label="涨跌幅"><template #default="{ row }">{{ percent(row.pxChangeRate) }}</template></el-table-column><el-table-column label="看涨期权"><template #default="{ row }">{{ signal(row.call) }}</template></el-table-column><el-table-column label="看跌期权"><template #default="{ row }">{{ signal(row.put) }}</template></el-table-column></el-table></el-card>
  </div>
</template>

<script setup name="OptionOverview">
import * as echarts from 'echarts'
import { getMarketOptionDailyResearch, getMarketOptionIntraday, getOptionChain, listOptionLinkageSummary, listOptionUnderlyings } from '@/api/future/option'

const thscode = ref('IO2610-C-4000.CFE'), underlyingCode = ref('IO2610'), underlyings = ref([]), contracts = ref([]), loading = ref(false), bars = ref([]), intraday = ref({}), summary = ref([]), chartRef = ref(), chart = ref()
const latest = computed(() => bars.value.at(-1) || {})
function date(value) { return value ? new Date(value).toLocaleDateString('zh-CN') : '-' }
function time(value) { return value ? new Date(value).toLocaleString('zh-CN', { hour12: false }) : '-' }
function percent(value) { return value === null || value === undefined ? '-' : `${Number(value) > 0 ? '+' : ''}${Number(value).toFixed(2)}%` }
function signal(value) { return value ? `顺趋势 ${Number(value.rate).toFixed(0)}%（${value.aligned}/${value.total}）` : '样本不足' }
function render() { if (!chartRef.value) return; chart.value ||= echarts.init(chartRef.value); const rows = bars.value.slice(-180); chart.value.setOption({ animation: false, tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } }, grid: [{ left: 56, right: 20, top: 28, height: '56%' }, { left: 56, right: 20, top: '73%', height: '15%' }], xAxis: [{ type: 'category', data: rows.map(row => date(row.timestamp)), boundaryGap: false }, { type: 'category', gridIndex: 1, data: rows.map(row => date(row.timestamp)), axisLabel: { show: false }, axisTick: { show: false }, axisLine: { show: false } }], yAxis: [{ scale: true, splitArea: { show: true } }, { scale: true, gridIndex: 1, splitNumber: 2 }], dataZoom: [{ type: 'inside', xAxisIndex: [0, 1], start: 55, end: 100 }, { show: true, xAxisIndex: [0, 1], bottom: 8, start: 55, end: 100 }], series: [{ name: '日K', type: 'candlestick', data: rows.map(row => [row.open_price, row.close_price, row.low_price, row.high_price]) }, { name: '成交量', type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: rows.map(row => row.volume) }] }, true) }
async function load() { loading.value = true; try { const [daily, minute, linkage] = await Promise.all([getMarketOptionDailyResearch(thscode.value), getMarketOptionIntraday(thscode.value), listOptionLinkageSummary()]); bars.value = (daily.data?.item || []).slice().sort((a, b) => a.timestamp - b.timestamp); intraday.value = (minute.data?.item || []).at(-1) || {}; summary.value = linkage.data || []; render() } finally { loading.value = false } }
async function loadContracts() { const response = await getOptionChain(underlyingCode.value); contracts.value = response.data?.rows || []; thscode.value = contracts.value[0]?.thscode || ''; if (thscode.value) load() }
function resize() { chart.value?.resize() }
onMounted(async () => { underlyings.value = (await listOptionUnderlyings()).data || []; if (!underlyings.value.some(item => item.underlyingCode === underlyingCode.value)) underlyingCode.value = underlyings.value[0]?.underlyingCode || ''; if (underlyingCode.value) await loadContracts(); window.addEventListener('resize', resize) })
onBeforeUnmount(() => { window.removeEventListener('resize', resize); chart.value?.dispose() })
</script>

<style scoped>
.option-overview { padding: 20px; }.toolbar,.chart-card,.summary-card { margin-top: 16px; }.code-input { width: 220px; }.contract-select { width: 360px; }.metrics { margin: 16px 0; }.metrics small { color: var(--el-text-color-secondary); }.chart { height: 560px; }
</style>
