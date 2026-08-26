<template>
  <div class="algorithm-page">
    <el-card>
      <el-form inline @submit.prevent>
        <el-form-item label="??"><el-input v-model="experimentKey" placeholder="? dde_rule_v1" clearable /></el-form-item>
        <el-form-item label="??"><el-select v-model="status" clearable style="width: 120px"><el-option label="??" value="accepted" /><el-option label="???" value="pruned" /></el-select></el-form-item>
        <el-button type="primary" :loading="loading" @click="load">????</el-button>
      </el-form>
      <el-alert :title="`? ${rows.length} ??????????????????????`" type="info" :closable="false" show-icon />
      <el-table :data="rows" v-loading="loading" stripe border size="small" class="rule-table">
        <el-table-column type="index" label="#" width="55" />
        <el-table-column prop="experimentKey" label="??" width="145" />
        <el-table-column prop="ruleKey" label="????" min-width="330" show-overflow-tooltip />
        <el-table-column label="?????" width="115" sortable><template #default="{ row }">{{ pct(row.trainMetrics.hit_rate) }}</template></el-table-column>
        <el-table-column label="?????" width="115" sortable><template #default="{ row }">{{ pct(row.validationMetrics.hit_rate) }}</template></el-table-column>
        <el-table-column label="????" width="95" sortable><template #default="{ row }">{{ row.validationMetrics.sample_count }}</template></el-table-column>
        <el-table-column label="????" width="100"><template #default="{ row }">{{ fixed(row.validationMetrics.average_max_return_pct) }}%</template></el-table-column>
        <el-table-column label="??" width="90"><template #default="{ row }"><el-tag :type="row.status === 'accepted' ? 'success' : 'info'">{{ row.status === 'accepted' ? '??' : '??' }}</el-tag></template></el-table-column>
      </el-table>
    </el-card>
    <el-row :gutter="16" class="metrics">
      <el-col :span="6"><el-statistic title="????" :value="rows.length" /></el-col>
      <el-col :span="6"><el-statistic title="????" :value="accepted" /></el-col>
      <el-col :span="6"><el-statistic title="???????" :value="maxRate" suffix="%" /></el-col>
      <el-col :span="6"><el-statistic title="??????" :value="maxReturn" suffix="%" /></el-col>
    </el-row>
    <el-card header="????? Top 20" class="chart-card"><div ref="chartRef" class="chart" /></el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { listDdeRuleCandidates } from '@/api/stock/algorithm'
const loading = ref(false); const rows = ref([]); const experimentKey = ref('dde_rule_v1'); const status = ref('accepted'); const chartRef = ref(); let chart
const accepted = computed(() => rows.value.filter(r => r.status === 'accepted').length)
const maxRate = computed(() => rows.value.length ? Math.max(...rows.value.map(r => Number(r.validationMetrics?.hit_rate || 0) * 100)) : 0)
const maxReturn = computed(() => rows.value.length ? Math.max(...rows.value.map(r => Number(r.validationMetrics?.average_max_return_pct || 0))) : 0)
function pct(v) { return `${(Number(v || 0) * 100).toFixed(2)}%` }; function fixed(v) { return Number(v || 0).toFixed(2) }
function renderChart() { const top = rows.value.slice(0, 20).slice().reverse(); chart?.setOption({ grid: { left: 180, right: 30, top: 20, bottom: 30 }, xAxis: { type: 'value', axisLabel: { formatter: '{value}%' } }, yAxis: { type: 'category', data: top.map(r => r.ruleKey) }, series: [{ type: 'bar', data: top.map(r => Number(r.validationMetrics?.hit_rate || 0) * 100), itemStyle: { color: '#409eff' }, label: { show: true, position: 'right', formatter: '{c}%' } }] }, true) }
async function load() { loading.value = true; try { const res = await listDdeRuleCandidates({ experimentKey: experimentKey.value || undefined, status: status.value || undefined }); rows.value = res.data || []; renderChart() } finally { loading.value = false } }
onMounted(() => { chart = echarts.init(chartRef.value); load(); window.addEventListener('resize', chart.resize) }); onBeforeUnmount(() => { window.removeEventListener('resize', chart.resize); chart?.dispose() })
</script>
<style scoped>.algorithm-page{padding:20px}.rule-table{margin-top:16px}.metrics{margin-top:16px}.chart-card{margin-top:16px}.chart{height:460px}</style>
