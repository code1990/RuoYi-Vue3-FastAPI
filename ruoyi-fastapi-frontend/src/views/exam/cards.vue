<template>
  <div class="app-container exam-cards">
    <el-card shadow="never" class="review-heatmap"><div class="list-header"><span>学习热力图</span><div><el-button v-for="year in years" :key="year" size="small" :type="year === selectedYear ? 'primary' : 'default'" @click="loadHeatmap(year)">{{ year }}</el-button><el-tag>今日 {{ reviewOverview.completedToday || 0 }} 次</el-tag></div></div><div class="heatmap-wrap"><div class="heatmap-months"><span v-for="month in heatmapMonths" :key="month.label" :style="{ gridColumn: month.column }">{{ month.label }}</span></div><div class="heatmap"><span v-for="day in heatmapDays" :key="day.date" :title="day.planned ? `${day.date}：待复习 ${day.planned} 张` : `${day.date}：${day.count} 次`" :class="['heatmap-day', day.planned ? 'planned' : heatLevel(day.count)]" /></div></div><div class="heatmap-legend"><span>Less</span><i /><i class="low" /><i class="mid" /><i class="high" /><i class="max" /><span>More</span><i class="planned" /><span>待复习</span></div></el-card>
    <el-card shadow="never" class="chapter-filter">
      <div class="filter-title">知识分类</div>
      <div class="filter-options">
        <el-button :type="selectedCategoryIds.length ? 'default' : 'primary'" @click="clearCategories">全部</el-button>
        <el-check-tag v-for="chapter in chapters" :key="chapter.category_id" :checked="selectedCategoryIds.includes(chapter.category_id)" @change="toggleCategory(chapter.category_id)">
          {{ chapter.name }}
        </el-check-tag>
      </div>
    </el-card>
    <el-card shadow="never">
      <template #header>
        <div class="list-header"><span>{{ selectedName }}知识卡片</span><el-tag>{{ cards.length }} / {{ allCards.length }} 张</el-tag></div>
      </template>
      <div class="table-tools">
        <el-input v-model="keyword" clearable placeholder="搜索题目、答案、总结、要点或标签" class="keyword-input" />
        <el-select v-model="selectedType" clearable placeholder="全部类型" class="type-select"><el-option v-for="(label, value) in typeLabels" :key="value" :label="label" :value="value" /></el-select>
      </div>
      <el-table v-loading="loading" :data="cards" row-key="card_id" border max-height="calc(100vh - 310px)">
        <el-table-column type="index" label="#" width="56" />
        <el-table-column label="分类" width="150" show-overflow-tooltip><template #default="{ row }">{{ categoryName(row.category_id) }}</template></el-table-column>
        <el-table-column prop="question" label="题目" min-width="260" show-overflow-tooltip />
        <el-table-column prop="answer" label="参考答案" min-width="360" show-overflow-tooltip />
        <el-table-column prop="ai_summary" label="AI 总结" min-width="300" show-overflow-tooltip />
        <el-table-column prop="key_points" label="关键得分点" min-width="220" show-overflow-tooltip />
        <el-table-column label="标签" min-width="160"><template #default="{ row }"><div class="tags"><el-tag v-for="tag in tags(row)" :key="tag" size="small" type="info">{{ tag }}</el-tag></div></template></el-table-column>
        <el-table-column label="类型" width="92"><template #default="{ row }"><el-tag size="small">{{ typeLabel(row.card_type) }}</el-tag></template></el-table-column>
        <el-table-column label="难度" width="76"><template #default="{ row }">{{ row.difficulty }}</template></el-table-column>
        <el-table-column label="AI 总结方案" width="130" fixed="right"><template #default="{ row }"><el-button link type="primary" @click="openSummaryVersions(row)" v-hasPermi="['exam:card:edit']">管理</el-button></template></el-table-column>
      </el-table>
      <el-empty v-if="!loading && !cards.length" description="暂无匹配的知识卡片" />
    </el-card>
    <el-dialog v-model="summaryDialog.open" :title="summaryDialog.card ? `AI 总结方案：${summaryDialog.card.question}` : 'AI 总结方案'" width="760px" append-to-body destroy-on-close>
      <el-table :data="summaryDialog.versions" border>
        <el-table-column label="版本" width="80"><template #default="{ row }">v{{ row.version_no }}</template></el-table-column>
        <el-table-column prop="title" label="方案名称" width="160" show-overflow-tooltip />
        <el-table-column label="总结内容" min-width="300"><template #default="{ row }"><div class="summary-version-content">{{ row.ai_summary }}</div></template></el-table-column>
        <el-table-column label="状态" width="88"><template #default="{ row }"><el-tag v-if="row.summary_version_id === summaryDialog.activeId" type="success">当前</el-tag><el-tag v-else type="info">未启用</el-tag></template></el-table-column>
        <el-table-column label="操作" width="88"><template #default="{ row }"><el-button v-if="row.summary_version_id !== summaryDialog.activeId" link type="primary" @click="activateSummaryVersion(row)">设为当前</el-button></template></el-table-column>
      </el-table>
      <el-divider content-position="left">新增学习方案</el-divider>
      <el-form :model="summaryForm" label-width="82px">
        <el-form-item label="方案名称" required><el-input v-model="summaryForm.title" maxlength="100" show-word-limit placeholder="例如：1 分钟面试版" /></el-form-item>
        <el-form-item label="AI 总结" required><el-input v-model="summaryForm.aiSummary" type="textarea" :rows="6" maxlength="300" show-word-limit placeholder="最多 300 字；保存后需手动设为当前才会在移动端显示。" /></el-form-item>
        <el-form-item><el-button type="primary" :loading="summaryDialog.saving" @click="addSummaryVersion">保存为新方案</el-button></el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup name="ExamJavaCards">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { activateExamCardAiSummaryVersion, addExamCardAiSummaryVersion, getExamReviewOverview, listExamCardAiSummaryVersions, listExamCards, listExamCategories } from '@/api/exam/card'

const categories = ref([])
const allCards = ref([])
const loading = ref(false)
const selectedCategoryIds = ref([])
const keyword = ref('')
const selectedType = ref('')
const reviewOverview = ref({})
const selectedYear = ref(new Date().getFullYear())
const summaryDialog = ref({ open: false, card: null, versions: [], activeId: null, saving: false })
const summaryForm = ref({ title: '', aiSummary: '' })
const years = computed(() => Array.from({ length: 4 }, (_, index) => new Date().getFullYear() - index))
const formatDate = day => `${day.getFullYear()}-${String(day.getMonth() + 1).padStart(2, '0')}-${String(day.getDate()).padStart(2, '0')}`
const heatmapDays = computed(() => { const map = Object.fromEntries((reviewOverview.value.heatmap || []).map(item => [item.date, item.count])); const planned = Object.fromEntries((reviewOverview.value.plannedReviews || []).map(item => [item.date, item.count])); const first = new Date(selectedYear.value, 0, 1); first.setDate(first.getDate() - first.getDay()); const last = new Date(selectedYear.value, 11, 31); last.setDate(last.getDate() + 6 - last.getDay()); const days = []; for (const day = new Date(first); day <= last; day.setDate(day.getDate() + 1)) days.push({ date: formatDate(day), count: day.getFullYear() === selectedYear.value ? map[formatDate(day)] || 0 : null, planned: day.getFullYear() === selectedYear.value ? planned[formatDate(day)] || 0 : null }); return days })
const heatmapMonths = computed(() => heatmapDays.value.reduce((months, day, index) => { if (day.date.endsWith('-01') && !months.some(item => item.label === `${Number(day.date.slice(5, 7))}月`)) months.push({ label: `${Number(day.date.slice(5, 7))}月`, column: Math.floor(index / 7) + 1 }); return months }, []))
const heatLevel = count => count >= 30 ? 'max' : count >= 20 ? 'high' : count >= 10 ? 'mid' : count ? 'low' : ''
const chapters = computed(() => categories.value.filter(item => item.parent_id !== 0))
const categoryNames = computed(() => Object.fromEntries(categories.value.map(item => [item.category_id, item.name])))
const cards = computed(() => allCards.value.filter(item => {
  if (selectedCategoryIds.value.length && !selectedCategoryIds.value.includes(item.category_id)) return false
  if (selectedType.value && item.card_type !== selectedType.value) return false
  const query = keyword.value.trim().toLowerCase()
  return !query || [item.question, item.answer, item.ai_summary, item.key_points, item.tags].some(value => String(value || '').toLowerCase().includes(query))
}))
const selectedName = computed(() => selectedCategoryIds.value.length ? '已选章节 ' : '全部 ')
const typeLabels = { concept: '概念', enumeration: '枚举', comparison: '对比', scenario: '场景' }
const typeLabel = type => typeLabels[type] || '知识卡'
const categoryName = categoryId => categoryNames.value[categoryId] || '未分类'
const tags = row => String(row.tags || '').split(',').map(tag => tag.trim()).filter(Boolean)

function clearCategories() {
  selectedCategoryIds.value = []
}

function toggleCategory(categoryId) {
  selectedCategoryIds.value = selectedCategoryIds.value.includes(categoryId)
    ? selectedCategoryIds.value.filter(id => id !== categoryId)
    : [...selectedCategoryIds.value, categoryId]
}

async function loadSummaryVersions() {
  const response = await listExamCardAiSummaryVersions(summaryDialog.value.card.card_id)
  summaryDialog.value.versions = response.data?.versions || []
  summaryDialog.value.activeId = response.data?.active_summary_version_id || null
}

async function openSummaryVersions(card) {
  summaryDialog.value = { open: true, card, versions: [], activeId: null, saving: false }
  summaryForm.value = { title: '', aiSummary: '' }
  try { await loadSummaryVersions() } catch { ElMessage.error('AI 总结方案加载失败') }
}

async function addSummaryVersion() {
  const title = summaryForm.value.title.trim()
  const aiSummary = summaryForm.value.aiSummary.trim()
  if (!title || !aiSummary) return ElMessage.warning('请填写方案名称和 AI 总结')
  summaryDialog.value.saving = true
  try {
    await addExamCardAiSummaryVersion(summaryDialog.value.card.card_id, { title, aiSummary })
    summaryForm.value = { title: '', aiSummary: '' }
    await loadSummaryVersions()
    ElMessage.success('已保存为新方案，设为当前后才会在移动端显示')
  } finally { summaryDialog.value.saving = false }
}

async function activateSummaryVersion(version) {
  await activateExamCardAiSummaryVersion(summaryDialog.value.card.card_id, version.summary_version_id)
  summaryDialog.value.activeId = version.summary_version_id
  summaryDialog.value.card.ai_summary = version.ai_summary
  ElMessage.success('已设为当前 AI 总结')
}

async function loadHeatmap(year) { selectedYear.value = year; reviewOverview.value = (await getExamReviewOverview(year)).data || {} }

onMounted(async () => {
  loading.value = true
  try {
    const [categoryResponse, cardResponse, overviewResponse] = await Promise.all([listExamCategories(), listExamCards(), getExamReviewOverview(selectedYear.value)])
    categories.value = categoryResponse.data || []
    allCards.value = cardResponse.data || []
    reviewOverview.value = overviewResponse.data || {}
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.chapter-filter { margin-bottom: 16px; }
.review-heatmap { margin-bottom: 16px; }
.heatmap-wrap { overflow-x:auto; padding-top:8px; }.heatmap-months { display:grid; grid-template-columns:repeat(53, 12px); gap:4px; height:18px; color:#57606a; font-size:12px; }.heatmap { display:grid; grid-template-rows:repeat(7, 12px); grid-auto-flow:column; grid-auto-columns:12px; gap:4px; }
.heatmap-day,.heatmap-legend i { width:12px; height:12px; border-radius:2px; background:#ebedf0; }.heatmap-day.low,.heatmap-legend .low { background:#9be9a8; }.heatmap-day.mid,.heatmap-legend .mid { background:#40c463; }.heatmap-day.high,.heatmap-legend .high { background:#30a14e; }.heatmap-day.max,.heatmap-legend .max { background:#216e39; }.heatmap-day.planned,.heatmap-legend .planned { background:#f9a8d4; }
.heatmap-legend { display:flex; align-items:center; justify-content:flex-end; gap:4px; margin-top:12px; color:#57606a; font-size:12px; }.heatmap-legend span { margin:0 4px; }
.filter-title { margin-bottom: 12px; font-weight: 600; }
.filter-options { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
.filter-options :deep(.el-check-tag) { margin: 0; }
.list-header { display: flex; align-items: center; justify-content: space-between; }
.table-tools { display: flex; gap: 12px; margin-bottom: 16px; }
.keyword-input { max-width: 420px; }
.type-select { width: 140px; }
.tags { display: flex; flex-wrap: wrap; gap: 6px; }
.summary-version-content { white-space: pre-wrap; line-height: 1.55; }
</style>
