<template>
  <div class="dde-combo-page">
    <el-card shadow="never">
      <template #header><div class="header"><span>2日DDE捡漏</span><div class="header-actions"><el-date-picker v-model="dateRange" class="date-range" type="daterange" value-format="YYYYMMDD" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" /><el-button type="primary" icon="Search" @click="handleQuery">查询</el-button></div></div></template>
      <el-table v-loading="loading" :data="rows" border @sort-change="handleSortChange">
        <el-table-column label="交易日" prop="signalDate" width="100" sortable="custom" fixed="left">
          <template #default="{ row }">
            <div class="trade-dates">
              <span>{{ row.signalDate }}</span>
              <span>{{ row.previousSignalDate }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="股票" min-width="100" fixed="left"><template #default="{ row }">{{ row.stockCode }} {{ row.stockName }}</template></el-table-column>

        <el-table-column label="行业" min-width="80" fixed="left"><template #default="{ row }">{{ getStockIndustry(row.stockCode) }}</template></el-table-column>

        <el-table-column label="概念" min-width="180" fixed="left"><template #default="{ row }">{{ getStockConcept(row.stockCode) }}</template></el-table-column>
        <el-table-column label="昨日次数" prop="previousSignalCount" min-width="90" sortable="custom" />
        <el-table-column label="今日次数" prop="todaySignalCount" min-width="90" sortable="custom" />
        <el-table-column label="昨日强度" prop="previousMainNetRatio" min-width="90" sortable="custom"><template #default="{ row }">{{ percent(row.previousMainNetRatio, true) }}</template></el-table-column>
        <el-table-column label="今日强度" prop="todayMainNetRatio" min-width="90" sortable="custom"><template #default="{ row }">{{ percent(row.todayMainNetRatio, true) }}</template></el-table-column>
        <el-table-column v-for="day in 5" :key="day" :label="`T+${day}最高`" :prop="`t${day}MaxReturnPct`" min-width="95" sortable="custom"><template #default="{ row }"><span :class="['return-value', returnClass(row[`t${day}MaxReturnPct`])]">{{ percent(row[`t${day}MaxReturnPct`]) }}</span></template></el-table-column>
      </el-table>
      <pagination v-show="total > 0" v-model:page="query.pageNum" v-model:limit="query.pageSize" :total="total" @pagination="getList" />
    </el-card>
  </div>
</template>

<script setup>
import { listDdeCombo } from '@/api/stock/ddeFund'
import { getStockConcept, getStockIndustry } from '@/utils/stockMetadata'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const dateRange = ref([])
const query = reactive({ pageNum: 1, pageSize: 20, sortBy: undefined, sortOrder: undefined })

function getList() {
  loading.value = true
  listDdeCombo({ ...query, startDate: dateRange.value?.[0], endDate: dateRange.value?.[1] }).then(response => {
    rows.value = response.data.rows
    total.value = response.data.total
  }).finally(() => { loading.value = false })
}

function handleQuery() { query.pageNum = 1; getList() }
function handleSortChange({ prop, order }) { query.sortBy = order ? prop : undefined; query.sortOrder = order || undefined; query.pageNum = 1; getList() }
function percent(value, ratio = false) { return value === null || value === undefined ? '-' : `${(ratio ? value * 100 : value).toFixed(2)}%` }
function number(value) { return value === null || value === undefined ? '-' : value.toFixed(2) }
function returnClass(value) {
  if (value === null || value === undefined) return ''
  return value > 1.8 ? 'return-high' : 'return-low'
}

getList()
</script>

<style scoped>
.dde-combo-page { padding: 20px; }
.header { display: flex; align-items: center; justify-content: space-between; font-size: 18px; font-weight: 600; }
.header-actions { display: flex; gap: 10px; align-items: center; }
.date-range { width: 280px; }
:deep(.el-table) { white-space: nowrap; }
.trade-dates { display: flex; flex-direction: column; line-height: 1.5; }
.return-value { display: block; padding: 1px 4px; border-radius: 3px; text-align: center; }
.return-high { background: #fef0f0; color: #f56c6c; }
.return-low { background: #f0f9eb; color: #67c23a; }
</style>
