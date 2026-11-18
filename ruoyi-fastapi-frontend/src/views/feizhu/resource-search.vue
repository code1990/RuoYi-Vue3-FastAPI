<template>
  <div class="app-container resource-search-page">
    <main class="resource-shell">
      <section class="search-hero">
        <div class="brand-line"><el-icon><CollectionTag /></el-icon><strong>网盘资源搜索</strong><span>静态页面演示</span></div>
        <div class="search-box"><el-input v-model="inputKeyword" size="large" clearable placeholder="搜索你需要的资源" @keyup.enter="search"><template #prefix><el-icon><Search /></el-icon></template><template #append><el-button type="primary" :disabled="!inputKeyword.trim()" @click="search">搜索</el-button></template></el-input></div>
      </section>

      <section class="filter-panel">
        <div class="platforms"><span class="filter-label">网盘平台</span><button v-for="platform in platforms" :key="platform.value" class="platform" :class="{ active: query.resType === platform.value, disabled: platform.disabled }" :disabled="platform.disabled" @click="setPlatform(platform.value)"><el-icon><FolderOpened /></el-icon>{{ platform.label }}</button></div>
        <div class="filters"><span class="filter-label">筛选</span><el-select v-model="filters.ext" clearable placeholder="文件类型" @change="resetPage"><el-option label="PDF" value="pdf" /><el-option label="视频" value="mp4" /><el-option label="文档" value="md" /><el-option label="电子书" value="mobi" /></el-select><el-select v-model="filters.size" clearable placeholder="文件大小" @change="resetPage"><el-option label="1GB 以上" value="large" /><el-option label="100MB - 1GB" value="middle" /><el-option label="100MB 以下" value="small" /></el-select><el-select v-model="filters.time" clearable placeholder="文件时间" @change="resetPage"><el-option label="近一个月" value="month" /><el-option label="近半年" value="half-year" /></el-select><el-button v-if="hasFilters" link type="primary" @click="clearFilters">清除筛选</el-button></div>
      </section>

      <section ref="resultSection" class="result-section">
        <div class="result-heading"><div><strong v-if="query.kw">“{{ query.kw }}”的搜索结果</strong><strong v-else>资源搜索</strong><span>共 {{ total.toLocaleString() }} 个结果</span></div><span class="result-hint">当前为静态数据演示</span></div>
        <el-empty v-if="!rows.length" description="未找到相关资源，可更换关键词或清除筛选" />
        <div v-else class="resource-list">
          <article v-for="(item, index) in rows" :key="`${item.id}-${index}`" class="resource-card" @click="openDetail(item)">
            <div class="resource-icon" :class="item.isdir ? 'folder' : 'file'"><el-icon><FolderOpened v-if="item.isdir" /><Document v-else /></el-icon></div>
            <div class="resource-main"><h2><template v-for="(part, partIndex) in highlighted(item.filename)" :key="partIndex"><mark v-if="part.marked">{{ part.text }}</mark><template v-else>{{ part.text }}</template></template></h2><div class="metadata"><el-tag size="small" effect="plain">{{ platformName(item.type) }}</el-tag><span>{{ formatSize(item.size) }}</span><span>{{ item.updatetime.slice(0, 10) }}</span><span class="status">资源状态未知</span></div><ul v-if="item.filelist?.length" class="file-preview"><li v-for="file in item.filelist.slice(0, 4)" :key="`${item.id}-${file.filename}`" :class="{ directory: file.isdir }"><el-icon><FolderOpened v-if="file.isdir" /><Document v-else /></el-icon><span>{{ file.filename }}</span><em v-if="file.size">{{ formatSize(file.size) }}</em></li><li v-if="item.filelist.length > 4" class="more-files">……</li></ul></div>
            <div class="card-action"><span>查看详情</span><el-icon><ArrowRight /></el-icon></div>
          </article>
        </div>
      </section>

      <footer v-if="total" class="result-pagination"><span class="page-total">共 {{ total.toLocaleString() }} 个结果</span><pagination v-model:page="query.page" :limit="pageSize" :total="total" :page-sizes="[pageSize]" layout="prev, pager, next" :auto-scroll="false" @pagination="changePage" /><span>第 {{ query.page }} 页，共 {{ pageCount }} 页</span></footer>
    </main>
  </div>
</template>

<script setup name="FeizhuResourceSearch">
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowRight, CollectionTag, Document, FolderOpened, Search } from '@element-plus/icons-vue'
import { feizhuDemoResources, feizhuDemoTotal, feizhuPageSize, feizhuPlatforms } from '@/mock/feizhuResources'

const route = useRoute(), router = useRouter(), resultSection = ref()
const inputKeyword = ref(typeof route.query.kw === 'string' ? route.query.kw : '')
const query = reactive({ kw: inputKeyword.value, page: Math.max(Number(route.query.page) || 1, 1), resType: typeof route.query.resType === 'string' ? route.query.resType : 'baidu' })
const filters = reactive({ ext: '', size: '', time: '' })
const pageSize = feizhuPageSize, platforms = feizhuPlatforms
const hasFilters = computed(() => Object.values(filters).some(Boolean))
const matchedResources = computed(() => feizhuDemoResources.filter(item => matchesKeyword(item) && matchesFilters(item)))
const isUnfilteredDemo = computed(() => !query.kw && !hasFilters.value)
const total = computed(() => isUnfilteredDemo.value ? feizhuDemoTotal : matchedResources.value.length)
const pageCount = computed(() => Math.max(Math.ceil(total.value / pageSize), 1))
const rows = computed(() => {
  const source = matchedResources.value
  if (!source.length) return []
  const start = (query.page - 1) * pageSize
  return isUnfilteredDemo.value
    ? Array.from({ length: pageSize }, (_, index) => source[(start + index) % source.length])
    : source.slice(start, start + pageSize)
})

function matchesFilters(item) {
  const ext = item.ext || item.filelist?.find(file => file.ext)?.ext
  if (filters.ext && ext !== filters.ext) return false
  if (filters.size === 'large' && item.size < 1024 ** 3) return false
  if (filters.size === 'middle' && (item.size < 100 * 1024 ** 2 || item.size >= 1024 ** 3)) return false
  if (filters.size === 'small' && item.size >= 100 * 1024 ** 2) return false
  if (filters.time === 'month' && item.updatetime < '2026-10-18') return false
  if (filters.time === 'half-year' && item.updatetime < '2026-05-18') return false
  return true
}
function matchesKeyword(item) { const keyword = query.kw.trim().toLowerCase(); return !keyword || `${item.filename} ${item.filelist.map(file => file.filename).join(' ')}`.toLowerCase().includes(keyword) }
function syncRoute() { router.replace({ query: { kw: query.kw || undefined, page: query.page > 1 ? String(query.page) : undefined, resType: query.resType } }) }
function search() { query.kw = inputKeyword.value.trim(); query.page = 1; syncRoute() }
function resetPage() { query.page = 1; syncRoute() }
function setPlatform(value) { query.resType = value; resetPage() }
function clearFilters() { Object.assign(filters, { ext: '', size: '', time: '' }); resetPage() }
function changePage({ page }) { query.page = page; syncRoute(); resultSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' }) }
function openDetail(item) { router.push({ path: '/feizhu/resource-detail', query: { id: item.id, kw: query.kw || undefined } }) }
function platformName(type) { return platforms.find(item => item.value === type)?.label || type }
function formatSize(value) { const size = Number(value); if (!Number.isFinite(size) || size <= 0) return '--'; const units = ['B', 'KB', 'MB', 'GB', 'TB']; const index = Math.min(Math.floor(Math.log(size) / Math.log(1024)), units.length - 1); return `${Math.floor(size / 1024 ** index)}${units[index]}` }
function highlighted(text) { const keyword = query.kw.trim(); if (!keyword) return [{ text, marked: false }]; const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); return text.split(new RegExp(`(${escaped})`, 'ig')).filter(Boolean).map(part => ({ text: part, marked: part.toLowerCase() === keyword.toLowerCase() })) }
watch(() => route.query, value => { const page = Math.max(Number(value.page) || 1, 1); if (page !== query.page) query.page = page }, { deep: true })
</script>

<style scoped lang="scss">
.resource-search-page { min-height:100%; background:#f6f7fb; }.resource-shell { max-width:1180px; margin:0 auto; padding:28px 16px 44px; }.search-hero { padding:8px 0 26px; text-align:center; }.brand-line { display:flex; justify-content:center; align-items:center; gap:8px; color:#20232a; font-size:20px; }.brand-line .el-icon { color:var(--el-color-primary); }.brand-line span { padding-left:8px; border-left:1px solid var(--el-border-color); color:var(--el-text-color-secondary); font-size:13px; font-weight:400; }.search-box { max-width:700px; margin:22px auto 0; }.search-box :deep(.el-input-group__append) { padding:0; overflow:hidden; }.search-box :deep(.el-input-group__append .el-button) { height:40px; border-radius:0; }.filter-panel { padding:18px 22px; background:#fff; border:1px solid #ebeef5; border-radius:10px; box-shadow:0 3px 12px rgba(0,0,0,.035); }.platforms,.filters { display:flex; align-items:center; flex-wrap:wrap; gap:10px; }.filters { margin-top:16px; padding-top:16px; border-top:1px solid #f0f1f4; }.filter-label { width:58px; color:var(--el-text-color-regular); font-size:14px; }.platform { display:inline-flex; align-items:center; gap:5px; height:32px; padding:0 12px; border:1px solid var(--el-border-color); border-radius:5px; background:#fff; color:var(--el-text-color-regular); cursor:pointer; }.platform:hover,.platform.active { border-color:var(--el-color-primary); color:var(--el-color-primary); background:var(--el-color-primary-light-9); }.platform.disabled { cursor:not-allowed; opacity:.45; }.filters :deep(.el-select) { width:132px; }.result-section { padding-top:25px; scroll-margin-top:16px; }.result-heading { display:flex; justify-content:space-between; align-items:center; margin:0 2px 14px; }.result-heading strong { color:#26272b; font-size:16px; }.result-heading strong + span { margin-left:10px; color:var(--el-text-color-secondary); font-size:13px; }.result-hint { color:#9aa1ad; font-size:12px; }.resource-list { display:grid; gap:16px; }.resource-card { display:grid; grid-template-columns:46px minmax(0,1fr) auto; gap:15px; padding:20px 22px; border:1px solid #ebeef5; border-radius:10px; background:#fff; cursor:pointer; box-shadow:0 3px 12px rgba(0,0,0,.025); transition:.18s ease; }.resource-card:hover { border-color:var(--el-color-primary-light-5); box-shadow:0 8px 22px rgba(0,0,0,.08); }.resource-icon { display:grid; place-items:center; width:44px; height:44px; border-radius:8px; font-size:24px; }.resource-icon.folder { color:#d99723; background:#fff7e7; }.resource-icon.file { color:var(--el-color-primary); background:var(--el-color-primary-light-9); }.resource-main { min-width:0; }.resource-main h2 { overflow:hidden; margin:0; color:#303133; font-size:16px; font-weight:600; line-height:24px; text-overflow:ellipsis; white-space:nowrap; }.resource-main mark { padding:0; color:var(--el-color-primary); background:transparent; }.metadata { display:flex; align-items:center; flex-wrap:wrap; gap:10px; margin-top:8px; color:#8a919f; font-size:12px; }.metadata .status { color:#909399; }.file-preview { display:grid; gap:5px; margin:14px 0 0; padding:10px 12px; border-radius:6px; background:#fafbfc; list-style:none; }.file-preview li { display:flex; align-items:center; min-width:0; gap:6px; color:#606266; font-size:13px; }.file-preview li .el-icon { flex:none; color:#a8b0bd; }.file-preview li.directory { color:#4d5560; font-weight:600; }.file-preview li span { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }.file-preview li em { margin-left:auto; color:#a3a6ad; font-style:normal; white-space:nowrap; }.file-preview .more-files { padding-left:20px; color:#a3a6ad; }.card-action { display:flex; align-items:center; align-self:center; gap:4px; color:var(--el-color-primary); font-size:13px; white-space:nowrap; }.result-pagination { display:flex; justify-content:center; align-items:center; gap:16px; flex-wrap:wrap; margin-top:26px; color:#8a919f; font-size:13px; }.result-pagination :deep(.pagination-container) { margin-top:0; }.result-pagination :deep(.el-pagination) { justify-content:center; }.page-total { color:#606266; }
@media (max-width:768px) { .resource-shell { padding:18px 10px 30px; }.filter-panel { padding:15px; }.filter-label { width:100%; }.filters :deep(.el-select) { width:calc(50% - 5px); }.resource-card { grid-template-columns:38px minmax(0,1fr); padding:16px; gap:11px; }.resource-icon { width:38px; height:38px; }.card-action { grid-column:2; justify-self:start; }.result-heading { align-items:flex-start; gap:8px; flex-direction:column; }.result-pagination { gap:7px; }.page-total { display:none; } }
</style>
