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

export function listDdeTop30Performance(params) {
  return request({ url: '/stock/dde/top30/performance/list', method: 'get', params })
}
