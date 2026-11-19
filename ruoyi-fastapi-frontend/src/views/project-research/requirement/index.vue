<template>
  <div class="app-container">
    <el-form :inline="true" :model="query" @submit.prevent>
      <el-form-item label="标题"><el-input v-model="query.title" clearable placeholder="需求、原文或笔记标题" @keyup.enter="load" /></el-form-item>
      <el-form-item><el-button type="primary" @click="load">查询</el-button></el-form-item>
    </el-form>
    <el-button type="primary" icon="Plus" @click="openAdd" v-hasPermi="['research:requirement:add']">新增需求</el-button>
    <el-table v-loading="loading" :data="rows" class="mt12">
      <el-table-column prop="requirementCode" label="编号" width="140" />
      <el-table-column prop="title" label="需求标题" min-width="220" show-overflow-tooltip />
      <el-table-column label="原文" min-width="280" show-overflow-tooltip>
        <template #default="{ row }">
          <div>{{ row.sourceDocumentTitle || '未填写原文标题' }}</div>
          <small>原文 ID：{{ row.sourceDocumentId || '-' }}</small>
        </template>
      </el-table-column>
      <el-table-column label="笔记" min-width="260" show-overflow-tooltip>
        <template #default="{ row }">
          <div>{{ row.sourceNoteTitle || '未填写笔记标题' }}</div>
          <small>笔记 ID：{{ row.sourceNoteId || '-' }}</small>
        </template>
      </el-table-column>
      <el-table-column prop="coreConcepts" label="核心概念" min-width="220" show-overflow-tooltip />
      <el-table-column prop="coreViewpoints" label="核心观点" min-width="260" show-overflow-tooltip />
      <el-table-column prop="priority" label="优先级" width="90" />
      <el-table-column prop="status" label="状态" width="110" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)" v-hasPermi="['research:requirement:edit']">编辑</el-button>
          <el-button link type="danger" @click="remove(row)" v-hasPermi="['research:requirement:remove']">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total" :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="load" />
    <el-dialog v-model="dialog" :title="form.id ? '编辑需求' : '新增需求'" width="720px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="需求编号" prop="requirementCode"><el-input v-model="form.requirementCode" placeholder="REQ-SMC-001" /></el-form-item>
        <el-form-item label="需求名称" prop="title"><el-input v-model="form.title" /></el-form-item>
        <el-row :gutter="12"><el-col :span="12"><el-form-item label="原文ID"><el-input-number v-model="form.sourceDocumentId" :min="0" /></el-form-item></el-col><el-col :span="12"><el-form-item label="笔记ID"><el-input-number v-model="form.sourceNoteId" :min="0" /></el-form-item></el-col></el-row>
        <el-form-item label="原文标题"><el-input v-model="form.sourceDocumentTitle" placeholder="MinDoc 原文章节标题" /></el-form-item>
        <el-form-item label="笔记标题"><el-input v-model="form.sourceNoteTitle" placeholder="MinDoc AI 笔记标题" /></el-form-item>
        <el-form-item label="核心概念"><el-input v-model="form.coreConcepts" type="textarea" :rows="3" placeholder="课程中需要统一理解的术语、对象或关系" /></el-form-item>
        <el-form-item label="核心观点"><el-input v-model="form.coreViewpoints" type="textarea" :rows="3" placeholder="课程提出的判断原则、限制或验证方法" /></el-form-item>
        <el-form-item label="问题"><el-input v-model="form.problem" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="目标"><el-input v-model="form.goal" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="范围"><el-input v-model="form.scope" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="验收标准"><el-input v-model="form.acceptance" type="textarea" :rows="3" /></el-form-item>
        <el-row :gutter="12"><el-col :span="12"><el-form-item label="优先级"><el-select v-model="form.priority"><el-option label="P0" value="P0" /><el-option label="P1" value="P1" /><el-option label="P2" value="P2" /></el-select></el-form-item></el-col><el-col :span="12"><el-form-item label="状态"><el-select v-model="form.status"><el-option label="草稿" value="draft" /><el-option label="待评审" value="review" /><el-option label="已确认" value="confirmed" /><el-option label="废弃" value="dropped" /></el-select></el-form-item></el-col></el-row>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup name="ResearchRequirementManage">
import { addResearchRequirement, delResearchRequirement, listResearchRequirements, updateResearchRequirement } from '@/api/project-research/requirement'

const { proxy } = getCurrentInstance()
const loading = ref(false), dialog = ref(false), total = ref(0), rows = ref([]), formRef = ref()
const query = reactive({ pageNum: 1, pageSize: 10, title: undefined })
const form = reactive({})
const rules = { requirementCode: [{ required: true, message: '需求编号不能为空', trigger: 'blur' }], title: [{ required: true, message: '需求名称不能为空', trigger: 'blur' }] }
function load() { loading.value = true; listResearchRequirements(query).then(res => { rows.value = res.rows; total.value = res.total }).finally(() => { loading.value = false }) }
function openAdd() { Object.assign(form, { id: undefined, requirementCode: '', title: '', sourceDocumentId: undefined, sourceDocumentTitle: '', sourceNoteId: undefined, sourceNoteTitle: '', coreConcepts: '', coreViewpoints: '', problem: '', goal: '', scope: '', acceptance: '', priority: 'P1', status: 'draft' }); dialog.value = true }
function openEdit(row) { Object.assign(form, row); dialog.value = true }
function save() { formRef.value.validate(valid => { if (!valid) return; (form.id ? updateResearchRequirement : addResearchRequirement)(form).then(() => { proxy.$modal.msgSuccess('保存成功'); dialog.value = false; load() }) }) }
function remove(row) { proxy.$modal.confirm(`确认删除需求“${row.title}”吗？`).then(() => delResearchRequirement(row.id)).then(() => { proxy.$modal.msgSuccess('删除成功'); load() }) }
load()
</script>

<style scoped>.mt12 { margin-top: 12px; }</style>
