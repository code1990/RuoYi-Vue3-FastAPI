import request from '@/utils/request'

export function listMarginLongPerformance(params) {
  return request({ url: '/stock/margin/long-performance/list', method: 'get', params })
}
