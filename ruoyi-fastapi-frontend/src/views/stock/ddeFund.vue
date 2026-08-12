<template>
  <div class="dde-fund-page">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <span>DDE资金</span>
          <div class="header-actions">
            <el-date-picker v-model="dateRange" class="date-range" type="daterange" value-format="YYYYMMDD" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" />
            <el-button type="primary" icon="Search" @click="handleQuery">查询</el-button>
          </div>
        </div>
      </template>
      <el-table v-loading="loading" :data="rows" border>
        <el-table-column label="交易日" prop="tradeDate" width="88" />
        <el-table-column label="股票" min-width="88"><template #default="{ row }">{{ row.stockCode }} {{ row.stockName }}</template></el-table-column>
        <el-table-column label="时段" min-width="60"><template #default="{ row }">{{ signalSlot(row.signalSlot) }}</template></el-table-column>
        <el-table-column label="买入价" prop="entryPrice" min-width="60" />
        <el-table-column label="涨跌幅" min-width="80"><template #default="{ row }">{{ percent(row.signalChangePct) }}</template></el-table-column>
        <el-table-column label="大单净额" min-width="80"><template #default="{ row }">{{ amount(row.largeNetAmount) }}</template></el-table-column>
        <el-table-column label="市值" min-width="90"><template #default="{ row }">{{ amount(row.marketCap) }}</template></el-table-column>
        <el-table-column label="强度" min-width="88"><template #default="{ row }">{{ percent(row.mainNetRatio, true) }}</template></el-table-column>
        <el-table-column label="行业" prop="industryName" min-width="60" />
        <el-table-column label="概念" min-width="180"><template #default="{ row }">{{ getStockConcept(row.stockCode) }}</template></el-table-column>
        <el-table-column label="机构" min-width="70"><template #default="{ row }">{{ getStockOrgNum(row.stockCode) }}</template></el-table-column>
        <el-table-column label="尾盘" min-width="96"><template #default="{ row }">{{ percent(row.closeReturnPct) }}</template></el-table-column>
        <el-table-column v-for="day in 5" :key="day" :label="`T+${day}涨幅`" min-width="110"><template #default="{ row }">{{ percent(row[`t${day}MaxReturnPct`]) }}</template></el-table-column>
      </el-table>
      <pagination v-show="total > 0" v-model:page="query.pageNum" v-model:limit="query.pageSize" :total="total" @pagination="getList" />
    </el-card>
  </div>
</template>

<script setup>
import { listDdeSignalPerformance } from '@/api/stock/ddeFund'
import { getStockConcept, getStockOrgNum } from '@/utils/stockMetadata'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const dateRange = ref([])
const query = reactive({ pageNum: 1, pageSize: 20 })

function getList() {
  loading.value = true
  listDdeSignalPerformance({ ...query, startDate: dateRange.value?.[0], endDate: dateRange.value?.[1] }).then(response => {
    rows.value = response.data.rows
    total.value = response.data.total
  }).finally(() => { loading.value = false })
}

function handleQuery() {
  query.pageNum = 1
  getList()
}

function percent(value, ratio = false) {
  if (value === null || value === undefined) return '-'
  const percentValue = ratio ? value * 100 : value
  return `${percentValue >= 0 ? '+' : ''}${percentValue.toFixed(2)}%`
}

function amount(value) {
  if (value === null || value === undefined) return '-'
  if (Math.abs(value) >= 100000000) return `${(value / 100000000).toFixed(2)}亿`
  if (Math.abs(value) >= 10000) return `${(value / 10000).toFixed(2)}万`
  return value.toFixed(2)
}

function signalSlot(value) {
  return { morning: '早盘', noon: '午盘', close: '尾盘' }[value] || value || '-'
}

getList()
</script>

<style scoped>
.dde-fund-page {
  padding: 20px;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 18px;
  font-weight: 600;
}

:deep(.el-table) { white-space: nowrap; }
.header-actions { display: flex; flex: 0 0 auto; gap: 10px; align-items: center; margin-left: 16px; margin-right: auto; }
:deep(.date-range.el-date-editor) { width: 280px !important; flex: 0 0 280px; }
</style>
