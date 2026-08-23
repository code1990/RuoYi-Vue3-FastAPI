import request from '@/utils/request'

export function listMarginLongPerformance(params) {
  return request({ url: '/stock/margin/long-performance/list', method: 'get', params })
}

export function getMarginLongStatistics(params) {
  return request({ url: '/stock/margin/long-performance/statistics', method: 'get', params })
}

export function listMarginCombo(params) {
  return request({ url: '/stock/margin/combo/list', method: 'get', params })
}
