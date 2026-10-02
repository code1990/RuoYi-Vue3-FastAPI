<template>
  <div class="future-relation-page">
    <el-card shadow="never">
      <template #header>合约关联</template>
      <el-table v-loading="loading" :data="groups" border>
        <el-table-column label="品种" prop="groupName" min-width="100" />
        <el-table-column label="合约汇总详情" min-width="520"><template #default="{ row }"><div v-for="item in row.items" :key="item.linkId" class="relation-line"><el-tag :type="tagType(item.relationType)">{{ relationLabel(item.relationType) }}</el-tag> {{ contractName(item.sourceContract, item.marketCode, item.contractPrefix) }}（<span :class="rateClass(item.sourceChangeRate)">{{ percent(item.sourceChangeRate) }}</span>） → {{ contractName(item.relatedContract, item.relatedMarketCode, item.relatedContractPrefix) }}（<span :class="rateClass(item.relatedChangeRate)">{{ percent(item.relatedChangeRate) }}</span>）<span class="remark">{{ item.remark }}</span></div></template></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup name="FutureRelation">
import { computed, ref } from 'vue'
import { listFutureRelations } from '@/api/future/relation'

const loading = ref(false)
const rows = ref([])
const labels = { similar: '相似', positive: '正向', inverse: '反向' }
const groups = computed(() => Object.values(rows.value.reduce((result, item) => { (result[item.groupName] ||= { groupName: item.groupName, items: [] }).items.push(item); return result }, {})))

function contractName(name, market, prefix) { return name || `${market}/${prefix}` }
function percent(rate) { return rate === null || rate === undefined ? '--' : `${Number(rate).toFixed(2)}%` }
function rateClass(rate) { return Number(rate) > 0 ? 'rise' : Number(rate) < 0 ? 'fall' : '' }
function relationLabel(type) { return labels[type] || type }
function tagType(type) { return type === 'similar' ? 'danger' : type === 'inverse' ? 'primary' : 'warning' }
function getList() { loading.value = true; listFutureRelations().then(response => { rows.value = response.data || [] }).finally(() => { loading.value = false }) }

getList()
</script>

<style scoped>
.future-relation-page { padding: 20px; }
.relation-line { display: flex; align-items: center; gap: 8px; min-height: 32px; }.remark { color: #909399; }.rise { color: #f56c6c; }.fall { color: #67c23a; }
</style>
