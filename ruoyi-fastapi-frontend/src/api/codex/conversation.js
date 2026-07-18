import request from '@/utils/request'

export function getConversationViewList(params) {
  return request({
    url: '/codex/conversations/views',
    method: 'get',
    params
  })
}

export function getConversationReadModel(conversationId) {
  return request({
    url: `/codex/conversations/${conversationId}/read-model`,
    method: 'get'
  })
}

export function getConversationDetail(conversationId) {
  return request({
    url: `/codex/conversations/${conversationId}`,
    method: 'get'
  })
}

export function getConversationMessages(conversationId) {
  return request({
    url: `/codex/conversations/${conversationId}/messages`,
    method: 'get'
  })
}

export function getConversationEvents(conversationId) {
  return request({
    url: `/codex/conversations/${conversationId}/events`,
    method: 'get'
  })
}

export function getConversationTasks(conversationId) {
  return request({
    url: `/codex/conversations/${conversationId}/tasks`,
    method: 'get'
  })
}
