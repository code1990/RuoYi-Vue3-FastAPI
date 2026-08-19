<template>
  <div class="dde-observation-page">
    <el-card shadow="never">
      <template #header><div class="header"><span>{{ pageTitle }}</span><div class="header-actions"><el-date-picker v-model="dateRange" type="daterange" value-format="YYYYMMDD" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" /><el-button type="primary" icon="Search" @click="handleQuery">查询</el-button></div></div></template>
      <el-descriptions border :column="4" class="summary"><el-descriptions-item label="观察样本">{{ total }}</el-descriptions-item><el-descriptions-item label="可交易样本">{{ summary.tradableCount }}</el-descriptions-item><el-descriptions-item label="完成5日样本">{{ summary.completedCount }}</el-descriptions-item><el-descriptions-item label="5日达标率">{{ rate(summary.targetHitRate) }}（{{ summary.targetHitCount }}）</el-descriptions-item></el-descriptions>
      <el-table v-loading="loading" :data="rows" border>
        <el-table-column label="交易日" prop="tradeDate" width="95" /><el-table-column label="股票" min-width="110"><template #default="{ row }">{{ row.stockCode }} {{ row.stockName }}</template></el-table-column><el-table-column label="DDE次数" prop="signalCount" width="80" /><el-table-column label="早/午/尾" min-width="80"><template #default="{ row }">{{ row.morningCount }}/{{ row.noonCount }}/{{ row.closeCount }}</template></el-table-column><el-table-column label="最佳排名" prop="bestRank" width="85" />
        <el-table-column v-if="dimension === 'intraday_combo'" label="日内连续" min-width="120"><template #default="{ row }">{{ comboName(row.comboType) }}</template></el-table-column><el-table-column label="14:40价格" min-width="95"><template #default="{ row }">{{ number(row.entryPrice) }}</template></el-table-column><el-table-column label="市值" min-width="85"><template #default="{ row }">{{ amount(row.marketCap) }}</template></el-table-column><el-table-column label="涨跌幅" min-width="80"><template #default="{ row }">{{ percent(row.changePct) }}</template></el-table-column>
        <el-table-column label="交易状态" min-width="85"><template #default="{ row }"><el-tag v-if="row.isLimitUp" size="small" type="danger">涨停</el-tag><el-tag v-else size="small" type="success">可交易</el-tag></template></el-table-column><el-table-column label="5日结果" min-width="95"><template #default="{ row }"><el-tag v-if="!row.isTradable" size="small" type="info">不统计</el-tag><el-tag v-else-if="!row.isCompleted" size="small" type="warning">待完成</el-tag><el-tag v-else :type="row.targetHit ? 'success' : 'danger'" size="small">{{ row.targetHit ? '达标' : '未达标' }}</el-tag></template></el-table-column>
      </el-table>
      <pagination v-show="total > 0" v-model:page="query.pageNum" v-model:limit="query.pageSize" :total="total" @pagination="getList" />
    </el-card>
  </div>
</template>

<script setup>
import { listDdeObservation } from '@/api/stock/ddeFund'

const route = useRoute()
const loading = ref(false)
const rows = ref([])
const total = ref(0)
const dateRange = ref([])
const summary = reactive({ tradableCount: 0, completedCount: 0, targetHitCount: 0, targetHitRate: null })
const query = reactive({ pageNum: 1, pageSize: 20 })
const dimensions = { high_price: 'DDE高价股', large_cap: 'DDE高市值', intraday_combo: 'DDE日内连续' }
const dimension = computed(() => dimensions[route.query.dimension] ? route.query.dimension : 'high_price')
const pageTitle = computed(() => dimensions[dimension.value])

function getList() {
  loading.value = true
  listDdeObservation({ ...query, dimension: dimension.value, startDate: dateRange.value?.[0], endDate: dateRange.value?.[1] }).then(response => {
    rows.value = response.data.rows
    total.value = response.data.total
    Object.assign(summary, response.data)
  }).finally(() => { loading.value = false })
}

function handleQuery() { query.pageNum = 1; getList() }
function percent(value) { return value === null || value === undefined ? '-' : `${value.toFixed(2)}%` }
function rate(value) { return value === null || value === undefined ? '-' : `${(value * 100).toFixed(2)}%` }
function number(value) { return value === null || value === undefined ? '-' : value.toFixed(2) }
function amount(value) { return value === null || value === undefined ? '-' : `${(value / 100000000).toFixed(0)}亿` }
function comboName(value) { return { morning_noon: '早盘+午盘', noon_close: '午盘+尾盘', morning_close: '早盘+尾盘', morning_noon_close: '早盘+午盘+尾盘' }[value] || '-' }

watch(() => route.query.dimension, handleQuery)
getList()
</script>

<style scoped>
.dde-observation-page { padding: 20px; }
.header, .header-actions { display: flex; align-items: center; gap: 10px; }
.header { justify-content: space-between; font-size: 18px; font-weight: 600; }
.summary { margin-bottom: 16px; }
:deep(.el-table) { white-space: nowrap; }
</style>
