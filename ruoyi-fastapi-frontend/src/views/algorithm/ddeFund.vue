<template>
  <div class="algorithm-page">
    <el-card>
      <el-form inline><el-form-item label="状态"><el-select v-model="status" clearable placeholder="全部" style="width: 120px"><el-option label="观察中" value="observing" /><el-option label="已剪枝" value="rejected" /></el-select></el-form-item><el-button type="primary" :loading="loading" @click="loadExperiments">筛选</el-button></el-form>
      <el-table :data="experiments" v-loading="loading" size="small" row-key="experimentKey" :default-sort="{ prop: 'validationRate', order: 'descending' }">
        <el-table-column prop="experimentKey" label="实验" min-width="150" />
        <el-table-column label="数据区间" min-width="170"><template #default="{ row }">{{ row.dataStartDate }} ~ {{ row.dataEndDate }}</template></el-table-column>
        <el-table-column label="训练命中率" prop="trainRate" sortable width="120"><template #default="{ row }">{{ percent(row.trainMetrics.root.hit_rate) }}</template></el-table-column>
        <el-table-column label="验证命中率" prop="validationRate" sortable width="120"><template #default="{ row }">{{ percent(row.validationMetrics.root.hit_rate) }}</template></el-table-column>
        <el-table-column label="验证样本" prop="validationSamples" sortable width="100"><template #default="{ row }">{{ row.validationMetrics.root.sample_count }}</template></el-table-column>
        <el-table-column label="状态" width="100"><template #default="{ row }"><el-tag :type="row.status === 'observing' ? 'success' : 'info'">{{ row.status === 'observing' ? '观察中' : '已剪枝' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="100"><template #default="{ row }"><el-button link type="primary" @click="selectExperiment(row.experimentKey)">查看树</el-button></template></el-table-column>
      </el-table>
    </el-card>
    <el-alert :title="summary" :type="experiment?.status === 'observing' ? 'success' : 'warning'" :closable="false" show-icon class="summary" />
    <el-row :gutter="16" class="metrics">
      <el-col :span="6"><el-statistic title="训练样本" :value="experiment?.trainMetrics.root.sample_count || 0" /></el-col>
      <el-col :span="6"><el-statistic title="训练命中率" :value="rate(experiment?.trainMetrics.root.hit_rate)" suffix="%" /></el-col>
      <el-col :span="6"><el-statistic title="验证样本" :value="experiment?.validationMetrics.root.sample_count || 0" /></el-col>
      <el-col :span="6"><el-statistic title="验证命中率" :value="rate(experiment?.validationMetrics.root.hit_rate)" suffix="%" /></el-col>
    </el-row>
    <el-card header="DDE 二分剪枝树" class="chart-row"><div ref="chartRef" v-loading="loading" class="chart" /></el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { getDdeAlgorithm, listDdeAlgorithms } from '@/api/stock/algorithm'

const chartRef = ref()
const loading = ref(false)
const experiment = ref(null)
const experiments = ref([])
const status = ref('')
let chart

const summary = computed(() => {
  if (!experiment.value) return '尚无 DDE 二分实验结果，请先运行 stock_cron/algorithm/run_dde_binary_experiment.py。'
  return `${experiment.value.dataStartDate} 至 ${experiment.value.dataEndDate}｜${experiment.value.targetRule}｜${experiment.value.conclusion}`
})

function rate(value) {
  return value == null ? 0 : Math.round(value * 10000) / 100
}

function percent(value) {
  return `${rate(value)}%`
}

function renderTree(data) {
  const root = {
    name: `${data.tree.name}\n训练 ${data.trainMetrics.root.sample_count}｜验证 ${data.validationMetrics.root.sample_count}`,
    children: data.tree.children.map(node => ({
      name: `${node.name}\n训练 ${rate(node.train.hit_rate)}% (${node.train.sample_count})\n验证 ${rate(node.validation.hit_rate)}% (${node.validation.sample_count})`,
      itemStyle: { color: node.pruned ? '#909399' : '#67c23a' }
    }))
  }
  chart.setOption({
    tooltip: { trigger: 'item' },
    series: [{ type: 'tree', data: [root], top: '8%', bottom: '8%', left: '8%', right: '8%', symbolSize: 12, label: { position: 'top', verticalAlign: 'middle', align: 'center', fontSize: 13, lineHeight: 20 }, leaves: { label: { position: 'bottom', verticalAlign: 'middle', align: 'center' } }, expandAndCollapse: false, initialTreeDepth: -1 }]
  }, true)
}

async function selectExperiment(experimentKey) {
  loading.value = true
  try {
    const response = await getDdeAlgorithm(experimentKey)
    experiment.value = response.data
    if (response.data) renderTree(response.data)
  } finally {
    loading.value = false
  }
}

async function loadExperiments() {
  loading.value = true
  try {
    const response = await listDdeAlgorithms({ status: status.value || undefined })
    experiments.value = response.data.map(row => ({
      ...row,
      trainRate: rate(row.trainMetrics.root.hit_rate),
      validationRate: rate(row.validationMetrics.root.hit_rate),
      validationSamples: row.validationMetrics.root.sample_count
    }))
    if (experiments.value.length) await selectExperiment(experiments.value[0].experimentKey)
    else experiment.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  chart = echarts.init(chartRef.value)
  loadExperiments()
  window.addEventListener('resize', chart.resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', chart.resize)
  chart.dispose()
})
</script>

<style scoped>
.algorithm-page { padding: 20px; }
.metrics { margin-top: 16px; }
.summary { margin-top: 16px; }
.chart-row { margin-top: 16px; }
.chart { height: 460px; }
</style>
