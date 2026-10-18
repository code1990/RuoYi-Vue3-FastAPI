<template>
  <div class="app-container exam-cards">
    <el-card shadow="never" class="chapter-filter">
      <div class="filter-title">Java 章节</div>
      <div class="filter-options">
        <el-button :type="selectedCategoryIds.length ? 'default' : 'primary'" @click="clearCategories">全部</el-button>
        <el-check-tag v-for="chapter in chapters" :key="chapter.category_id" :checked="selectedCategoryIds.includes(chapter.category_id)" @change="toggleCategory(chapter.category_id)">
          {{ chapter.name }}
        </el-check-tag>
      </div>
    </el-card>
    <el-card shadow="never">
      <template #header>
        <div class="list-header"><span>{{ selectedName }}知识卡片</span><el-tag>{{ cards.length }} 张</el-tag></div>
      </template>
      <el-table v-loading="loading" :data="cards" row-key="card_id" border>
            <el-table-column type="expand" width="52">
              <template #default="{ row }">
                <div class="answer-detail">
                  <p><strong>参考答案：</strong>{{ row.answer }}</p>
                  <p><strong>关键得分点：</strong>{{ row.key_points }}</p>
                  <div class="tags"><el-tag v-for="tag in row.tags.split(',').filter(Boolean)" :key="tag" size="small" type="info">{{ tag }}</el-tag></div>
                </div>
              </template>
            </el-table-column>
            <el-table-column type="index" label="#" width="56" />
            <el-table-column prop="question" label="题目" min-width="360" show-overflow-tooltip />
            <el-table-column prop="answer" label="原文" min-width="260" show-overflow-tooltip />
            <el-table-column label="类型" width="92"><template #default="{ row }"><el-tag size="small">{{ typeLabel(row.card_type) }}</el-tag></template></el-table-column>
            <el-table-column label="难度" width="76"><template #default="{ row }">{{ row.difficulty }}</template></el-table-column>
      </el-table>
      <el-empty v-if="!loading && !cards.length" description="所选章节的知识卡片正在整理中" />
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
const chapters = computed(() => categories.value.filter(item => item.parent_id !== 0))
const cards = computed(() => selectedCategoryIds.value.length
  ? allCards.value.filter(item => selectedCategoryIds.value.includes(item.category_id))
  : allCards.value)
const selectedName = computed(() => selectedCategoryIds.value.length ? '已选章节 ' : '全部 ')
const typeLabels = { concept: '概念', enumeration: '枚举', comparison: '对比', scenario: '场景' }
const typeLabel = type => typeLabels[type] || '知识卡'

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
.answer-detail { padding: 4px 24px; line-height: 1.8; white-space: pre-line; }
.answer-detail p { margin: 8px 0; }
.tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
</style>
