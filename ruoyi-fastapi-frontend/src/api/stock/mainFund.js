import request from '@/utils/request'

export function listMainFundPerformance(params) {
  return request({ url: '/stock/main-fund/performance/list', method: 'get', params })
}
