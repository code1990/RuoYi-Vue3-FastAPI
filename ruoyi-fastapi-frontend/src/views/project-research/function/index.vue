<template>
  <div class="app-container">
    <el-form :inline="true" :model="query"><el-form-item label="函数名称"><el-input v-model="query.funcName" clearable @keyup.enter="load" /></el-form-item><el-form-item><el-button type="primary" @click="load">查询</el-button></el-form-item></el-form>
    <el-button type="primary" icon="Plus" @click="openAdd" v-hasPermi="['function:manage:add']">新增函数</el-button>
    <el-table v-loading="loading" :data="rows" class="mt12"><el-table-column prop="funcName" label="函数名称" width="180" show-overflow-tooltip /><el-table-column prop="language" label="语言" width="110" /><el-table-column prop="funcType" label="类型" width="110" /><el-table-column prop="funcDesc" label="功能描述" show-overflow-tooltip /><el-table-column prop="visualSummary" label="可视化简述" width="220" show-overflow-tooltip /><el-table-column label="操作" width="210"><template #default="{ row }"><el-button v-if="canVisualize(row)" link type="success" @click="openVisual(row)">可视化</el-button><span v-else class="visual-placeholder">-</span><el-button link type="primary" @click="openEdit(row)" v-hasPermi="['function:manage:edit']">编辑</el-button><el-button link type="danger" @click="remove(row)" v-hasPermi="['function:manage:remove']">删除</el-button></template></el-table-column></el-table>
    <pagination v-show="total" :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="load" />
    <el-dialog v-model="dialog" :title="form.id ? '编辑函数' : '新增函数'" width="760px"><el-form ref="formRef" :model="form" :rules="rules" label-width="90px"><el-form-item label="所属项目" prop="projectId"><el-select v-model="form.projectId" style="width:100%"><el-option v-for="item in projects" :key="item.id" :label="item.projectName" :value="item.id" /></el-select></el-form-item><el-form-item label="函数名称" prop="funcName"><el-input v-model="form.funcName" /></el-form-item><el-form-item label="编程语言" prop="language"><el-input v-model="form.language" placeholder="Python / JavaScript" /></el-form-item><el-form-item label="类型"><el-select v-model="form.funcType"><el-option label="Function" value="Function" /><el-option label="Method" value="Method" /></el-select></el-form-item><el-form-item label="可视化"><el-switch v-model="form.visualEnabled" active-text="启用" inactive-text="停用" /></el-form-item><el-form-item label="可视化简述"><el-input v-model="form.visualSummary" maxlength="200" show-word-limit placeholder="例如：区间块，表示未回补的失衡区域" /></el-form-item><el-form-item label="文件路径"><el-input v-model="form.filePath" /></el-form-item><el-form-item label="功能描述"><el-input v-model="form.funcDesc" /></el-form-item><el-form-item label="逻辑说明"><el-input v-model="form.logic" type="textarea" :rows="8" /></el-form-item><el-form-item label="函数源码" prop="funcCode"><el-input v-model="form.funcCode" type="textarea" :rows="16" spellcheck="false" /></el-form-item></el-form><template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template></el-dialog>
    <el-dialog v-model="visualDialog" :title="`${visualRow.funcName || ''} - 可视化展示`" width="1100px" destroy-on-close @opened="loadVisual" @closed="closeVisual"><div class="visual-toolbar"><span>数据源</span><el-select v-model="visualSource" size="small" style="width:180px" @change="loadVisual"><el-option label="项目静态测试数据" value="static" /><el-option label="真实行情接口（待接入）" value="real" disabled /></el-select><span class="source-tip">EURUSD · 15分钟</span></div><el-row :gutter="16"><el-col :span="17"><div class="visual-summary">{{ getVisualSummary(visualRow) }}</div><div ref="chartRef" class="chart-box" /></el-col><el-col :span="7"><el-descriptions :column="1" border size="small"><el-descriptions-item label="函数">{{ visualRow.funcName }}</el-descriptions-item><el-descriptions-item label="功能">{{ visualRow.funcDesc }}</el-descriptions-item><el-descriptions-item label="逻辑"><div class="logic-text">{{ visualRow.logic }}</div></el-descriptions-item></el-descriptions></el-col></el-row></el-dialog>
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
const legacyVisualFunctions = new Set(['swing_highs_lows', 'fvg', 'bos_choch', 'ob', 'liquidity', 'previous_high_low', 'sessions', 'retracements'])
const defaultVisualSummaries = { swing_highs_lows: '高点/低点标记', fvg: '失衡区间块', bos_choch: '结构突破与变化标记', ob: '订单块区间', liquidity: '流动性水平线', previous_high_low: '前高/前低水平线', sessions: '交易时段区块', retracements: '当前与最大回撤曲线' }
const query = reactive({ pageNum: 1, pageSize: 10, funcName: undefined })
const form = reactive({})
const rules = { projectId: [{ required: true, message: '请选择项目', trigger: 'change' }], funcName: [{ required: true, message: '函数名称不能为空', trigger: 'blur' }], language: [{ required: true, message: '编程语言不能为空', trigger: 'blur' }], funcCode: [{ required: true, message: '函数源码不能为空', trigger: 'blur' }] }
function load() { loading.value = true; listFunction(query).then(res => { rows.value = res.rows.map(row => ({ ...row, funcName: row.funcName ?? row.func_name, visualEnabled: row.visualEnabled ?? row.visual_enabled, visualSummary: row.visualSummary ?? row.visual_summary })); total.value = res.total }).finally(() => loading.value = false) }
function chooseProjects() { return listProject({ pageNum: 1, pageSize: 1000 }).then(res => { projects.value = res.rows }) }
function openAdd() { Object.assign(form, { id: undefined, projectId: undefined, funcName: '', language: 'Python', funcType: 'Function', visualEnabled: false, visualSummary: '', filePath: '', funcDesc: '', logic: '', funcCode: '' }); chooseProjects().then(() => { dialog.value = true }) }
function openEdit(row) { Object.assign(form, row); chooseProjects().then(() => { dialog.value = true }) }
function save() { formRef.value.validate(valid => { if (!valid) return; (form.id ? updateFunction : addFunction)(form).then(() => { proxy.$modal.msgSuccess('保存成功'); dialog.value = false; load() }) }) }
function remove(row) { proxy.$modal.confirm(`确认删除函数“${row.funcName}”吗？`).then(() => delFunction(row.id)).then(() => { proxy.$modal.msgSuccess('删除成功'); load() }) }
function canVisualize(row) { return row.visualEnabled == null ? legacyVisualFunctions.has(row.funcName) : row.visualEnabled === true || row.visualEnabled === 1 || row.visualEnabled === '1' }
function getVisualSummary(row) { return row?.visualSummary || row?.visual_summary || defaultVisualSummaries[row?.funcName] || '暂无可视化简述' }
function openVisual(row) { visualRow.value = row; visualSource.value = 'static'; visualDialog.value = true }
function closeVisual() { chart?.dispose(); chart = null }
function buildOverlay(name, indicator, data) {
  const last = data.length - 1
  const points = [], areas = [], lines = []
  indicator.forEach((item, index) => {
    // shortcut: static swing levels use another price scale, so anchor markers to the current candle until results are recalculated.
    if (name === 'swing_highs_lows' && item.highLow && data[index]) points.push({ value: item.highLow > 0 ? '高点' : '低点', coord: [index, item.highLow > 0 ? data[index].high : data[index].low], symbol: 'triangle', symbolRotate: item.highLow > 0 ? 0 : 180, itemStyle: { color: item.highLow > 0 ? '#dc2626' : '#16a34a' } })
    // shortcut: static zone prices use another price scale, so anchor the zone to current candles until results are recalculated.
    if (['fvg', 'ob'].includes(name) && item.top != null && item.bottom != null && data[index]) areas.push([{ xAxis: index, yAxis: data[index].low }, { xAxis: Math.min(item.mitigatedIndex ?? last, last), yAxis: data[index].high }])
    if (name === 'bos_choch' && item.level != null && (item.bos || item.choch) && data[index]) points.push({ value: item.bos ? 'BOS' : 'CHOCH', coord: [index, (item.bos || item.choch) > 0 ? data[index].high : data[index].low], itemStyle: { color: item.bos ? '#2563eb' : '#f59e0b' } })
    if (name === 'liquidity' && item.level != null && data[index]) lines.push([{ xAxis: index, yAxis: item.liquidity > 0 ? data[index].high : data[index].low }, { xAxis: Math.min(item.end ?? last, last), yAxis: item.liquidity > 0 ? data[index].high : data[index].low }])
    if (name === 'previous_high_low') {
      if (item.previousHigh && data[index]) lines.push([{ xAxis: index, yAxis: data[index].high }, { xAxis: last, yAxis: data[index].high }])
      if (item.previousLow && data[index]) lines.push([{ xAxis: index, yAxis: data[index].low }, { xAxis: last, yAxis: data[index].low }])
    }
    // shortcut: static session prices use another price scale, so anchor the zone to the current candle.
    if (name === 'sessions' && item.active && data[index]) areas.push([{ xAxis: index, yAxis: data[index].low }, { xAxis: Math.min(index + 1, last), yAxis: data[index].high }])
  })
  return { markPoint: points.length ? { symbolSize: 16, label: { show: true, position: 'top' }, data: points } : undefined, markArea: areas.length ? { itemStyle: { color: 'rgba(59, 130, 246, 0.12)' }, data: areas } : undefined, markLine: lines.length ? { symbol: 'none', data: lines } : undefined }
}
function loadVisual() {
  if (!visualDialog.value) return
  getFunctionVisualData(visualRow.value.id, visualRow.value.funcName, visualSource.value).then(res => {
    visualRow.value = { ...visualRow.value, funcName: res.data.funcName ?? res.data.func_name ?? visualRow.value.funcName, visualEnabled: res.data.visualEnabled ?? res.data.visual_enabled ?? visualRow.value.visualEnabled, visualSummary: res.data.visualSummary ?? res.data.visual_summary ?? visualRow.value.visualSummary }
    const data = res.data.rows
    const indicator = res.data.indicator
    if (!chartRef.value) return
    chart ||= echarts.init(chartRef.value)
    const times = data.map(item => item.time)
    const candles = data.map(item => [item.open, item.close, item.low, item.high])
    const chartTitle = { text: getVisualSummary(visualRow.value), left: 12, top: 8, textStyle: { fontSize: 13, color: '#64748b' } }
    if (visualRow.value.funcName !== 'retracements' || !indicator) {
      const overlay = indicator ? buildOverlay(visualRow.value.funcName, indicator, data) : {}
      const indicatorValues = ['swing_highs_lows', 'fvg', 'ob', 'sessions', 'previous_high_low', 'liquidity', 'bos_choch'].includes(visualRow.value.funcName) ? [] : indicator?.flatMap(item => ['level', 'top', 'bottom', 'previousHigh', 'previousLow', 'high', 'low'].map(key => item[key])).filter(value => Number.isFinite(value) && value !== 0) || []
      const priceValues = candles.flatMap(item => item.slice(2))
      chart.setOption({ animation: false, title: chartTitle, tooltip: { trigger: 'axis' }, dataZoom: [{ type: 'inside' }, { type: 'slider' }], xAxis: { type: 'category', data: times, axisLabel: { show: false } }, yAxis: { min: Math.min(...priceValues, ...indicatorValues), max: Math.max(...priceValues, ...indicatorValues), scale: true }, series: [{ name: 'EURUSD', type: 'candlestick', data: candles, ...overlay }] }, true)
      chart.resize()
      return
    }
    const directionMarks = indicator.map((item, index) => index > 0 && item.direction && item.direction !== indicator[index - 1].direction ? { value: item.direction === 1 ? '多头' : '空头', coord: [index, data[index].close], itemStyle: { color: item.direction === 1 ? '#16a34a' : '#dc2626' } } : null).filter(Boolean)
    chart.setOption({
      animation: false,
      title: chartTitle,
      tooltip: { trigger: 'axis' },
      legend: { top: 0, data: ['EURUSD', '当前回撤%', '最大回撤%'] },
      grid: [{ left: 48, right: 20, top: 32, height: '57%' }, { left: 48, right: 20, top: '68%', height: '22%' }],
      dataZoom: [{ type: 'inside', xAxisIndex: [0, 1] }, { type: 'slider', xAxisIndex: [0, 1] }],
      xAxis: [{ type: 'category', data: times, axisLabel: { show: false } }, { type: 'category', gridIndex: 1, data: times, axisLabel: { show: false } }],
      yAxis: [{ scale: true }, { gridIndex: 1, name: '%', scale: true }],
      series: [
        { name: 'EURUSD', type: 'candlestick', data: candles, markPoint: { symbol: 'triangle', symbolSize: 16, label: { show: true, position: 'top' }, data: directionMarks } },
        { name: '当前回撤%', type: 'line', xAxisIndex: 1, yAxisIndex: 1, showSymbol: false, data: indicator.map(item => item.currentRetracement) },
        { name: '最大回撤%', type: 'line', xAxisIndex: 1, yAxisIndex: 1, showSymbol: false, data: indicator.map(item => item.deepestRetracement) },
      ],
    }, true)
    chart.resize()
  })
}
load()
</script>

<style scoped>.mt12 { margin-top: 12px; }.visual-placeholder { display: inline-block; width: 48px; color: var(--el-text-color-secondary); text-align: center; }.visual-toolbar { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }.source-tip { color: var(--el-text-color-secondary); }.visual-summary { margin-bottom: 8px; color: var(--el-text-color-secondary); font-size: 13px; }.chart-box { width: 100%; height: 600px; }.logic-text { white-space: pre-line; line-height: 1.7; }</style>
