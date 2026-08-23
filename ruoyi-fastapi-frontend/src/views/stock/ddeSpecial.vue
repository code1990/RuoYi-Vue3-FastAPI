<template>
  <div class="dde-special-page">
    <el-card shadow="never">
      <template #header><div class="header"><span>DDE专项回测</span><div class="header-actions"><el-date-picker v-model="dateRange" type="daterange" value-format="YYYYMMDD" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" /><el-button type="primary" icon="Search" @click="handleQuery">查询</el-button></div></div></template>
      <el-alert title="按信号日14:40价格假设参与；涨停样本也纳入回测统计。T+N最高为该交易日最高价相对入场价的收益。" type="info" :closable="false" show-icon />
      <el-row :gutter="12" class="summary-row">
        <el-col v-for="item in statistics" :key="item.dimension" :xs="24" :sm="8"><el-card shadow="never" class="summary-card"><div class="summary-title">{{ dimensions[item.dimension] }}</div><div>样本 {{ item.sampleCount }} ｜ 涨停 {{ item.limitUpCount }} ｜ 完成 {{ item.completedCount }}</div><div>5日达标 {{ rate(item.targetHitRate) }} ｜ 平均最高 {{ percent(item.averageMaxReturnT5Pct) }}</div><div>正收益 {{ rate(item.positiveRate) }}</div></el-card></el-col>
      </el-row>
      <el-radio-group v-model="dimension" class="dimension-tabs"><el-radio-button v-for="(_name, key) in dimensions" :key="key" :label="key">{{ _name }}</el-radio-button></el-radio-group>
      <el-table v-loading="loading" :data="rows" border @sort-change="handleSortChange">
        <el-table-column label="交易日" prop="tradeDate" width="95" sortable="custom" fixed="left" />
        <el-table-column label="股票" min-width="110" fixed="left"><template #default="{ row }">{{ row.stockCode }} {{ row.stockName }}</template></el-table-column>
        <el-table-column label="DDE次数" prop="signalCount" width="80" sortable="custom" />
        <el-table-column label="14:40价格" prop="entryPrice" min-width="95" sortable="custom"><template #default="{ row }">{{ number(row.entryPrice) }}</template></el-table-column>
        <el-table-column label="资金强度" min-width="90"><template #default="{ row }">{{ rate(row.mainNetRatio) }}</template></el-table-column>
        <el-table-column v-for="day in 5" :key="day" :label="`T+${day}最高`" :prop="`t${day}MaxReturnPct`" min-width="95" sortable="custom"><template #default="{ row }"><span :class="['return-value', returnClass(row[`t${day}MaxReturnPct`])]">{{ percent(row[`t${day}MaxReturnPct`]) }}</span></template></el-table-column>
        <el-table-column label="5日最高" prop="maxReturnT5Pct" min-width="95" sortable="custom"><template #default="{ row }"><span :class="['return-value', returnClass(row.maxReturnT5Pct)]">{{ percent(row.maxReturnT5Pct) }}</span></template></el-table-column>
        <el-table-column label="参与假设" min-width="85"><template #default="{ row }"><el-tag :type="row.isLimitUp ? 'danger' : 'success'" size="small">{{ row.isLimitUp ? '涨停参与' : '正常参与' }}</el-tag></template></el-table-column>
      </el-table>
      <pagination v-show="total > 0" v-model:page="query.pageNum" v-model:limit="query.pageSize" :total="total" @pagination="getList" />
    </el-card>
  </div>
</template>

<script setup>
import { getDdeObservationStatistics, listDdeObservation } from '@/api/stock/ddeFund'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const statistics = ref([])
const dateRange = ref([])
const dimension = ref('high_price')
const query = reactive({ pageNum: 1, pageSize: 20, sortBy: undefined, sortOrder: undefined })
const dimensions = { high_price: '高股价', large_cap: '高市值', high_strength: '高强度' }

function params() { return { startDate: dateRange.value?.[0], endDate: dateRange.value?.[1] } }
function getList() {
  loading.value = true
  listDdeObservation({ ...query, ...params(), dimension: dimension.value }).then(response => {
    rows.value = response.data.rows
    total.value = response.data.total
  }).finally(() => { loading.value = false })
}
function getStatistics() { getDdeObservationStatistics(params()).then(response => { statistics.value = response.data }) }
function handleQuery() { query.pageNum = 1; getList(); getStatistics() }
function handleSortChange({ prop, order }) { query.sortBy = order ? prop : undefined; query.sortOrder = order || undefined; query.pageNum = 1; getList() }
function number(value) { return value === null || value === undefined ? '-' : value.toFixed(2) }
function percent(value) { return value === null || value === undefined ? '-' : `${value.toFixed(2)}%` }
function rate(value) { return value === null || value === undefined ? '-' : `${(value * 100).toFixed(2)}%` }
function returnClass(value) { return value === null || value === undefined ? '' : value >= 2 ? 'return-high' : 'return-low' }

watch(dimension, () => { query.pageNum = 1; getList() })
getList()
getStatistics()
</script>

<style scoped>
.dde-special-page { padding: 20px; }
.header, .header-actions { display: flex; align-items: center; gap: 10px; }
.header { justify-content: space-between; font-size: 18px; font-weight: 600; }
.summary-row { margin: 14px 0; }
.summary-card { line-height: 2; }
.summary-title { font-size: 16px; font-weight: 600; }
.dimension-tabs { margin-bottom: 12px; }
:deep(.el-table) { white-space: nowrap; }
.return-value { display: block; padding: 1px 4px; border-radius: 3px; text-align: center; }
.return-high { background: #fef0f0; color: #f56c6c; }
.return-low { background: #f0f9eb; color: #67c23a; }
</style>
