<template>
  <div class="app-container">
    <el-form :inline="true" :model="query" @submit.prevent>
      <el-form-item label="标题"><el-input v-model="query.title" clearable placeholder="需求、原文或笔记标题" @keyup.enter="load" /></el-form-item>
      <el-form-item><el-button type="primary" @click="load">查询</el-button></el-form-item>
    </el-form>
    <el-button type="primary" icon="Plus" @click="openAdd" v-hasPermi="['research:requirement:add']">新增需求</el-button>
    <el-table v-loading="loading" :data="rows" class="mt12">
      <el-table-column prop="requirementCode" label="编号" width="140" />
      <el-table-column prop="title" label="需求问题" min-width="260" show-overflow-tooltip />
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
          <el-button link type="primary" @click="openDetail(row)">详情</el-button>
          <el-button link type="primary" @click="openEdit(row)" v-hasPermi="['research:requirement:edit']">编辑</el-button>
          <el-button link type="danger" @click="remove(row)" v-hasPermi="['research:requirement:remove']">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total" :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="load" />
  </div>
</template>

<script setup name="ResearchRequirementManage">
import { delResearchRequirement, listResearchRequirements } from '@/api/project-research/requirement'
import { useRouter } from 'vue-router'

const { proxy } = getCurrentInstance()
const router = useRouter()
const loading = ref(false), total = ref(0), rows = ref([])
const query = reactive({ pageNum: 1, pageSize: 10, title: undefined })
function load() { loading.value = true; listResearchRequirements(query).then(res => { rows.value = res.rows; total.value = res.total }).finally(() => { loading.value = false }) }
function openDetail(row) { router.push({ name: 'ResearchRequirementDetail', params: { requirementId: row.id } }) }
function openAdd() { router.push({ name: 'ResearchRequirementDetail', params: { requirementId: 'new' } }) }
function openEdit(row) { openDetail(row) }
function remove(row) { proxy.$modal.confirm(`确认删除需求“${row.title}”吗？`).then(() => delResearchRequirement(row.id)).then(() => { proxy.$modal.msgSuccess('删除成功'); load() }) }
load()
</script>

<style scoped>.mt12 { margin-top: 12px; }</style>
