<template>
  <div class="app-container resource-search-page">
    <main class="resource-shell">
      <section class="search-hero">
        <div class="brand-line"><el-icon><CollectionTag /></el-icon><strong>网盘资源搜索</strong><span>静态页面演示</span></div>
        <div class="search-box"><el-select v-model="inputKeyword" size="large" filterable clearable placeholder="选择或筛选主题" @change="search"><template #prefix><el-icon><Search /></el-icon></template><el-option v-for="topic in topicOptions" :key="topic" :label="topic" :value="topic" /></el-select></div>
      </section>

      <section class="filter-panel">
        <div class="filters"><span class="filter-label">筛选:</span><el-select v-model="filters.mode" placeholder="模式" @change="resetPage"><el-option label="系统默认" value="default" /><el-option label="精确搜索" value="exact" /><el-option label="模糊搜索" value="fuzzy" /></el-select><el-select v-model="filters.ext" placeholder="文件类型" @change="resetPage"><el-option label="全部类型" value="" /><el-option label="文件夹" value="folder" /><el-option label="视频" value="mp4" /><el-option label="音乐" value="music" /><el-option label="图片" value="image" /><el-option label="文档" value="document" /><el-option label="软件" value="software" /><el-option label="压缩包" value="archive" /><el-option label="BT种子" value="torrent" /></el-select><el-select v-model="filters.size" placeholder="文件大小" @change="resetPage"><el-option label="全部大小" value="" /><el-option label="小于20MB" value="tiny" /><el-option label="20MB-200MB" value="small" /><el-option label="200MB-2GB" value="middle" /><el-option label="大于2GB" value="large" /></el-select><el-select v-model="filters.time" placeholder="文件时间" @change="resetPage"><el-option label="全部时间" value="" /><el-option label="最近一周" value="week" /><el-option label="最近一月" value="month" /><el-option label="最近半年" value="half-year" /><el-option label="最近一年" value="year" /></el-select><el-select v-model="filters.source" placeholder="百度网盘" @change="setSource"><el-option label="全部来源" value="" /><el-option v-for="platform in platforms" :key="platform.value" :label="platform.label" :value="platform.value" /></el-select><el-button link type="primary" :disabled="!hasFilters" @click="clearFilters">清除</el-button></div>
        <div class="platforms"><span class="filter-label">网盘:</span><button v-for="platform in platforms" :key="platform.value" class="platform" :class="{ active: query.resType === platform.value }" @click="setPlatform(platform.value)"><el-icon><FolderOpened /></el-icon>{{ platform.label }}</button></div>
      </section>

      <section ref="resultSection" class="result-section">
        <div class="result-heading"><div><strong v-if="query.kw">“{{ query.kw }}”的搜索结果</strong><strong v-else>资源搜索</strong><span>共 {{ total.toLocaleString() }} 个结果</span></div><span class="result-hint">当前为静态数据演示</span></div>
        <el-empty v-if="!query.kw" description="请从上方下拉框选择主题" />
        <el-empty v-else-if="!loading && !rows.length" description="未找到相关资源，可更换主题或清除筛选" />
        <div v-else v-loading="loading" class="resource-list">
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
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowRight, CollectionTag, Document, FolderOpened, Search } from '@element-plus/icons-vue'
import { listResourceTopics, searchResources } from '@/api/feizhu/resource'

const route = useRoute(), router = useRouter(), resultSection = ref()
const inputKeyword = ref(typeof route.query.kw === 'string' ? route.query.kw : '')
const query = reactive({ kw: inputKeyword.value, page: Math.max(Number(route.query.page) || 1, 1), resType: typeof route.query.resType === 'string' ? route.query.resType : 'baidu' })
const filters = reactive({ mode: 'default', ext: '', size: '', time: '', source: 'baidu' })
const pageSize = 15, platforms = [{ value: 'baidu', label: '百度网盘' }, { value: 'aliyun', label: '阿里网盘' }, { value: 'quark', label: '夸克网盘' }, { value: 'xunlei', label: '迅雷网盘' }]
const topicOptions = ref([]), rows = ref([]), total = ref(0), loading = ref(false)
const hasFilters = computed(() => filters.mode !== 'default' || Boolean(filters.ext || filters.size || filters.time) || filters.source !== 'baidu')
const pageCount = computed(() => Math.max(Math.ceil(total.value / pageSize), 1))
async function load() { if (!query.kw) { rows.value = []; total.value = 0; return }; loading.value = true; try { const data = await searchResources({ kw: query.kw, page: query.page, line: pageSize, resType: filters.source || undefined, fileType: filters.ext || undefined, size: filters.size || undefined, time: filters.time || undefined }); rows.value = data.resources.map(item => item.res); total.value = data.total } finally { loading.value = false } }
function syncRoute() { router.replace({ query: { kw: query.kw || undefined, page: query.page > 1 ? String(query.page) : undefined, resType: query.resType } }) }
function search() { query.kw = inputKeyword.value || ''; query.page = 1; syncRoute(); load() }
function resetPage() { query.page = 1; syncRoute(); load() }
function setPlatform(value) { query.resType = value; filters.source = value; resetPage() }
function setSource() { if (filters.source) query.resType = filters.source; resetPage() }
function clearFilters() { Object.assign(filters, { mode: 'default', ext: '', size: '', time: '', source: 'baidu' }); resetPage() }
function changePage({ page }) { query.page = page; syncRoute(); load(); resultSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' }) }
function openDetail(item) { router.push({ path: '/feizhu/resource-detail', query: { id: item.id, kw: query.kw || undefined } }) }
function platformName(type) { return platforms.find(item => item.value === type)?.label || type }
function formatSize(value) { const size = Number(value); if (!Number.isFinite(size) || size <= 0) return '--'; const units = ['B', 'KB', 'MB', 'GB', 'TB']; const index = Math.min(Math.floor(Math.log(size) / Math.log(1024)), units.length - 1); return `${Math.floor(size / 1024 ** index)}${units[index]}` }
function highlighted(text) { const keyword = query.kw.trim(); if (!keyword) return [{ text, marked: false }]; const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); return text.split(new RegExp(`(${escaped})`, 'ig')).filter(Boolean).map(part => ({ text: part, marked: part.toLowerCase() === keyword.toLowerCase() })) }
watch(() => route.query, value => { const page = Math.max(Number(value.page) || 1, 1); if (page !== query.page) { query.page = page; load() } }, { deep: true })
onMounted(async () => { topicOptions.value = await listResourceTopics(); load() })
</script>

<style scoped lang="scss">
.resource-search-page { min-height:100%; background:#f6f7fb; }.resource-shell { max-width:1180px; margin:0 auto; padding:28px 16px 44px; }.search-hero { padding:8px 0 26px; text-align:center; }.brand-line { display:flex; justify-content:center; align-items:center; gap:8px; color:#20232a; font-size:20px; }.brand-line .el-icon { color:var(--el-color-primary); }.brand-line span { padding-left:8px; border-left:1px solid var(--el-border-color); color:var(--el-text-color-secondary); font-size:13px; font-weight:400; }.search-box { max-width:700px; margin:22px auto 0; }.search-box :deep(.el-select) { width:100%; }.filter-panel { padding:18px 22px; background:#fff; border:1px solid #ebeef5; border-radius:10px; box-shadow:0 3px 12px rgba(0,0,0,.035); }.platforms,.filters { display:flex; align-items:center; flex-wrap:wrap; gap:10px; }.platforms { margin-top:16px; padding-top:16px; border-top:1px solid #f0f1f4; }.filter-label { width:58px; color:var(--el-text-color-regular); font-size:14px; }.platform { display:inline-flex; align-items:center; gap:5px; height:32px; padding:0 12px; border:1px solid var(--el-border-color); border-radius:5px; background:#fff; color:var(--el-text-color-regular); cursor:pointer; }.platform:hover,.platform.active { border-color:var(--el-color-primary); color:var(--el-color-primary); background:var(--el-color-primary-light-9); }.filters :deep(.el-select) { width:132px; }.result-section { padding-top:25px; scroll-margin-top:16px; }.result-heading { display:flex; justify-content:space-between; align-items:center; margin:0 2px 14px; }.result-heading strong { color:#26272b; font-size:16px; }.result-heading strong + span { margin-left:10px; color:var(--el-text-color-secondary); font-size:13px; }.result-hint { color:#9aa1ad; font-size:12px; }.resource-list { display:grid; gap:16px; }.resource-card { display:grid; grid-template-columns:46px minmax(0,1fr) auto; gap:15px; padding:20px 22px; border:1px solid #ebeef5; border-radius:10px; background:#fff; cursor:pointer; box-shadow:0 3px 12px rgba(0,0,0,.025); transition:.18s ease; }.resource-card:hover { border-color:var(--el-color-primary-light-5); box-shadow:0 8px 22px rgba(0,0,0,.08); }.resource-icon { display:grid; place-items:center; width:44px; height:44px; border-radius:8px; font-size:24px; }.resource-icon.folder { color:#d99723; background:#fff7e7; }.resource-icon.file { color:var(--el-color-primary); background:var(--el-color-primary-light-9); }.resource-main { min-width:0; }.resource-main h2 { overflow:hidden; margin:0; color:#303133; font-size:16px; font-weight:600; line-height:24px; text-overflow:ellipsis; white-space:nowrap; }.resource-main mark { padding:0; color:var(--el-color-primary); background:transparent; }.metadata { display:flex; align-items:center; flex-wrap:wrap; gap:10px; margin-top:8px; color:#8a919f; font-size:12px; }.metadata .status { color:#909399; }.file-preview { display:grid; gap:5px; margin:14px 0 0; padding:10px 12px; border-radius:6px; background:#fafbfc; list-style:none; }.file-preview li { display:flex; align-items:center; min-width:0; gap:6px; color:#606266; font-size:13px; }.file-preview li .el-icon { flex:none; color:#a8b0bd; }.file-preview li.directory { color:#4d5560; font-weight:600; }.file-preview li span { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }.file-preview li em { margin-left:auto; color:#a3a6ad; font-style:normal; white-space:nowrap; }.file-preview .more-files { padding-left:20px; color:#a3a6ad; }.card-action { display:flex; align-items:center; align-self:center; gap:4px; color:var(--el-color-primary); font-size:13px; white-space:nowrap; }.result-pagination { display:flex; justify-content:center; align-items:center; gap:16px; flex-wrap:wrap; margin-top:26px; color:#8a919f; font-size:13px; }.result-pagination :deep(.pagination-container) { margin-top:0; }.result-pagination :deep(.el-pagination) { justify-content:center; }.page-total { color:#606266; }
@media (max-width:768px) { .resource-shell { padding:18px 10px 30px; }.filter-panel { padding:15px; }.filter-label { width:100%; }.filters :deep(.el-select) { width:calc(50% - 5px); }.resource-card { grid-template-columns:38px minmax(0,1fr); padding:16px; gap:11px; }.resource-icon { width:38px; height:38px; }.card-action { grid-column:2; justify-self:start; }.result-heading { align-items:flex-start; gap:8px; flex-direction:column; }.result-pagination { gap:7px; }.page-total { display:none; } }
</style>
