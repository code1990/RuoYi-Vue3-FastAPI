import request from '@/utils/request'

export function listMainFundPerformance(params) {
  return request({ url: '/stock/main-fund/performance/list', method: 'get', params })
}

export function getMainFundStatistics(params) {
  return request({ url: '/stock/main-fund/statistics', method: 'get', params })
}
