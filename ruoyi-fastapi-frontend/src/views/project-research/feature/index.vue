<template>
  <div class="app-container">
    <el-form :inline="true" :model="query" @submit.prevent>
      <el-form-item label="功能名称"><el-input v-model="query.title" clearable @keyup.enter="load" /></el-form-item>
      <el-form-item label="需求"><el-select v-model="query.requirementId" clearable filterable style="width:260px"><el-option v-for="item in requirements" :key="item.id" :label="`${item.requirementCode} ${item.title}`" :value="item.id" /></el-select></el-form-item>
      <el-form-item><el-button type="primary" @click="load">查询</el-button></el-form-item>
    </el-form>
    <el-button type="primary" icon="Plus" @click="openAdd" v-hasPermi="['research:feature:add']">新增功能</el-button>
    <el-table v-loading="loading" :data="rows" class="mt12" border :span-method="spanMethod">
      <el-table-column label="原文" min-width="230">
        <template #default="{ row }">
          <div>{{ requirementMap[row.requirementId]?.sourceDocumentTitle || '未关联原文' }}</div>
          <small>原文 ID：{{ requirementMap[row.requirementId]?.sourceDocumentId || '-' }}</small>
        </template>
      </el-table-column>
      <el-table-column label="笔记" min-width="220">
        <template #default="{ row }">
          <div>{{ requirementMap[row.requirementId]?.sourceNoteTitle || '未关联笔记' }}</div>
          <small>笔记 ID：{{ requirementMap[row.requirementId]?.sourceNoteId || '-' }}</small>
        </template>
      </el-table-column>
      <el-table-column label="需求" min-width="240">
        <template #default="{ row }">
          <div>{{ requirementMap[row.requirementId]?.requirementCode || '-' }}</div>
          <small>{{ requirementMap[row.requirementId]?.title || '需求已删除' }}</small>
        </template>
      </el-table-column>
      <el-table-column prop="featureCode" label="功能编号" width="140" />
      <el-table-column prop="title" label="功能" min-width="220" show-overflow-tooltip />
      <el-table-column prop="logic" label="功能逻辑" min-width="260" show-overflow-tooltip />
      <el-table-column label="开源函数" min-width="220"><template #default="{ row }"><div>{{ row.openSourceFunction || '-' }}</div><small>{{ row.openSourceProject || '未关联开源项目' }}</small></template></el-table-column>
      <el-table-column label="本地化函数" min-width="180"><template #default="{ row }"><template v-if="row.functionIds?.length"><el-tag v-for="id in row.functionIds" :key="id" class="function-tag" size="small">{{ functionMap[id]?.funcName || `函数${id}` }}</el-tag></template><span v-else>-</span></template></el-table-column>
      <el-table-column prop="reuseScope" label="可复用范围" min-width="220" show-overflow-tooltip />
      <el-table-column prop="localizationPlan" label="本地化改造" min-width="220" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="110" />
      <el-table-column label="操作" width="150"><template #default="{ row }"><el-button link type="primary" @click="openEdit(row)" v-hasPermi="['research:feature:edit']">编辑</el-button><el-button link type="danger" @click="remove(row)" v-hasPermi="['research:feature:remove']">删除</el-button></template></el-table-column>
    </el-table>
    <pagination v-show="total" :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="load" />
    <el-dialog v-model="dialog" :title="form.id ? '编辑功能' : '新增功能'" width="900px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
        <el-row :gutter="12"><el-col :span="12"><el-form-item label="关联需求" prop="requirementId"><el-select v-model="form.requirementId" filterable style="width:100%"><el-option v-for="item in requirements" :key="item.id" :label="`${item.requirementCode} ${item.title}`" :value="item.id" /></el-select></el-form-item></el-col><el-col :span="12"><el-form-item label="功能编号" prop="featureCode"><el-input v-model="form.featureCode" placeholder="FUNC-001" /></el-form-item></el-col></el-row>
        <el-form-item label="功能名称" prop="title"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="功能逻辑"><el-input v-model="form.logic" type="textarea" :rows="4" /></el-form-item>
        <el-row :gutter="12"><el-col :span="12"><el-form-item label="输入数据"><el-input v-model="form.inputData" type="textarea" :rows="3" /></el-form-item></el-col><el-col :span="12"><el-form-item label="输出结果"><el-input v-model="form.outputData" type="textarea" :rows="3" /></el-form-item></el-col></el-row>
        <el-form-item label="关联已有函数"><el-select v-model="form.functionIds" multiple filterable collapse-tags style="width:100%" placeholder="可选：一个功能可关联多个函数"><el-option v-for="item in functions" :key="item.id" :label="item.funcName" :value="item.id" /></el-select></el-form-item>
        <el-divider content-position="left">开源实现</el-divider>
        <el-row :gutter="12"><el-col :span="12"><el-form-item label="项目"><el-input v-model="form.openSourceProject" /></el-form-item></el-col><el-col :span="12"><el-form-item label="函数/模块"><el-input v-model="form.openSourceFunction" /></el-form-item></el-col></el-row>
        <el-form-item label="实现逻辑"><el-input v-model="form.openSourceLogic" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="可复用范围"><el-input v-model="form.reuseScope" type="textarea" :rows="3" /></el-form-item>
        <el-divider content-position="left">本地化实现</el-divider>
        <el-form-item label="差异"><el-input v-model="form.localizationGap" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="改造方案"><el-input v-model="form.localizationPlan" type="textarea" :rows="3" /></el-form-item>
        <el-row :gutter="12"><el-col :span="12"><el-form-item label="代码位置"><el-input v-model="form.codeLocation" /></el-form-item></el-col><el-col :span="12"><el-form-item label="状态"><el-select v-model="form.status" style="width:100%"><el-option label="待实现" value="draft" /><el-option label="开发中" value="developing" /><el-option label="已完成" value="done" /><el-option label="暂停" value="paused" /></el-select></el-form-item></el-col></el-row>
        <el-form-item label="功能验收"><el-input v-model="form.acceptance" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup name="ResearchFeatureManage">
import { addResearchFeature, delResearchFeature, listResearchFeatures, updateResearchFeature, listResearchRequirements } from '@/api/project-research/requirement'
import { listFunction } from '@/api/project-research/function'

const { proxy } = getCurrentInstance()
const loading = ref(false), dialog = ref(false), total = ref(0), rows = ref([]), requirements = ref([]), functions = ref([]), formRef = ref()
const requirementMap = computed(() => Object.fromEntries(requirements.value.map(item => [item.id, item])))
const functionMap = computed(() => Object.fromEntries(functions.value.map(item => [item.id, item])))
const query = reactive({ pageNum: 1, pageSize: 10, title: undefined, requirementId: undefined })
const form = reactive({})
const rules = { requirementId: [{ required: true, message: '请选择关联需求', trigger: 'change' }], featureCode: [{ required: true, message: '功能编号不能为空', trigger: 'blur' }], title: [{ required: true, message: '功能名称不能为空', trigger: 'blur' }] }
function loadRequirements() { listResearchRequirements({ pageNum: 1, pageSize: 1000 }).then(res => { requirements.value = res.rows }) }
function loadFunctions() { listFunction({ pageNum: 1, pageSize: 1000 }).then(res => { functions.value = res.rows }) }
function load() { loading.value = true; listResearchFeatures(query).then(res => { rows.value = res.rows; total.value = res.total }).finally(() => { loading.value = false }) }
function spanMethod({ rowIndex, columnIndex }) {
  if (columnIndex > 2) return [1, 1]
  if (rowIndex && rows.value[rowIndex - 1].requirementId === rows.value[rowIndex].requirementId) return [0, 0]
  return [rows.value.findIndex((row, index) => index >= rowIndex && row.requirementId !== rows.value[rowIndex].requirementId) - rowIndex || rows.value.length - rowIndex, 1]
}
function openAdd() { Object.assign(form, { id: undefined, requirementId: undefined, functionIds: [], featureCode: '', title: '', logic: '', inputData: '', outputData: '', openSourceProject: '', openSourceFunction: '', openSourceLogic: '', reuseScope: '', localizationGap: '', localizationPlan: '', codeLocation: '', acceptance: '', status: 'draft' }); loadRequirements(); loadFunctions(); dialog.value = true }
function openEdit(row) { Object.assign(form, row, { functionIds: row.functionIds || [] }); loadRequirements(); loadFunctions(); dialog.value = true }
function save() { formRef.value.validate(valid => { if (!valid) return; (form.id ? updateResearchFeature : addResearchFeature)(form).then(() => { proxy.$modal.msgSuccess('保存成功'); dialog.value = false; load() }) }) }
function remove(row) { proxy.$modal.confirm(`确认删除功能“${row.title}”吗？`).then(() => delResearchFeature(row.id)).then(() => { proxy.$modal.msgSuccess('删除成功'); load() }) }
loadRequirements(); loadFunctions(); load()
</script>

<style scoped>.mt12 { margin-top: 12px; }.function-tag { margin: 2px; }</style>
