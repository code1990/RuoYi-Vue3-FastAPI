<template>
  <div class="visual-page">
    <el-card shadow="never">
      <el-form inline @submit.prevent>
        <el-form-item label="可比公司"><el-input v-model="stockCodes" placeholder="000001,000002" style="width: 280px" @keyup.enter="loadChart" /></el-form-item>
        <el-button type="primary" :loading="loading" @click="loadChart">对比</el-button>
      </el-form>
      <el-alert title="所有可比公司在同一张图显示；以 2026 年首个交易日收盘价为 0% 基准，展示累计收盘收益。" type="info" :closable="false" show-icon />
      <el-alert v-if="errorMessage" :title="errorMessage" type="warning" :closable="false" show-icon class="notice" />
      <div v-show="!errorMessage" ref="chartRef" v-loading="loading" class="chart" />
    </el-card>
    <el-card shadow="never" class="table-card">
      <el-table :data="companies" border stripe>
        <el-table-column label="交易日" prop="tradeDate" width="100" fixed="left" />
        <el-table-column label="股票" width="130" fixed="left"><template #default="{ row }">{{ row.stockCode }} {{ row.stockName }}</template></el-table-column>
        <el-table-column label="行业" prop="industry" min-width="120" fixed="left" />
        <el-table-column label="概念" prop="concept" min-width="180" fixed="left" />
        <el-table-column label="市值" min-width="100"><template #default="{ row }">{{ marketCap(row.marketCap) }}</template></el-table-column>
        <el-table-column label="报告期" prop="reportDate" width="110" />
        <el-table-column label="主力持仓" min-width="100"><template #default="{ row }">{{ percent(row.mainHoldingRate) }}</template></el-table-column>
        <el-table-column label="基金持仓" min-width="100"><template #default="{ row }">{{ percent(row.fundHoldingRate) }}</template></el-table-column>
        <el-table-column label="最新收盘" prop="close" min-width="100" />
        <el-table-column label="2026累计收益" min-width="120"><template #default="{ row }"><span :class="row.returnPct >= 0 ? 'up' : 'down'">{{ row.returnPct.toFixed(2) }}%</span></template></el-table-column>
      </el-table>
    </el-card>
    <el-card shadow="never" class="distribution-card">
      <template #header>
        <div class="distribution-header">
          <span>月度高点收益分布</span>
          <el-select v-model="distributionCode" style="width: 180px" @change="renderDistribution">
            <el-option v-for="company in companies" :key="company.stockCode" :label="`${company.stockCode} ${company.stockName}`" :value="company.stockCode" />
          </el-select>
        </div>
      </template>
      <el-alert title="以每月首个交易日收盘价为基准，统计每日最高价收益落入各 2% 区间的交易日数。" type="info" :closable="false" show-icon />
      <div ref="distributionRef" class="distribution-chart" />
    </el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { getCompanyCompareHistory } from '@/api/stock/companyCompare'

const chartRef = ref()
const stockCodes = ref('000001,000002')
const loading = ref(false)
const errorMessage = ref('')
const companies = ref([])
const distributionRef = ref()
const distributionCode = ref('')
let compareData
let chart
let distributionChart

function renderChart(data) {
  compareData = data
  const quotes = data.quotes
  const grouped = quotes.reduce((result, quote) => {
    ;(result[quote.stockCode] ||= []).push(quote)
    return result
  }, {})
  const dates = [...new Set(quotes.map(quote => String(quote.tradeDate)))].sort()
  const series = Object.entries(grouped).map(([stockCode, rows]) => {
    const closes = new Map(rows.map(row => [String(row.tradeDate), Number(row.close)]))
    const firstClose = Number(rows[0].close)
    const last = rows[rows.length - 1]
    const company = data.companies.find(item => item.stockCode === stockCode) || { stockCode, stockName: '', industry: '', concept: '', marketCap: 0 }
    companies.value.push({ ...company, tradeDate: last.tradeDate, close: last.close, returnPct: (Number(last.close) / firstClose - 1) * 100 })
    return { name: `${company.stockName || stockCode} ${stockCode}`, type: 'line', showSymbol: false, data: dates.map(date => closes.has(date) ? (closes.get(date) / firstClose - 1) * 100 : null) }
  })
  companies.value.sort((left, right) => Number(right.marketCap) - Number(left.marketCap))
  distributionCode.value = companies.value[0]?.stockCode || ''
  chart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: value => value == null ? '-' : `${Number(value).toFixed(2)}%` },
    legend: { top: 2 }, grid: { left: 60, right: 24, top: 44, bottom: 80 },
    xAxis: { type: 'category', data: dates, axisLabel: { formatter: value => `${value.slice(4, 6)}-${value.slice(6)}` } },
    yAxis: { type: 'value', name: '2026累计收益', axisLabel: { formatter: value => `${value}%` } },
    dataZoom: [{ type: 'inside' }, { type: 'slider', bottom: 12 }], series
  }, true)
  renderDistribution()
}

function renderDistribution() {
  if (!distributionChart || !distributionCode.value) return
  const quotes = compareData.quotes.filter(quote => quote.stockCode === distributionCode.value)
  const months = [...new Set(quotes.map(quote => String(quote.tradeDate).slice(0, 6)))].sort()
  const buckets = ['<0%', '0–2%', '2–4%', '4–6%', '6–8%', '≥8%']
  const values = Object.fromEntries(buckets.map(bucket => [bucket, months.map(() => 0)]))
  months.forEach((month, monthIndex) => {
    const rows = quotes.filter(quote => String(quote.tradeDate).startsWith(month))
    const baseClose = Number(rows[0]?.close)
    rows.forEach(row => {
      const gain = (Number(row.high) / baseClose - 1) * 100
      const bucket = gain < 0 ? '<0%' : gain < 2 ? '0–2%' : gain < 4 ? '2–4%' : gain < 6 ? '4–6%' : gain < 8 ? '6–8%' : '≥8%'
      values[bucket][monthIndex] += 1
    })
  })
  distributionChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { top: 2 }, grid: { left: 52, right: 24, top: 42, bottom: 36 },
    xAxis: { type: 'category', data: months.map(month => `${month.slice(0, 4)}-${month.slice(4)}`) },
    yAxis: { type: 'value', name: '交易日数', minInterval: 1 },
    series: buckets.map(bucket => ({ name: bucket, type: 'bar', stack: 'days', data: values[bucket] }))
  }, true)
}

async function loadChart() {
  const codes = stockCodes.value.split(',').map(code => code.trim()).filter(Boolean)
  if (codes.length < 2 || codes.length > 10 || codes.some(code => !/^\d{6}$/.test(code))) {
    errorMessage.value = '请输入 2 至 10 个六位股票代码，使用英文逗号分隔'
    return
  }
  loading.value = true; errorMessage.value = ''; companies.value = []
  try {
    const response = await getCompanyCompareHistory({ stockCodes: codes.join(',') })
    if (!response.data.quotes.length) errorMessage.value = '没有可比较的行情数据'
    else renderChart(response.data)
  } catch (error) {
    errorMessage.value = error.message || '可比公司数据加载失败'
  } finally { loading.value = false }
}

function marketCap(value) { return value ? `${(Number(value) / 100000000).toFixed(0)}亿` : '-' }
function percent(value) { return value == null ? '-' : `${Number(value).toFixed(2)}%` }

onMounted(() => {
  chart = echarts.init(chartRef.value)
  distributionChart = echarts.init(distributionRef.value)
  loadChart()
  window.addEventListener('resize', chart.resize)
  window.addEventListener('resize', distributionChart.resize)
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', chart.resize)
  window.removeEventListener('resize', distributionChart.resize)
  chart.dispose()
  distributionChart.dispose()
})
</script>

<style scoped>
.visual-page { padding: 20px; }
.chart { height: 520px; margin-top: 16px; }
.notice, .table-card, .distribution-card { margin-top: 16px; }
.distribution-header { display: flex; align-items: center; justify-content: space-between; }
.distribution-chart { height: 420px; margin-top: 16px; }
.up { color: #f56c6c; }
.down { color: #67c23a; }
</style>
