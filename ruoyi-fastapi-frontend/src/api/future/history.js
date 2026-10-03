import request from '@/utils/request'

export const listFutureHistorySeries = () => request({ url: '/future/history/series', method: 'get' })
export const listFutureHistoryDaily = thscode => request({ url: '/future/history/daily', method: 'get', params: { thscode } })
export const listFutureHistoryContracts = params => request({ url: '/future/history/contracts', method: 'get', params })
export const listFutureBasis = thscode => request({ url: '/future/history/basis', method: 'get', params: thscode ? { thscode } : undefined })
export const listFutureCatalog = kind => request({ url: `/future/history/catalog/${kind}`, method: 'get' })
