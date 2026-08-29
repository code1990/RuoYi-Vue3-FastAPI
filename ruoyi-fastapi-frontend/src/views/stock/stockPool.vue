<template>
  <div class="stock-data-page">
    <el-card shadow="never">
      <template #header><div class="header"><span>股票池</span><el-date-picker v-model="tradeDate" type="date" value-format="YYYYMMDD" placeholder="交易日" @change="loadResults" /></div></template>
      <div class="result">
          <el-empty v-if="!activeCode" description="请选择 stock-admin 选股公式" />
          <template v-else><div class="result-title">{{ activeName }} <el-tag type="info">stock-admin 结果</el-tag></div><el-table v-loading="loading" :data="rows" border><el-table-column label="交易日" prop="tradeDate" width="100" fixed="left"/><el-table-column label="股票" min-width="110" fixed="left"><template #default="{row}">{{ row.stockCode }} {{ row.stockName }}</template></el-table-column><el-table-column label="行业" min-width="80" fixed="left"><template #default="{row}">{{ getStockIndustry(row.stockCode) }}</template></el-table-column><el-table-column label="概念" min-width="180" fixed="left"><template #default="{row}">{{ getStockConcept(row.stockCode) }}</template></el-table-column><el-table-column label="交易时间" prop="slotTradeDate"/><el-table-column label="买入价" prop="hitPrice"/></el-table></template>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { listStockPoolFormulas, listStockPoolResults } from '@/api/stock/marginTrading'
import { getStockConcept, getStockIndustry } from '@/utils/stockMetadata'

const route = useRoute()
const formulas = ref([]); const rows = ref([]); const loading = ref(false); const activeCode = ref(''); const tradeDate = ref('')
const activeName = computed(() => formulas.value.find(item => item.code === activeCode.value)?.name || activeCode.value)
async function loadResults() { if (!activeCode.value) return; loading.value = true; try { const response = await listStockPoolResults({ formulaCode: activeCode.value, tradeDate: tradeDate.value || undefined, limit: 500 }); rows.value = response.data?.items || [] } finally { loading.value = false } }
async function loadFormula() { const formulaId = route.query.formulaId || route.path.split('/').at(-1); const response = await listStockPoolFormulas(); formulas.value = response.data || []; const formula = formulas.value.find(item => String(item.id) === String(formulaId)); activeCode.value = formula?.code || ''; rows.value = []; if (formula) await loadResults() }
watch(() => [route.path, route.query.formulaId], loadFormula, { immediate: true })
</script>

<style scoped>.stock-data-page{padding:20px}.header,.result-title{display:flex;align-items:center;justify-content:space-between;font-size:18px;font-weight:600}.result{overflow:auto}.result-title{margin-bottom:16px}:deep(.el-table){white-space:nowrap}</style>
