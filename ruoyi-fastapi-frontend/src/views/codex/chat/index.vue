<template>
  <div class="app-container codex-chat-page">
    <div class="page-shell">
      <aside class="sidebar-panel">
        <div class="sidebar-head">
          <div>
            <div class="eyebrow">Codex</div>
            <h2>Conversations</h2>
          </div>
          <div class="sidebar-actions">
            <el-button type="primary" @click="startDraftConversation">New</el-button>
            <el-button :icon="Refresh" circle :loading="refreshing" @click="refreshAll" />
          </div>
        </div>

        <div class="sidebar-filters">
          <el-input
            v-model="queryParams.searchText"
            placeholder="Search title / preview / id"
            clearable
            @keyup.enter="handleQuery"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-input
            v-model="queryParams.workspaceId"
            placeholder="Workspace ID"
            clearable
            @keyup.enter="handleQuery"
          />
          <el-select v-model="queryParams.status" placeholder="Status" clearable>
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
          <div class="filter-actions">
            <el-button type="primary" @click="handleQuery">Search</el-button>
            <el-button @click="resetQuery">Reset</el-button>
          </div>
        </div>

        <div class="conversation-head">
          <span>History</span>
          <span class="conversation-count">{{ conversationRows.length }}</span>
        </div>

        <div class="conversation-list" v-loading="listLoading">
          <button
            type="button"
            class="conversation-item draft-item"
            :class="{ active: isDraftMode }"
            @click="startDraftConversation"
          >
            <div class="conversation-title-row">
              <div class="conversation-title">New conversation</div>
              <el-tag size="small" type="info">draft</el-tag>
            </div>
            <div class="conversation-preview">
              Start from a workspace and requirement, then continue with follow-up messages.
            </div>
          </button>

          <button
            v-for="row in conversationRows"
            :key="row.conversationId"
            type="button"
            class="conversation-item"
            :class="{ active: selectedConversationId === row.conversationId && !isDraftMode }"
            @click="openConversation(row.conversationId)"
          >
            <div class="conversation-title-row">
              <div class="conversation-title">{{ row.title || row.conversationId }}</div>
              <el-tag size="small" :type="tagTypeMap[row.statusTone]">
                {{ row.status || 'unknown' }}
              </el-tag>
            </div>
            <div class="conversation-preview">
              {{ row.latestMessagePreview || row.lastMessagePreview || 'No preview yet.' }}
            </div>
            <div class="conversation-meta">
              <span>{{ row.workspaceId || '--' }}</span>
              <span>{{ formatMsTime(row.lastActivityAtMs || row.updatedAtMs) }}</span>
            </div>
          </button>

          <el-empty v-if="!listLoading && !conversationRows.length" description="No conversations found" />
        </div>
      </aside>

      <section class="detail-panel">
        <template v-if="isDraftMode">
          <el-card class="summary-card" shadow="never">
            <div class="summary-head">
              <div>
                <div class="eyebrow">Create</div>
                <h1 class="summary-title">Start Codex Conversation</h1>
                <div class="summary-meta">
                  <span>Uses `POST /codex/chat/conversations` after backend deploy.</span>
                </div>
              </div>
            </div>

            <el-form
              ref="draftFormRef"
              :model="draftForm"
              :rules="draftRules"
              label-position="top"
              class="draft-form"
            >
              <div class="composer-grid">
                <el-form-item label="Workspace ID" prop="workspaceId">
                  <el-input v-model="draftForm.workspaceId" placeholder="e.g. ws-member" clearable />
                </el-form-item>
                <el-form-item label="Title">
                  <el-input v-model="draftForm.title" placeholder="Optional title" clearable maxlength="120" />
                </el-form-item>
              </div>
              <el-form-item label="Requirement" prop="requirement">
                <el-input
                  v-model="draftForm.requirement"
                  type="textarea"
                  :rows="8"
                  maxlength="4000"
                  show-word-limit
                  placeholder="Describe the task to start the conversation."
                />
              </el-form-item>
              <div class="composer-grid">
                <el-form-item label="Access Mode">
                  <el-input v-model="draftForm.accessMode" placeholder="Optional, e.g. full-access" clearable />
                </el-form-item>
                <el-form-item label="Model">
                  <el-input v-model="draftForm.model" placeholder="Optional model id" clearable />
                </el-form-item>
              </div>
              <div class="composer-actions">
                <el-button type="primary" :loading="submitting" @click="submitDraftConversation">
                  Start Conversation
                </el-button>
                <el-button :disabled="submitting" @click="resetDraftForm">Reset</el-button>
              </div>
            </el-form>
          </el-card>
        </template>

        <template v-else-if="selectedConversationId">
          <el-card class="summary-card" shadow="never" v-loading="detailLoading">
            <div class="summary-head">
              <div>
                <div class="eyebrow">Conversation</div>
                <h1 class="summary-title">{{ readModel.conversation?.title || selectedConversationId }}</h1>
                <div class="summary-meta">
                  <span>ID: {{ readModel.conversation?.conversationId || selectedConversationId }}</span>
                  <span>Workspace: {{ readModel.conversation?.workspaceId || '--' }}</span>
                  <span>Thread: {{ readModel.conversation?.threadId || '--' }}</span>
                </div>
              </div>
              <div class="summary-actions">
                <el-tag :type="tagTypeMap[statusTone]" size="large">
                  {{ readModel.currentState?.status || '--' }}
                </el-tag>
                <el-tag :type="streamState.connected ? 'success' : 'info'" effect="plain">
                  {{ streamState.label }}
                </el-tag>
                <el-button type="primary" :loading="detailLoading" @click="reloadCurrentConversation">Refresh</el-button>
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
                <div class="metric-value metric-time">
                  {{ formatMsTime(readModel.currentState?.lastActivityAtMs) }}
                </div>
              </div>
            </div>

            <div class="composer-panel">
              <el-input
                v-model="messageForm.text"
                type="textarea"
                :rows="4"
                maxlength="4000"
                show-word-limit
                placeholder="Send a follow-up message to the current conversation."
                @keydown.ctrl.enter.prevent="submitMessage"
              />
              <div class="composer-meta">
                <span>Ctrl+Enter to send</span>
                <div class="composer-actions">
                  <el-button :disabled="submitting || !messageForm.text.trim()" @click="clearMessageForm">Clear</el-button>
                  <el-button type="primary" :loading="submitting" @click="submitMessage">Send</el-button>
                </div>
              </div>
            </div>
          </el-card>

          <el-card class="content-card" shadow="never">
            <el-tabs v-model="activeTab">
              <el-tab-pane :label="`Messages (${messages.length})`" name="messages">
                <div v-if="messages.length" class="message-list">
                  <div
                    v-for="(message, index) in messages"
                    :key="message.id || message.messageId || `${message.turnId || 'msg'}-${index}`"
                    class="message-row"
                    :class="{ user: isUserMessage(message), assistant: isAssistantMessage(message) }"
                  >
                    <div class="message-avatar" :class="isUserMessage(message) ? 'user-avatar' : 'assistant-avatar'">
                      <el-icon>
                        <UserFilled v-if="isUserMessage(message)" />
                        <Cpu v-else />
                      </el-icon>
                    </div>
                    <div class="message-bubble">
                      <div class="message-head">
                        <strong>{{ isUserMessage(message) ? 'User' : 'Assistant' }}</strong>
                        <span>{{ message.messageType || message.type || '--' }}</span>
                        <span>{{ formatMsTime(message.createdAtMs) }}</span>
                      </div>
                      <div v-if="isAssistantMessage(message)" class="message-content">
                        <AiMessage :content="getMessageContent(message)" />
                      </div>
                      <pre v-else class="plain-message">{{ getMessageContent(message) }}</pre>
                      <el-collapse>
                        <el-collapse-item title="payloadJson">
                          <pre class="json-block">{{ toPrettyJson(parsePayloadJson(message.payloadJson)) }}</pre>
                        </el-collapse-item>
                      </el-collapse>
                    </div>
                  </div>
                </div>
                <el-empty v-else description="No messages" />
              </el-tab-pane>

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
        </template>

        <div v-else class="empty-state">
          <div class="empty-icon"><el-icon><ChatDotRound /></el-icon></div>
          <h3>No conversation selected</h3>
          <p>Start a new conversation or pick one from the left.</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup name="CodexChat">
import { ChatDotRound, Cpu, Refresh, Search, UserFilled } from '@element-plus/icons-vue'
import AiMessage from '@/views/ai/chat/components/AiMessage.vue'
import { createCodexChatConversation, sendCodexChatConversationMessage } from '@/api/codex/chat'
import { getConversationReadModel, getConversationViewList } from '@/api/codex/conversation'
import { formatCount, formatMsTime, getStatusTone, openCodexStream, parsePayloadJson, toPrettyJson } from '@/utils/codex'

const route = useRoute()
const router = useRouter()
const { proxy } = getCurrentInstance()

const draftFormRef = ref()
const listLoading = ref(false)
const detailLoading = ref(false)
const refreshing = ref(false)
const submitting = ref(false)
const isDraftMode = ref(false)
const draftRequested = ref(false)
const activeTab = ref('messages')
const conversationRows = ref([])
const selectedConversationId = ref(String(route.query.conversationId || '').trim())
const readModel = ref(createEmptyReadModel())
const streamAbortController = ref(null)
const pollingTimer = ref(null)
const streamState = reactive({
  connected: false,
  label: 'idle'
})

const statusOptions = [
  { label: 'running', value: 'running' },
  { label: 'completed', value: 'completed' },
  { label: 'failed', value: 'failed' },
  { label: 'waiting_input', value: 'waiting_input' },
  { label: 'waiting_approval', value: 'waiting_approval' },
  { label: 'streaming', value: 'streaming' },
  { label: 'accepted', value: 'accepted' }
]

const tagTypeMap = {
  info: 'info',
  warning: 'warning',
  success: 'success',
  danger: 'danger'
}

const queryParams = reactive({
  pageNum: 1,
  pageSize: 30,
  searchText: '',
  workspaceId: '',
  status: '',
  orderByColumn: 'updatedAtMs',
  isAsc: 'descending'
})

const draftForm = reactive({
  workspaceId: '',
  title: '',
  requirement: '',
  accessMode: 'full-access',
  model: '',
})

const messageForm = reactive({
  text: ''
})

const draftRules = {
  workspaceId: [{ required: true, message: 'Workspace ID is required', trigger: 'blur' }],
  requirement: [{ required: true, message: 'Requirement is required', trigger: 'blur' }]
}

const messages = computed(() => readModel.value.messages || [])
const tasks = computed(() => readModel.value.tasks || [])
const events = computed(() => readModel.value.events || [])
const rawJson = computed(() => toPrettyJson(readModel.value))
const statusTone = computed(() => getStatusTone(readModel.value.currentState?.status, readModel.value.currentState?.hasError))

async function refreshAll() {
  refreshing.value = true
  try {
    await loadConversations()
  } finally {
    refreshing.value = false
  }
}

async function loadConversations() {
  listLoading.value = true
  try {
    const response = await getConversationViewList(normalizeQueryParams())
    conversationRows.value = Array.isArray(response.rows) ? response.rows.map(mapConversationRow) : []

    if (draftRequested.value) {
      return
    }

    const preferredConversationId = String(route.query.conversationId || selectedConversationId.value || '').trim()
    const targetConversationId = preferredConversationId || conversationRows.value[0]?.conversationId || ''

    if (!targetConversationId) {
      showDraftConversation()
      return
    }

    const stillExists = conversationRows.value.some((item) => item.conversationId === targetConversationId)
    if (stillExists) {
      await openConversation(targetConversationId, false)
      return
    }

    await openConversation(conversationRows.value[0]?.conversationId || '', true)
  } catch (error) {
    proxy?.$modal?.msgError(error.message || 'Failed to load conversations')
  } finally {
    listLoading.value = false
  }
}

function normalizeQueryParams() {
  return {
    ...queryParams,
    searchText: queryParams.searchText || undefined,
    workspaceId: queryParams.workspaceId || undefined,
    status: queryParams.status || undefined,
  }
}

function mapConversationRow(item) {
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
    statusTone: getStatusTone(currentState.status || conversation.status, currentState.hasError),
  }
}

function startDraftConversation() {
  draftRequested.value = true
  showDraftConversation()
  resetDraftForm()
  router.replace({ path: '/chat' })
}

function showDraftConversation() {
  stopRealtime()
  isDraftMode.value = true
  selectedConversationId.value = ''
  readModel.value = createEmptyReadModel()
  streamState.connected = false
  streamState.label = 'idle'
  messageForm.text = ''
}

async function submitDraftConversation() {
  const isValid = await draftFormRef.value?.validate?.().catch(() => false)
  if (!isValid) {
    return
  }

  submitting.value = true
  try {
    const response = await createCodexChatConversation(buildDraftPayload())
    const conversationId = extractConversationId(response)
    if (!conversationId) {
      throw new Error('Conversation ID missing from start response')
    }

    proxy?.$modal?.msgSuccess('Conversation started')
    resetDraftForm()
    isDraftMode.value = false
    await refreshAll()
    await openConversation(conversationId, true)
  } catch (error) {
    proxy?.$modal?.msgError(error.message || 'Failed to start conversation')
  } finally {
    submitting.value = false
  }
}

function buildDraftPayload() {
  const requirement = draftForm.requirement.trim()
  const title = draftForm.title.trim() || requirement.slice(0, 60)

  return {
    workspaceId: draftForm.workspaceId.trim(),
    title,
    requirement,
    accessMode: draftForm.accessMode.trim() || undefined,
    model: draftForm.model.trim() || undefined,
  }
}

function extractConversationId(response) {
  return String(
    response?.data?.conversation?.conversationId ||
    response?.data?.conversationId ||
    response?.conversation?.conversationId ||
    response?.conversationId ||
    ''
  ).trim()
}

function resetDraftForm() {
  draftFormRef.value?.clearValidate?.()
  draftForm.workspaceId = String(
    readModel.value?.conversation?.workspaceId ||
    queryParams.workspaceId ||
    ''
  ).trim()
  draftForm.title = ''
  draftForm.requirement = ''
  draftForm.accessMode = 'full-access'
  draftForm.model = ''
}

async function openConversation(conversationId, updateRoute = true) {
  if (!conversationId) {
    clearCurrentConversation()
    return
  }

  draftRequested.value = false
  isDraftMode.value = false
  selectedConversationId.value = conversationId
  if (updateRoute) {
    router.replace({ path: '/chat', query: { conversationId } })
  }

  detailLoading.value = true
  try {
    const response = await getConversationReadModel(conversationId)
    applyReadModel(response.data || createEmptyReadModel())
    startRealtime(conversationId)
  } catch (error) {
    proxy?.$modal?.msgError(error.message || 'Failed to load conversation detail')
    clearCurrentConversation()
  } finally {
    detailLoading.value = false
  }
}

function reloadCurrentConversation() {
  if (!selectedConversationId.value) {
    return refreshAll()
  }
  return openConversation(selectedConversationId.value, false)
}

function applyReadModel(data) {
  readModel.value = {
    conversation: data.conversation || {},
    currentState: data.currentState || {},
    historySummary: data.historySummary || {},
    messages: Array.isArray(data.messages) ? data.messages : [],
    events: Array.isArray(data.events) ? data.events : [],
    tasks: Array.isArray(data.tasks) ? data.tasks : [],
  }
  upsertConversationSummary(readModel.value)
}

function upsertConversationSummary(model) {
  const conversationId = model?.conversation?.conversationId
  if (!conversationId) {
    return
  }

  const row = mapConversationRow(model)
  const index = conversationRows.value.findIndex((item) => item.conversationId === conversationId)
  if (index >= 0) {
    conversationRows.value[index] = {
      ...conversationRows.value[index],
      ...row,
    }
    return
  }
  conversationRows.value.unshift(row)
}

async function submitMessage() {
  const text = messageForm.text.trim()
  if (!selectedConversationId.value || !text) {
    return
  }

  submitting.value = true
  try {
    await sendCodexChatConversationMessage(selectedConversationId.value, { text })
    messageForm.text = ''
    activeTab.value = 'messages'
    await reloadCurrentConversation()
  } catch (error) {
    proxy?.$modal?.msgError(error.message || 'Failed to send message')
  } finally {
    submitting.value = false
  }
}

function clearMessageForm() {
  messageForm.text = ''
}

async function startRealtime(conversationId) {
  stopRealtime()
  streamAbortController.value = new AbortController()
  streamState.connected = false
  streamState.label = 'connecting'

  try {
    await openCodexStream({
      conversationId,
      pollIntervalMs: 1000,
      signal: streamAbortController.value.signal,
      onData: handleStreamEvent,
    })
  } catch (error) {
    if (error.name !== 'AbortError') {
      streamState.connected = false
      streamState.label = 'polling'
      startPolling(conversationId)
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

function startPolling(conversationId) {
  stopPolling()
  const run = () => getConversationReadModel(conversationId)
    .then((response) => {
      applyReadModel(response.data || createEmptyReadModel())
    })
    .catch(() => {
      streamState.connected = false
      streamState.label = 'polling'
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

function clearCurrentConversation() {
  stopRealtime()
  isDraftMode.value = false
  draftRequested.value = false
  selectedConversationId.value = ''
  readModel.value = createEmptyReadModel()
  streamState.connected = false
  streamState.label = 'idle'
  messageForm.text = ''
}

function handleQuery() {
  queryParams.pageNum = 1
  refreshAll()
}

function resetQuery() {
  queryParams.pageNum = 1
  queryParams.pageSize = 30
  queryParams.searchText = ''
  queryParams.workspaceId = ''
  queryParams.status = ''
  queryParams.orderByColumn = 'updatedAtMs'
  queryParams.isAsc = 'descending'
  resetDraftForm()
  refreshAll()
}

function isUserMessage(message) {
  const role = String(message?.role || '').trim().toLowerCase()
  const type = String(message?.messageType || message?.type || '').trim().toLowerCase()
  return role === 'user' || type === 'user' || type === 'usermessage'
}

function isAssistantMessage(message) {
  const role = String(message?.role || '').trim().toLowerCase()
  const type = String(message?.messageType || message?.type || '').trim().toLowerCase()
  return role === 'assistant' || type === 'assistant' || type === 'agentmessage'
}

function getMessageContent(message) {
  const directContent = firstNonEmpty(message?.content, message?.text)
  if (directContent) {
    return directContent
  }

  const payload = parsePayloadJson(message?.payloadJson)
  if (typeof payload === 'string') {
    return payload
  }
  if (payload && typeof payload === 'object') {
    const payloadContent = firstNonEmpty(payload.content, payload.text, payload.summary, payload.output)
    if (payloadContent) {
      return payloadContent
    }
    if (Array.isArray(payload.content)) {
      return payload.content
        .map((item) => {
          if (item?.type === 'text') {
            return item.text || ''
          }
          return ''
        })
        .filter(Boolean)
        .join('\n')
    }
  }
  return '--'
}

function firstNonEmpty(...values) {
  for (const value of values) {
    if (typeof value === 'string' && value.trim()) {
      return value
    }
  }
  return ''
}

function createEmptyReadModel() {
  return {
    conversation: {},
    currentState: {},
    historySummary: {},
    messages: [],
    events: [],
    tasks: [],
  }
}

watch(
  () => route.query.conversationId,
  (conversationId) => {
    const normalizedId = String(conversationId || '').trim()
    if (!normalizedId) {
      return
    }
    if (normalizedId === selectedConversationId.value && !isDraftMode.value) {
      return
    }
    openConversation(normalizedId, false)
  }
)

onMounted(() => {
  resetDraftForm()
  isDraftMode.value = false
  refreshAll()
})

onBeforeUnmount(() => {
  stopRealtime()
})
</script>

<style scoped lang="scss">
.codex-chat-page {
  height: calc(100vh - 84px);
  padding: 0;
  background:
    radial-gradient(circle at top left, rgba(14, 165, 233, 0.12), transparent 24%),
    radial-gradient(circle at right top, rgba(20, 184, 166, 0.12), transparent 28%),
    linear-gradient(180deg, #f4f7fb 0%, #ecf2f8 100%);
}

.page-shell {
  display: grid;
  grid-template-columns: 360px minmax(0, 1fr);
  gap: 18px;
  height: 100%;
  padding: 18px;
}

.sidebar-panel,
.detail-panel {
  min-height: 0;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(14px);
  box-shadow: 0 14px 40px rgba(15, 23, 42, 0.08);
}

.sidebar-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-head,
.summary-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 22px;
}

.sidebar-actions,
.filter-actions,
.conversation-title-row,
.summary-actions,
.message-head,
.composer-meta,
.composer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.eyebrow {
  color: #0f766e;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.sidebar-head h2,
.summary-title,
.empty-state h3 {
  margin: 6px 0 0;
  color: #0f172a;
}

.sidebar-filters {
  display: grid;
  gap: 12px;
  padding: 0 18px 18px;
}

.conversation-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 22px 12px;
  color: #334155;
  font-weight: 600;
}

.conversation-count {
  color: #64748b;
  font-size: 12px;
}

.conversation-list {
  flex: 1;
  overflow: auto;
  padding: 0 14px 18px;
}

.conversation-item {
  width: 100%;
  margin-bottom: 10px;
  padding: 14px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 16px;
  background: #fff;
  text-align: left;
  cursor: pointer;
  transition: 0.2s ease;
}

.conversation-item:hover,
.conversation-item.active {
  border-color: rgba(14, 165, 233, 0.36);
  box-shadow: 0 8px 24px rgba(14, 165, 233, 0.12);
  transform: translateY(-1px);
}

.draft-item {
  background: linear-gradient(135deg, rgba(236, 254, 255, 0.95), rgba(240, 253, 250, 0.95));
}

.conversation-title {
  color: #0f172a;
  font-weight: 700;
}

.conversation-preview,
.conversation-meta,
.summary-meta,
.metric-label,
.plain-message,
.composer-meta span {
  color: #64748b;
  font-size: 13px;
}

.conversation-preview {
  margin-top: 10px;
  line-height: 1.5;
}

.conversation-meta,
.summary-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 10px;
}

.detail-panel {
  overflow: auto;
  padding: 18px;
}

.empty-state {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #475569;
  text-align: center;
}

.empty-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  margin-bottom: 18px;
  border-radius: 22px;
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.16), rgba(20, 184, 166, 0.16));
  color: #0f766e;
  font-size: 34px;
}

.summary-card,
.content-card,
:deep(.el-card) {
  border-radius: 20px;
}

.summary-grid,
.overview-grid,
.composer-grid {
  display: grid;
  gap: 16px;
}

.summary-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-top: 18px;
}

.overview-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.composer-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.metric-card {
  padding: 16px 18px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.88);
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

.draft-form,
.composer-panel {
  margin-top: 20px;
}

.composer-panel {
  padding-top: 20px;
  border-top: 1px solid rgba(148, 163, 184, 0.18);
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

.message-list {
  display: grid;
  gap: 16px;
}

.message-row {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.message-row.user {
  flex-direction: row-reverse;
}

.message-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  color: #fff;
  flex-shrink: 0;
}

.user-avatar {
  background: linear-gradient(135deg, #0f766e, #14b8a6);
}

.assistant-avatar {
  background: linear-gradient(135deg, #0f172a, #334155);
}

.message-bubble {
  width: min(960px, 100%);
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 18px;
  background: #fff;
  padding: 16px 18px;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
}

.message-row.user .message-bubble {
  background: linear-gradient(135deg, #ecfeff, #f0fdfa);
}

.message-content {
  margin-top: 12px;
}

.plain-message,
.json-block,
.json-inline {
  margin: 12px 0 0;
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

@media (max-width: 1200px) {
  .page-shell {
    grid-template-columns: 1fr;
    height: auto;
  }

  .codex-chat-page {
    height: auto;
    min-height: calc(100vh - 84px);
  }

  .sidebar-panel {
    min-height: 420px;
  }
}

@media (max-width: 768px) {
  .page-shell,
  .detail-panel {
    padding: 12px;
    gap: 12px;
  }

  .sidebar-head,
  .summary-head,
  .composer-meta {
    flex-direction: column;
    align-items: stretch;
  }

  .summary-grid,
  .overview-grid,
  .composer-grid {
    grid-template-columns: 1fr;
  }

  .message-row {
    gap: 10px;
  }

  .message-bubble {
    width: 100%;
  }
}
</style>
