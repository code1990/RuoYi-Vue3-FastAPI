<template>
  <div class="stat-page">
    <el-card shadow="never">
      <el-form inline @submit.prevent>
        <el-form-item label="股票代码"><el-input v-model="stockCode" maxlength="6" clearable @keyup.enter="handleQuery" /></el-form-item>
        <el-form-item label="年份"><el-select v-model="query.year" clearable placeholder="全部" style="width: 120px" @change="handleQuery"><el-option label="全部年份" value="" /><el-option v-for="year in years" :key="year" :label="`${year}年`" :value="year" /></el-select></el-form-item>
        <el-form-item label="信号状态"><el-select v-model="query.signalStatus" style="width: 120px" @change="handleStatusChange"><el-option label="全部" value="all" /><el-option label="候选(≥2)" value="candidate" /><el-option label="达标" value="hit" /><el-option label="未达标" value="fail" /><el-option label="待完成" value="pending" /></el-select></el-form-item>
        <el-button type="primary" :loading="loading" @click="handleQuery">查询</el-button>
      </el-form>
      <el-alert v-if="errorMessage" :title="errorMessage" type="warning" :closable="false" show-icon />
      <div v-show="!errorMessage" ref="chartRef" v-loading="loading" class="chart" />
    </el-card>
    <el-card shadow="never" class="audit-card">
      <template #header><div class="audit-header"><span>KDJ双周期信号回测明细</span><span class="summary">候选 {{ summary.candidateCount }} ｜ 完成 {{ summary.completedCount }} ｜ 达标 {{ summary.hitCount }} ｜ 达标率 {{ rate(summary.hitRate) }}</span></div></template>
      <el-table v-loading="tableLoading" :data="rows" border stripe height="560" @sort-change="handleSortChange">
        <el-table-column label="交易日" prop="signalDate" width="100" sortable="custom" fixed="left" />
        <el-table-column label="股票" min-width="110" fixed="left"><template #default="{ row }">{{ row.stockCode }} {{ row.stockName }}</template></el-table-column>
        <el-table-column label="行业" prop="industryName" min-width="100" fixed="left" />
        <el-table-column label="概念" prop="concept" min-width="180" fixed="left" />
        <el-table-column label="技术状态" min-width="230"><template #default="{ row }"><div>{{ row.activeSignals || '-' }}</div><small>9(K/D/J): {{ metric(row, 'kdj9') }} · 90(K/D/J): {{ metric(row, 'kdj90') }}</small></template></el-table-column>
        <el-table-column label="六信号" prop="signalCode" width="82" />
        <el-table-column label="信号数" prop="signalCount" width="78" sortable="custom" />
        <el-table-column v-for="day in 5" :key="day" :label="`T+${day}最高`" :prop="`t${day}MaxReturnPct`" width="95"><template #default="{ row }"><span :class="returnClass(row[`t${day}MaxReturnPct`])">{{ percent(row[`t${day}MaxReturnPct`]) }}</span></template></el-table-column>
        <el-table-column v-for="day in 5" :key="`close-${day}`" :label="`T+${day}收盘`" :prop="`t${day}CloseReturnPct`" width="95"><template #default="{ row }">{{ percent(row[`t${day}CloseReturnPct`]) }}</template></el-table-column>
        <el-table-column label="5日最高" prop="maxReturnPct" width="95" sortable="custom"><template #default="{ row }"><span :class="returnClass(row.maxReturnPct)">{{ percent(row.maxReturnPct) }}</span></template></el-table-column>
        <el-table-column label="达标情况" width="100"><template #default="{ row }"><el-tag v-if="!row.isCompleted" type="warning" size="small">待完成</el-tag><el-tag v-else :type="row.targetHit ? 'success' : 'danger'" size="small">{{ row.targetHit ? '达标' : '未达标' }}</el-tag></template></el-table-column>
      </el-table>
      <pagination v-show="total > 0" v-model:page="query.pageNum" v-model:limit="query.pageSize" :total="total" @pagination="loadBacktest" />
    </el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { getKdjHistory, listKdjBacktest } from '@/api/stock/kdj'

const chartRef = ref()
const stockCode = ref('000001')
const loading = ref(false)
const errorMessage = ref('')
const tableLoading = ref(false)
const rows = ref([])
const total = ref(0)
const summary = reactive({ candidateCount: 0, completedCount: 0, hitCount: 0, hitRate: null })
const query = reactive({ year: '', signalStatus: 'all', pageNum: 1, pageSize: 20, sortBy: undefined, sortOrder: undefined })
const years = Array.from({ length: new Date().getFullYear() - 2019 }, (_, index) => new Date().getFullYear() - index)
let chart

function valueOf(row, camel, snake = camel) {
  return row[camel] ?? row[snake]
}

function formatDate(value) {
  const text = String(value)
  return text.length === 8 ? `${text.slice(4, 6)}-${text.slice(6)}` : text
}

function isGoldenCross(row) {
  return valueOf(row, 'goldenCross', 'golden_cross') === true || Number(valueOf(row, 'goldenCross', 'golden_cross')) === 1
}

function isSignal(row, camel, snake) {
  return valueOf(row, camel, snake) === true || Number(valueOf(row, camel, snake)) === 1
}

function roundKdj(value) {
  return value == null ? value : Math.round(Number(value) * 100) / 100
}

function fixed(value) {
  return value == null ? '--' : Number(value).toFixed(2)
}

function formatDateWithWeekday(value) {
  const text = String(value)
  const date = new Date(Number(text.slice(0, 4)), Number(text.slice(4, 6)) - 1, Number(text.slice(6)))
  return `${text.slice(0, 4)}/${text.slice(4, 6)}/${text.slice(6)}/${['日', '一', '二', '三', '四', '五', '六'][date.getDay()]}`
}

function formatAmount(value) {
  return value == null ? '--' : `${(Number(value) / 100000000).toFixed(2)}亿`
}

function renderChart(payload) {
  const candles = payload?.candles || []
  const indicators = payload?.indicators || []
  if (!candles.length) {
    errorMessage.value = '没有可显示的 K 线数据'
    return
  }
  const dates = candles.map(row => String(valueOf(row, 'tradeDate', 'trade_date')))
  const candleByDate = new Map(candles.map(candle => [String(valueOf(candle, 'tradeDate', 'trade_date')), candle]))
  const indicatorByKey = new Map(indicators.map(row => [`${valueOf(row, 'tradeDate', 'trade_date')}:${row.period}`, row]))
  const lineSeries = [9, 90].flatMap(period => ['K', 'D', 'J'].map((name, index) => ({
    name: `${period}${name}`,
    type: 'line',
    xAxisIndex: 1,
    yAxisIndex: 1,
    showSymbol: false,
    lineStyle: { width: 1.5, type: period === 90 ? 'dashed' : 'solid', color: period === 9 ? ['#409eff', '#67c23a', '#e6a23c'][index] : ['#8ec5ff', '#a9dca7', '#f4c98c'][index] },
    data: dates.map(date => roundKdj(valueOf(indicatorByKey.get(`${date}:${period}`) || {}, name.toLowerCase())))
  })))
  const goldenCrossSeries = [9, 90].map(period => ({
    name: `${period} 金叉`,
    type: 'scatter',
    xAxisIndex: 0,
    yAxisIndex: 0,
    symbol: 'pin',
    symbolSize: 30,
    itemStyle: { color: period === 9 ? '#f56c6c' : '#8e44ad' },
    label: { show: true, formatter: `金${period}`, color: '#fff', fontSize: 10 },
    data: candles.flatMap(candle => {
      const date = String(valueOf(candle, 'tradeDate', 'trade_date'))
      const indicator = indicatorByKey.get(`${date}:${period}`)
      return indicator && isGoldenCross(indicator) ? [[date, valueOf(candle, 'low')]] : []
    })
  }))
  const rsvCrossSeries = [9, 90].flatMap(period => [
    {
      name: `${period} K1`,
      type: 'scatter',
      xAxisIndex: 0,
      yAxisIndex: 0,
      symbol: 'arrow',
      symbolSize: [8, 20],
      symbolOffset: [period === 9 ? -5 : 5, 16],
      itemStyle: { color: '#f5222d' },
      data: candles.flatMap(candle => {
        const date = String(valueOf(candle, 'tradeDate', 'trade_date'))
        const indicator = indicatorByKey.get(`${date}:${period}`)
        return indicator && isSignal(indicator, 'rsvCrossK', 'rsv_cross_k') ? [[date, valueOf(candle, 'low')]] : []
      })
    },
    {
      name: `${period} K2`,
      type: 'scatter',
      xAxisIndex: 0,
      yAxisIndex: 0,
      symbol: 'arrow',
      symbolSize: [8, 20],
      symbolOffset: [period === 9 ? -5 : 5, -16],
      itemStyle: { color: '#f5222d' },
      data: candles.flatMap(candle => {
        const date = String(valueOf(candle, 'tradeDate', 'trade_date'))
        const indicator = indicatorByKey.get(`${date}:${period}`)
        return indicator && isSignal(indicator, 'rsvCrossD', 'rsv_cross_d') ? [[date, valueOf(candle, 'high')]] : []
      })
    }
  ])

  chart.setOption({
    animation: false,
    legend: { top: 4, data: ['K线', '9K', '9D', '9J', '90K', '90D', '90J', '9 金叉', '90 金叉'] },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: params => {
        const candle = candleByDate.get(String(params[0]?.axisValue))
        if (!candle) return ''
        const high = Number(valueOf(candle, 'high'))
        const low = Number(valueOf(candle, 'low'))
        const preClose = Number(valueOf(candle, 'preClose', 'pre_close'))
        const amplitude = Number.isFinite(preClose) && preClose ? (high - low) / preClose * 100 : null
        return [
          formatDateWithWeekday(valueOf(candle, 'tradeDate', 'trade_date')),
          `开盘：${fixed(valueOf(candle, 'open'))}`,
          `最高：${fixed(high)}`,
          `最低：${fixed(low)}`,
          `收盘：${fixed(valueOf(candle, 'close'))}`,
          `总量：${valueOf(candle, 'vol') == null ? '--' : Math.round(Number(valueOf(candle, 'vol'))).toLocaleString('zh-CN')}`,
          `换手：${fixed(valueOf(candle, 'volRate', 'vol_rate'))}%`,
          `总额：${formatAmount(valueOf(candle, 'amount'))}`,
          `振幅：${fixed(amplitude)}%`,
          `涨跌：${fixed(valueOf(candle, 'changes'))}`,
          `涨幅：${fixed(valueOf(candle, 'percent'))}%`
        ].join('<br/>')
      }
    },
    axisPointer: { link: [{ xAxisIndex: 'all' }] },
    grid: [
      { left: 60, right: 20, top: 42, height: '52%' },
      { left: 60, right: 20, top: '68%', bottom: 50 }
    ],
    xAxis: [
      { type: 'category', data: dates, boundaryGap: true, axisLabel: { formatter: formatDate }, axisPointer: { label: { formatter: params => formatDate(params.value) } } },
      { type: 'category', gridIndex: 1, data: dates, boundaryGap: true, axisLabel: { show: false } }
    ],
    yAxis: [
      { scale: true, splitArea: { show: true } },
      { gridIndex: 1, scale: true, name: 'KDJ' }
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: dates.length > 120 ? 100 - 12000 / dates.length : 0, end: 100 },
      { type: 'slider', xAxisIndex: [0, 1], bottom: 10 }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: candles.map(row => [valueOf(row, 'open'), valueOf(row, 'close'), valueOf(row, 'low'), valueOf(row, 'high')]),
        itemStyle: { color: '#ef5350', color0: '#26a69a', borderColor: '#ef5350', borderColor0: '#26a69a' }
      },
      ...goldenCrossSeries,
      ...rsvCrossSeries,
      ...lineSeries
    ]
  }, true)
}

async function loadChart() {
  if (!stockCode.value) return
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await getKdjHistory({ stockCode: stockCode.value, year: query.year || undefined })
    renderChart(response.data)
  } catch (error) {
    errorMessage.value = error.message || 'KDJ 数据加载失败'
  } finally {
    loading.value = false
  }
}

function handleQuery() { query.pageNum = 1; loadChart(); loadBacktest() }
function handleStatusChange() { query.pageNum = 1; loadBacktest() }
function handleSortChange({ prop, order }) { query.sortBy = order ? prop : undefined; query.sortOrder = order || undefined; query.pageNum = 1; loadBacktest() }
async function loadBacktest() {
  tableLoading.value = true
  try {
    const response = await listKdjBacktest({ ...query, stockCode: stockCode.value || undefined, year: query.year || undefined })
    rows.value = response.data.rows || []
    total.value = response.data.total || 0
    Object.assign(summary, response.data)
  } finally { tableLoading.value = false }
}
function percent(value) { return value == null ? '-' : `${Number(value).toFixed(2)}%` }
function rate(value) { return value == null ? '-' : `${(Number(value) * 100).toFixed(2)}%` }
function returnClass(value) { return value == null ? '' : Number(value) >= 1.8 ? 'return-high' : 'return-low' }
function metric(row, prefix) {
  const values = [row[`${prefix}K`], row[`${prefix}D`], row[`${prefix}J`]].map(value => value == null ? '-' : Number(value).toFixed(1))
  return `${values.join('/') } ${row[`${prefix}JTrend`] || 'flat'}`
}

onMounted(() => {
  chart = echarts.init(chartRef.value)
  loadChart(); loadBacktest()
  window.addEventListener('resize', chart.resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', chart.resize)
  chart.dispose()
})
</script>

<style scoped>
.stat-page { padding: 20px; }
.chart { height: 720px; margin-top: 12px; }
.audit-card { margin-top: 16px; }
.audit-header { display: flex; justify-content: space-between; align-items: center; }
.summary { color: #606266; font-size: 13px; }
.return-high { color: #f56c6c; font-weight: 600; }
.return-low { color: #67c23a; }
:deep(.el-table) { white-space: nowrap; }
</style>
