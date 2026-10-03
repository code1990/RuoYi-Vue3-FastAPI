<template>
  <div class="app-container">
    <el-alert title="展示已入库的连续、主连、加权期货原始日线；连续/主连不是可交易具体合约，仅供研究观察，不构成投资建议。" type="info" :closable="false" show-icon />
    <el-form inline class="query"><el-form-item label="历史序列"><el-select v-model="thscode" filterable style="width:300px" @change="loadDaily"><el-option v-for="item in series" :key="item.thscode" :value="item.thscode" :label="`${item.thscode}｜${item.series_name || item.product_code}（${label(item.series_type)}，${item.samples}）`" /></el-select></el-form-item></el-form>
    <el-descriptions v-if="selected" :column="4" border class="summary"><el-descriptions-item label="名称">{{ selected.series_name || '--' }}</el-descriptions-item><el-descriptions-item label="序列类型">{{ label(selected.series_type) }}</el-descriptions-item><el-descriptions-item label="样本区间">{{ selected.first_trade_date }} ~ {{ selected.last_trade_date }}</el-descriptions-item><el-descriptions-item label="日线数">{{ selected.samples }}</el-descriptions-item></el-descriptions>
    <el-table v-loading="loading" :data="rows" border height="620"><el-table-column prop="trade_date" label="交易日" width="110" /><el-table-column prop="open_price" label="开盘" /><el-table-column prop="high_price" label="最高" /><el-table-column prop="low_price" label="最低" /><el-table-column prop="close_price" label="收盘" /><el-table-column prop="volume" label="成交量" /><el-table-column prop="turnover" label="成交额" /></el-table>
  </div>
</template>
<script setup name="FutureHistory">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { listFutureHistoryDaily, listFutureHistorySeries } from '@/api/future/history'
const series = ref([]); const thscode = ref(''); const rows = ref([]); const loading = ref(false)
const selected = computed(() => series.value.find(item => item.thscode === thscode.value))
const label = value => ({ continuous: '连续', main: '主连', weighted: '加权' }[value] || value || '--')
function loadDaily() { if (!thscode.value) return; loading.value = true; listFutureHistoryDaily(thscode.value).then(response => { rows.value = response.data || [] }).catch(() => ElMessage.error('历史日线查询失败')).finally(() => { loading.value = false }) }
listFutureHistorySeries().then(response => { series.value = response.data || []; thscode.value = series.value[0]?.thscode || ''; loadDaily() }).catch(() => ElMessage.error('历史序列加载失败'))
</script>
<style scoped>.query,.summary{margin:16px 0}</style>
