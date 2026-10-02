<template>
  <div class="linkage-page">
    <el-alert title="以期货主标的观察整条期权链：Call 代表看涨权利，Put 代表看跌权利；日涨跌来自已缓存的相邻两根日线。" type="info" :closable="false" show-icon />
    <el-form inline class="form"><el-form-item label="期货主标的"><el-input v-model="underlyingCode" style="width:160px" placeholder="如 I2709" /></el-form-item><el-form-item label="期货查询"><el-input v-model="keyword" style="width:140px" placeholder="如 铁矿" /></el-form-item><el-button type="primary" :loading="loading" @click="load">查询期权链</el-button><el-button :loading="refreshing" @click="refreshDaily">更新链日线</el-button></el-form>
    <el-card shadow="never"><template #header>{{ underlyingCode }} 期权日涨跌（Call 红 / Put 绿）</template><div class="bars"><div v-for="row in strikeRows" :key="row.strike" class="strike"><span class="rate rise">{{ percent(row.call?.dayChangeRate) }}</span><span class="bar rise" :style="{ height: height(row.call?.dayChangeRate) }" /><b>{{ row.strike }}</b><span class="bar fall" :style="{ height: height(row.put?.dayChangeRate) }" /><span class="rate fall">{{ percent(row.put?.dayChangeRate) }}</span></div></div></el-card>
    <el-card shadow="never" class="card"><template #header>期货主力行情</template><el-table :data="futureRows"><el-table-column prop="contractCode" label="代码" /><el-table-column prop="contractName" label="名称" /><el-table-column prop="lastPx" label="最新价" /><el-table-column label="涨跌幅"><template #default="{ row }"><span :class="color(row.pxChangeRate)">{{ percent(row.pxChangeRate) }}</span></template></el-table-column></el-table></el-card>
    <el-card shadow="never" class="card"><template #header>对应期权涨跌列表</template><el-table :data="chainRows" v-loading="loading"><el-table-column prop="strikePrice" label="行权价" width="100" /><el-table-column prop="optionType" label="方向" width="90"><template #default="{ row }"><el-tag :type="row.optionType === 'call' ? 'danger' : 'success'">{{ row.optionType === 'call' ? 'Call 看涨' : 'Put 看跌' }}</el-tag></template></el-table-column><el-table-column prop="thscode" label="期权合约" min-width="190" /><el-table-column prop="name" label="名称" min-width="150" /><el-table-column label="日涨跌"><template #default="{ row }"><span :class="color(row.dayChangeRate)">{{ percent(row.dayChangeRate) }}</span></template></el-table-column></el-table></el-card>
  </div>
</template>
<script setup name="OptionFutureLinkage">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getOptionChain, refreshOptionChainDaily } from '@/api/future/option'
import { listFutureQuote } from '@/api/future/market'
const underlyingCode = ref('I2709'); const keyword = ref('铁矿'); const loading = ref(false); const refreshing = ref(false); const chainRows = ref([]); const futureRows = ref([])
const strikeRows = computed(() => Object.values(chainRows.value.reduce((rows, item) => { const row = rows[item.strikePrice] || (rows[item.strikePrice] = { strike: item.strikePrice }); row[item.optionType === 'call' ? 'call' : 'put'] = item; return rows }, {})))
function percent(value) { return value === null || value === undefined ? '--' : `${Number(value) > 0 ? '+' : ''}${Number(value).toFixed(2)}%` }
function color(value) { return Number(value) > 0 ? 'rise' : Number(value) < 0 ? 'fall' : '' }
function height(value) { return `${value === null || value === undefined ? 2 : Math.max(2, Math.min(160, Math.abs(Number(value)) * 12))}px` }
function load() { loading.value = true; Promise.all([getOptionChain(underlyingCode.value), listFutureQuote({ scope: 'domestic', keyword: keyword.value || undefined, pageNum: 1, pageSize: 10 })]).then(([chain, future]) => { chainRows.value = chain.data || []; futureRows.value = future.data.rows || [] }).catch(() => ElMessage.error('查询失败，请确认期货主标的')).finally(() => { loading.value = false }) }
function refreshDaily() { refreshing.value = true; refreshOptionChainDaily(underlyingCode.value).then(() => { ElMessage.success('期权链日线已更新'); load() }).catch(() => ElMessage.error('日线更新失败')).finally(() => { refreshing.value = false }) }
load()
</script>
<style scoped>
.linkage-page{padding:20px}.form,.card{margin-top:16px}.bars{height:270px;display:flex;align-items:center;gap:9px;overflow-x:auto;padding:12px}.strike{height:230px;min-width:68px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px}.bar{width:22px;background:#909399}.bar.rise{background:#f56c6c}.bar.fall{background:#67c23a}.rate{font-size:11px;white-space:nowrap}.rise{color:#f56c6c}.fall{color:#67c23a}
</style>
