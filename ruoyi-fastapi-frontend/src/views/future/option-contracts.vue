<template><div class="option-page"><el-table v-loading="loading" :data="rows" stripe><el-table-column prop="varietyCode" label="品种" width="100" /><el-table-column prop="thscode" label="完整合约代码" min-width="210" /><el-table-column prop="name" label="名称" min-width="160" /><el-table-column prop="lastTradeDate" label="最后交易日" width="120" /></el-table><pagination v-show="total > 0" v-model:page="query.pageNum" v-model:limit="query.pageSize" :total="total" @pagination="getList" /></div></template>
<script setup name="OptionContracts">
import { reactive, ref } from 'vue'
import { listMarketOptionContracts } from '@/api/future/option'
const loading = ref(false); const rows = ref([]); const total = ref(0); const query = reactive({ pageNum: 1, pageSize: 100 })
function getList(){ loading.value=true; listMarketOptionContracts(query).then(response=>{ rows.value=response.data.rows||[]; total.value=response.data.total||0 }).finally(()=>{loading.value=false}) } getList()
</script><style scoped>.option-page{padding:20px}</style>
