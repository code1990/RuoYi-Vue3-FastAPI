<template>
  <div class="future-market-page">
    <el-card shadow="never">
      <template #header><div class="header"><span>{{ title }}</span><div><el-input v-model="query.keyword" placeholder="代码或名称" clearable @keyup.enter="handleQuery" /><el-button type="primary" icon="Search" @click="handleQuery">查询</el-button></div></div></template>
      <el-table v-loading="loading" :data="rows" border>
        <el-table-column label="排名" width="65"><template #default="{ $index }">{{ (query.pageNum - 1) * query.pageSize + $index + 1 }}</template></el-table-column>
        <el-table-column label="代码" prop="contractCode" min-width="130" />
        <el-table-column label="名称" prop="contractName" min-width="120" />
        <el-table-column label="交易日" prop="marketDate" min-width="95" />
        <el-table-column label="现价" prop="lastPx" min-width="90"><template #default="{ row }">{{ number(row.lastPx) }}</template></el-table-column>
        <el-table-column label="涨幅%" prop="pxChangeRate" min-width="90"><template #default="{ row }"><span :class="color(row.pxChangeRate)">{{ percent(row.pxChangeRate) }}</span></template></el-table-column>
        <el-table-column label="涨速%" prop="min5Chgpct" min-width="90"><template #default="{ row }"><span :class="color(row.min5Chgpct)">{{ percent(row.min5Chgpct) }}</span></template></el-table-column>
        <el-table-column label="涨跌" prop="pxChange" min-width="90"><template #default="{ row }"><span :class="color(row.pxChange)">{{ number(row.pxChange, true) }}</span></template></el-table-column>
        <el-table-column label="今开" prop="openPx" min-width="90"><template #default="{ row }">{{ number(row.openPx) }}</template></el-table-column>
        <el-table-column label="最高" prop="highPx" min-width="90"><template #default="{ row }">{{ number(row.highPx) }}</template></el-table-column>
        <el-table-column label="最低" prop="lowPx" min-width="90"><template #default="{ row }">{{ number(row.lowPx) }}</template></el-table-column>
        <el-table-column label="昨收" prop="prevSettlement" min-width="90"><template #default="{ row }">{{ number(row.prevSettlement) }}</template></el-table-column>
        <el-table-column label="交易所" prop="marketName" min-width="130" />
        <el-table-column label="品种" prop="productName" min-width="120" />
      </el-table>
      <pagination v-show="total > 0" v-model:page="query.pageNum" v-model:limit="query.pageSize" :total="total" @pagination="getList" />
    </el-card>
  </div>
</template>

<script setup>
import { listFutureQuote } from '@/api/future/market'

const route = useRoute()
const scope = computed(() => route.query.scope === 'overseas' ? 'overseas' : 'domestic')
const title = computed(() => scope.value === 'overseas' ? '国际期货行情' : '国内期货行情')
const loading = ref(false)
const rows = ref([])
const total = ref(0)
const query = reactive({ pageNum: 1, pageSize: 100, keyword: '' })

function getList() { loading.value = true; listFutureQuote({ ...query, scope: scope.value, keyword: query.keyword || undefined }).then(response => { rows.value = response.data.rows; total.value = response.data.total }).finally(() => { loading.value = false }) }
function handleQuery() { query.pageNum = 1; getList() }
function number(value, signed = false) { if (value === null || value === undefined) return '-'; const number = Number(value); return `${signed && number > 0 ? '+' : ''}${number}` }
function percent(value) { return value === null || value === undefined ? '-' : `${Number(value) > 0 ? '+' : ''}${Number(value).toFixed(2)}%` }
function color(value) { return Number(value) > 0 ? 'rise' : Number(value) < 0 ? 'fall' : '' }
watch(scope, handleQuery)
getList()
</script>

<style scoped>
.future-market-page { padding: 20px; }
.header, .header > div { display: flex; align-items: center; gap: 10px; }
.header { justify-content: space-between; font-size: 18px; font-weight: 600; }
:deep(.el-table) { white-space: nowrap; }
.rise { color: #f56c6c; }.fall { color: #67c23a; }
</style>
