import request from '@/utils/request'

export function listDdeSignalPerformance(params) {
  return request({
    url: '/stock/dde/performance/list',
    method: 'get',
    params
  })
}
