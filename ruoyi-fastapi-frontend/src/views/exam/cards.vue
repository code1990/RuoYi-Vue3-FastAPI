<template>
  <div class="app-container exam-cards">
    <el-card shadow="never" class="category-card">
      <template #header>Java 知识卡片</template>
      <el-tabs v-model="selectedCategory" @tab-change="loadCards">
        <el-tab-pane v-for="category in chapters" :key="category.category_id" :label="category.name" :name="String(category.category_id)" />
      </el-tabs>
    </el-card>
    <el-empty v-if="!loading && !cards.length" description="该章节的知识卡片正在整理中" />
    <el-row v-loading="loading" :gutter="16">
      <el-col v-for="card in cards" :key="card.card_id" :xs="24" :lg="12" class="card-column">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header"><span>{{ card.question }}</span><el-tag size="small">{{ typeLabel(card.card_type) }}</el-tag></div>
          </template>
          <el-collapse>
            <el-collapse-item title="点击查看答案" name="answer"><p>{{ card.answer }}</p></el-collapse-item>
            <el-collapse-item title="关键得分点" name="points"><p>{{ card.key_points }}</p></el-collapse-item>
          </el-collapse>
          <div class="tags"><el-tag v-for="tag in card.tags.split(',').filter(Boolean)" :key="tag" size="small" type="info">{{ tag }}</el-tag></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup name="ExamJavaCards">
import { ref, computed, onMounted } from 'vue'
import { listExamCards, listExamCategories } from '@/api/exam/card'

const categories = ref([])
const cards = ref([])
const loading = ref(false)
const selectedCategory = ref('')
const chapters = computed(() => categories.value.filter(item => item.parent_id !== 0))
const typeLabels = { concept: '概念', enumeration: '枚举', comparison: '对比', scenario: '场景' }
const typeLabel = type => typeLabels[type] || '知识卡'

async function loadCards() {
  if (!selectedCategory.value) return
  loading.value = true
  try {
    const response = await listExamCards(Number(selectedCategory.value))
    cards.value = response.data || []
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const response = await listExamCategories()
  categories.value = response.data || []
  selectedCategory.value = String(chapters.value[0]?.category_id || '')
  await loadCards()
})
</script>

<style scoped>
.category-card { margin-bottom: 16px; }
.card-column { margin-bottom: 16px; }
.card-header { display: flex; align-items: center; justify-content: space-between; gap: 12px; font-weight: 600; }
.tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 16px; }
.el-collapse p { margin: 0; line-height: 1.75; white-space: pre-line; }
</style>
