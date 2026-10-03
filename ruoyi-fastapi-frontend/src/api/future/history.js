import request from '@/utils/request'

export const listFutureHistorySeries = () => request({ url: '/future/history/series', method: 'get' })
export const listFutureHistoryDaily = thscode => request({ url: '/future/history/daily', method: 'get', params: { thscode } })
