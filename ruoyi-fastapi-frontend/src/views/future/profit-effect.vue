<template>
  <div class="profit-effect-page">
    <el-alert title="开盘方向一致的事后收益效应：全部国内主力合约按当日开盘价开仓 1 手，按最新价计算；股票比较固定为只能做多，且按普通 A 股单日涨跌停 ±10% 封顶。未单独校准的合约按 10% 参考保证金率、开平 2 元参考成本试算。" type="warning" :closable="false" show-icon />
    <el-table v-loading="loading" :data="rows" stripe class="table">
      <el-table-column type="index" label="排名" width="64" />
      <el-table-column prop="contractName" label="合约名称" min-width="135" />
      <el-table-column prop="marketDate" label="行情日" width="105" />
      <el-table-column prop="direction" label="假设方向" width="90"><template #default="{ row }"><span :class="row.direction === '做多' ? 'rise' : 'fall'">{{ row.direction }}</span></template></el-table-column>
      <el-table-column label="开盘 / 最新" min-width="140"><template #default="{ row }">{{ price(row.openPx) }} / {{ price(row.lastPx) }}</template></el-table-column>
      <el-table-column label="涨跌幅" width="100"><template #default="{ row }"><span :class="changeRate(row) > 0 ? 'rise' : changeRate(row) < 0 ? 'fall' : ''">{{ signedPercent(changeRate(row)) }}</span></template></el-table-column>
      <el-table-column label="盈利价差" width="115"><template #default="{ row }">{{ price(row.priceSpread) }}</template></el-table-column>
      <el-table-column label="1手净赚" width="115"><template #default="{ row }"><span class="rise">+{{ money(row.netProfit) }}</span></template></el-table-column>
      <el-table-column label="保证金" width="110"><template #default="{ row }">{{ money(row.margin) }}</template></el-table-column>
      <el-table-column label="开平成本" width="100"><template #default="{ row }">{{ money(row.fee) }}</template></el-table-column>
      <el-table-column label="需准备资金" width="120"><template #default="{ row }">{{ money(row.capital) }}</template></el-table-column>
      <el-table-column label="期货收益率" width="115"><template #default="{ row }"><span class="rise">+{{ percent(row.profitRate) }}</span></template></el-table-column>
      <el-table-column label="同成本股票结果(±10%)" min-width="165"><template #default="{ row }"><span :class="row.stockSameMoveProfit >= 0 ? 'rise' : 'fall'">{{ signedMoney(row.stockSameMoveProfit) }}</span></template></el-table-column>
      <el-table-column label="股票等额需涨" min-width="165"><template #default="{ row }">{{ stockRequired(row.stockRequiredChangeRate) }}</template></el-table-column>
    </el-table>
  </div>
</template>

<script setup name="FutureProfitEffect">
import { ref } from 'vue'
import { listFutureProfitEffect } from '@/api/future/profit-effect'

const loading = ref(false)
const rows = ref([])
const money = value => `${Number(value || 0).toFixed(2)} 元`
const signedMoney = value => `${Number(value || 0) >= 0 ? '+' : ''}${money(value)}`
const price = value => Number(value || 0).toFixed(2)
const percent = value => `${Number(value || 0).toFixed(2)}%`
const signedPercent = value => `${Number(value || 0) >= 0 ? '+' : ''}${percent(value)}`
const changeRate = row => (Number(row.lastPx) - Number(row.openPx)) / Number(row.openPx) * 100
const stockRequired = value => `${percent(value)}${Number(value || 0) > 10 ? '（超单日涨停）' : ''}`
function getList() { loading.value = true; listFutureProfitEffect().then(response => { rows.value = response.data || [] }).finally(() => { loading.value = false }) }
getList()
</script>

<style scoped>
.profit-effect-page { padding: 20px; }.table { margin-top: 16px; }.rise { color: #f56c6c; font-weight: 600; }.fall { color: #67c23a; font-weight: 600; }
</style>
