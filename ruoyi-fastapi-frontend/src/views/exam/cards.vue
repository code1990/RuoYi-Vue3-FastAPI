<template>
  <div class="app-container exam-cards">
    <el-row :gutter="16">
      <el-col :xs="24" :md="6" :lg="5">
        <el-card shadow="never" class="chapter-list">
          <template #header>Java 章节</template>
          <el-menu :default-active="selectedCategory" @select="selectCategory">
            <el-menu-item v-for="chapter in chapters" :key="chapter.category_id" :index="String(chapter.category_id)">
              {{ chapter.name }}
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="18" :lg="19">
        <el-card shadow="never">
          <template #header>
            <div class="list-header"><span>{{ selectedName }} 知识卡片</span><el-tag>{{ cards.length }} 张</el-tag></div>
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
            <el-table-column label="类型" width="92"><template #default="{ row }"><el-tag size="small">{{ typeLabel(row.card_type) }}</el-tag></template></el-table-column>
            <el-table-column label="难度" width="76"><template #default="{ row }">{{ row.difficulty }}</template></el-table-column>
          </el-table>
          <el-empty v-if="!loading && !cards.length" description="该章节的知识卡片正在整理中" />
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
const selectedName = computed(() => chapters.value.find(item => String(item.category_id) === selectedCategory.value)?.name || 'Java')
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

async function selectCategory(categoryId) {
  selectedCategory.value = categoryId
  await loadCards()
}

onMounted(async () => {
  const response = await listExamCategories()
  categories.value = response.data || []
  selectedCategory.value = String(chapters.value[0]?.category_id || '')
  await loadCards()
})
</script>

<style scoped>
.chapter-list { margin-bottom: 16px; }
.chapter-list :deep(.el-card__body) { padding: 0; }
.chapter-list .el-menu { border-right: 0; }
.list-header { display: flex; align-items: center; justify-content: space-between; }
.answer-detail { padding: 4px 24px; line-height: 1.8; white-space: pre-line; }
.answer-detail p { margin: 8px 0; }
.tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
</style>
