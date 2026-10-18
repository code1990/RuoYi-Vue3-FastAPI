<template>
  <div class="app-container exam-cards">
    <el-card shadow="never" class="review-heatmap"><div class="list-header"><span>学习热力图</span><div><el-button v-for="year in years" :key="year" size="small" :type="year === selectedYear ? 'primary' : 'default'" @click="loadHeatmap(year)">{{ year }}</el-button><el-tag>今日 {{ reviewOverview.completedToday || 0 }} 次</el-tag></div></div><div class="heatmap-wrap"><div class="heatmap-months"><span v-for="month in heatmapMonths" :key="month.label" :style="{ gridColumn: month.column }">{{ month.label }}</span></div><div class="heatmap"><span v-for="day in heatmapDays" :key="day.date" :title="`${day.date}：${day.count} 次`" :class="['heatmap-day', heatLevel(day.count)]" /></div></div><div class="heatmap-legend"><span>Less</span><i /><i class="low" /><i class="mid" /><i class="high" /><i class="max" /><span>More</span></div></el-card>
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
      </el-table>
      <el-empty v-if="!loading && !cards.length" description="暂无匹配的知识卡片" />
    </el-card>
  </div>
</template>

<script setup name="ExamJavaCards">
import { ref, computed, onMounted } from 'vue'
import { getExamReviewOverview, listExamCards, listExamCategories } from '@/api/exam/card'

const categories = ref([])
const allCards = ref([])
const loading = ref(false)
const selectedCategoryIds = ref([])
const keyword = ref('')
const selectedType = ref('')
const reviewOverview = ref({})
const selectedYear = ref(new Date().getFullYear())
const years = computed(() => Array.from({ length: 4 }, (_, index) => selectedYear.value - index))
const formatDate = day => `${day.getFullYear()}-${String(day.getMonth() + 1).padStart(2, '0')}-${String(day.getDate()).padStart(2, '0')}`
const heatmapDays = computed(() => { const map = Object.fromEntries((reviewOverview.value.heatmap || []).map(item => [item.date, item.count])); const first = new Date(selectedYear.value, 0, 1); first.setDate(first.getDate() - first.getDay()); const last = new Date(selectedYear.value, 11, 31); last.setDate(last.getDate() + 6 - last.getDay()); const days = []; for (const day = new Date(first); day <= last; day.setDate(day.getDate() + 1)) days.push({ date: formatDate(day), count: day.getFullYear() === selectedYear.value ? map[formatDate(day)] || 0 : null }); return days })
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
.heatmap-day,.heatmap-legend i { width:12px; height:12px; border-radius:2px; background:#ebedf0; }.heatmap-day.low,.heatmap-legend .low { background:#9be9a8; }.heatmap-day.mid,.heatmap-legend .mid { background:#40c463; }.heatmap-day.high,.heatmap-legend .high { background:#30a14e; }.heatmap-day.max,.heatmap-legend .max { background:#216e39; }
.heatmap-legend { display:flex; align-items:center; justify-content:flex-end; gap:4px; margin-top:12px; color:#57606a; font-size:12px; }.heatmap-legend span { margin:0 4px; }
.filter-title { margin-bottom: 12px; font-weight: 600; }
.filter-options { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
.filter-options :deep(.el-check-tag) { margin: 0; }
.list-header { display: flex; align-items: center; justify-content: space-between; }
.table-tools { display: flex; gap: 12px; margin-bottom: 16px; }
.keyword-input { max-width: 420px; }
.type-select { width: 140px; }
.tags { display: flex; flex-wrap: wrap; gap: 6px; }
</style>
