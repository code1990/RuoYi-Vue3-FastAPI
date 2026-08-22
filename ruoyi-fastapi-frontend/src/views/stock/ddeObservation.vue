<template>
  <div class="dde-observation-page">
    <el-card shadow="never">
      <template #header><div class="header"><span>{{ pageTitle }}</span><div class="header-actions"><el-input v-model="query.stockCode" placeholder="股票代码" clearable maxlength="6" style="width: 120px" @keyup.enter="handleQuery" /><el-date-picker v-model="dateRange" type="daterange" value-format="YYYYMMDD" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" /><el-button type="primary" icon="Search" @click="handleQuery">查询</el-button></div></div></template>
      <el-table v-loading="loading" :data="rows" border @sort-change="handleSortChange">
        <el-table-column label="交易日" prop="tradeDate" sortable="custom" width="95" fixed="left" />
        <el-table-column label="股票" min-width="110" fixed="left"><template #default="{ row }">{{ row.stockCode }} {{ row.stockName }}</template></el-table-column>
        <el-table-column label="行业" min-width="70" fixed="left"><template #default="{ row }">{{ getStockIndustry(row.stockCode) }}</template></el-table-column>
        <el-table-column label="概念" min-width="180" fixed="left"><template #default="{ row }">{{ getStockConcept(row.stockCode) }}</template></el-table-column>
        <el-table-column label="DDE次数" prop="signalCount" sortable="custom" width="80" />
        <el-table-column label="早/午/尾" min-width="80"><template #default="{ row }">{{ row.morningCount }}/{{ row.noonCount }}/{{ row.closeCount }}</template></el-table-column>
        <el-table-column label="最佳排名" prop="bestRank" sortable="custom" width="85" />
        <el-table-column v-if="dimension === 'intraday_combo'" label="日内连续" min-width="120"><template #default="{ row }">{{ comboName(row.comboType) }}</template></el-table-column>
        <el-table-column label="14:40价格" prop="entryPrice" sortable="custom" min-width="95"><template #default="{ row }">{{ number(row.entryPrice) }}</template></el-table-column>
        <el-table-column label="市值" prop="marketCap" sortable="custom" min-width="85"><template #default="{ row }">{{ amount(row.marketCap) }}</template></el-table-column>
        <el-table-column label="涨跌幅" prop="changePct" sortable="custom" min-width="80"><template #default="{ row }">{{ percent(row.changePct) }}</template></el-table-column>
        <el-table-column label="交易状态" min-width="100"><template #default="{ row }"><el-tag v-for="slot in row.limitUpSlots" :key="slot" size="small" type="danger">{{ slotName(slot) }}涨停</el-tag><el-tag v-if="!row.limitUpSlots?.length && row.isLimitUp" size="small" type="danger">涨停</el-tag><el-tag v-if="!row.isLimitUp" size="small" type="success">可交易</el-tag></template></el-table-column>
        <el-table-column label="5日结果" min-width="95"><template #default="{ row }"><el-tag v-if="!row.isTradable" size="small" type="info">不统计</el-tag><el-tag v-else-if="!row.isCompleted" size="small" type="warning">待完成</el-tag><el-tag v-else :type="row.targetHit ? 'success' : 'danger'" size="small">{{ row.targetHit ? '达标' : '未达标' }}</el-tag></template></el-table-column>
      </el-table>
      <pagination v-show="total > 0" v-model:page="query.pageNum" v-model:limit="query.pageSize" :total="total" @pagination="getList" />
    </el-card>
  </div>
</template>

<script setup>
import { listDdeObservation } from '@/api/stock/ddeFund'
import { getStockConcept, getStockIndustry } from '@/utils/stockMetadata'

const route = useRoute()
const loading = ref(false)
const rows = ref([])
const total = ref(0)
const dateRange = ref([])
const summary = reactive({ tradableCount: 0, completedCount: 0, targetHitCount: 0, targetHitRate: null })
const query = reactive({ pageNum: 1, pageSize: 20, stockCode: '', sortBy: undefined, sortOrder: undefined })
const dimensions = { high_price: 'DDE高价股', large_cap: 'DDE高市值', intraday_combo: 'DDE日内连续' }
const dimension = computed(() => dimensions[route.query.dimension] ? route.query.dimension : 'high_price')
const pageTitle = computed(() => dimensions[dimension.value])

function getList() {
  loading.value = true
  listDdeObservation({ ...query, stockCode: query.stockCode || undefined, dimension: dimension.value, startDate: dateRange.value?.[0], endDate: dateRange.value?.[1] }).then(response => {
    rows.value = response.data.rows.filter(row => !query.stockCode || row.stockCode === query.stockCode)
    total.value = query.stockCode ? rows.value.length : response.data.total
    Object.assign(summary, response.data)
  }).finally(() => { loading.value = false })
}

function handleQuery() { query.pageNum = 1; getList() }
function handleSortChange({ prop, order }) { query.sortBy = order ? prop : undefined; query.sortOrder = order || undefined; query.pageNum = 1; getList() }
function percent(value) { return value === null || value === undefined ? '-' : `${value.toFixed(2)}%` }
function rate(value) { return value === null || value === undefined ? '-' : `${(value * 100).toFixed(2)}%` }
function number(value) { return value === null || value === undefined ? '-' : value.toFixed(2) }
function amount(value) { return value === null || value === undefined ? '-' : `${(value / 100000000).toFixed(0)}亿` }
function comboName(value) { return { morning_noon: '早盘+午盘', noon_close: '午盘+尾盘', morning_close: '早盘+尾盘', morning_noon_close: '早盘+午盘+尾盘' }[value] || '-' }
function slotName(value) { return { morning: '早盘', noon: '午盘', close: '尾盘' }[value] || value }

watch(() => route.query.dimension, handleQuery)
getList()
</script>

<style scoped>
.dde-observation-page { padding: 20px; }
.header, .header-actions { display: flex; align-items: center; gap: 10px; }
.header { justify-content: space-between; font-size: 18px; font-weight: 600; }
.header-actions { flex: 0 0 auto; margin-left: 16px; margin-right: auto; }
.summary { margin-bottom: 16px; }
:deep(.el-table) { white-space: nowrap; }
</style>
