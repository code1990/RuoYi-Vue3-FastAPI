import request from '@/utils/request'

export function listDdeAlgorithms(params) {
  return request({ url: '/stock/algorithm/dde/list', method: 'get', params })
}

export function getDdeAlgorithm(experimentKey) {
  return request({ url: `/stock/algorithm/dde/${experimentKey}`, method: 'get' })
}


export function listDdeRuleCandidates(params) {
  return request({ url: '/stock/algorithm/dde/rules/list', method: 'get', params })
}
