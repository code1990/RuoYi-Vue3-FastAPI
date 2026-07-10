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
