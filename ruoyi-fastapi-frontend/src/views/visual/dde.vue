<template>
  <div class="visual-page">
    <el-card>
      <el-form inline @submit.prevent>
        <el-form-item label="股票代码"><el-input v-model="stockCode" maxlength="6" clearable @keyup.enter="loadChart" /></el-form-item>
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
import { listDdeSignalPerformance } from '@/api/stock/ddeFund'
import { listMainFundPerformance } from '@/api/stock/mainFund'
import { listMarginLongPerformance } from '@/api/stock/marginTrading'

const chartRef = ref()
const stockCode = ref('000001')
const loading = ref(false)
const errorMessage = ref('')
let chart

function valueOf(row, camel, snake = camel) {
  return row[camel] ?? row[snake]
}

function dateKey(value) {
  return String(value).replaceAll('-', '')
}

function formatDate(value) {
  const text = String(value)
  return `${text.slice(4, 6)}-${text.slice(6)}`
}

function percent(value) {
  return value == null ? '-' : Math.round(Number(value) * 10000) / 100
}

function signalSeries(name, rows, dates, candles, dateField, valueField, color, offset) {
  const values = new Map(rows.map(row => [dateKey(row[dateField]), percent(row[valueField])]))
  const candleByDate = new Map(candles.map(row => [dateKey(valueOf(row, 'tradeDate', 'trade_date')), row]))
  return {
    name,
    type: 'scatter',
    xAxisIndex: 0,
    yAxisIndex: 0,
    symbol: 'arrow',
    symbolSize: [8, 20],
    symbolOffset: [offset, 16],
    itemStyle: { color },
    data: dates.flatMap(date => candleByDate.has(date) && values.has(date) ? [[date, valueOf(candleByDate.get(date), 'low')]] : [])
  }
}

function renderChart(kdj, mainFund, margin, dde) {
  const candles = kdj.candles || []
  if (!candles.length) {
    errorMessage.value = '没有可显示的 K 线数据'
    return
  }
  const dates = candles.map(row => dateKey(valueOf(row, 'tradeDate', 'trade_date')))
  const bar = (rows, field, dateField) => {
    const values = new Map(rows.map(row => [dateKey(row[dateField]), percent(row[field])]))
    return dates.map(date => values.get(date) ?? '-')
  }
  chart.setOption({
    animation: false,
    legend: { top: 2, data: ['K线', '55日主连资金', '融资融券', 'DDE'] },
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    axisPointer: { link: [{ xAxisIndex: 'all' }] },
    grid: [
      { left: 60, right: 24, top: 38, height: '38%' },
      { left: 60, right: 24, top: '52%', height: '11%' },
      { left: 60, right: 24, top: '66%', height: '11%' },
      { left: 60, right: 24, top: '80%', height: '11%' }
    ],
    xAxis: [0, 1, 2, 3].map(index => ({ type: 'category', gridIndex: index, data: dates, boundaryGap: true, axisLabel: { show: index === 3, formatter: formatDate } })),
    yAxis: [
      { scale: true, splitArea: { show: true } },
      { gridIndex: 1, name: '55日%', axisLabel: { formatter: '{value}%' } },
      { gridIndex: 2, name: '两融%', axisLabel: { formatter: '{value}%' } },
      { gridIndex: 3, name: 'DDE%', axisLabel: { formatter: '{value}%' } }
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1, 2, 3], start: dates.length > 120 ? 100 - 12000 / dates.length : 0, end: 100 },
      { type: 'slider', xAxisIndex: [0, 1, 2, 3], bottom: 8 }
    ],
    series: [
      { name: 'K线', type: 'candlestick', data: candles.map(row => [valueOf(row, 'open'), valueOf(row, 'close'), valueOf(row, 'low'), valueOf(row, 'high')]), itemStyle: { color: '#ef5350', color0: '#26a69a', borderColor: '#ef5350', borderColor0: '#26a69a' } },
      signalSeries('55日主连资金', mainFund, dates, candles, 'signalDate', 'signalScore', '#f56c6c', -8),
      signalSeries('融资融券', margin, dates, candles, 'signalDate', 'score', '#409eff', 0),
      signalSeries('DDE', dde, dates, candles, 'tradeDate', 'mainNetRatio', '#e6a23c', 8),
      { name: '55日主连资金强度', type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: bar(mainFund, 'signalScore', 'signalDate'), itemStyle: { color: '#f56c6c' } },
      { name: '融资融券强度', type: 'bar', xAxisIndex: 2, yAxisIndex: 2, data: bar(margin, 'score', 'signalDate'), itemStyle: { color: '#409eff' } },
      { name: 'DDE资金强度', type: 'bar', xAxisIndex: 3, yAxisIndex: 3, data: bar(dde, 'mainNetRatio', 'tradeDate'), itemStyle: { color: '#e6a23c' } }
    ]
  }, true)
}

async function loadChart() {
  if (!stockCode.value) return
  loading.value = true
  errorMessage.value = ''
  try {
    const params = { stockCode: stockCode.value, pageNum: 1, pageSize: 200 }
    const [kdj, mainFund, margin, dde] = await Promise.all([
      getKdjHistory({ stockCode: stockCode.value }),
      listMainFundPerformance(params),
      listMarginLongPerformance(params),
      listDdeSignalPerformance(params)
    ])
    renderChart(kdj.data, mainFund.data.rows, margin.data.rows, dde.data.rows)
  } catch (error) {
    errorMessage.value = error.message || '资金数据加载失败'
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
.visual-page { padding: 20px; }
.chart { height: 980px; margin-top: 12px; }
</style>
