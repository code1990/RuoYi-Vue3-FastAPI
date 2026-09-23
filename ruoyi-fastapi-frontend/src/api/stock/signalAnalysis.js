import request from '@/utils/request'

export function listSignalAnalysis(params) {
  return request({ url: '/stock/signal-analysis/page', method: 'get', params })
}
