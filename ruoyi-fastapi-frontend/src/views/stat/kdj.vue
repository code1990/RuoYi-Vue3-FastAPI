<template>
  <div class="stat-page">
    <el-card>
      <el-form inline @submit.prevent>
        <el-form-item label="股票代码">
          <el-input v-model="stockCode" maxlength="6" clearable @keyup.enter="loadChart" />
        </el-form-item>
        <el-button type="primary" :loading="loading" @click="loadChart">查询</el-button>
      </el-form>
      <el-alert v-if="errorMessage" :title="errorMessage" type="warning" :closable="false" show-icon />
      <div v-show="!errorMessage" ref="chartRef" v-loading="loading" class="chart" />
    </el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { getKdjHistory } from '@/api/stock/kdj'

const chartRef = ref()
const stockCode = ref('000001')
const loading = ref(false)
const errorMessage = ref('')
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

function renderChart(payload) {
  const candles = payload?.candles || []
  const indicators = payload?.indicators || []
  if (!candles.length) {
    errorMessage.value = '没有可显示的 K 线数据'
    return
  }
  const dates = candles.map(row => String(valueOf(row, 'tradeDate', 'trade_date')))
  const indicatorByKey = new Map(indicators.map(row => [`${valueOf(row, 'tradeDate', 'trade_date')}:${row.period}`, row]))
  const lineSeries = [9, 90].flatMap(period => ['K', 'D', 'J'].map((name, index) => ({
    name: `${period}${name}`,
    type: 'line',
    xAxisIndex: 1,
    yAxisIndex: 1,
    showSymbol: false,
    lineStyle: { width: 1.5, type: period === 90 ? 'dashed' : 'solid', color: period === 9 ? ['#409eff', '#67c23a', '#e6a23c'][index] : ['#8ec5ff', '#a9dca7', '#f4c98c'][index] },
    data: dates.map(date => valueOf(indicatorByKey.get(`${date}:${period}`) || {}, name.toLowerCase()))
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

  chart.setOption({
    animation: false,
    legend: { top: 4, data: ['K线', '9K', '9D', '9J', '90K', '90D', '90J', '9 金叉', '90 金叉'] },
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
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
      ...lineSeries
    ]
  }, true)
}

async function loadChart() {
  if (!stockCode.value) return
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await getKdjHistory({ stockCode: stockCode.value })
    renderChart(response.data)
  } catch (error) {
    errorMessage.value = error.message || 'KDJ 数据加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  chart = echarts.init(chartRef.value)
  loadChart()
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
</style>
