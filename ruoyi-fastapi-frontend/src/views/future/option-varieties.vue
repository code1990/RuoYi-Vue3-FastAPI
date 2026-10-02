<template><div class="option-page"><el-alert title="大盘期权池：沪深300、上证50及宽基 ETF 期权；商品期权不纳入。" type="info" :closable="false" show-icon /><el-table v-loading="loading" :data="rows" stripe><el-table-column prop="varietyCode" label="代码" width="110" /><el-table-column prop="name" label="品种" min-width="180" /><el-table-column prop="exchangeName" label="交易所" min-width="150" /><el-table-column prop="settlementType" label="结算" width="100" /><el-table-column prop="contractMultiplier" label="合约乘数" width="110" /></el-table></div></template>
<script setup name="OptionVarieties">
import { ref } from 'vue'
import { listMarketOptionVarieties } from '@/api/future/option'
const loading = ref(false); const rows = ref([])
loading.value = true; listMarketOptionVarieties().then(response => { rows.value = response.data || [] }).finally(() => { loading.value = false })
</script><style scoped>.option-page{padding:20px}.el-table{margin-top:16px}</style>
