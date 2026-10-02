import request from '@/utils/request'

export const listMarketOptionVarieties = () => request({ url: '/future/option/varieties/market', method: 'get' })
export const listMarketOptionContracts = params => request({ url: '/future/option/contracts/market', method: 'get', params })
export const getMarketOptionIntraday = thscode => request({ url: '/future/option/prices/intraday', method: 'get', params: { thscode } })
export const getMarketOptionDailyResearch = thscode => request({ url: '/future/option/prices/daily-research', method: 'get', params: { thscode } })
export const getMarketOptionTimeline = thscode => request({ url: '/future/option/calendar/session-timeline', method: 'get', params: { thscode } })
