<template>
  <div class="app-container">
    <el-form :inline="true" :model="query"><el-form-item label="函数名称"><el-input v-model="query.funcName" clearable @keyup.enter="load" /></el-form-item><el-form-item><el-button type="primary" @click="load">查询</el-button></el-form-item></el-form>
    <el-button type="primary" icon="Plus" @click="openAdd" v-hasPermi="['function:manage:add']">新增函数</el-button>
    <el-table v-loading="loading" :data="rows" class="mt12"><el-table-column prop="funcName" label="函数名称" width="180" show-overflow-tooltip /><el-table-column prop="language" label="语言" width="110" /><el-table-column prop="funcType" label="类型" width="110" /><el-table-column prop="funcDesc" label="功能描述" show-overflow-tooltip /><el-table-column label="操作" width="210"><template #default="{ row }"><el-button link type="success" @click="openVisual(row)">可视化</el-button><el-button link type="primary" @click="openEdit(row)" v-hasPermi="['function:manage:edit']">编辑</el-button><el-button link type="danger" @click="remove(row)" v-hasPermi="['function:manage:remove']">删除</el-button></template></el-table-column></el-table>
    <pagination v-show="total" :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="load" />
    <el-dialog v-model="dialog" :title="form.id ? '编辑函数' : '新增函数'" width="760px"><el-form ref="formRef" :model="form" :rules="rules" label-width="90px"><el-form-item label="所属项目" prop="projectId"><el-select v-model="form.projectId" style="width:100%"><el-option v-for="item in projects" :key="item.id" :label="item.projectName" :value="item.id" /></el-select></el-form-item><el-form-item label="函数名称" prop="funcName"><el-input v-model="form.funcName" /></el-form-item><el-form-item label="编程语言" prop="language"><el-input v-model="form.language" placeholder="Python / JavaScript" /></el-form-item><el-form-item label="类型"><el-select v-model="form.funcType"><el-option label="Function" value="Function" /><el-option label="Method" value="Method" /></el-select></el-form-item><el-form-item label="文件路径"><el-input v-model="form.filePath" /></el-form-item><el-form-item label="功能描述"><el-input v-model="form.funcDesc" /></el-form-item><el-form-item label="逻辑说明"><el-input v-model="form.logic" type="textarea" :rows="8" /></el-form-item><el-form-item label="函数源码" prop="funcCode"><el-input v-model="form.funcCode" type="textarea" :rows="16" spellcheck="false" /></el-form-item></el-form><template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template></el-dialog>
    <el-dialog v-model="visualDialog" :title="`${visualRow.funcName || ''} - 可视化展示`" width="1100px" destroy-on-close><div class="visual-toolbar"><span>数据源</span><el-select v-model="visualSource" size="small" style="width:180px" @change="loadVisual"><el-option label="项目静态测试数据" value="static" /><el-option label="真实行情接口（待接入）" value="real" disabled /></el-select><span class="source-tip">EURUSD · 15分钟</span></div><el-row :gutter="16"><el-col :span="17"><div ref="chartRef" class="chart-box" /></el-col><el-col :span="7"><el-descriptions :column="1" border size="small"><el-descriptions-item label="函数">{{ visualRow.funcName }}</el-descriptions-item><el-descriptions-item label="功能">{{ visualRow.funcDesc }}</el-descriptions-item><el-descriptions-item label="逻辑"><div class="logic-text">{{ visualRow.logic }}</div></el-descriptions-item></el-descriptions></el-col></el-row></el-dialog>
  </div>
</template>

<script setup name="FunctionManage">
import * as echarts from 'echarts'
import { addFunction, delFunction, getFunctionVisualData, listFunction, updateFunction } from '@/api/project-research/function'
import { listProject } from '@/api/project-research/project'

const { proxy } = getCurrentInstance()
const loading = ref(false), dialog = ref(false), total = ref(0), rows = ref([]), projects = ref([]), formRef = ref()
const visualDialog = ref(false), visualSource = ref('static'), visualRow = ref({}), chartRef = ref()
let chart
const query = reactive({ pageNum: 1, pageSize: 10, funcName: undefined })
const form = reactive({})
const rules = { projectId: [{ required: true, message: '请选择项目', trigger: 'change' }], funcName: [{ required: true, message: '函数名称不能为空', trigger: 'blur' }], language: [{ required: true, message: '编程语言不能为空', trigger: 'blur' }], funcCode: [{ required: true, message: '函数源码不能为空', trigger: 'blur' }] }
function load() { loading.value = true; listFunction(query).then(res => { rows.value = res.rows; total.value = res.total }).finally(() => loading.value = false) }
function chooseProjects() { return listProject({ pageNum: 1, pageSize: 1000 }).then(res => { projects.value = res.rows }) }
function openAdd() { Object.assign(form, { id: undefined, projectId: undefined, funcName: '', language: 'Python', funcType: 'Function', filePath: '', funcDesc: '', logic: '', funcCode: '' }); chooseProjects().then(() => { dialog.value = true }) }
function openEdit(row) { Object.assign(form, row); chooseProjects().then(() => { dialog.value = true }) }
function save() { formRef.value.validate(valid => { if (!valid) return; (form.id ? updateFunction : addFunction)(form).then(() => { proxy.$modal.msgSuccess('保存成功'); dialog.value = false; load() }) }) }
function remove(row) { proxy.$modal.confirm(`确认删除函数“${row.funcName}”吗？`).then(() => delFunction(row.id)).then(() => { proxy.$modal.msgSuccess('删除成功'); load() }) }
function openVisual(row) { visualRow.value = row; visualSource.value = 'static'; visualDialog.value = true; nextTick(loadVisual) }
function loadVisual() { if (!visualDialog.value) return; getFunctionVisualData(visualRow.value.id, visualSource.value).then(res => { const data = res.data.rows; chart ||= echarts.init(chartRef.value); chart.setOption({ animation: false, tooltip: { trigger: 'axis' }, dataZoom: [{ type: 'inside' }, { type: 'slider' }], xAxis: { type: 'category', data: data.map(item => item.time), axisLabel: { show: false } }, yAxis: { scale: true }, series: [{ name: 'EURUSD', type: 'candlestick', data: data.map(item => [item.open, item.close, item.low, item.high]) }] }, true) }) }
load()
</script>

<style scoped>.mt12 { margin-top: 12px; }.visual-toolbar { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }.source-tip { color: var(--el-text-color-secondary); }.chart-box { width: 100%; height: 600px; }.logic-text { white-space: pre-line; line-height: 1.7; }</style>
