<template>
  <div class="app-container future-overview">
    <el-alert title="研究观察，非投资建议。指标仅基于已同步的日线、基差、仓单与持仓数据。" type="info" :closable="false" show-icon />
    <el-card shadow="never" class="toolbar"><el-form inline><el-form-item label="合约序列"><el-select v-model="thscode" filterable placeholder="选择连续、主力或指数合约" class="series-select"><el-option v-for="item in series" :key="item.thscode" :value="item.thscode" :label="`${item.thscode}｜${item.series_name || item.product_code}`" /></el-select></el-form-item><el-form-item><el-button :loading="loading" type="primary" @click="load">刷新</el-button></el-form-item></el-form></el-card>
    <el-row :gutter="16" class="metrics">
      <el-col :xs="24" :sm="12" :lg="6"><el-card shadow="never"><el-statistic title="最新收盘" :value="latest.close_price ?? 0" :precision="2" /><small>{{ latest.trade_date || '-' }}</small></el-card></el-col>
      <el-col :xs="24" :sm="12" :lg="6"><el-card shadow="never"><el-statistic title="收盘基差" :value="basis.close_basis ?? 0" :precision="2" /><small>{{ basis.trade_date || '-' }}｜{{ basis.thscode || '-' }}</small></el-card></el-col>
      <el-col :xs="24" :sm="12" :lg="6"><el-card shadow="never"><el-statistic title="仓单变化" :value="warehouse.amount_change ?? 0" :precision="0" /><small>{{ warehouse.trade_date || '-' }}｜仓单 {{ display(warehouse.amount) }}</small></el-card></el-col>
      <el-col :xs="24" :sm="12" :lg="6"><el-card shadow="never"><el-statistic title="净持仓变化" :value="position.net_position_change ?? 0" :precision="0" /><small>{{ position.company_name || '-' }}｜{{ position.trade_date || '-' }}</small></el-card></el-col>
    </el-row>
    <el-card v-loading="loading" shadow="never" class="chart-card"><template #header><span>{{ title }} 日 K 与成交量</span><span class="role">{{ roleLabel }}</span></template><div ref="chartRef" class="chart" /><el-empty v-if="!loading && !bars.length" description="暂无已同步的日线数据" :image-size="70" /></el-card>
    <el-row :gutter="16">
      <el-col :xs="24" :lg="12"><el-card shadow="never" header="最新基差"><el-descriptions :column="2" border><el-descriptions-item label="合约">{{ basis.thscode || '-' }}</el-descriptions-item><el-descriptions-item label="交易日">{{ basis.trade_date || '-' }}</el-descriptions-item><el-descriptions-item label="现货价">{{ display(basis.spot_price) }}</el-descriptions-item><el-descriptions-item label="主连收盘">{{ display(basis.close_price) }}</el-descriptions-item><el-descriptions-item label="收盘基差">{{ display(basis.close_basis) }}</el-descriptions-item><el-descriptions-item label="基差率">{{ percent(basis.close_basis_rate) }}</el-descriptions-item></el-descriptions></el-card></el-col>
      <el-col :xs="24" :lg="12"><el-card shadow="never" header="仓单与公司持仓"><el-descriptions :column="2" border><el-descriptions-item label="仓单合约">{{ warehouse.thscode || '-' }}</el-descriptions-item><el-descriptions-item label="仓单日期">{{ warehouse.trade_date || '-' }}</el-descriptions-item><el-descriptions-item label="仓单数量">{{ display(warehouse.amount) }}</el-descriptions-item><el-descriptions-item label="等效手数">{{ display(warehouse.equivalent_lots) }}</el-descriptions-item><el-descriptions-item label="持仓公司">{{ position.company_name || '-' }}</el-descriptions-item><el-descriptions-item label="净持仓">{{ display(position.net_position) }}</el-descriptions-item></el-descriptions></el-card></el-col>
    </el-row>
  </div>
</template>

<script setup name="FutureOverview">
import * as echarts from 'echarts'
import { listFutureHistoryDaily, listFutureHistorySeries, listFutureBasis, listFutureCatalog, listFutureResearch } from '@/api/future/history'

const chartRef = ref(), chart = ref(), loading = ref(false), series = ref([]), thscode = ref(''), bars = ref([]), roles = ref([]), bases = ref([]), warehouses = ref([]), positions = ref([])
const current = computed(() => series.value.find(item => item.thscode === thscode.value) || {})
const title = computed(() => `${thscode.value || '期货'}｜${current.value.series_name || current.value.product_code || ''}`)
const relatedRole = computed(() => roles.value.find(item => item.thscode === thscode.value) || roles.value.find(item => item.variety_code === current.value.product_code && item.role_type === 'main_continuous') || {})
const roleLabel = computed(() => ({ main_continuous: '主连', main: '主力', secondary_main: '次主力', commodity_index: '商品指数' })[relatedRole.value.role_type] || '-')
const latest = computed(() => bars.value.at(-1) || {})
const basis = computed(() => bases.value.find(item => item.thscode === relatedRole.value.thscode) || bases.value.find(item => item.thscode === thscode.value) || {})
const warehouse = computed(() => warehouses.value.find(item => item.thscode === relatedRole.value.thscode) || warehouses.value.find(item => item.thscode === thscode.value) || {})
const position = computed(() => positions.value.find(item => item.thscode === relatedRole.value.thscode) || positions.value.find(item => item.thscode === thscode.value) || {})

function display(value) { return value === null || value === undefined ? '-' : Number(value).toLocaleString('zh-CN', { maximumFractionDigits: 2 }) }
function percent(value) { return value === null || value === undefined ? '-' : `${(Number(value) * 100).toFixed(2)}%` }
function renderChart() {
  if (!chartRef.value) return
  chart.value ||= echarts.init(chartRef.value)
  const data = bars.value.slice(-180)
  chart.value.setOption({ animation: false, tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } }, axisPointer: { link: [{ xAxisIndex: 'all' }] }, grid: [{ left: 56, right: 20, top: 28, height: '56%' }, { left: 56, right: 20, top: '73%', height: '15%' }], xAxis: [{ type: 'category', data: data.map(row => row.trade_date), boundaryGap: false, axisLine: { onZero: false } }, { type: 'category', gridIndex: 1, data: data.map(row => row.trade_date), boundaryGap: false, axisLabel: { show: false }, axisTick: { show: false }, axisLine: { show: false } }], yAxis: [{ scale: true, splitArea: { show: true } }, { scale: true, gridIndex: 1, splitNumber: 2 }], dataZoom: [{ type: 'inside', xAxisIndex: [0, 1], start: 55, end: 100 }, { show: true, xAxisIndex: [0, 1], bottom: 8, start: 55, end: 100 }], series: [{ name: '日K', type: 'candlestick', data: data.map(row => [row.open_price, row.close_price, row.low_price, row.high_price]) }, { name: '成交量', type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: data.map(row => ({ value: row.volume, itemStyle: { color: Number(row.close_price) >= Number(row.open_price) ? '#ef5350' : '#26a69a' } })) }] }, true)
}
async function load() { if (!thscode.value) return; loading.value = true; try { bars.value = (await listFutureHistoryDaily(thscode.value)).data?.reverse() || []; renderChart() } finally { loading.value = false } }
async function bootstrap() {
  loading.value = true
  try {
    const [seriesResponse, rolesResponse, basisResponse, warehouseResponse, positionResponse] = await Promise.all([listFutureHistorySeries(), listFutureCatalog('roles'), listFutureBasis(), listFutureResearch('warehouse'), listFutureResearch('positions')])
    series.value = seriesResponse.data || []; roles.value = rolesResponse.data || []; bases.value = basisResponse.data || []; warehouses.value = warehouseResponse.data || []; positions.value = positionResponse.data || []; thscode.value = series.value[0]?.thscode || ''
  } finally { loading.value = false }
}
watch(thscode, load)
function resizeChart() { chart.value?.resize() }
onMounted(() => { bootstrap(); window.addEventListener('resize', resizeChart) })
onBeforeUnmount(() => { window.removeEventListener('resize', resizeChart); chart.value?.dispose() })
</script>

<style scoped>
.future-overview { padding: 20px; }.toolbar,.chart-card { margin-top: 16px; }.series-select { width: 340px; }.metrics { margin: 16px 0; }.metrics small { color: var(--el-text-color-secondary); }.chart-card :deep(.el-card__header) { display:flex; justify-content:space-between; }.role { color: var(--el-text-color-secondary); font-size: 13px; }.chart { height: 560px; }
</style>
