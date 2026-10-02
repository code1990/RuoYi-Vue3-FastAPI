<template>
  <div class="future-relation-page">
    <el-card shadow="never">
      <template #header>合约关联</template>
      <el-table v-loading="loading" :data="rows" border>
        <el-table-column label="品种" prop="groupName" min-width="100" />
        <el-table-column label="类别" min-width="90"><template #default="{ row }"><el-tag :type="tagType(row.relationType)">{{ relationLabel(row.relationType) }}</el-tag></template></el-table-column>
        <el-table-column label="合约汇总详情" min-width="300"><template #default="{ row }">{{ contract(row.marketCode, row.contractPrefix) }} → {{ contract(row.relatedMarketCode, row.relatedContractPrefix) }}</template></el-table-column>
        <el-table-column label="状态" min-width="100"><template #default="{ row }"><el-tag type="warning">{{ row.reviewStatus === 'pending' ? '待验证' : row.reviewStatus }}</el-tag></template></el-table-column>
        <el-table-column label="说明" prop="remark" min-width="220" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup name="FutureRelation">
import { listFutureRelations } from '@/api/future/relation'

const loading = ref(false)
const rows = ref([])
const labels = { similar: '相似', positive: '正向', inverse: '反向' }

function contract(market, prefix) { return `${market}/${prefix}` }
function relationLabel(type) { return labels[type] || type }
function tagType(type) { return type === 'positive' ? 'success' : type === 'inverse' ? 'danger' : 'info' }
function getList() { loading.value = true; listFutureRelations().then(response => { rows.value = response.data || [] }).finally(() => { loading.value = false }) }

getList()
</script>

<style scoped>
.future-relation-page { padding: 20px; }
</style>
