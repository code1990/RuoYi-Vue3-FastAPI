<template>
  <div class="linkage-page">
    <el-alert title="期权与期货联动观察：期权涨跌以当日首笔至最新分时计算，不能替代持仓量、增仓和隐含波动率的多空研判。" type="warning" :closable="false" show-icon />
    <el-form inline class="form"><el-form-item label="期权完整代码"><el-input v-model="thscode" style="width:270px" /></el-form-item><el-form-item label="对应期货"><el-input v-model="keyword" style="width:150px" placeholder="如：铁矿石" /></el-form-item><el-button type="primary" :loading="loading" @click="load">联动查询</el-button></el-form>
    <el-card shadow="never"><template #header>期权—期货涨跌联动</template><div class="bars"><div v-for="item in bars" :key="item.name" class="bar-item"><strong>{{ item.name }}</strong><span :class="rateClass(item.rate)">{{ percent(item.rate) }}</span><span :class="['bar', rateClass(item.rate)]" :style="{ height: `${Math.max(2, Math.min(180, Math.abs(item.rate) * 18))}px` }" /></div></div></el-card>
    <el-card shadow="never" class="card"><template #header>对应国内主力期货</template><el-table :data="futureRows" v-loading="loading"><el-table-column prop="contractCode" label="代码" /><el-table-column prop="contractName" label="名称" /><el-table-column prop="lastPx" label="最新价" /><el-table-column label="涨跌幅"><template #default="{ row }"><span :class="rateClass(row.pxChangeRate)">{{ percent(row.pxChangeRate) }}</span></template></el-table-column></el-table></el-card>
  </div>
</template>
<script setup name="OptionFutureLinkage">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getMarketOptionIntraday } from '@/api/future/option'
import { listFutureQuote } from '@/api/future/market'
const thscode = ref('I2709-C-780.DCE'); const keyword = ref('铁矿'); const loading = ref(false); const optionRate = ref(null); const futureRows = ref([])
const bars = computed(() => [{ name: '期权当日涨跌', rate: optionRate.value }, ...futureRows.value.slice(0, 1).map(row => ({ name: row.contractName || row.contractCode, rate: Number(row.pxChangeRate) }))])
function percent(value) { return value === null || value === undefined || Number.isNaN(Number(value)) ? '--' : `${Number(value) > 0 ? '+' : ''}${Number(value).toFixed(2)}%` }
function rateClass(value) { return Number(value) > 0 ? 'rise' : Number(value) < 0 ? 'fall' : '' }
function load() { loading.value = true; Promise.all([getMarketOptionIntraday(thscode.value), listFutureQuote({ scope: 'domestic', keyword: keyword.value || undefined, pageNum: 1, pageSize: 10 })]).then(([option, future]) => { const points = option.data.item || []; optionRate.value = points.length > 1 && Number(points[0].price) ? (Number(points.at(-1).price) / Number(points[0].price) - 1) * 100 : null; futureRows.value = future.data.rows || [] }).catch(() => ElMessage.error('联动数据查询失败，请确认期权完整代码与期货名称')).finally(() => { loading.value = false }) }
load()
</script>
<style scoped>
.linkage-page{padding:20px}.form,.card{margin-top:16px}.bars{height:250px;display:flex;align-items:end;gap:80px;padding:15px 40px}.bar-item{height:220px;min-width:100px;display:flex;flex-direction:column;justify-content:end;align-items:center;gap:8px}.bar{width:36px;background:#909399}.bar.rise{background:#f56c6c}.bar.fall{background:#67c23a}.rise{color:#f56c6c}.fall{color:#67c23a}
</style>
