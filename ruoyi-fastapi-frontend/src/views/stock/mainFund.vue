<template>
  <div class="stock-data-page">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <span>主连资金</span>
          <div class="header-actions">
            <el-date-picker v-model="dateRange" class="date-range" type="daterange" value-format="YYYYMMDD" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" />
            <el-button type="primary" icon="Search" @click="handleQuery">查询</el-button>
          </div>
        </div>
      </template>
      <el-table v-loading="loading" :data="rows" border>
        <el-table-column label="交易日" prop="signalDate" width="100" />
        <el-table-column label="股票" min-width="88"><template #default="{ row }">{{ row.stockCode }} {{ row.stockName }}</template></el-table-column>
        <el-table-column label="策略" prop="strategy" min-width="60" />
        <el-table-column label="信号" prop="signalType" min-width="60" />
        <el-table-column label="行业" prop="industryName" min-width="60" />
        <el-table-column label="概念" min-width="180"><template #default="{ row }">{{ getStockConcept(row.stockCode) }}</template></el-table-column>
        <el-table-column label="机构" min-width="70"><template #default="{ row }">{{ getStockOrgNum(row.stockCode) }}</template></el-table-column>
        <el-table-column label="买入价" prop="entryPrice" min-width="80" />
        <el-table-column label="评分" min-width="60"><template #default="{ row }">{{ number(row.signalScore) }}</template></el-table-column>
        <el-table-column label="10日强度" prop="strength10d" min-width="95" />
        <el-table-column label="55日强度" prop="strength55d" min-width="95" />
        <el-table-column label="连续流入" min-width="90"><template #default="{ row }">{{ days(row.consecutiveInflowDays) }}</template></el-table-column>
        <el-table-column label="尾盘" min-width="60"><template #default="{ row }">{{ percent(row.closeReturnPct) }}</template></el-table-column>
        <el-table-column v-for="day in 5" :key="day" :label="`T+${day}涨幅`" min-width="110"><template #default="{ row }">{{ percent(row[`t${day}MaxReturnPct`]) }}</template></el-table-column>
      </el-table>
      <pagination v-show="total > 0" v-model:page="query.pageNum" v-model:limit="query.pageSize" :total="total" @pagination="getList" />
    </el-card>
  </div>
</template>

<script setup>
import { listMainFundPerformance } from '@/api/stock/mainFund'
import { getStockConcept, getStockOrgNum } from '@/utils/stockMetadata'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const dateRange = ref([])
const query = reactive({ pageNum: 1, pageSize: 20 })

function getList() {
  loading.value = true
  listMainFundPerformance({ ...query, startDate: dateRange.value?.[0], endDate: dateRange.value?.[1] }).then(response => {
    rows.value = response.data.rows
    total.value = response.data.total
  }).finally(() => { loading.value = false })
}

function handleQuery() {
  query.pageNum = 1
  getList()
}

function percent(value) {
  if (value === null || value === undefined) return '-'
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
}

function days(value) {
  return value === null || value === undefined ? '-' : `${value}天`
}

function number(value) {
  return value === null || value === undefined ? '-' : value.toFixed(2)
}

getList()
</script>

<style scoped>
.stock-data-page { padding: 20px; }
.header { display: flex; align-items: center; justify-content: space-between; font-size: 18px; font-weight: 600; }
:deep(.el-table) { white-space: nowrap; }
.header-actions { display: flex; flex: 0 0 auto; gap: 10px; align-items: center; margin-left: 16px; margin-right: auto; }
:deep(.date-range.el-date-editor) { width: 280px !important; flex: 0 0 280px; }
</style>
