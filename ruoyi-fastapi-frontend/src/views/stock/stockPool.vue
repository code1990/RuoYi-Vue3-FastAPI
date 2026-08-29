<template>
  <div class="stock-data-page">
    <el-card shadow="never">
      <template #header><div class="header"><span>股票池</span><el-date-picker v-model="tradeDate" type="date" value-format="YYYYMMDD" placeholder="交易日" @change="loadResults" /></div></template>
      <div class="pool-layout">
        <el-menu class="formula-menu" :default-active="activeFormulaId" @select="selectFormula">
          <el-menu-item v-for="item in formulas" :key="item.id" :index="String(item.id)">{{ item.name }}</el-menu-item>
        </el-menu>
        <div class="result">
          <el-empty v-if="!activeCode" description="请选择 stock-admin 选股公式" />
          <template v-else><div class="result-title">{{ activeName }} <el-tag type="info">stock-admin 结果</el-tag></div><el-table v-loading="loading" :data="rows" border><el-table-column label="交易日" prop="tradeDate" width="100" fixed="left"/><el-table-column label="股票" min-width="110" fixed="left"><template #default="{row}">{{ row.stockCode }} {{ row.stockName }}</template></el-table-column><el-table-column label="行业" min-width="80" fixed="left"><template #default="{row}">{{ getStockIndustry(row.stockCode) }}</template></el-table-column><el-table-column label="概念" min-width="180" fixed="left"><template #default="{row}">{{ getStockConcept(row.stockCode) }}</template></el-table-column><el-table-column label="交易时间" prop="slotTradeDate"/><el-table-column label="买入价" prop="hitPrice"/></el-table></template>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { listStockPoolFormulas, listStockPoolResults } from '@/api/stock/marginTrading'
import { getStockConcept, getStockIndustry } from '@/utils/stockMetadata'
import useAppStore from '@/store/modules/app'

const route = useRoute(); const router = useRouter(); const appStore = useAppStore(); const initialSidebarHidden = appStore.sidebar.hide
const formulas = ref([]); const rows = ref([]); const loading = ref(false); const activeCode = ref(''); const activeFormulaId = ref(''); const tradeDate = ref('')
const activeName = computed(() => formulas.value.find(item => item.code === activeCode.value)?.name || activeCode.value)
async function selectFormula(id) { const formula = formulas.value.find(item => String(item.id) === String(id)); if (!formula) return; activeFormulaId.value = String(formula.id); activeCode.value = formula.code; if (route.params.formulaPath !== String(formula.id)) router.replace({ path: `/stock-pools/${formula.id}` }); await loadResults() }
async function loadResults() { if (!activeCode.value) return; loading.value = true; try { const response = await listStockPoolResults({ formulaCode: activeCode.value, tradeDate: tradeDate.value || undefined, limit: 500 }); rows.value = response.data?.items || [] } finally { loading.value = false } }
onMounted(async () => { appStore.toggleSideBarHide(true); const response = await listStockPoolFormulas(); formulas.value = response.data || []; const selectedId = route.params.formulaPath || route.query.formulaId; const formula = formulas.value.find(item => String(item.id) === String(selectedId)); if (formula) selectFormula(formula.id); else if (formulas.value.length) selectFormula(formulas.value[0].id) })
onBeforeUnmount(() => appStore.toggleSideBarHide(initialSidebarHidden))
</script>

<style scoped>.stock-data-page{padding:20px}.header,.result-title{display:flex;align-items:center;justify-content:space-between;font-size:18px;font-weight:600}.pool-layout{display:flex;min-height:620px}.formula-menu{width:220px;flex:none}.result{padding:0 20px;flex:1;overflow:auto}.result-title{margin-bottom:16px}:deep(.el-table){white-space:nowrap}</style>
