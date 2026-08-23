import request from '@/utils/request'

export function getLimitUpThemeTop15(params) {
  return request({ url: '/stock/limit-up/theme/top15', method: 'get', params })
}
