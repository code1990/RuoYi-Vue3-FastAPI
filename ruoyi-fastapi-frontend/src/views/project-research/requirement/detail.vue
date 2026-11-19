<template>
  <div class="app-container" v-loading="loading">
    <div class="page-tools"><el-button @click="router.push('/project-research/requirement')">返回需求列表</el-button></div>
    <el-empty v-if="!loading && !requirement" description="未找到需求" />
    <template v-else-if="requirement">
      <el-card shadow="never" class="section"><template #header><div class="header"><span>{{ requirement.requirementCode }}</span><el-tag>{{ requirement.status }}</el-tag></div></template><h2>{{ requirement.title }}</h2></el-card>
      <el-card shadow="never" class="section"><template #header>来源内容</template><el-descriptions :column="1" border><el-descriptions-item label="原文">{{ requirement.sourceDocumentTitle || '-' }}（ID：{{ requirement.sourceDocumentId || '-' }}）</el-descriptions-item><el-descriptions-item label="笔记">{{ requirement.sourceNoteTitle || '-' }}（ID：{{ requirement.sourceNoteId || '-' }}）</el-descriptions-item></el-descriptions><section-text title="原文概述" :text="requirement.sourceSummary" /><section-text title="笔记摘要" :text="requirement.noteSummary" /><section-text title="核心概念" :text="requirement.coreConcepts" /><section-text title="核心观点（AI总结）" :text="requirement.coreViewpoints" /></el-card>
      <el-card shadow="never" class="section"><template #header>需求定义</template><section-text title="要解决的问题" :text="requirement.problem || requirement.title" /><section-text title="需求目标" :text="requirement.goal" /><section-text title="使用方式与边界" :text="requirement.scope" /><section-text title="验收标准" :text="requirement.acceptance" /></el-card>
      <el-card shadow="never" class="section"><template #header>功能方案</template><el-empty v-if="!features.length" description="尚未拆分功能" /><el-table v-else :data="features" border><el-table-column prop="featureCode" label="编号" width="180" /><el-table-column prop="title" label="功能" min-width="220" /><el-table-column prop="logic" label="解决方式" min-width="320" /><el-table-column prop="status" label="状态" width="100" /></el-table></el-card>
    </template>
  </div>
</template>

<script setup name="ResearchRequirementDetail">
import { h, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getResearchRequirement, listResearchFeatures } from '@/api/project-research/requirement'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const requirement = ref(null)
const features = ref([])
const sentences = value => String(value || '待补充').replace(/\r?\n/g, '').match(/[^。！？!?]+[。！？!?]?/g)?.map(item => item.trim()).filter(Boolean) || ['待补充']
const SectionText = {
  props: { title: String, text: String },
  setup(props) { return () => h('section', { class: 'text-section' }, [h('h3', props.title), ...sentences(props.text).map(sentence => h('p', sentence))]) },
}

async function load() {
  loading.value = true
  try {
    const id = Number(route.params.requirementId)
    const [requirementResponse, featureResponse] = await Promise.all([getResearchRequirement(id), listResearchFeatures({ pageNum: 1, pageSize: 1000, requirementId: id })])
    requirement.value = requirementResponse.data || null
    features.value = featureResponse.rows || []
  } finally { loading.value = false }
}
onMounted(load)
</script>

<style scoped>
.page-tools { margin-bottom: 16px; }.section { margin-bottom: 16px; }.header { display: flex; justify-content: space-between; align-items: center; }.text-section { margin-top: 20px; }.text-section h3 { font-size: 14px; color: #303133; margin: 0 0 8px; }.text-section p { margin: 0 0 8px; line-height: 1.8; color: #606266; }h2 { margin: 0; font-size: 20px; line-height: 1.6; }
</style>
