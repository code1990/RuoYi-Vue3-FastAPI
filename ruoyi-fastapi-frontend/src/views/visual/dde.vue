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
import { getFundVisualHistory } from '@/api/stock/fundVisual'

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

function isSignal(row, camel, snake) {
  return valueOf(row, camel, snake) === true || Number(valueOf(row, camel, snake)) === 1
}

function kdjMarks(candles, indicators, dates) {
  const candleByDate = new Map(candles.map(row => [dateKey(valueOf(row, 'tradeDate', 'trade_date')), row]))
  const indicatorByKey = new Map(indicators.map(row => [`${dateKey(valueOf(row, 'tradeDate', 'trade_date'))}:${row.period}`, row]))
  return [9, 90].flatMap(period => [
    {
      name: `${period} 金叉`, type: 'scatter', xAxisIndex: 0, yAxisIndex: 0, symbol: 'pin', symbolSize: 28,
      itemStyle: { color: period === 9 ? '#f56c6c' : '#8e44ad' }, label: { show: true, formatter: `金${period}`, color: '#fff', fontSize: 10 },
      data: dates.flatMap(date => {
        const indicator = indicatorByKey.get(`${date}:${period}`)
        return indicator && isSignal(indicator, 'goldenCross', 'golden_cross') ? [[date, valueOf(candleByDate.get(date), 'low')]] : []
      })
    },
    {
      name: `${period} K1`, type: 'scatter', xAxisIndex: 0, yAxisIndex: 0, symbol: 'arrow', symbolSize: [8, 20],
      symbolOffset: [period === 9 ? -5 : 5, 16], itemStyle: { color: '#f5222d' },
      data: dates.flatMap(date => {
        const indicator = indicatorByKey.get(`${date}:${period}`)
        return indicator && isSignal(indicator, 'rsvCrossK', 'rsv_cross_k') ? [[date, valueOf(candleByDate.get(date), 'low')]] : []
      })
    },
    {
      name: `${period} K2`, type: 'scatter', xAxisIndex: 0, yAxisIndex: 0, symbol: 'arrow', symbolSize: [8, 20],
      symbolOffset: [period === 9 ? -5 : 5, -16], itemStyle: { color: '#f5222d' },
      data: dates.flatMap(date => {
        const indicator = indicatorByKey.get(`${date}:${period}`)
        return indicator && isSignal(indicator, 'rsvCrossD', 'rsv_cross_d') ? [[date, valueOf(candleByDate.get(date), 'high')]] : []
      })
    }
  ])
}

function renderChart(kdj, funds) {
  const candles = kdj.candles || []
  if (!candles.length) {
    errorMessage.value = '没有可显示的 K 线数据'
    return
  }
  const dates = candles.map(row => dateKey(valueOf(row, 'tradeDate', 'trade_date')))
  const bars = rows => {
    const values = new Map(rows.map(row => [dateKey(row.tradeDate), row.value]))
    return dates.map(date => values.get(date) ?? '-')
  }
  chart.setOption({
    animation: false,
    legend: { top: 2, data: ['K线', '9 金叉', '90 金叉'] },
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
      { gridIndex: 1, name: '55日净流入(亿)' },
      { gridIndex: 2, name: '融资买入(亿)' },
      { gridIndex: 3, name: 'DDE%' }
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1, 2, 3], start: dates.length > 120 ? 100 - 12000 / dates.length : 0, end: 100 },
      { type: 'slider', xAxisIndex: [0, 1, 2, 3], bottom: 8 }
    ],
    series: [
      { name: 'K线', type: 'candlestick', data: candles.map(row => [valueOf(row, 'open'), valueOf(row, 'close'), valueOf(row, 'low'), valueOf(row, 'high')]), itemStyle: { color: '#ef5350', color0: '#26a69a', borderColor: '#ef5350', borderColor0: '#26a69a' } },
      ...kdjMarks(candles, kdj.indicators || [], dates),
      { name: '55日主连资金净流入', type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: bars(funds.mainFund), itemStyle: { color: '#f56c6c' } },
      { name: '融资买入额', type: 'bar', xAxisIndex: 2, yAxisIndex: 2, data: bars(funds.margin), itemStyle: { color: '#409eff' } },
      { name: 'DDE资金强度', type: 'bar', xAxisIndex: 3, yAxisIndex: 3, data: bars(funds.dde), itemStyle: { color: '#e6a23c' } }
    ]
  }, true)
}

async function loadChart() {
  if (!stockCode.value) return
  loading.value = true
  errorMessage.value = ''
  try {
    const [kdj, funds] = await Promise.all([getKdjHistory({ stockCode: stockCode.value }), getFundVisualHistory({ stockCode: stockCode.value })])
    renderChart(kdj.data, funds.data)
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
