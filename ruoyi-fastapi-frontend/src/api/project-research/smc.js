import request from '@/utils/request'

export const listSmcRequirements = query => request({ url: '/smc/requirement/list', method: 'get', params: query })
export const addSmcRequirement = data => request({ url: '/smc/requirement', method: 'post', data })
export const updateSmcRequirement = data => request({ url: '/smc/requirement', method: 'put', data })
export const delSmcRequirement = id => request({ url: '/smc/requirement/' + id, method: 'delete' })

export const listSmcFeatures = query => request({ url: '/smc/feature/list', method: 'get', params: query })
export const addSmcFeature = data => request({ url: '/smc/feature', method: 'post', data })
export const updateSmcFeature = data => request({ url: '/smc/feature', method: 'put', data })
export const delSmcFeature = id => request({ url: '/smc/feature/' + id, method: 'delete' })
