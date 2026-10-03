<template>
  <div class="app-container">
    <el-alert title="连续期货日线与期权日线同交易日联动研究；连续合约换月可能产生跳空，仅供研究观察，不构成投资建议。" type="info" :closable="false" show-icon />
    <el-form inline class="query"><el-form-item label="标的合约"><el-select v-model="contract" filterable placeholder="选择合约" style="width:220px" @change="load"><el-option v-for="item in contracts" :key="item.underlyingContract" :label="`${item.underlyingContract}（${item.samples}）`" :value="item.underlyingContract" /></el-select></el-form-item></el-form>
    <el-descriptions v-if="result.contractCode" :column="4" border class="summary"><el-descriptions-item label="样本区间">{{ result.firstTradeDate }} ~ {{ result.lastTradeDate }}</el-descriptions-item><el-descriptions-item label="总顺趋势">{{ summary({ aligned: result.aligned, total: result.total, rate: result.rate }) }}</el-descriptions-item><el-descriptions-item label="Call">{{ summary(result.call) }}</el-descriptions-item><el-descriptions-item label="Put">{{ summary(result.put) }}</el-descriptions-item></el-descriptions>
    <el-table :data="result.rows || []" v-loading="loading" border><el-table-column prop="tradeDate" label="交易日" width="110" /><el-table-column prop="futureContinuousCode" label="连续期货" width="120" /><el-table-column label="期货涨跌幅" width="120"><template #default="{ row }"><span :class="color(row.futureChangeRate)">{{ percent(row.futureChangeRate) }}</span></template></el-table-column><el-table-column label="Call 联动"><template #default="{ row }">{{ summary(row.call) }}</template></el-table-column><el-table-column label="Put 联动"><template #default="{ row }">{{ summary(row.put) }}</template></el-table-column></el-table>
  </div>
</template>
<script setup name="OptionFutureLinkageHistory">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getOptionLinkageHistory, listOptionLinkageHistoryContracts } from '@/api/future/option'
const contracts = ref([]); const contract = ref(''); const result = ref({ rows: [] }); const loading = ref(false)
function summary(value) { return value && value.total ? `顺趋势 ${Number(value.rate).toFixed(1)}%（${value.aligned}/${value.total}）` : '--' }
function percent(value) { return value === null || value === undefined ? '--' : `${Number(value) > 0 ? '+' : ''}${Number(value).toFixed(2)}%` }
function color(value) { return Number(value) > 0 ? 'rise' : Number(value) < 0 ? 'fall' : '' }
function load() { if (!contract.value) return; loading.value = true; getOptionLinkageHistory(contract.value).then(response => { result.value = response.data || { rows: [] } }).catch(() => ElMessage.error('历史联动查询失败')).finally(() => { loading.value = false }) }
listOptionLinkageHistoryContracts().then(response => { contracts.value = response.data || []; contract.value = contracts.value[0]?.underlyingContract || ''; load() }).catch(() => ElMessage.error('历史合约加载失败'))
</script>
<style scoped>.query,.summary{margin:16px 0}.rise{color:#f56c6c}.fall{color:#67c23a}</style>
