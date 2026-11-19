<template>
  <div class="app-container" v-loading="loading">
    <div class="page-tools">
      <el-button @click="backToList">返回需求列表</el-button>
      <template v-if="requirement">
        <el-button v-if="!editing" type="primary" @click="editing = true" v-hasPermi="['research:requirement:edit']">编辑</el-button>
        <template v-else><el-button @click="cancelEdit">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
      </template>
    </div>
    <el-empty v-if="!loading && !requirement" description="未找到需求"><el-button @click="backToList">返回需求列表</el-button></el-empty>
    <template v-else-if="requirement">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px" class="requirement-form">
        <el-divider content-position="left">需求</el-divider>
        <el-form-item label="需求编号" prop="requirementCode"><el-input v-model="form.requirementCode" :disabled="!editing" /></el-form-item>
        <el-form-item label="需求问题" prop="title"><el-input v-model="form.title" :disabled="!editing" /></el-form-item>
        <el-row :gutter="12"><el-col :span="12"><el-form-item label="优先级"><el-select v-model="form.priority" :disabled="!editing"><el-option label="P0" value="P0" /><el-option label="P1" value="P1" /><el-option label="P2" value="P2" /></el-select></el-form-item></el-col><el-col :span="12"><el-form-item label="状态"><el-select v-model="form.status" :disabled="!editing"><el-option label="草稿" value="draft" /><el-option label="待评审" value="review" /><el-option label="已确认" value="confirmed" /><el-option label="废弃" value="dropped" /></el-select></el-form-item></el-col></el-row>
        <el-divider content-position="left">原文与笔记</el-divider>
        <el-row :gutter="12"><el-col :span="12"><el-form-item label="原文 ID"><el-input-number v-model="form.sourceDocumentId" :min="0" :disabled="!editing" /></el-form-item></el-col><el-col :span="12"><el-form-item label="笔记 ID"><el-input-number v-model="form.sourceNoteId" :min="0" :disabled="!editing" /></el-form-item></el-col></el-row>
        <el-form-item label="原文标题"><el-input v-model="form.sourceDocumentTitle" :disabled="!editing" /></el-form-item>
        <el-form-item label="笔记标题"><el-input v-model="form.sourceNoteTitle" :disabled="!editing" /></el-form-item>
        <text-field label="原文概述" v-model="form.sourceSummary" :editing="editing" />
        <text-field label="笔记摘要" v-model="form.noteSummary" :editing="editing" />
        <text-field label="核心概念" v-model="form.coreConcepts" :editing="editing" />
        <text-field label="核心观点" v-model="form.coreViewpoints" :editing="editing" />
        <el-divider content-position="left">需求定义</el-divider>
        <text-field label="要解决的问题" v-model="form.problem" :editing="editing" />
        <text-field label="需求目标" v-model="form.goal" :editing="editing" />
        <text-field label="使用方式与边界" v-model="form.scope" :editing="editing" />
        <text-field label="验收标准" v-model="form.acceptance" :editing="editing" />
      </el-form>
      <template v-if="!isNew"><el-divider content-position="left">功能方案</el-divider><el-empty v-if="!features.length" description="尚未拆分功能" /><el-table v-else :data="features" border><el-table-column prop="featureCode" label="编号" width="180" /><el-table-column prop="title" label="功能" min-width="220" /><el-table-column prop="logic" label="解决方式" min-width="320" /><el-table-column prop="status" label="状态" width="100" /></el-table></template>
    </template>
  </div>
</template>

<script setup name="ResearchRequirementDetail">
import { computed, h, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { addResearchRequirement, getResearchRequirement, listResearchFeatures, updateResearchRequirement } from '@/api/project-research/requirement'

const { proxy } = getCurrentInstance()
const route = useRoute(), router = useRouter(), loading = ref(false), editing = ref(false), formRef = ref(), requirement = ref(null), features = ref([]), form = reactive({})
const rules = { requirementCode: [{ required: true, message: '需求编号不能为空', trigger: 'blur' }], title: [{ required: true, message: '需求问题不能为空', trigger: 'blur' }] }
const isNew = computed(() => route.params.requirementId === 'new')
const emptyForm = () => ({ id: undefined, requirementCode: '', title: '', sourceDocumentId: undefined, sourceDocumentTitle: '', sourceSummary: '', sourceNoteId: undefined, sourceNoteTitle: '', noteSummary: '', coreConcepts: '', coreViewpoints: '', problem: '', goal: '', scope: '', acceptance: '', priority: 'P1', status: 'draft' })
const normalize = data => ({ ...data, requirementCode: data.requirementCode ?? data.requirement_code, sourceDocumentId: data.sourceDocumentId ?? data.source_document_id, sourceDocumentTitle: data.sourceDocumentTitle ?? data.source_document_title, sourceSummary: data.sourceSummary ?? data.source_summary, sourceNoteId: data.sourceNoteId ?? data.source_note_id, sourceNoteTitle: data.sourceNoteTitle ?? data.source_note_title, noteSummary: data.noteSummary ?? data.note_summary, coreConcepts: data.coreConcepts ?? data.core_concepts, coreViewpoints: data.coreViewpoints ?? data.core_viewpoints })
const sentenceLines = value => String(value || '待补充').replace(/\r?\n/g, '').match(/[^。！？!?]+[。！？!?]?/g)?.map(item => item.trim()).filter(Boolean) || ['待补充']
const TextField = { props: { label: String, modelValue: String, editing: Boolean }, emits: ['update:modelValue'], setup(props, { emit }) { return () => h('el-form-item', { label: props.label }, props.editing ? h('el-input', { modelValue: props.modelValue, 'onUpdate:modelValue': value => emit('update:modelValue', value), type: 'textarea', rows: 3 }) : h('div', { class: 'sentence-lines' }, sentenceLines(props.modelValue).map(line => h('p', line)))) } }
function backToList() { router.push('/project-research/requirement') }
function cancelEdit() { if (isNew.value) return backToList(); Object.assign(form, requirement.value); editing.value = false }
function save() { formRef.value.validate(valid => { if (!valid) return; (isNew.value ? addResearchRequirement : updateResearchRequirement)(form).then(() => { proxy.$modal.msgSuccess('保存成功'); if (isNew.value) backToList(); else { requirement.value = { ...form }; editing.value = false } }) }) }
async function load() {
  if (isNew.value) { requirement.value = emptyForm(); Object.assign(form, requirement.value); editing.value = true; return }
  loading.value = true
  try { const id = Number(route.params.requirementId); const [detail, featureResponse] = await Promise.all([getResearchRequirement(id), listResearchFeatures({ pageNum: 1, pageSize: 1000, requirementId: id })]); requirement.value = detail.data ? normalize(detail.data) : null; Object.assign(form, requirement.value || {}); features.value = featureResponse.rows || [] } finally { loading.value = false }
}
onMounted(load)
</script>

<style scoped>
.page-tools { margin-bottom: 16px; display: flex; gap: 8px; }.requirement-form { max-width: 980px; }.sentence-lines { width: 100%; min-height: 32px; padding: 5px 11px; border: 1px solid var(--el-border-color); border-radius: 4px; background: var(--el-fill-color-light); color: var(--el-text-color-regular); }.sentence-lines p { margin: 0; min-height: 24px; line-height: 24px; }.sentence-lines p + p { border-top: 1px solid var(--el-border-color-lighter); }
</style>
