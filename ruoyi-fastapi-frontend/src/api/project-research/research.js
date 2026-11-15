import request from '@/utils/request'

export const listBacktest = query => request({ url: '/research/backtest/list', method: 'get', params: query })
export const addBacktest = data => request({ url: '/research/backtest', method: 'post', data })
export const delBacktest = id => request({ url: '/research/backtest/' + id, method: 'delete' })
export const listSimulation = query => request({ url: '/research/simulation/list', method: 'get', params: query })
export const addSimulation = data => request({ url: '/research/simulation', method: 'post', data })
export const delSimulation = id => request({ url: '/research/simulation/' + id, method: 'delete' })
export const listReview = query => request({ url: '/research/review/list', method: 'get', params: query })
export const addReview = data => request({ url: '/research/review', method: 'post', data })
export const delReview = id => request({ url: '/research/review/' + id, method: 'delete' })
