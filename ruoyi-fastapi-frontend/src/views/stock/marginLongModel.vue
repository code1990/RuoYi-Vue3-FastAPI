<template>
  <div class="stock-data-page"><el-card shadow="never"><template #header><div class="header"><span>融资做多强度</span><div><el-date-picker v-model="dateRange" type="daterange" value-format="YYYYMMDD" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" @change="handleQuery" /><el-tag type="info">历史模型监控</el-tag></div></div></template>
    <el-table v-loading="loading" :data="rows" border>
      <el-table-column label="交易日" prop="tradeDate" width="100" fixed="left" />
      <el-table-column label="股票" min-width="110" fixed="left"><template #default="{ row }">{{ row.stockCode }} {{ row.stockName }}</template></el-table-column>
      <el-table-column label="行业" prop="industryName" min-width="80" fixed="left" />
      <el-table-column label="概念" min-width="180" fixed="left"><template #default="{ row }">{{ getStockConcept(row.stockCode) }}</template></el-table-column>
      <el-table-column label="排名" prop="rankNo" width="70" sortable="custom" />
      <el-table-column label="综合分" prop="score" width="90" sortable="custom"><template #default="{ row }">{{ number(row.score) }}</template></el-table-column>
      <el-table-column label="净融资参与度" prop="netBuyRatio" min-width="115" sortable="custom"><template #default="{ row }">{{ percent(row.netBuyRatio, true) }}</template></el-table-column>
      <el-table-column label="5日余额变化" prop="balanceChangeRatio" min-width="110" sortable="custom"><template #default="{ row }">{{ percent(row.balanceChangeRatio, true) }}</template></el-table-column>
      <el-table-column label="20日涨跌" prop="priceReturn20d" min-width="90"><template #default="{ row }">{{ percent(row.priceReturn20d) }}</template></el-table-column>
      <el-table-column label="分类" prop="signalType" width="95"><template #default="{ row }"><el-tag size="small" :type="tagType(row.signalType)">{{ labels[row.signalType] || row.signalType }}</el-tag></template></el-table-column>
      <el-table-column v-for="day in [1, 3, 5, 10, 20]" :key="day" :label="`T+${day}`" :prop="`next${day}dReturnPct`" min-width="85"><template #default="{ row }"><span :class="returnClass(row[`next${day}dReturnPct`])">{{ percent(row[`next${day}dReturnPct`]) }}</span></template></el-table-column>
    </el-table><pagination v-show="total > 0" v-model:page="query.pageNum" v-model:limit="query.pageSize" :total="total" @pagination="getList" />
  </el-card></div>
</template>
<script setup>
import { listMarginLongModel } from '@/api/stock/marginTrading'
import { getStockConcept } from '@/utils/stockMetadata'
const loading = ref(false); const rows = ref([]); const total = ref(0); const dateRange = ref([]); const query = reactive({ pageNum: 1, pageSize: 30 }); const labels = { strong: '强势加仓', watch: '观察', avoid: '回避' }
function getList() { loading.value = true; listMarginLongModel({ ...query, startDate: dateRange.value?.[0], endDate: dateRange.value?.[1] }).then(({ data }) => { rows.value = data.rows; total.value = data.total }).finally(() => { loading.value = false }) }
function handleQuery() { query.pageNum = 1; getList() }
function percent(value, ratio = false) { if (value === null || value === undefined) return '-'; const n = ratio ? value * 100 : value; return `${n >= 0 ? '+' : ''}${n.toFixed(2)}%` }
function number(value) { return value === null || value === undefined ? '-' : Number(value).toFixed(1) }
function tagType(value) { return value === 'strong' ? 'success' : value === 'avoid' ? 'danger' : 'warning' }
function returnClass(value) { return value === null || value === undefined ? '' : value > 0 ? 'return-high' : 'return-low' }
getList()
</script>
<style scoped>.stock-data-page{padding:20px}.header{display:flex;align-items:center;justify-content:space-between;font-size:18px;font-weight:600}.header>div{display:flex;align-items:center;gap:12px}:deep(.el-table){white-space:nowrap}.return-high{color:#f56c6c}.return-low{color:#67c23a}</style>
