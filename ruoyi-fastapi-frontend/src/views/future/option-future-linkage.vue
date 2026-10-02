<template>
  <div class="linkage-page">
    <el-alert title="Call 上涨：看涨权利金升温，偏多；Put 上涨：看跌权利金升温，偏空或对冲需求增强。未含持仓量时，不能直接认定为主力单向看空。" type="info" :closable="false" show-icon />
    <el-form inline class="form"><el-form-item label="标的期货合约"><el-select v-model="underlyingCode" filterable style="width:320px" @change="load"><el-option v-for="item in underlyings" :key="item.underlyingCode" :label="`${item.underlyingCode} · ${item.name || ''}`" :value="item.underlyingCode" /></el-select></el-form-item><el-button :loading="refreshing" @click="refreshDaily">下载日线数据</el-button></el-form>
    <el-card shadow="never" class="future-card"><el-descriptions :column="4" border><el-descriptions-item label="主力代码">{{ future.contractCode || '--' }}</el-descriptions-item><el-descriptions-item label="主力名称">{{ future.contractName || '--' }}</el-descriptions-item><el-descriptions-item label="最新价">{{ future.lastPx ?? '--' }}</el-descriptions-item><el-descriptions-item label="涨跌幅"><span :class="color(future.pxChangeRate)">{{ percent(future.pxChangeRate) }}</span></el-descriptions-item></el-descriptions></el-card>
    <el-table :data="rows" v-loading="loading" :span-method="spanMethod" border>
      <el-table-column prop="strikePrice" label="行权价" width="90" /><el-table-column prop="optionType" label="方向" width="95"><template #default="{ row }"><el-tag :type="row.optionType === 'call' ? 'danger' : 'success'">{{ row.optionType === 'call' ? 'Call 看涨' : 'Put 看跌' }}</el-tag></template></el-table-column><el-table-column prop="thscode" label="期权合约" min-width="185" /><el-table-column prop="name" label="名称" min-width="150" /><el-table-column label="日涨跌" width="95"><template #default="{ row }"><span :class="color(row.dayChangeRate)">{{ percent(row.dayChangeRate) }}</span></template></el-table-column><el-table-column label="说明" min-width="210"><template #default="{ row }">{{ signal(row) }}</template></el-table-column>
    </el-table>
  </div>
</template>
<script setup name="OptionFutureLinkage">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getOptionChain, listOptionUnderlyings, refreshOptionChainDaily } from '@/api/future/option'
const underlyingCode = ref('I2709'); const underlyings = ref([]); const loading = ref(false); const refreshing = ref(false); const chainRows = ref([]); const future = ref({})
const rows = computed(() => chainRows.value)
function percent(value) { return value === null || value === undefined ? '--' : `${Number(value) > 0 ? '+' : ''}${Number(value).toFixed(2)}%` }
function color(value) { return Number(value) > 0 ? 'rise' : Number(value) < 0 ? 'fall' : '' }
function signal(row) { if (row.dayChangeRate === null || row.dayChangeRate === undefined) return '暂无日线数据'; return row.optionType === 'call' ? '看涨权利金升温，偏多' : '看跌权利金升温，偏空或对冲增强' }
function load() { loading.value = true; getOptionChain(underlyingCode.value).then(response => { chainRows.value = response.data.rows || []; future.value = response.data.future || {} }).catch(() => ElMessage.error('期权链查询失败')).finally(() => { loading.value = false }) }
function refreshDaily() { refreshing.value = true; refreshOptionChainDaily(underlyingCode.value).then(() => { ElMessage.success('期权链日线已更新'); load() }).catch(() => ElMessage.error('日线更新失败')).finally(() => { refreshing.value = false }) }
listOptionUnderlyings().then(response => { underlyings.value = response.data || [] }); load()
</script>
<style scoped>.linkage-page{padding:20px}.form,.future-card{margin:16px 0}.rise{color:#f56c6c}.fall{color:#67c23a}</style>
