<template>
  <div class="app-container">
    <el-form :inline="true" :model="query"><el-form-item label="组合名称"><el-input v-model="query.combinationName" clearable @keyup.enter="load" /></el-form-item><el-form-item><el-button type="primary" @click="load">查询</el-button></el-form-item></el-form>
    <el-button type="primary" icon="Plus" @click="openAdd" v-hasPermi="['function:combination:add']">新增组合</el-button>
    <el-table v-loading="loading" :data="rows" class="mt12"><el-table-column prop="combinationName" label="组合名称" width="200" /><el-table-column prop="researchDirection" label="研究方向" width="140" /><el-table-column prop="description" label="功能说明" show-overflow-tooltip /><el-table-column label="函数数量" width="100"><template #default="{ row }">{{ row.functionIds?.length || 0 }}</template></el-table-column><el-table-column label="操作" width="220"><template #default="{ row }"><el-button link type="success" @click="openChart(row)">综合图表</el-button><el-button link type="primary" @click="openEdit(row)" v-hasPermi="['function:combination:edit']">编辑</el-button><el-button link type="danger" @click="remove(row)" v-hasPermi="['function:combination:remove']">删除</el-button></template></el-table-column></el-table>
    <pagination v-show="total" :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="load" />
    <el-dialog v-model="dialog" :title="form.id ? '编辑组合' : '新增组合'" width="600px"><el-form ref="formRef" :model="form" :rules="rules" label-width="90px"><el-form-item label="所属项目" prop="projectId"><el-select v-model="form.projectId" style="width:100%"><el-option v-for="item in projects" :key="item.id" :label="item.projectName" :value="item.id" /></el-select></el-form-item><el-form-item label="组合名称" prop="combinationName"><el-input v-model="form.combinationName" /></el-form-item><el-form-item label="研究方向"><el-input v-model="form.researchDirection" placeholder="SMC、缠论、EA量化" /></el-form-item><el-form-item label="功能说明"><el-input v-model="form.description" type="textarea" /></el-form-item><el-form-item label="选择函数"><el-select v-model="form.functionIds" multiple style="width:100%"><el-option v-for="item in functions" :key="item.id" :label="item.funcName" :value="item.id" /></el-select></el-form-item></el-form><template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template></el-dialog>
    <el-dialog v-model="chartDialog" :title="`${chartRow.combinationName || ''} - 综合图表`" width="1100px" destroy-on-close @opened="loadChart" @closed="closeChart"><div class="chart-toolbar"><el-checkbox v-for="item in chartLayers" :key="item.id" v-model="item.visible" @change="renderChart">{{ item.name }}</el-checkbox></div><div ref="chartRef" class="chart-box" /></el-dialog>
  </div>
</template>

<script setup name="FunctionCombination">
import { addCombination, delCombination, listCombination, updateCombination } from '@/api/project-research/combination'
import { listProject } from '@/api/project-research/project'
import * as echarts from 'echarts'
import { getFunctionVisualData, listFunction } from '@/api/project-research/function'

const { proxy } = getCurrentInstance()
const loading = ref(false), dialog = ref(false), total = ref(0), rows = ref([]), projects = ref([]), functions = ref([]), formRef = ref()
const query = reactive({ pageNum: 1, pageSize: 10, combinationName: undefined })
const form = reactive({})
const chartDialog = ref(false), chartRow = ref({}), chartLayers = ref([]), chartRef = ref()
let chart
const rules = { projectId: [{ required: true, message: '请选择项目', trigger: 'change' }], combinationName: [{ required: true, message: '组合名称不能为空', trigger: 'blur' }] }
function load() { loading.value = true; listCombination(query).then(res => { rows.value = res.rows; total.value = res.total }).finally(() => loading.value = false) }
function loadOptions() { return Promise.all([listProject({ pageNum: 1, pageSize: 1000 }), listFunction({ pageNum: 1, pageSize: 1000 })]).then(([p, f]) => { projects.value = p.rows; functions.value = f.rows }) }
function openAdd() { Object.assign(form, { id: undefined, projectId: undefined, combinationName: '', researchDirection: '', description: '', functionIds: [] }); loadOptions().then(() => { dialog.value = true }) }
function openEdit(row) { Object.assign(form, row, { functionIds: row.functionIds || [] }); loadOptions().then(() => { dialog.value = true }) }
function save() { formRef.value.validate(valid => { if (!valid) return; (form.id ? updateCombination : addCombination)(form).then(() => { proxy.$modal.msgSuccess('保存成功'); dialog.value = false; load() }) }) }
function remove(row) { proxy.$modal.confirm(`确认删除组合“${row.combinationName}”吗？`).then(() => delCombination(row.id)).then(() => { proxy.$modal.msgSuccess('删除成功'); load() }) }
function openChart(row) { chartRow.value = row; loadOptions().then(() => { chartLayers.value = (row.functionIds || []).map(id => { const fn = functions.value.find(item => item.id === id); return { id, name: fn?.funcName || `函数${id}`, visible: true, data: null } }); chartDialog.value = true }) }
function closeChart() { chart?.dispose(); chart = null }
function renderChart() { const base = chartLayers.value.find(item => item.data)?.data; if (!chart || !base) return; const points = [], areas = []; chartLayers.value.filter(item => item.visible && item.data?.indicator).forEach(layer => layer.data.indicator.forEach((item, index) => { if (layer.name === 'swing_highs_lows' && item.highLow && base.rows[index]) points.push({ value: item.highLow > 0 ? '高点' : '低点', coord: [index, item.highLow > 0 ? base.rows[index].high : base.rows[index].low], itemStyle: { color: item.highLow > 0 ? '#dc2626' : '#16a34a' } }); if (['fvg', 'ob'].includes(layer.name) && base.rows[index]) areas.push([{ xAxis: index, yAxis: base.rows[index].low }, { xAxis: Math.min(item.mitigatedIndex || base.rows.length - 1, base.rows.length - 1), yAxis: base.rows[index].high }]) })); chart.setOption({ animation: false, tooltip: { trigger: 'axis' }, dataZoom: [{ type: 'inside' }, { type: 'slider' }], xAxis: { type: 'category', data: base.rows.map(item => item.time), axisLabel: { show: false } }, yAxis: { scale: true }, series: [{ type: 'candlestick', name: 'BTC', data: base.rows.map(item => [item.open, item.close, item.low, item.high]), markPoint: points.length ? { data: points, symbolSize: 14 } : undefined, markArea: areas.length ? { itemStyle: { color: 'rgba(59,130,246,.12)' }, data: areas } : undefined }] }, true); chart.resize() }
function loadChart() { chart = echarts.init(chartRef.value); Promise.all(chartLayers.value.map(layer => { const fn = functions.value.find(item => item.id === layer.id); return getFunctionVisualData(layer.id, fn?.funcName).then(res => { layer.data = res.data }).catch(() => null) })).then(renderChart) }
load()
</script>

<style scoped>.mt12 { margin-top: 12px; }.chart-toolbar { display: flex; gap: 16px; margin-bottom: 10px; }.chart-box { height: 620px; width: 100%; }</style>
