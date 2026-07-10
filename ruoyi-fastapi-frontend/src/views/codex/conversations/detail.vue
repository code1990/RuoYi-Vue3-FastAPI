<template>
  <div class="app-container codex-detail-page">
    <el-card class="summary-card" shadow="never" v-loading="loading">
      <div class="summary-head">
        <div>
          <div class="summary-kicker">Conversation</div>
          <h1 class="summary-title">{{ readModel.conversation?.title || conversationId }}</h1>
          <div class="summary-meta">
            <span>ID: {{ readModel.conversation?.conversationId || conversationId }}</span>
            <span>Workspace: {{ readModel.conversation?.workspaceId || '--' }}</span>
            <span>Thread: {{ readModel.conversation?.threadId || '--' }}</span>
          </div>
        </div>
        <div class="summary-actions">
          <el-tag :type="tagTypeMap[statusTone]" size="large">{{ readModel.currentState?.status || '--' }}</el-tag>
          <el-tag :type="streamState.connected ? 'success' : 'info'" effect="plain">
            {{ streamState.label }}
          </el-tag>
          <el-button type="primary" icon="Refresh" :loading="loading" @click="loadDetail">Refresh</el-button>
        </div>
      </div>

      <div class="summary-grid">
        <div class="metric-card">
          <div class="metric-label">Phase</div>
          <div class="metric-value">{{ readModel.currentState?.phase || '--' }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Active Tasks</div>
          <div class="metric-value">{{ formatCount(readModel.currentState?.activeTaskCount) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Messages</div>
          <div class="metric-value">{{ formatCount(readModel.historySummary?.messageCount) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Last Active</div>
          <div class="metric-value metric-time">{{ formatMsTime(readModel.currentState?.lastActivityAtMs) }}</div>
        </div>
      </div>
    </el-card>

    <el-card shadow="never">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="Overview" name="overview">
          <div class="overview-grid">
            <el-card shadow="hover">
              <template #header>Conversation</template>
              <div class="kv-list">
                <div class="kv-item"><span>Title</span><span>{{ readModel.conversation?.title || '--' }}</span></div>
                <div class="kv-item"><span>Status</span><span>{{ readModel.conversation?.status || '--' }}</span></div>
                <div class="kv-item"><span>Operator</span><span>{{ readModel.conversation?.operator || '--' }}</span></div>
                <div class="kv-item"><span>Created</span><span>{{ formatMsTime(readModel.conversation?.createdAtMs) }}</span></div>
                <div class="kv-item"><span>Last Error</span><span>{{ readModel.conversation?.lastError || '--' }}</span></div>
              </div>
            </el-card>
            <el-card shadow="hover">
              <template #header>Current State</template>
              <div class="kv-list">
                <div class="kv-item"><span>Phase</span><span>{{ readModel.currentState?.phase || '--' }}</span></div>
                <div class="kv-item"><span>Latest Task</span><span>{{ readModel.currentState?.latestTaskId || '--' }}</span></div>
                <div class="kv-item"><span>Latest Event</span><span>{{ readModel.currentState?.latestEventType || '--' }}</span></div>
                <div class="kv-item"><span>Turn</span><span>{{ readModel.currentState?.currentTurnId || '--' }}</span></div>
                <div class="kv-item"><span>Has Error</span><span>{{ readModel.currentState?.hasError ? 'yes' : 'no' }}</span></div>
              </div>
            </el-card>
            <el-card shadow="hover">
              <template #header>History Summary</template>
              <div class="kv-list">
                <div class="kv-item"><span>Messages</span><span>{{ formatCount(readModel.historySummary?.messageCount) }}</span></div>
                <div class="kv-item"><span>Events</span><span>{{ formatCount(readModel.historySummary?.eventCount) }}</span></div>
                <div class="kv-item"><span>Tasks</span><span>{{ formatCount(readModel.historySummary?.taskCount) }}</span></div>
                <div class="kv-item"><span>Started</span><span>{{ formatMsTime(readModel.historySummary?.startedAtMs) }}</span></div>
                <div class="kv-item"><span>Finished</span><span>{{ formatMsTime(readModel.historySummary?.finishedAtMs) }}</span></div>
              </div>
            </el-card>
          </div>
        </el-tab-pane>

        <el-tab-pane :label="`Messages (${messages.length})`" name="messages">
          <div v-if="messages.length" class="timeline-list">
            <el-card v-for="(item, index) in messages" :key="`${item.turnId || 'msg'}-${index}`" shadow="hover" class="stream-card">
              <div class="stream-header">
                <div>
                  <strong>{{ item.role || '--' }}</strong>
                  <span class="stream-type">{{ item.messageType || '--' }}</span>
                </div>
                <span>{{ formatMsTime(item.createdAtMs) }}</span>
              </div>
              <pre class="stream-content">{{ item.content || '--' }}</pre>
              <el-collapse>
                <el-collapse-item title="payloadJson">
                  <pre class="json-block">{{ toPrettyJson(parsePayloadJson(item.payloadJson)) }}</pre>
                </el-collapse-item>
              </el-collapse>
            </el-card>
          </div>
          <el-empty v-else description="No messages" />
        </el-tab-pane>

        <el-tab-pane :label="`Tasks (${tasks.length})`" name="tasks">
          <el-table :data="tasks">
            <el-table-column label="Task ID" prop="taskId" min-width="180" show-overflow-tooltip />
            <el-table-column label="Status" prop="status" width="120" />
            <el-table-column label="Created Thread" width="120">
              <template #default="{ row }">
                {{ row.createdThread ? 'yes' : 'no' }}
              </template>
            </el-table-column>
            <el-table-column label="Submitted" min-width="180">
              <template #default="{ row }">
                {{ formatMsTime(row.submittedAtMs) }}
              </template>
            </el-table-column>
            <el-table-column label="Completed" min-width="180">
              <template #default="{ row }">
                {{ formatMsTime(row.completedAtMs) }}
              </template>
            </el-table-column>
            <el-table-column label="Last Error" prop="lastError" min-width="240" show-overflow-tooltip />
          </el-table>
        </el-tab-pane>

        <el-tab-pane :label="`Events (${events.length})`" name="events">
          <el-table :data="events">
            <el-table-column label="Event Type" prop="eventType" min-width="180" show-overflow-tooltip />
            <el-table-column label="Event Status" prop="eventStatus" width="140" />
            <el-table-column label="Turn" prop="turnId" min-width="140" show-overflow-tooltip />
            <el-table-column label="Created" min-width="180">
              <template #default="{ row }">
                {{ formatMsTime(row.createdAtMs) }}
              </template>
            </el-table-column>
            <el-table-column label="payloadJson" min-width="320">
              <template #default="{ row }">
                <pre class="json-inline">{{ toPrettyJson(parsePayloadJson(row.payloadJson)) }}</pre>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="Raw JSON" name="raw">
          <pre class="json-block">{{ rawJson }}</pre>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup name="CodexConversationDetail">
import { getConversationReadModel } from '@/api/codex/conversation'
import { formatCount, formatMsTime, getStatusTone, openCodexStream, parsePayloadJson, toPrettyJson } from '@/utils/codex'

const route = useRoute()
const { proxy } = getCurrentInstance()

const conversationId = computed(() => route.params.conversationId)
const loading = ref(false)
const activeTab = ref('overview')
const readModel = ref(createEmptyReadModel())
const streamAbortController = ref(null)
const pollingTimer = ref(null)
const streamState = reactive({
  connected: false,
  label: 'disconnected'
})

const tagTypeMap = {
  info: 'info',
  warning: 'warning',
  success: 'success',
  danger: 'danger'
}

const messages = computed(() => readModel.value.messages || [])
const tasks = computed(() => readModel.value.tasks || [])
const events = computed(() => readModel.value.events || [])
const statusTone = computed(() => getStatusTone(readModel.value.currentState?.status, readModel.value.currentState?.hasError))
const rawJson = computed(() => toPrettyJson(readModel.value))

async function loadDetail() {
  loading.value = true
  try {
    const response = await getConversationReadModel(conversationId.value)
    applyReadModel(response.data || createEmptyReadModel())
  } finally {
    loading.value = false
  }
}

function applyReadModel(data) {
  readModel.value = {
    conversation: data.conversation || {},
    currentState: data.currentState || {},
    historySummary: data.historySummary || {},
    messages: Array.isArray(data.messages) ? data.messages : [],
    events: Array.isArray(data.events) ? data.events : [],
    tasks: Array.isArray(data.tasks) ? data.tasks : []
  }
}

async function startRealtime() {
  stopRealtime()
  streamAbortController.value = new AbortController()
  streamState.connected = false
  streamState.label = 'connecting'

  try {
    await openCodexStream({
      conversationId: conversationId.value,
      pollIntervalMs: 1000,
      signal: streamAbortController.value.signal,
      onData: handleStreamEvent
    })
  } catch (error) {
    if (error.name !== 'AbortError') {
      streamState.connected = false
      streamState.label = 'polling'
      startPolling()
    }
  }
}

function handleStreamEvent(payload) {
  if (payload.event === 'snapshot' || payload.event === 'update') {
    applyReadModel(payload.data || createEmptyReadModel())
    streamState.connected = true
    streamState.label = 'sse'
    stopPolling()
    return
  }

  if (payload.event === 'ping') {
    streamState.connected = true
    streamState.label = 'ping'
  }
}

function startPolling() {
  stopPolling()
  const run = () => loadDetail().catch(() => {
    proxy?.$modal?.msgWarning('Conversation polling failed')
  })

  run()
  pollingTimer.value = window.setInterval(() => {
    if (document.hidden) {
      return
    }
    run()
  }, document.hasFocus() ? 3000 : 10000)
}

function stopRealtime() {
  streamAbortController.value?.abort?.()
  streamAbortController.value = null
  stopPolling()
}

function stopPolling() {
  if (pollingTimer.value) {
    window.clearInterval(pollingTimer.value)
    pollingTimer.value = null
  }
}

function createEmptyReadModel() {
  return {
    conversation: {},
    currentState: {},
    historySummary: {},
    messages: [],
    events: [],
    tasks: []
  }
}

onMounted(async () => {
  await loadDetail()
  startRealtime()
})

onBeforeUnmount(() => {
  stopRealtime()
})
</script>

<style scoped lang="scss">
.codex-detail-page {
  background:
    radial-gradient(circle at top left, rgba(20, 184, 166, 0.08), transparent 20%),
    linear-gradient(180deg, #f8fbff 0%, #f4f7fb 100%);
}

.summary-card,
:deep(.el-card) {
  border-radius: 20px;
}

.summary-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.summary-kicker {
  color: #0f766e;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.summary-title {
  margin: 6px 0 10px;
  color: #0f172a;
  font-size: 30px;
}

.summary-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  color: #64748b;
  font-size: 13px;
}

.summary-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-top: 18px;
}

.metric-card {
  padding: 16px 18px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.88);
}

.metric-label {
  color: #64748b;
  font-size: 12px;
}

.metric-value {
  margin-top: 8px;
  color: #0f172a;
  font-size: 24px;
  font-weight: 700;
}

.metric-time {
  font-size: 18px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.kv-list {
  display: grid;
  gap: 12px;
}

.kv-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 10px;
  border-bottom: 1px dashed rgba(148, 163, 184, 0.22);
  color: #334155;
}

.timeline-list {
  display: grid;
  gap: 14px;
}

.stream-card {
  border-radius: 18px;
}

.stream-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
  color: #475569;
}

.stream-type {
  margin-left: 10px;
  color: #0f766e;
}

.stream-content,
.json-block,
.json-inline {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: Consolas, Monaco, monospace;
}

.json-block,
.json-inline {
  padding: 12px;
  border-radius: 12px;
  background: #0f172a;
  color: #e2e8f0;
}

.json-inline {
  max-height: 180px;
  overflow: auto;
}

@media (max-width: 992px) {
  .summary-grid,
  .overview-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .summary-head {
    flex-direction: column;
  }

  .summary-grid,
  .overview-grid {
    grid-template-columns: 1fr;
  }
}
</style>
