<template>
  <div class="algorithm-page">
    <el-alert :title="summary" :type="experiment?.status === 'observing' ? 'success' : 'warning'" :closable="false" show-icon />
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
import { getLatestDdeAlgorithm } from '@/api/stock/algorithm'

const chartRef = ref()
const loading = ref(false)
const experiment = ref(null)
let chart

const summary = computed(() => {
  if (!experiment.value) return '尚无 DDE 二分实验结果，请先运行 stock_cron/algorithm/run_dde_binary_experiment.py。'
  return `${experiment.value.dataStartDate} 至 ${experiment.value.dataEndDate}｜${experiment.value.targetRule}｜${experiment.value.conclusion}`
})

function rate(value) {
  return value == null ? 0 : Math.round(value * 10000) / 100
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

async function loadExperiment() {
  loading.value = true
  try {
    const response = await getLatestDdeAlgorithm()
    experiment.value = response.data
    if (response.data) renderTree(response.data)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  chart = echarts.init(chartRef.value)
  loadExperiment()
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
.chart-row { margin-top: 16px; }
.chart { height: 460px; }
</style>
