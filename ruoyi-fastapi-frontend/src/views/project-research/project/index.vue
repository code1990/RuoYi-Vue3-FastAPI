<template>
  <div class="app-container">
    <el-form :inline="true" :model="query"><el-form-item label="项目名称"><el-input v-model="query.projectName" clearable @keyup.enter="load" /></el-form-item><el-form-item><el-button type="primary" @click="load">查询</el-button><el-button @click="resetQuery">重置</el-button></el-form-item></el-form>
    <el-button type="primary" icon="Plus" @click="openAdd" v-hasPermi="['project:manage:add']">新增项目</el-button>
    <el-table v-loading="loading" :data="rows" class="mt12"><el-table-column prop="projectName" label="项目名称" /><el-table-column prop="researchDirection" label="研究方向" width="140" /><el-table-column prop="language" label="语言" width="120" /><el-table-column prop="repoUrl" label="仓库地址" show-overflow-tooltip /><el-table-column prop="description" label="描述" show-overflow-tooltip /><el-table-column label="操作" width="150"><template #default="{ row }"><el-button link type="primary" @click="openEdit(row)" v-hasPermi="['project:manage:edit']">编辑</el-button><el-button link type="danger" @click="remove(row)" v-hasPermi="['project:manage:remove']">删除</el-button></template></el-table-column></el-table>
    <pagination v-show="total" :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="load" />
    <el-dialog v-model="dialog" :title="form.id ? '编辑项目' : '新增项目'" width="520px"><el-form ref="formRef" :model="form" :rules="rules" label-width="90px"><el-form-item label="项目名称" prop="projectName"><el-input v-model="form.projectName" /></el-form-item><el-form-item label="研究方向"><el-select v-model="form.researchDirection" filterable allow-create default-first-option style="width:100%" placeholder="如：SMC、缠论、EA量化"><el-option label="SMC" value="SMC" /><el-option label="缠论" value="缠论" /><el-option label="EA量化" value="EA量化" /></el-select></el-form-item><el-form-item label="编程语言"><el-input v-model="form.language" placeholder="Python / JavaScript" /></el-form-item><el-form-item label="仓库地址"><el-input v-model="form.repoUrl" /></el-form-item><el-form-item label="版本"><el-input v-model="form.version" /></el-form-item><el-form-item label="项目描述"><el-input v-model="form.description" type="textarea" /></el-form-item></el-form><template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template></el-dialog>
  </div>
</template>

<script setup name="ProjectManage">
import { addProject, delProject, listProject, updateProject } from '@/api/project-research/project'

const { proxy } = getCurrentInstance()
const loading = ref(false), dialog = ref(false), total = ref(0), rows = ref([]), formRef = ref()
const query = reactive({ pageNum: 1, pageSize: 10, projectName: undefined })
const form = reactive({})
const rules = { projectName: [{ required: true, message: '项目名称不能为空', trigger: 'blur' }] }
function load() { loading.value = true; listProject(query).then(res => { rows.value = res.rows; total.value = res.total }).finally(() => loading.value = false) }
function resetQuery() { query.projectName = undefined; query.pageNum = 1; load() }
function openAdd() { Object.assign(form, { id: undefined, projectName: '', researchDirection: '', language: '', repoUrl: '', version: '', description: '' }); dialog.value = true }
function openEdit(row) { Object.assign(form, row); dialog.value = true }
function save() { formRef.value.validate(valid => { if (!valid) return; (form.id ? updateProject : addProject)(form).then(() => { proxy.$modal.msgSuccess('保存成功'); dialog.value = false; load() }) }) }
function remove(row) { proxy.$modal.confirm(`确认删除项目“${row.projectName}”吗？`).then(() => delProject(row.id)).then(() => { proxy.$modal.msgSuccess('删除成功'); load() }) }
load()
</script>

<style scoped>.mt12 { margin-top: 12px; }</style>
