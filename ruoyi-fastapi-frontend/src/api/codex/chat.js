import request from '@/utils/request'

async function requestWithFallback(configs) {
  let lastError = null

  for (const config of configs) {
    try {
      return await request(config)
    } catch (error) {
      lastError = error
      if (error?.response?.status !== 404) {
        throw error
      }
    }
  }

  throw lastError || new Error('Codex chat request failed')
}

export function getCodexChatHealth() {
  return request({
    url: '/codex/chat/health',
    method: 'get'
  })
}

export function getCodexChatWorkspaces() {
  return request({
    url: '/codex/chat/workspaces',
    method: 'get'
  })
}

export function getCodexChatConversations(params) {
  return request({
    url: '/codex/chat/conversations',
    method: 'get',
    params
  })
}

export function createCodexChatConversation(data) {
  return requestWithFallback([
    {
      url: '/codex/chat/start',
      method: 'post',
      data
    },
    {
      url: '/codex/chat/conversations',
      method: 'post',
      data
    }
  ])
}

export function getCodexChatConversationDetail(conversationId) {
  return request({
    url: `/codex/chat/conversations/${conversationId}`,
    method: 'get'
  })
}

export function getCodexChatConversationMessages(conversationId) {
  return request({
    url: `/codex/chat/conversations/${conversationId}/messages`,
    method: 'get'
  })
}

export function sendCodexChatConversationMessage(conversationId, data) {
  return requestWithFallback([
    {
      url: `/codex/chat/${conversationId}/messages`,
      method: 'post',
      data
    },
    {
      url: `/codex/chat/conversations/${conversationId}/messages`,
      method: 'post',
      data
    }
  ])
}

export function respondCodexChatServerRequest(data) {
  return request({
    url: '/codex/chat/server-requests/respond',
    method: 'post',
    data
  })
}
