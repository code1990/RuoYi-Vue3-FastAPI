import request from '@/utils/request'

export const listOptionVarieties = params => request({ url: '/future/option/varieties', method: 'get', params })
export const listOptionContracts = params => request({ url: '/future/option/contracts', method: 'get', params })
export const getOptionChain = underlyingCode => request({ url: '/future/option/chain', method: 'get', params: { underlyingCode } })
export const listOptionUnderlyings = () => request({ url: '/future/option/underlyings', method: 'get' })
export const refreshOptionChainDaily = underlyingCode => request({ url: '/future/option/chain/daily-research', method: 'get', params: { underlyingCode } })
export const getMarketOptionIntraday = thscode => request({ url: '/future/option/prices/intraday', method: 'get', params: { thscode } })
export const getMarketOptionDailyResearch = thscode => request({ url: '/future/option/prices/daily-research', method: 'get', params: { thscode } })
export const getMarketOptionTimeline = thscode => request({ url: '/future/option/calendar/session-timeline', method: 'get', params: { thscode } })
