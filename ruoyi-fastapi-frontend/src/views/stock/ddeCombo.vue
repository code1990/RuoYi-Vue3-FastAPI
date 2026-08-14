<template>
  <div class="dde-combo-page">
    <el-card shadow="never">
      <template #header><div class="header"><span>2日DDE捡漏</span><div class="header-actions"><el-date-picker v-model="dateRange" class="date-range" type="daterange" value-format="YYYYMMDD" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" /><el-button type="primary" icon="Search" @click="handleQuery">查询</el-button></div></div></template>
      <el-table v-loading="loading" :data="rows" border>
        <el-table-column label="今日" prop="signalDate" width="100" />
        <el-table-column label="昨日" prop="previousSignalDate" width="100" />
        <el-table-column label="排名" prop="comboRank" width="68" />
        <el-table-column label="股票" min-width="100"><template #default="{ row }">{{ row.stockCode }} {{ row.stockName }}</template></el-table-column>
        <el-table-column label="今日最佳名次" prop="todayBestRank" min-width="110" />
        <el-table-column label="昨日次数" prop="previousSignalCount" min-width="90" />
        <el-table-column label="今日次数" prop="todaySignalCount" min-width="90" />
        <el-table-column label="早/午/尾" min-width="90"><template #default="{ row }">{{ row.todayMorningCount }}/{{ row.todayNoonCount }}/{{ row.todayCloseCount }}</template></el-table-column>
        <el-table-column label="当前价" min-width="80"><template #default="{ row }">{{ number(row.entryPrice) }}</template></el-table-column>
        <el-table-column label="今日强度" min-width="90"><template #default="{ row }">{{ percent(row.todayMainNetRatio) }}</template></el-table-column>
        <el-table-column label="昨日强度" min-width="90"><template #default="{ row }">{{ percent(row.previousMainNetRatio) }}</template></el-table-column>
        <el-table-column label="概念" min-width="180"><template #default="{ row }">{{ getStockConcept(row.stockCode) }}</template></el-table-column>
      </el-table>
      <pagination v-show="total > 0" v-model:page="query.pageNum" v-model:limit="query.pageSize" :total="total" @pagination="getList" />
    </el-card>
  </div>
</template>

<script setup>
import { listDdeCombo } from '@/api/stock/ddeFund'
import { getStockConcept } from '@/utils/stockMetadata'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const dateRange = ref([])
const query = reactive({ pageNum: 1, pageSize: 20 })

function getList() {
  loading.value = true
  listDdeCombo({ ...query, startDate: dateRange.value?.[0], endDate: dateRange.value?.[1] }).then(response => {
    rows.value = response.data.rows
    total.value = response.data.total
  }).finally(() => { loading.value = false })
}

function handleQuery() { query.pageNum = 1; getList() }
function percent(value) { return value === null || value === undefined ? '-' : `${(value * 100).toFixed(2)}%` }
function number(value) { return value === null || value === undefined ? '-' : value.toFixed(2) }

getList()
</script>

<style scoped>
.dde-combo-page { padding: 20px; }
.header { display: flex; align-items: center; justify-content: space-between; font-size: 18px; font-weight: 600; }
.header-actions { display: flex; gap: 10px; align-items: center; }
.date-range { width: 280px; }
:deep(.el-table) { white-space: nowrap; }
</style>
