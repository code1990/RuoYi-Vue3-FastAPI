<template>
  <div class="dde-hot-rank-page">
    <el-card shadow="never">
      <template #header><div class="header"><span>DDE热度榜</span><div class="header-actions"><span class="range">统计区间：{{ rangeText }}</span><el-checkbox v-model="largeCapOnly" @change="handleQuery">大盘股（≥800亿）</el-checkbox><el-checkbox v-model="highPriceOnly" @change="handleQuery">高价股（≥80元）</el-checkbox></div></div></template>
      <el-table v-loading="loading" :data="rows" border @sort-change="handleSortChange">
        <el-table-column label="交易日" prop="latestSignalDate" width="95" sortable="custom" fixed="left" /><el-table-column label="股票" min-width="110" fixed="left"><template #default="{ row }">{{ row.stockCode }} {{ row.stockName }}</template></el-table-column><el-table-column label="行业" min-width="70" fixed="left"><template #default="{ row }">{{ getStockIndustry(row.stockCode) }}</template></el-table-column><el-table-column label="概念" min-width="180" fixed="left"><template #default="{ row }">{{ getStockConcept(row.stockCode) }}</template></el-table-column><el-table-column label="排名" prop="rankNo" width="60" sortable="custom" />
        <el-table-column label="累计出现" prop="appearanceCount" min-width="85" sortable="custom" /><el-table-column label="出现天数" prop="signalDayCount" min-width="80" sortable="custom" /><el-table-column label="早/午/尾" min-width="80"><template #default="{ row }">{{ row.morningCount }}/{{ row.noonCount }}/{{ row.closeCount }}</template></el-table-column><el-table-column label="近5日" prop="recent5Count" width="70" sortable="custom" />
        <el-table-column label="最近信号" prop="latestSignalDate" min-width="120" sortable="custom"><template #default="{ row }">{{ row.latestSignalDate }} {{ slotName(row.latestSignalSlot) }}</template></el-table-column><el-table-column label="最佳/平均排名" min-width="105"><template #default="{ row }">{{ row.bestRank }}/{{ row.averageRank.toFixed(1) }}</template></el-table-column>
        <el-table-column label="涨停次数" prop="limitUpCount" min-width="80" sortable="custom" /><el-table-column label="可交易次数" prop="tradableSignalCount" min-width="90" sortable="custom" /><el-table-column label="完成样本" prop="completedTradableSampleDayCount" min-width="80" sortable="custom"><template #default="{ row }">{{ row.completedTradableSampleDayCount }}/{{ row.tradableSampleDayCount }}</template></el-table-column><el-table-column label="5日达标" prop="targetHitCount" min-width="80" sortable="custom"><template #default="{ row }">{{ row.targetHitCount }}</template></el-table-column><el-table-column label="可交易5日达标率" prop="targetHitRate" min-width="130" sortable="custom"><template #default="{ row }">{{ percent(row.targetHitRate) }}</template></el-table-column>
        <el-table-column label="尾盘价" prop="latestTailPrice" min-width="75" sortable="custom"><template #default="{ row }">{{ number(row.latestTailPrice) }}</template></el-table-column><el-table-column label="尾盘市值" prop="latestTailMarketCap" min-width="85" sortable="custom"><template #default="{ row }">{{ amount(row.latestTailMarketCap) }}</template></el-table-column><el-table-column label="标签" min-width="130"><template #default="{ row }"><el-tag v-if="row.isLargeCap" size="small">大盘股</el-tag><el-tag v-if="row.isHighPrice" class="tag" size="small" type="warning">高价股</el-tag><el-tag v-if="row.isLatestSignalLimitUp" class="tag" size="small" type="danger">最近涨停</el-tag></template></el-table-column>
      </el-table>
      <pagination v-show="total > 0" v-model:page="query.pageNum" v-model:limit="query.pageSize" :total="total" @pagination="getList" />
    </el-card>
  </div>
</template>

<script setup>
import { listDdeHotRank } from '@/api/stock/ddeFund'
import { getStockConcept, getStockIndustry } from '@/utils/stockMetadata'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const statStartDate = ref(null)
const statEndDate = ref(null)
const largeCapOnly = ref(false)
const highPriceOnly = ref(false)
const query = reactive({ pageNum: 1, pageSize: 20, sortBy: undefined, sortOrder: undefined })
const rangeText = computed(() => statStartDate.value ? `${statStartDate.value} 至 ${statEndDate.value}` : '-')

function getList() {
  loading.value = true
  listDdeHotRank({ ...query, largeCap: largeCapOnly.value || undefined, highPrice: highPriceOnly.value || undefined }).then(response => {
    rows.value = response.data.rows
    total.value = response.data.total
    statStartDate.value = response.data.statStartDate
    statEndDate.value = response.data.statEndDate
  }).finally(() => { loading.value = false })
}

function handleQuery() { query.pageNum = 1; getList() }
function handleSortChange({ prop, order }) { query.sortBy = order ? prop : undefined; query.sortOrder = order || undefined; query.pageNum = 1; getList() }
function slotName(value) { return { morning: '早盘', noon: '午盘', close: '尾盘' }[value] || value }
function percent(value) { return value === null || value === undefined ? '待完成' : `${(value * 100).toFixed(2)}%` }
function number(value) { return value === null || value === undefined ? '-' : value.toFixed(2) }
function amount(value) { return value === null || value === undefined ? '-' : `${(value / 100000000).toFixed(0)}亿` }

getList()
</script>

<style scoped>
.dde-hot-rank-page { padding: 20px; }
.header, .header-actions { display: flex; align-items: center; gap: 12px; }
.header { justify-content: space-between; font-size: 18px; font-weight: 600; }
.range { color: var(--el-text-color-secondary); font-size: 14px; font-weight: 400; }
.tag + .tag { margin-left: 4px; }
:deep(.el-table) { white-space: nowrap; }
</style>
