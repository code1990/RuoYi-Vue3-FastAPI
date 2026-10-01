import request from '@/utils/request'

export function listFutureQuote(params) {
  return request({ url: '/future/quote/list', method: 'get', params })
}
