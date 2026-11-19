import request from '@/utils/request'

export const listResearchRequirements = query => request({ url: '/research/requirement/list', method: 'get', params: query })
export const getResearchRequirement = id => request({ url: '/research/requirement/' + id, method: 'get' })
export const addResearchRequirement = data => request({ url: '/research/requirement', method: 'post', data })
export const updateResearchRequirement = data => request({ url: '/research/requirement', method: 'put', data })
export const delResearchRequirement = id => request({ url: '/research/requirement/' + id, method: 'delete' })

export const listResearchFeatures = query => request({ url: '/research/feature/list', method: 'get', params: query })
export const addResearchFeature = data => request({ url: '/research/feature', method: 'post', data })
export const updateResearchFeature = data => request({ url: '/research/feature', method: 'put', data })
export const delResearchFeature = id => request({ url: '/research/feature/' + id, method: 'delete' })
