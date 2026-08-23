import request from '@/utils/request'

export function listDdeSignalPerformance(params) {
  return request({
    url: '/stock/dde/performance/list',
    method: 'get',
    params
  })
}

export function listDdeCombo(params) {
  return request({ url: '/stock/dde/combo/list', method: 'get', params })
}

export function getDdeComboStatistics(params) {
  return request({ url: '/stock/dde/combo/statistics', method: 'get', params })
}

export function listDdeTop30Performance(params) {
  return request({ url: '/stock/dde/top30/performance/list', method: 'get', params })
}

export function getDdeStatistics(params) {
  return request({ url: '/stock/dde/statistics', method: 'get', params })
}

export function listDdeHotRank(params) {
  return request({ url: '/stock/dde/hot-rank/list', method: 'get', params })
}

export function listDdeObservation(params) {
  return request({ url: '/stock/dde/observation/list', method: 'get', params })
}

export function getDdeObservationStatistics(params) {
  return request({ url: '/stock/dde/observation/statistics', method: 'get', params })
}
