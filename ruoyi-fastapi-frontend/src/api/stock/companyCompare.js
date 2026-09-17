import request from '@/utils/request'

export function getCompanyCompareHistory(params) {
  return request({ url: '/stock/company-compare/history', method: 'get', params })
}
