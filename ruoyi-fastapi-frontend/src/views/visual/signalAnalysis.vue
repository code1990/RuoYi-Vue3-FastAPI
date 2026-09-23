<template>
  <div class="stat-page">
    <el-card shadow="never">
      <el-alert title="三表研究观察：原始统计、NM过滤统计、候选汇总；行业和概念来自股票池，缺失时留空。" type="info" :closable="false" show-icon />
      <el-form inline class="toolbar" @submit.prevent>
        <el-form-item label="统计表"><el-select v-model="query.table" style="width: 150px" @change="handleQuery"><el-option label="原始统计" value="raw" /><el-option label="NM过滤" value="filtered" /><el-option label="候选汇总" value="total" /></el-select></el-form-item>
        <el-form-item label="信号"><el-select v-model="query.signalName" clearable placeholder="全部" style="width: 140px" @change="handleQuery"><el-option v-for="name in signalNames" :key="name" :label="name" :value="name" /></el-select></el-form-item>
        <el-form-item label="股票"><el-input v-model="query.stockCode" maxlength="6" clearable style="width: 120px" @keyup.enter="handleQuery" /></el-form-item>
        <el-form-item v-if="query.table !== 'total'" label="年份"><el-input v-model="query.year" maxlength="4" clearable style="width: 100px" @keyup.enter="handleQuery" /></el-form-item>
        <el-button type="primary" :loading="loading" @click="handleQuery">查询</el-button>
      </el-form>
      <el-table v-loading="loading" :data="rows" border stripe height="650">
        <el-table-column label="交易日" prop="statYear" width="100" fixed="left"><template #default="{ row }">{{ row.statYear || '累计' }}</template></el-table-column>
        <el-table-column label="股票" min-width="125" fixed="left"><template #default="{ row }">{{ row.stockCode }} {{ row.stockName }}</template></el-table-column>
        <el-table-column label="行业" prop="industryName" min-width="110" fixed="left" />
        <el-table-column label="概念" prop="concept" min-width="180" fixed="left" />
        <el-table-column label="信号" prop="signalName" min-width="100" />
        <el-table-column label="样本数" width="90"><template #default="{ row }">{{ row.sampleCount ?? row.sampleCount2 ?? '-' }}</template></el-table-column>
        <el-table-column label="T+5达标率" width="105"><template #default="{ row }">{{ percent(row.winRate1) }}</template></el-table-column>
        <el-table-column label="T+10达标率" width="110"><template #default="{ row }">{{ percent(row.winRate2) }}</template></el-table-column>
        <el-table-column v-if="query.table === 'total'" label="过滤样本" prop="sampleCount2" width="100" />
      </el-table>
      <pagination v-show="total > 0" v-model:page="query.pageNum" v-model:limit="query.pageSize" :total="total" @pagination="load" />
    </el-card>
  </div>
</template>

<script setup>
import { listSignalAnalysis } from '@/api/stock/signalAnalysis'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const signalNames = ref([])
const query = reactive({ table: 'raw', signalName: '', stockCode: '', year: '', pageNum: 1, pageSize: 20 })

function percent(value) { return value == null ? '-' : `${(Number(value) * 100).toFixed(2)}%` }
async function load() {
  loading.value = true
  try {
    const response = await listSignalAnalysis({ ...query, year: query.year || undefined, signalName: query.signalName || undefined })
    rows.value = response.data.rows
    total.value = response.data.total
    signalNames.value = response.data.signalNames || []
  } finally { loading.value = false }
}
function handleQuery() { query.pageNum = 1; load() }
onMounted(load)
</script>

<style scoped>
.stat-page { padding: 20px; }
.toolbar { margin-top: 18px; }
</style>
