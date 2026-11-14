import request from '@/utils/request'

export const listCombination = query => request({ url: '/function/combination/list', method: 'get', params: query })
export const addCombination = data => request({ url: '/function/combination', method: 'post', data })
export const updateCombination = data => request({ url: '/function/combination', method: 'put', data })
export const delCombination = id => request({ url: '/function/combination/' + id, method: 'delete' })
