import request from '@/utils/request'

export function getFundVisualHistory(params) {
  return request({ url: '/stock/fund-visual/history', method: 'get', params })
}
