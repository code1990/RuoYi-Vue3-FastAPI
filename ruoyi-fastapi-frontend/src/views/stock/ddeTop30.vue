<template>
  <div class="dde-top30-page">
    <el-card shadow="never">
      <template #header><div class="header"><span>DDE资金30</span><div class="header-actions"><el-date-picker v-model="dateRange" type="daterange" value-format="YYYYMMDD" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" /><el-button type="primary" icon="Search" @click="handleQuery">查询</el-button></div></div></template>
      <el-table v-loading="loading" :data="rows" border>
        <el-table-column label="交易日" prop="tradeDate" width="88" /><el-table-column label="股票" min-width="100"><template #default="{ row }">{{ row.stockCode }} {{ row.stockName }}</template></el-table-column>
        <el-table-column label="时段" prop="signalSlot" width="65" /><el-table-column label="可交易排名" prop="signalRankNo" min-width="100" /><el-table-column label="原始排名" prop="rawRankNo" min-width="90" />
        <el-table-column label="买入价" prop="entryPrice" min-width="70" /><el-table-column label="主力净额" min-width="90"><template #default="{ row }">{{ amount(row.mainNetAmount) }}</template></el-table-column><el-table-column label="强度" min-width="80"><template #default="{ row }">{{ percent(row.mainNetRatio, true) }}</template></el-table-column>
        <el-table-column label="行业" prop="industryName" min-width="70" /><el-table-column label="尾盘" min-width="80"><template #default="{ row }">{{ percent(row.closeReturnPct) }}</template></el-table-column><el-table-column v-for="day in 5" :key="day" :label="`T+${day}最高`" min-width="90"><template #default="{ row }">{{ percent(row[`t${day}MaxReturnPct`]) }}</template></el-table-column>
      </el-table>
      <pagination v-show="total > 0" v-model:page="query.pageNum" v-model:limit="query.pageSize" :total="total" @pagination="getList" />
    </el-card>
  </div>
</template>

<script setup>
import { listDdeTop30Performance } from '@/api/stock/ddeFund'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const dateRange = ref([])
const query = reactive({ pageNum: 1, pageSize: 20 })
function getList() { loading.value = true; listDdeTop30Performance({ ...query, startDate: dateRange.value?.[0], endDate: dateRange.value?.[1] }).then(response => { rows.value = response.data.rows; total.value = response.data.total }).finally(() => { loading.value = false }) }
function handleQuery() { query.pageNum = 1; getList() }
function percent(value, ratio = false) { return value === null || value === undefined ? '-' : `${(ratio ? value * 100 : value).toFixed(2)}%` }
function amount(value) { return value === null || value === undefined ? '-' : `${(value / 100000000).toFixed(2)}亿` }
getList()
</script>

<style scoped>
.dde-top30-page { padding: 20px; }
.header, .header-actions { display: flex; align-items: center; gap: 10px; }
.header { justify-content: space-between; font-size: 18px; font-weight: 600; }
:deep(.el-table) { white-space: nowrap; }
</style>
