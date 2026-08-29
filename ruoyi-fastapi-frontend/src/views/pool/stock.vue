<template>
  <div class="stock-pool-page">
    <el-card shadow="never">
      <template #header><div class="header"><span>{{ activeName || '股票池' }}</span><div class="header-actions"><el-date-picker v-model="tradeDate" type="date" value-format="YYYYMMDD" placeholder="交易日" @change="loadResults" /><el-button type="primary" icon="Search" @click="loadResults">查询</el-button></div></div></template>
      <el-table v-loading="loading" :data="rows" border>
        <el-table-column label="交易日" prop="tradeDate" width="88" fixed="left" />
        <el-table-column label="股票" min-width="120" fixed="left"><template #default="{ row }">{{ row.stockCode }} {{ row.stockName }}</template></el-table-column>
        <el-table-column label="行业" min-width="80" fixed="left"><template #default="{ row }">{{ getStockIndustry(row.stockCode) }}</template></el-table-column>
        <el-table-column label="概念" min-width="180" fixed="left"><template #default="{ row }">{{ getStockConcept(row.stockCode) }}</template></el-table-column>
        <el-table-column label="交易时间" prop="slotTradeDate" min-width="100" />
        <el-table-column label="买入价" prop="hitPrice" min-width="90" />
        <el-table-column v-for="day in 5" :key="day" :label="`T+${day}涨幅`" :prop="`t${day}MaxReturnPct`" min-width="100"><template #default="{ row }"><span :class="['return-value', returnClass(row[`t${day}MaxReturnPct`])]">{{ percent(row[`t${day}MaxReturnPct`]) }}</span></template></el-table-column>
      </el-table>
      <pagination v-show="total > 0" v-model:page="pageNum" v-model:limit="pageSize" :total="total" @pagination="loadResults" />
    </el-card>
  </div>
</template>

<script setup>
import { listStockPoolFormulas, listStockPoolResults } from '@/api/stock/marginTrading'
import { getStockConcept, getStockIndustry } from '@/utils/stockMetadata'

const route = useRoute(); const formulas = ref([]); const rows = ref([]); const loading = ref(false); const tradeDate = ref(''); const pageNum = ref(1); const pageSize = ref(20); const total = ref(0); const formulaId = computed(() => route.query.formulaId || route.path.split('/').at(-1))
const activeName = computed(() => formulas.value.find(item => String(item.id) === String(formulaId.value))?.name || '')
async function loadResults() { if (!formulaId.value) return; loading.value = true; try { const response = await listStockPoolResults({ formulaId: formulaId.value, tradeDate: tradeDate.value || undefined, limit: 500 }); rows.value = response.data?.rows || response.data?.items || []; total.value = response.data?.total || rows.value.length } finally { loading.value = false } }
async function loadFormula() { try { const response = await listStockPoolFormulas(); formulas.value = response.data || []; await loadResults() } catch { rows.value = []; total.value = 0 } }
watch(() => [route.path, route.query.formulaId], loadFormula, { immediate: true })
function percent(value) { return value == null ? '-' : `${value >= 0 ? '+' : ''}${Number(value).toFixed(2)}%` }
function returnClass(value) { return value == null ? '' : value > 0 ? 'return-high' : 'return-low' }
</script>

<style scoped>.stock-pool-page{padding:20px}.header{display:flex;align-items:center;justify-content:space-between;font-size:18px;font-weight:600}.header-actions{display:flex;gap:10px;align-items:center}.return-value{display:block;padding:1px 4px;border-radius:3px;text-align:center}.return-high{background:#fef0f0;color:#f56c6c}.return-low{background:#f0f9eb;color:#67c23a}:deep(.el-table){white-space:nowrap}</style>
