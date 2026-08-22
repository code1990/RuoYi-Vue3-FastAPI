<template>
  <div class="dde-top30-page">
    <el-card shadow="never">
      <template #header><div class="header"><span>DDE资金30</span><div class="header-actions"><el-input v-model="query.stockCode" placeholder="股票代码" clearable maxlength="6" style="width: 120px" @keyup.enter="handleQuery" /><el-select v-model="query.signalSlot" style="width: 90px"><el-option label="全部" value="" /><el-option label="早盘" value="morning" /><el-option label="午盘" value="noon" /><el-option label="尾盘" value="close" /><el-option label="盘后" value="post_close" /></el-select><el-date-picker v-model="dateRange" type="daterange" value-format="YYYYMMDD" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" /><el-button type="primary" icon="Search" @click="handleQuery">查询</el-button></div></div></template>
      <el-table v-loading="loading" :data="rows" border @sort-change="handleSortChange">
        <el-table-column label="交易日" prop="tradeDate" width="88" sortable="custom" fixed="left" />
        <el-table-column label="股票" min-width="100" fixed="left"><template #default="{ row }">{{ row.stockCode }} {{ row.stockName }}</template></el-table-column>
        <el-table-column label="行业" min-width="70" fixed="left"><template #default="{ row }">{{ getStockIndustry(row.stockCode) }}</template></el-table-column>
        <el-table-column label="概念" min-width="180" fixed="left"><template #default="{ row }">{{ getStockConcept(row.stockCode) }}</template></el-table-column>
        <el-table-column label="时段" prop="signalSlot" width="65"><template #default="{ row }">{{ slotLabel(row.signalSlot) }}</template></el-table-column>
        <el-table-column label="可交易排名" prop="signalRankNo" min-width="100" sortable="custom" />
        <el-table-column label="原始排名" prop="rawRankNo" min-width="90" sortable="custom" />
        <el-table-column label="买入价" prop="entryPrice" min-width="70" sortable="custom" />
        <el-table-column label="主力净额" prop="mainNetAmount" min-width="90" sortable="custom"><template #default="{ row }">{{ amount(row.mainNetAmount) }}</template></el-table-column>
        <el-table-column label="强度" prop="mainNetRatio" min-width="80" sortable="custom"><template #default="{ row }">{{ percent(row.mainNetRatio, true) }}</template></el-table-column>
        <el-table-column label="尾盘" prop="closeReturnPct" min-width="80" sortable="custom"><template #default="{ row }">{{ percent(row.closeReturnPct) }}</template></el-table-column>
        <el-table-column v-for="day in 5" :key="day" :label="`T+${day}最高`" :prop="`t${day}MaxReturnPct`" min-width="90" sortable="custom"><template #default="{ row }"><span :class="['return-value', returnClass(row[`t${day}MaxReturnPct`])]">{{ percent(row[`t${day}MaxReturnPct`]) }}</span></template></el-table-column>
      </el-table>
      <pagination v-show="total > 0" v-model:page="query.pageNum" v-model:limit="query.pageSize" :total="total" @pagination="getList" />
    </el-card>
  </div>
</template>

<script setup>
import { listDdeTop30Performance } from '@/api/stock/ddeFund'
import { getStockConcept, getStockIndustry } from '@/utils/stockMetadata'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const dateRange = ref([])
const query = reactive({ pageNum: 1, pageSize: 20, stockCode: '', signalSlot: '', sortBy: undefined, sortOrder: undefined })
function getList() { loading.value = true; listDdeTop30Performance({ ...query, stockCode: query.stockCode || undefined, startDate: dateRange.value?.[0], endDate: dateRange.value?.[1] }).then(response => { rows.value = response.data.rows.filter(row => !query.stockCode || row.stockCode === query.stockCode); total.value = query.stockCode ? rows.value.length : response.data.total }).finally(() => { loading.value = false }) }
function handleQuery() { query.pageNum = 1; getList() }
function handleSortChange({ prop, order }) { query.sortBy = order ? prop : undefined; query.sortOrder = order || undefined; query.pageNum = 1; getList() }
function percent(value, ratio = false) { return value === null || value === undefined ? '-' : `${(ratio ? value * 100 : value).toFixed(2)}%` }
function amount(value) { return value === null || value === undefined ? '-' : `${(value / 100000000).toFixed(2)}亿` }
function slotLabel(slot) { return { morning: '早盘', noon: '午盘', close: '尾盘', post_close: '盘后' }[slot] || slot }
function returnClass(value) { return value === null || value === undefined ? '' : value > 1.8 ? 'return-high' : 'return-low' }
getList()
</script>

<style scoped>
.dde-top30-page { padding: 20px; }
.header, .header-actions { display: flex; align-items: center; gap: 10px; }
.header { justify-content: space-between; font-size: 18px; font-weight: 600; }
.header-actions { flex: 0 0 auto; margin-left: 16px; margin-right: auto; }
:deep(.el-table) { white-space: nowrap; }
.return-value { display: block; padding: 1px 4px; border-radius: 3px; text-align: center; }
.return-high { background: #fef0f0; color: #f56c6c; }
.return-low { background: #f0f9eb; color: #67c23a; }
</style>
