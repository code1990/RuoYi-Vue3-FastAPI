<template>
  <div class="app-container exam-card-detail" v-loading="loading">
    <div class="page-tools">
      <el-button @click="backToList">返回题库列表</el-button>
      <span v-if="card" class="position">第 {{ cardIndex + 1 }} / {{ candidates.length }} 题</span>
      <div class="navigation"><el-button :disabled="cardIndex <= 0" @click="move(-1)">上一题</el-button><el-button :disabled="cardIndex < 0 || cardIndex >= candidates.length - 1" @click="move(1)">下一题</el-button></div>
    </div>
    <el-empty v-if="!loading && !card" description="未找到题目"><el-button type="primary" @click="backToList">返回列表</el-button></el-empty>
    <template v-else-if="card">
      <el-card shadow="never" class="section"><template #header><div class="section-header"><span>题目</span><el-tag>{{ categoryName(card.category_id) }}</el-tag></div></template><div class="question">{{ card.question }}</div></el-card>
      <el-card shadow="never" class="section"><template #header>原文 / 参考答案</template><div class="content">{{ card.answer }}</div></el-card>
      <el-card shadow="never" class="section"><template #header><div class="section-header"><span>AI 总结方案 <el-badge :value="versions.length" type="success" /></span><el-tag v-if="activeVersion" type="success">当前 v{{ activeVersion.version_no }}</el-tag></div></template>
        <el-empty v-if="!versions.length" description="暂无 AI 总结方案" />
        <div v-for="version in versions" :key="version.summary_version_id" :class="['version-card', { active: version.summary_version_id === activeId }]">
          <div class="version-header"><span><b>v{{ version.version_no }}</b> · {{ version.title }}</span><div><el-tag v-if="version.summary_version_id === activeId" type="success">当前启用</el-tag><el-button v-else link type="primary" @click="activateVersion(version)" v-hasPermi="['exam:card:edit']">启用</el-button></div></div>
          <div v-for="section in summarySections(version.ai_summary)" :key="section.title" class="summary-section">
            <div class="summary-title">{{ section.title }}</div>
            <div v-if="section.title === '要点'" class="content summary-points">{{ section.content.replace(/；/g, '；\n') }}</div>
            <div v-else class="content">{{ section.content }}</div>
          </div>
        </div>
      </el-card>
      <el-card shadow="never" class="section" v-hasPermi="['exam:card:edit']"><template #header>新增版本</template>
        <el-form :model="form" label-width="82px" class="new-version-form"><el-form-item label="方案名称" required><el-input v-model="form.title" maxlength="100" show-word-limit placeholder="例如：1 分钟面试版" /></el-form-item><el-form-item label="AI 总结" required><el-input v-model="form.aiSummary" type="textarea" :rows="6" maxlength="300" show-word-limit placeholder="最多 300 字" /></el-form-item><el-form-item><el-button type="primary" :loading="saving" @click="addVersion">提交并启用</el-button></el-form-item></el-form>
      </el-card>
    </template>
  </div>
</template>

<script setup name="ExamCardDetail">
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { activateExamCardAiSummaryVersion, addExamCardAiSummaryVersion, listExamCardAiSummaryVersions, listExamCards, listExamCategories } from '@/api/exam/card'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const allCards = ref([])
const categories = ref([])
const versions = ref([])
const activeId = ref(null)
const form = ref({ title: '', aiSummary: '' })
const candidateIds = ref([])
const filters = computed(() => ({
  categoryIds: String(route.query.categoryIds || '').split(',').map(Number).filter(categoryId => Number.isInteger(categoryId) && categoryId > 0),
  type: typeof route.query.type === 'string' ? route.query.type : '',
  keyword: typeof route.query.keyword === 'string' ? route.query.keyword.trim().toLowerCase() : '',
}))
const candidates = computed(() => candidateIds.value.map(cardId => allCards.value.find(item => item.card_id === cardId)).filter(Boolean))
const matchesFilters = item => {
  if (filters.value.categoryIds.length && !filters.value.categoryIds.includes(item.category_id)) return false
  if (filters.value.type && item.card_type !== filters.value.type) return false
  return !filters.value.keyword || [item.question, item.answer, item.ai_summary, item.key_points, item.tags].some(value => String(value || '').toLowerCase().includes(filters.value.keyword))
}
const cardIndex = computed(() => candidates.value.findIndex(item => item.card_id === Number(route.params.cardId)))
const card = computed(() => candidates.value[cardIndex.value] || null)
const activeVersion = computed(() => versions.value.find(item => item.summary_version_id === activeId.value) || null)
const categoryNames = computed(() => Object.fromEntries(categories.value.map(item => [item.category_id, item.name])))
const categoryName = categoryId => categoryNames.value[categoryId] || '未分类'
const summarySections = summary => {
  const text = String(summary || '').trim()
  const sections = ['结论', '要点', '补充'].map(title => ({
    title,
    content: text.match(new RegExp(`${title}：([\\s\\S]*?)(?=结论：|要点：|补充：|$)`))?.[1]?.trim() || '',
  })).filter(section => section.content)
  return sections.length ? sections : [{ title: 'AI 总结', content: text }]
}

async function loadVersions() {
  if (!card.value) return
  const response = await listExamCardAiSummaryVersions(card.value.card_id)
  versions.value = response.data?.versions || []
  activeId.value = response.data?.active_summary_version_id || null
}

async function load() {
  loading.value = true
  try {
    const [cardResponse, categoryResponse] = await Promise.all([listExamCards(), listExamCategories()])
    allCards.value = cardResponse.data || []
    categories.value = categoryResponse.data || []
    candidateIds.value = allCards.value.filter(matchesFilters).map(item => item.card_id)
    await loadVersions()
  } catch { ElMessage.error('题目详情加载失败') } finally { loading.value = false }
}

function move(offset) {
  const next = candidates.value[cardIndex.value + offset]
  if (next) router.push({ name: 'ExamCardDetail', params: { cardId: next.card_id }, query: route.query })
}

function backToList() {
  router.push({ path: '/exam/java-cards', query: route.query })
}

async function activateVersion(version) {
  await activateExamCardAiSummaryVersion(card.value.card_id, version.summary_version_id)
  await loadVersions()
  const current = allCards.value.find(item => item.card_id === card.value.card_id)
  if (current) current.ai_summary = version.ai_summary
  ElMessage.success(`已启用 v${version.version_no}`)
}

async function addVersion() {
  const title = form.value.title.trim()
  const aiSummary = form.value.aiSummary.trim()
  if (!title || !aiSummary) return ElMessage.warning('请填写方案名称和 AI 总结')
  saving.value = true
  try {
    await addExamCardAiSummaryVersion(card.value.card_id, { title, aiSummary })
    form.value = { title: '', aiSummary: '' }
    await loadVersions()
    const current = allCards.value.find(item => item.card_id === card.value.card_id)
    if (current && activeVersion.value) current.ai_summary = activeVersion.value.ai_summary
    ElMessage.success('新版本已启用')
  } finally { saving.value = false }
}

watch(() => route.params.cardId, loadVersions)
onMounted(load)
</script>

<style scoped>
.page-tools,.section-header,.version-header { display:flex; align-items:center; gap:12px; }.page-tools { margin-bottom:16px; }.position { color:#606266; }.navigation { margin-left:auto; display:flex; gap:8px; }.section { margin-bottom:16px; }.section-header,.version-header { justify-content:space-between; }.question { font-size:18px; font-weight:600; line-height:1.7; }.content { white-space:pre-wrap; line-height:1.7; color:#303133; }.version-card { border:1px solid #dcdfe6; border-radius:6px; padding:14px; margin-top:12px; }.version-card.active { border-color:#67c23a; background:#f0f9eb; }.summary-section { margin-top:18px; }.summary-title { margin-bottom:6px; color:#1f4c7c; font-weight:700; }.summary-points { color:#303133; line-height:1.8; }.new-version-form { max-width:760px; }
</style>
