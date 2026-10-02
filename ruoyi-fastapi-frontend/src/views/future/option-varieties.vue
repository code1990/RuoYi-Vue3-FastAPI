<template><div class="option-page"><el-alert title="全部期权品种目录；默认每页 100 条。大盘期权合约、行情仍只纳入大盘相关池。" type="info" :closable="false" show-icon /><el-table v-loading="loading" :data="rows" stripe><el-table-column prop="varietyCode" label="代码" width="110" /><el-table-column prop="name" label="品种" min-width="180" /><el-table-column prop="exchangeName" label="交易所" min-width="150" /><el-table-column prop="settlementType" label="结算" width="100" /><el-table-column prop="contractMultiplier" label="合约乘数" width="110" /></el-table><pagination v-show="total > 0" v-model:page="query.pageNum" v-model:limit="query.pageSize" :total="total" @pagination="getList" /></div></template>
<script setup name="OptionVarieties">
import { reactive, ref } from 'vue'
import { listOptionVarieties } from '@/api/future/option'
const loading = ref(false); const rows = ref([]); const total = ref(0); const query = reactive({ pageNum: 1, pageSize: 100 })
function getList(){ loading.value = true; listOptionVarieties(query).then(response => { rows.value = response.data.rows || []; total.value = response.data.total || 0 }).finally(() => { loading.value = false }) } getList()
</script><style scoped>.option-page{padding:20px}.el-table{margin-top:16px}</style>
