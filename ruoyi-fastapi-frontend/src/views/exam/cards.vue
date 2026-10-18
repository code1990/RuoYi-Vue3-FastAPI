<template>
  <div class="app-container exam-cards">
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
import { listExamCards, listExamCategories } from '@/api/exam/card'

const categories = ref([])
const allCards = ref([])
const loading = ref(false)
const selectedCategoryIds = ref([])
const keyword = ref('')
const selectedType = ref('')
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

onMounted(async () => {
  loading.value = true
  try {
    const [categoryResponse, cardResponse] = await Promise.all([listExamCategories(), listExamCards()])
    categories.value = categoryResponse.data || []
    allCards.value = cardResponse.data || []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.chapter-filter { margin-bottom: 16px; }
.filter-title { margin-bottom: 12px; font-weight: 600; }
.filter-options { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
.filter-options :deep(.el-check-tag) { margin: 0; }
.list-header { display: flex; align-items: center; justify-content: space-between; }
.table-tools { display: flex; gap: 12px; margin-bottom: 16px; }
.keyword-input { max-width: 420px; }
.type-select { width: 140px; }
.tags { display: flex; flex-wrap: wrap; gap: 6px; }
</style>
