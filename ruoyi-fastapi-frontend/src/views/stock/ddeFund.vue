<template>
  <div class="dde-fund-page">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <span>DDE资金</span>
          <div class="header-actions"><el-input v-model="query.stockCode" placeholder="股票代码" clearable maxlength="6" style="width: 120px" @keyup.enter="handleQuery" />
            <el-date-picker v-model="dateRange" class="date-range" type="daterange" value-format="YYYYMMDD" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" />
            <el-button type="primary" icon="Search" @click="handleQuery">查询</el-button>
          </div>
        </div>
      </template>
      <el-table v-loading="loading" :data="rows" border @sort-change="handleSortChange">
        <el-table-column label="交易日" prop="tradeDate" width="88" sortable="custom" fixed="left" />
        <el-table-column label="股票" min-width="88" fixed="left"><template #default="{ row }">{{ row.stockCode }} {{ row.stockName }}</template></el-table-column>
        <el-table-column label="行业" min-width="60" fixed="left"><template #default="{ row }">{{ getStockIndustry(row.stockCode) }}</template></el-table-column>
        <el-table-column label="概念" min-width="180" fixed="left"><template #default="{ row }">{{ getStockConcept(row.stockCode) }}</template></el-table-column>
        <el-table-column label="时段" min-width="60"><template #default="{ row }">{{ signalSlot(row.signalSlot) }}</template></el-table-column>
        <el-table-column label="买入价" prop="entryPrice" min-width="60" sortable="custom" />
        <el-table-column label="涨跌幅" prop="signalChangePct" min-width="80" sortable="custom"><template #default="{ row }">{{ percent(row.signalChangePct) }}</template></el-table-column>
        <el-table-column label="大单净额" prop="largeNetAmount" min-width="80" sortable="custom"><template #default="{ row }">{{ amount(row.largeNetAmount) }}</template></el-table-column>
        <el-table-column label="市值" prop="marketCap" min-width="90" sortable="custom"><template #default="{ row }">{{ amount(row.marketCap) }}</template></el-table-column>
        <el-table-column label="强度" prop="mainNetRatio" min-width="88" sortable="custom"><template #default="{ row }">{{ percent(row.mainNetRatio, true) }}</template></el-table-column>
        <el-table-column label="机构" min-width="70"><template #default="{ row }">{{ getStockOrgNum(row.stockCode) }}</template></el-table-column>
        <el-table-column label="尾盘" prop="closeReturnPct" min-width="96" sortable="custom"><template #default="{ row }">{{ percent(row.closeReturnPct) }}</template></el-table-column>
        <el-table-column v-for="day in 5" :key="day" :label="`T+${day}涨幅`" :prop="`t${day}MaxReturnPct`" min-width="110" sortable="custom"><template #default="{ row }"><span :class="['return-value', returnClass(row[`t${day}MaxReturnPct`])]">{{ percent(row[`t${day}MaxReturnPct`]) }}</span></template></el-table-column>
      </el-table>
      <pagination v-show="total > 0" v-model:page="query.pageNum" v-model:limit="query.pageSize" :total="total" @pagination="getList" />
    </el-card>
  </div>
</template>

<script setup>
import { listDdeSignalPerformance } from '@/api/stock/ddeFund'
import { getStockConcept, getStockIndustry, getStockOrgNum } from '@/utils/stockMetadata'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const dateRange = ref([])
const query = reactive({ pageNum: 1, pageSize: 20, stockCode: '', sortBy: undefined, sortOrder: undefined })

function getList() {
  loading.value = true
  listDdeSignalPerformance({ ...query, stockCode: query.stockCode || undefined, startDate: dateRange.value?.[0], endDate: dateRange.value?.[1] }).then(response => {
    rows.value = response.data.rows.filter(row => !query.stockCode || row.stockCode === query.stockCode)
    total.value = query.stockCode ? rows.value.length : response.data.total
  }).finally(() => { loading.value = false })
}

function handleQuery() {
  query.pageNum = 1
  getList()
}

function handleSortChange({ prop, order }) { query.sortBy = order ? prop : undefined; query.sortOrder = order || undefined; query.pageNum = 1; getList() }

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

function returnClass(value) {
  if (value === null || value === undefined) return ''
  return value > 1.8 ? 'return-high' : 'return-low'
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
.return-value { display: block; padding: 1px 4px; border-radius: 3px; text-align: center; }
.return-high { background: #fef0f0; color: #f56c6c; }
.return-low { background: #f0f9eb; color: #67c23a; }
</style>
