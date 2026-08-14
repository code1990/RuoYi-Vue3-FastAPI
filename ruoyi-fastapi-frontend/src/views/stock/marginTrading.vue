<template>
  <div class="stock-data-page">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <span>{{ comboDays ? `融资${comboDays}天` : '融资融券' }}</span>
          <div class="header-actions">
            <el-date-picker v-model="dateRange" class="date-range" type="daterange" value-format="YYYYMMDD" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" />
            <el-button type="primary" icon="Search" @click="handleQuery">查询</el-button>
          </div>
        </div>
      </template>
      <el-table v-loading="loading" :data="rows" border>
        <el-table-column label="交易日" prop="signalDate" width="100" />
        <el-table-column label="排名" :prop="comboDays ? 'latestRank' : 'rankNo'" width="68" />
        <el-table-column label="股票" min-width="88"><template #default="{ row }">{{ row.stockCode }} {{ row.stockName }}</template></el-table-column>
        <el-table-column label="行业" prop="industryName" min-width="80" />
        <el-table-column label="概念" min-width="180"><template #default="{ row }">{{ getStockConcept(row.stockCode) }}</template></el-table-column>
        <el-table-column label="机构" min-width="70"><template #default="{ row }">{{ getStockOrgNum(row.stockCode) }}</template></el-table-column>
        <el-table-column label="买入价" prop="entryPrice" min-width="88" />
        <el-table-column label="早盘开盘涨幅" min-width="112"><template #default="{ row }">{{ percent(comboDays ? row.entryOpenReturnPct : row.entryChangePct) }}</template></el-table-column>
        <el-table-column :label="comboDays ? '累计评分' : '评分'" min-width="80"><template #default="{ row }">{{ number(comboDays ? row.totalScore : row.score) }}</template></el-table-column>
        <el-table-column label="融资参与度" min-width="105"><template #default="{ row }">{{ percent(comboDays ? row.avgParticipationRatio : row.participationRatio, true) }}</template></el-table-column>
        <el-table-column label="余额变化强度" min-width="115"><template #default="{ row }">{{ percent(comboDays ? row.avgBalanceChangeRatio : row.balanceChangeRatio, true) }}</template></el-table-column>
        <el-table-column label="尾盘" min-width="96"><template #default="{ row }">{{ percent(row.closeReturnPct) }}</template></el-table-column>
        <el-table-column v-for="day in 5" :key="day" :label="`T+${day}涨幅`" min-width="110"><template #default="{ row }">{{ percent(row[`t${day}MaxReturnPct`]) }}</template></el-table-column>
      </el-table>
      <pagination v-show="total > 0" v-model:page="query.pageNum" v-model:limit="query.pageSize" :total="total" @pagination="getList" />
    </el-card>
  </div>
</template>

<script setup>
import { listMarginCombo, listMarginLongPerformance } from '@/api/stock/marginTrading'
import { getStockConcept, getStockOrgNum } from '@/utils/stockMetadata'

const route = useRoute()
const comboDays = computed(() => [2, 3, 5].includes(Number(route.query.windowDays)) ? Number(route.query.windowDays) : 0)
const loading = ref(false)
const rows = ref([])
const total = ref(0)
const dateRange = ref([])
const query = reactive({ pageNum: 1, pageSize: 20 })

function getList() {
  loading.value = true
  const list = comboDays.value ? listMarginCombo : listMarginLongPerformance
  list({ ...query, windowDays: comboDays.value || undefined, startDate: dateRange.value?.[0], endDate: dateRange.value?.[1] }).then(response => {
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

function number(value) {
  return value === null || value === undefined ? '-' : value.toFixed(2)
}

getList()
watch(comboDays, handleQuery)
</script>

<style scoped>
.stock-data-page { padding: 20px; }
.header { display: flex; align-items: center; justify-content: space-between; font-size: 18px; font-weight: 600; }
:deep(.el-table) { white-space: nowrap; }
.header-actions { display: flex; flex: 0 0 auto; gap: 10px; align-items: center; margin-left: 16px; margin-right: auto; }
:deep(.date-range.el-date-editor) { width: 280px !important; flex: 0 0 280px; }
</style>
