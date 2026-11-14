<template>
  <div class="app-container">
    <el-form :inline="true" :model="query"><el-form-item label="组合名称"><el-input v-model="query.combinationName" clearable @keyup.enter="load" /></el-form-item><el-form-item><el-button type="primary" @click="load">查询</el-button></el-form-item></el-form>
    <el-button type="primary" icon="Plus" @click="openAdd" v-hasPermi="['function:combination:add']">新增组合</el-button>
    <el-table v-loading="loading" :data="rows" class="mt12"><el-table-column prop="combinationName" label="组合名称" width="200" /><el-table-column prop="researchDirection" label="研究方向" width="140" /><el-table-column prop="description" label="功能说明" show-overflow-tooltip /><el-table-column label="函数数量" width="100"><template #default="{ row }">{{ row.functionIds?.length || 0 }}</template></el-table-column><el-table-column label="操作" width="150"><template #default="{ row }"><el-button link type="primary" @click="openEdit(row)" v-hasPermi="['function:combination:edit']">编辑</el-button><el-button link type="danger" @click="remove(row)" v-hasPermi="['function:combination:remove']">删除</el-button></template></el-table-column></el-table>
    <pagination v-show="total" :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="load" />
    <el-dialog v-model="dialog" :title="form.id ? '编辑组合' : '新增组合'" width="600px"><el-form ref="formRef" :model="form" :rules="rules" label-width="90px"><el-form-item label="所属项目" prop="projectId"><el-select v-model="form.projectId" style="width:100%"><el-option v-for="item in projects" :key="item.id" :label="item.projectName" :value="item.id" /></el-select></el-form-item><el-form-item label="组合名称" prop="combinationName"><el-input v-model="form.combinationName" /></el-form-item><el-form-item label="研究方向"><el-input v-model="form.researchDirection" placeholder="SMC、缠论、EA量化" /></el-form-item><el-form-item label="功能说明"><el-input v-model="form.description" type="textarea" /></el-form-item><el-form-item label="选择函数"><el-select v-model="form.functionIds" multiple style="width:100%"><el-option v-for="item in functions" :key="item.id" :label="item.funcName" :value="item.id" /></el-select></el-form-item></el-form><template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template></el-dialog>
  </div>
</template>

<script setup name="FunctionCombination">
import { addCombination, delCombination, listCombination, updateCombination } from '@/api/project-research/combination'
import { listProject } from '@/api/project-research/project'
import { listFunction } from '@/api/project-research/function'

const { proxy } = getCurrentInstance()
const loading = ref(false), dialog = ref(false), total = ref(0), rows = ref([]), projects = ref([]), functions = ref([]), formRef = ref()
const query = reactive({ pageNum: 1, pageSize: 10, combinationName: undefined })
const form = reactive({})
const rules = { projectId: [{ required: true, message: '请选择项目', trigger: 'change' }], combinationName: [{ required: true, message: '组合名称不能为空', trigger: 'blur' }] }
function load() { loading.value = true; listCombination(query).then(res => { rows.value = res.rows; total.value = res.total }).finally(() => loading.value = false) }
function loadOptions() { return Promise.all([listProject({ pageNum: 1, pageSize: 1000 }), listFunction({ pageNum: 1, pageSize: 1000 })]).then(([p, f]) => { projects.value = p.rows; functions.value = f.rows }) }
function openAdd() { Object.assign(form, { id: undefined, projectId: undefined, combinationName: '', researchDirection: '', description: '', functionIds: [] }); loadOptions().then(() => { dialog.value = true }) }
function openEdit(row) { Object.assign(form, row, { functionIds: row.functionIds || [] }); loadOptions().then(() => { dialog.value = true }) }
function save() { formRef.value.validate(valid => { if (!valid) return; (form.id ? updateCombination : addCombination)(form).then(() => { proxy.$modal.msgSuccess('保存成功'); dialog.value = false; load() }) }) }
function remove(row) { proxy.$modal.confirm(`确认删除组合“${row.combinationName}”吗？`).then(() => delCombination(row.id)).then(() => { proxy.$modal.msgSuccess('删除成功'); load() }) }
load()
</script>

<style scoped>.mt12 { margin-top: 12px; }</style>
