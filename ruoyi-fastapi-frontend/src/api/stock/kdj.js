import request from '@/utils/request'

export function getKdjHistory(params) {
  return request({ url: '/stock/kdj/history', method: 'get', params })
}
