<template>
  <div class="app-container codex-page">
    <el-card class="hero-card" shadow="never">
      <div class="hero-header">
        <div>
          <p class="hero-kicker">Codex Monitor</p>
          <h1 class="hero-title">Conversation List</h1>
          <p class="hero-desc">Read live conversation summaries from the backend views API.</p>
        </div>
        <div class="hero-actions">
          <el-button type="primary" icon="Refresh" :loading="loading" @click="getList">Refresh</el-button>
        </div>
      </div>
    </el-card>

    <el-form ref="queryRef" :model="queryParams" :inline="true" class="query-form" label-width="88px">
      <el-form-item label="Search" prop="searchText">
        <el-input v-model="queryParams.searchText" placeholder="title / preview / id" clearable style="width: 240px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="Workspace" prop="workspaceId">
        <el-input v-model="queryParams.workspaceId" placeholder="workspaceId" clearable style="width: 220px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="Operator" prop="operator">
        <el-input v-model="queryParams.operator" placeholder="operator" clearable style="width: 180px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item label="Status" prop="status">
        <el-select v-model="queryParams.status" placeholder="all" clearable style="width: 180px">
          <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="Has Error" prop="hasError">
        <el-select v-model="queryParams.hasError" placeholder="all" clearable style="width: 120px">
          <el-option label="true" :value="true" />
          <el-option label="false" :value="false" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">Search</el-button>
        <el-button icon="RefreshLeft" @click="resetQuery">Reset</el-button>
      </el-form-item>
    </el-form>

    <el-card shadow="never">
      <el-table v-loading="loading" :data="tableList" row-key="conversationId" @row-click="goDetail">
        <el-table-column label="Conversation" min-width="280">
          <template #default="{ row }">
            <div class="title-cell">
              <div class="title-main">{{ row.title || row.conversationId }}</div>
              <div class="title-sub">{{ row.conversationId }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Workspace" prop="workspaceId" min-width="120" show-overflow-tooltip />
        <el-table-column label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="tagTypeMap[row.statusTone]" effect="light">{{ row.status || '--' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Phase" prop="phase" min-width="160" show-overflow-tooltip />
        <el-table-column label="Error" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.hasError ? 'danger' : 'info'" effect="plain">{{ row.hasError ? 'yes' : 'no' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Tasks" prop="activeTaskCount" width="100" align="center" />
        <el-table-column label="Msg / Task" width="120" align="center">
          <template #default="{ row }">
            <span>{{ row.messageCount }} / {{ row.taskCount }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Latest Preview" min-width="260" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.latestMessagePreview || row.lastMessagePreview || '--' }}
          </template>
        </el-table-column>
        <el-table-column label="Last Active" width="180">
          <template #default="{ row }">
            {{ formatMsTime(row.lastActivityAtMs || row.updatedAtMs) }}
          </template>
        </el-table-column>
        <el-table-column label="Operator" prop="operator" width="120" />
        <el-table-column label="Action" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click.stop="goDetail(row)">Detail</el-button>
          </template>
        </el-table-column>
      </el-table>

      <pagination
        v-show="total > 0"
        :total="total"
        v-model:page="queryParams.pageNum"
        v-model:limit="queryParams.pageSize"
        @pagination="getList"
      />
    </el-card>
  </div>
</template>

<script setup name="CodexConversationList">
import { getConversationViewList } from '@/api/codex/conversation'
import { formatCount, formatMsTime, getStatusTone } from '@/utils/codex'

const router = useRouter()
const queryRef = ref()
const loading = ref(false)
const total = ref(0)
const tableList = ref([])

const statusOptions = [
  { label: 'running', value: 'running' },
  { label: 'completed', value: 'completed' },
  { label: 'failed', value: 'failed' },
  { label: 'waiting_input', value: 'waiting_input' },
  { label: 'waiting_approval', value: 'waiting_approval' },
  { label: 'streaming', value: 'streaming' }
]

const tagTypeMap = {
  info: 'info',
  warning: 'warning',
  success: 'success',
  danger: 'danger'
}

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  searchText: undefined,
  workspaceId: undefined,
  operator: undefined,
  status: undefined,
  hasError: undefined,
  orderByColumn: 'updatedAtMs',
  isAsc: 'desc'
})

function getList() {
  loading.value = true
  return getConversationViewList(queryParams)
    .then((response) => {
      tableList.value = (response.rows || []).map((item) => mapRow(item))
      total.value = response.total || 0
    })
    .finally(() => {
      loading.value = false
    })
}

function mapRow(item) {
  const conversation = item.conversation || {}
  const currentState = item.currentState || {}
  const historySummary = item.historySummary || {}

  return {
    conversationId: conversation.conversationId,
    title: conversation.title,
    workspaceId: conversation.workspaceId,
    threadId: conversation.threadId,
    operator: conversation.operator,
    lastMessagePreview: conversation.lastMessagePreview,
    updatedAtMs: conversation.updatedAtMs,
    status: currentState.status || conversation.status,
    phase: currentState.phase,
    hasError: !!currentState.hasError,
    activeTaskCount: formatCount(currentState.activeTaskCount),
    lastActivityAtMs: currentState.lastActivityAtMs,
    latestMessagePreview: historySummary.latestMessagePreview,
    messageCount: formatCount(historySummary.messageCount),
    taskCount: formatCount(historySummary.taskCount),
    statusTone: getStatusTone(currentState.status || conversation.status, currentState.hasError)
  }
}

function handleQuery() {
  queryParams.pageNum = 1
  getList()
}

function resetQuery() {
  queryRef.value?.resetFields()
  queryParams.pageNum = 1
  queryParams.pageSize = 10
  queryParams.orderByColumn = 'updatedAtMs'
  queryParams.isAsc = 'desc'
  getList()
}

function goDetail(row) {
  router.push(`/codex/conversations/${row.conversationId}`)
}

onMounted(() => {
  getList()
})
</script>

<style scoped lang="scss">
.codex-page {
  background:
    radial-gradient(circle at top left, rgba(14, 165, 233, 0.08), transparent 24%),
    linear-gradient(180deg, #f8fbff 0%, #f3f7ff 100%);
}

.hero-card,
.query-form,
:deep(.el-card) {
  border-radius: 20px;
}

.hero-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.hero-kicker {
  margin: 0 0 8px;
  color: #0f766e;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.hero-title {
  margin: 0;
  color: #0f172a;
  font-size: 30px;
}

.hero-desc {
  margin: 10px 0 0;
  color: #475569;
  line-height: 1.7;
}

.query-form {
  padding: 18px 18px 0;
  margin: 16px 0;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.04);
}

.title-cell {
  display: grid;
  gap: 4px;
}

.title-main {
  color: #0f172a;
  font-weight: 700;
}

.title-sub {
  color: #64748b;
  font-size: 12px;
}

@media (max-width: 768px) {
  .hero-header {
    flex-direction: column;
  }
}
</style>
