import request from '@/utils/request'

export function getLatestDdeAlgorithm() {
  return request({ url: '/stock/algorithm/dde/latest', method: 'get' })
}
