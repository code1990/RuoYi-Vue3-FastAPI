<template>
  <div class="app-container file-detail-page">
    <el-card shadow="never" class="filter-card">
      <div class="page-heading"><div><h2>文件明细</h2><p>按关键字、主题和资源属性组合检索</p></div><el-input v-model="filters.keyword" clearable placeholder="文件名、主题或链接" class="search-input" @keyup.enter="search"><template #append><el-button icon="Search" @click="search">查询</el-button></template></el-input></div>
      <div v-if="activeFilters.length" class="selected-row"><strong>已选条件：</strong><el-tag v-for="item in activeFilters" :key="item.key" closable @close="removeFilter(item)">{{ item.label }}</el-tag><el-button link type="primary" @click="reset">清空条件</el-button></div>
      <div class="filter-list">
        <FilterRow label="主题"><el-check-tag :checked="!filters.topics.length" @change="setAll('topics')">不限</el-check-tag><el-check-tag v-for="item in options.topics" :key="item" :checked="filters.topics.includes(item)" @change="toggle('topics', item)">{{ item }}</el-check-tag></FilterRow>
        <FilterRow label="文件类型"><el-check-tag :checked="!filters.exts.length" @change="setAll('exts')">不限</el-check-tag><el-check-tag v-for="item in options.exts" :key="item" :checked="filters.exts.includes(item)" @change="toggle('exts', item)">{{ item }}</el-check-tag></FilterRow>
        <FilterRow v-if="showMore" label="资源类别"><el-check-tag :checked="filters.category === null" @change="setOne('category', null)">不限</el-check-tag><el-check-tag v-for="item in options.categories" :key="item" :checked="filters.category === item" @change="setOne('category', item)">{{ categoryLabel(item) }}</el-check-tag></FilterRow>
        <FilterRow v-if="showMore" label="链接类型"><el-check-tag :checked="!filters.resourceType" @change="setOne('resourceType', '')">不限</el-check-tag><el-check-tag v-for="item in options.types" :key="item" :checked="filters.resourceType === item" @change="setOne('resourceType', item)">{{ typeLabel(item) }}</el-check-tag></FilterRow>
        <FilterRow v-if="showMore" label="资源状态"><el-check-tag :checked="!filters.valid" @change="setOne('valid', '')">不限</el-check-tag><el-check-tag v-for="item in options.valids" :key="item" :checked="filters.valid === item" @change="setOne('valid', item)">{{ validLabel(item) }}</el-check-tag></FilterRow>
        <FilterRow v-if="showMore" label="提取码"><el-check-tag :checked="!filters.haspwd" @change="setOne('haspwd', '')">不限</el-check-tag><el-check-tag v-for="item in options.haspwds" :key="item" :checked="filters.haspwd === item" @change="setOne('haspwd', item)">{{ haspwdLabel(item) }}</el-check-tag></FilterRow>
      </div>
      <div class="more-row"><el-button link type="primary" @click="showMore = !showMore">{{ showMore ? '收起筛选' : '更多筛选' }}<el-icon><ArrowUp v-if="showMore" /><ArrowDown v-else /></el-icon></el-button></div>
    </el-card>

    <el-card shadow="never" class="table-card"><div class="table-title"><span>文件列表</span><el-tag type="info">共 {{ total }} 条</el-tag></div><el-table v-loading="loading" :data="rows" border row-key="id" max-height="calc(100vh - 430px)"><el-table-column type="index" label="#" width="56" /><el-table-column prop="topic" label="主题" min-width="140" show-overflow-tooltip /><el-table-column prop="filename" label="文件名" min-width="240" show-overflow-tooltip /><el-table-column prop="size" label="大小" width="110" /><el-table-column prop="ext" label="类型" width="100" show-overflow-tooltip /><el-table-column prop="valid" label="状态" width="100"><template #default="{ row }"><el-tag size="small" :type="row.valid === '1' ? 'success' : 'info'">{{ row.valid === '1' ? '有效' : '无效' }}</el-tag></template></el-table-column><el-table-column label="提取码" width="130"><template #default="{ row }"><span>{{ row.pwd || '-' }}</span><el-button v-if="row.pwd" link type="primary" icon="CopyDocument" @click="copy(row.pwd)" /></template></el-table-column><el-table-column prop="utime" label="更新时间" width="170" /><el-table-column label="操作" width="100" fixed="right"><template #default="{ row }"><el-button link type="primary" :disabled="!row.url" @click="open(row.url)">打开</el-button><el-button link type="primary" :disabled="!row.url" icon="CopyDocument" @click="copy(row.url)" /></template></el-table-column></el-table><pagination v-show="total > 0" v-model:page="filters.pageNum" v-model:limit="filters.pageSize" :total="total" @pagination="load" /></el-card>
  </div>
</template>

<script setup name="FeizhuFileDetail">
import { computed, h, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getFileDetailOptions, listFileDetails } from '@/api/feizhu/fileDetail'

const FilterRow = (_, { slots }) => h('div', { class: 'filter-row' }, [h('strong', { class: 'filter-label' }, _.label), h('div', { class: 'filter-values' }, slots.default())])
const categoryLabel = value => ({ 0: '其他', 1: '视频', 2: '音频', 3: '图片', 4: '文档', 5: '程序', 6: '其他/目录', 7: '种子' }[value] || '其他')
const typeLabel = value => ({ baidu: '百度网盘' }[value] || value)
const validLabel = value => value === '1' ? '有效' : '无效'
const haspwdLabel = value => value === '1' ? '有提取码' : '无提取码'
const loading = ref(false), rows = ref([]), total = ref(0), showMore = ref(false)
const options = reactive({ keywords: [], topics: [], exts: [], categories: [], types: [], valids: [], haspwds: [] })
const filters = reactive({ pageNum: 1, pageSize: 20, keywordIds: [], topics: [], exts: [], category: null, resourceType: '', valid: '', haspwd: '', keyword: '' })
const activeFilters = computed(() => [
  ...filters.keywordIds.map(id => ({ key: `keyword-${id}`, field: 'keywordIds', value: id, label: `关键字：${options.keywords.find(item => item.id === id)?.name || id}` })),
  ...filters.topics.map(value => ({ key: `topic-${value}`, field: 'topics', value, label: `主题：${value}` })),
  ...filters.exts.map(value => ({ key: `ext-${value}`, field: 'exts', value, label: `类型：${value}` })),
  ...(filters.category === null ? [] : [{ key: 'category', field: 'category', label: `类别：${categoryLabel(filters.category)}` }]),
  ...(['resourceType', 'valid', 'haspwd', 'keyword'].filter(field => filters[field]).map(field => ({ key: field, field, label: `${{ resourceType: '链接类型', valid: '资源状态', haspwd: '提取码', keyword: '搜索' }[field]}：${field === 'resourceType' ? typeLabel(filters[field]) : field === 'valid' ? validLabel(filters[field]) : field === 'haspwd' ? haspwdLabel(filters[field]) : filters[field]}` })))
])
const params = () => ({ ...filters, keywordIds: filters.keywordIds.join(',') || undefined, topics: filters.topics.join(',') || undefined, exts: filters.exts.join(',') || undefined, category: filters.category ?? undefined, resourceType: filters.resourceType || undefined, valid: filters.valid || undefined, haspwd: filters.haspwd || undefined, keyword: filters.keyword || undefined })
async function loadOptions() { Object.assign(options, (await getFileDetailOptions({ keywordIds: filters.keywordIds.join(',') || undefined })).data || {}) }
async function load() { loading.value = true; try { const { data } = await listFileDetails(params()); rows.value = data?.rows || []; total.value = data?.total || 0 } finally { loading.value = false } }
function apply() { filters.pageNum = 1; load() }
function toggle(field, value) { filters[field] = filters[field].includes(value) ? filters[field].filter(item => item !== value) : [...filters[field], value]; if (field === 'keywordIds') { filters.topics = []; loadOptions().then(apply) } else apply() }
function setAll(field) { filters[field] = []; if (field === 'keywordIds') { filters.topics = []; loadOptions().then(apply) } else apply() }
function setOne(field, value) { filters[field] = value; apply() }
function removeFilter(item) { Array.isArray(filters[item.field]) ? filters[item.field] = filters[item.field].filter(value => value !== item.value) : filters[item.field] = item.field === 'category' ? null : ''; if (item.field === 'keywordIds') { filters.topics = []; loadOptions().then(apply) } else apply() }
function reset() { Object.assign(filters, { pageNum: 1, keywordIds: [], topics: [], exts: [], category: null, resourceType: '', valid: '', haspwd: '', keyword: '' }); loadOptions().then(load) }
function search() { apply() }
function copy(value) { navigator.clipboard.writeText(value).then(() => ElMessage.success('已复制')) }
function open(url) { window.open(url, '_blank', 'noopener,noreferrer') }
watch(() => filters.keywordIds.join(','), () => { if (filters.topics.some(topic => !options.topics.includes(topic))) filters.topics = filters.topics.filter(topic => options.topics.includes(topic)) })
loadOptions().then(load)
</script>

<style scoped>
.filter-card,.table-card { border-color: var(--el-border-color-lighter); }.table-card { margin-top: 16px; }.page-heading,.table-title,.selected-row,.filter-row,.more-row { display:flex; align-items:center; }.page-heading { justify-content:space-between; gap:24px; }.page-heading h2 { margin:0; font-size:20px; color:var(--el-text-color-primary); }.page-heading p { margin:6px 0 0; color:var(--el-text-color-secondary); font-size:13px; }.search-input { width:340px; }.selected-row { gap:8px; flex-wrap:wrap; padding:14px 0; margin:14px 0 2px; border-top:1px solid var(--el-border-color-lighter); }.selected-row strong,.filter-label { color:var(--el-text-color-regular); font-size:14px; font-weight:600; }.filter-list { border-top:1px solid var(--el-border-color-lighter); }.filter-row { min-height:46px; border-bottom:1px solid var(--el-border-color-lighter); align-items:flex-start; padding:10px 0; }.filter-label { flex:0 0 82px; line-height:26px; }.filter-values { display:flex; gap:8px; flex-wrap:wrap; }.filter-values :deep(.el-check-tag) { margin:0; line-height:26px; padding:0 9px; }.more-row { justify-content:center; padding-top:8px; }.more-row .el-icon { margin-left:4px; }.table-title { justify-content:space-between; margin-bottom:14px; font-weight:600; }.el-table :deep(.cell) { white-space:nowrap; }.el-button + .el-button { margin-left:6px; }
@media (max-width: 768px) { .page-heading { align-items:flex-start; flex-direction:column; }.search-input { width:100%; }.filter-label { flex-basis:68px; } }
</style>
