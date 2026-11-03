<template>
  <div class="app-container">
    <el-card shadow="never">
      <template #header><div class="heading"><div><h2>关键词主题词</h2><p>删除后，资源检索立即不再按该主题词展开；下次导入不会恢复。</p></div><el-button @click="router.back()">返回文件明细</el-button></div></template>
      <el-table v-loading="loading" :data="keywords" border>
        <el-table-column prop="name" label="关键字" width="180" />
        <el-table-column label="主题词">
          <template #default="{ row }"><div class="topics"><el-tag v-for="topic in row.topics" :key="topic" closable @close="remove(row, topic)">{{ topic }}</el-tag><span v-if="!row.topics.length">暂无主题词</span></div></template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup name="FeizhuKeywordTopics">
import { ref } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { deleteFileKeywordTopic, listFileKeywords } from '@/api/feizhu/fileDetail'

const router = useRouter(), loading = ref(false), keywords = ref([])
async function load() { loading.value = true; try { keywords.value = (await listFileKeywords()).data || [] } finally { loading.value = false } }
async function remove(row, topic) {
  await ElMessageBox.confirm(`删除“${row.name}”的主题词“${topic}”？`, '确认删除', { type: 'warning' })
  await deleteFileKeywordTopic(row.id, topic)
  row.topics = row.topics.filter(item => item !== topic)
  ElMessage.success('已删除')
}
load()
</script>

<style scoped>
.heading { display:flex; align-items:center; justify-content:space-between; gap:16px; }.heading h2 { margin:0; font-size:18px; }.heading p { margin:6px 0 0; color:var(--el-text-color-secondary); font-size:13px; }.topics { display:flex; flex-wrap:wrap; gap:8px; }.topics span { color:var(--el-text-color-secondary); }
</style>
