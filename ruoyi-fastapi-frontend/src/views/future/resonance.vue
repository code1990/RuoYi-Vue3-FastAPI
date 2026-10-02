<template>
  <div class="future-resonance-page">
    <el-card v-for="chart in charts" :key="chart.scope" shadow="never" class="quote-chart">
      <template #header>{{ chart.title }}</template>
      <div class="chart-columns">
        <div v-for="row in chart.rows" :key="row.contractCode" class="chart-column" :title="`${row.contractName} ${percent(row.pxChangeRate)}`">
          <div class="chart-bar-area"><span :class="['chart-bar', color(row.pxChangeRate)]" :style="{ height: height(chart, row) }" /><span :class="['chart-value', color(row.pxChangeRate)]" :style="{ bottom: `calc(${height(chart, row)} + 2px)` }">{{ percent(row.pxChangeRate) }}</span></div>
          <span class="chart-name">{{ row.contractName }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup name="FutureResonance">
import { computed, ref } from 'vue'
import { listFutureQuote } from '@/api/future/market'

const data = ref({ domestic: [], overseas: [] })
const charts = computed(() => ['domestic', 'overseas'].map(scope => {
  const rows = [...data.value[scope]].sort((a, b) => Number(b.pxChangeRate || 0) - Number(a.pxChangeRate || 0))
  return { scope, rows, max: Math.max(1, ...rows.map(row => Math.abs(Number(row.pxChangeRate || 0)))), title: scope === 'domestic' ? '国内主力合约涨幅排名' : '国际主力合约涨幅排名' }
}))

function percent(value) { return value === null || value === undefined ? '--' : `${Number(value).toFixed(2)}%` }
function color(value) { return Number(value) > 0 ? 'rise' : Number(value) < 0 ? 'fall' : '' }
function height(chart, row) { return `${Math.abs(Number(row.pxChangeRate || 0)) / chart.max * 190}px` }
function getList(scope) { return listFutureQuote({ scope, pageNum: 1, pageSize: 100 }).then(response => { data.value[scope] = response.data.rows }) }

Promise.all(['domestic', 'overseas'].map(getList))
</script>

<style scoped>
.future-resonance-page { padding: 20px; }.quote-chart { margin-bottom: 16px; }.quote-chart :deep(.el-card__body) { overflow-y: hidden; }
.chart-columns { display: flex; gap: 5px; height: 365px; overflow-x: auto; overflow-y: hidden; padding: 0 4px; }.chart-column { display: grid; grid-template-rows: 210px 155px; flex: 0 0 36px; min-width: 36px; text-align: center; }.chart-bar-area { position: relative; border-bottom: 1px solid #dcdfe6; }.chart-bar { position: absolute; bottom: 0; left: 10px; width: 16px; min-height: 1px; }.chart-value { position: absolute; left: 50%; font-size: 11px; transform: translateX(-50%); white-space: nowrap; }.chart-name { display: flex; align-items: center; justify-content: center; font-size: 12px; line-height: 16px; writing-mode: vertical-rl; }.rise { color: #f56c6c; }.fall { color: #67c23a; }.chart-bar.rise { background: #f56c6c; }.chart-bar.fall { background: #67c23a; }
</style>
