import request from '@/utils/request'

export const listResourceTopics = () => request({ url: '/feizhu/resources/topics', method: 'get' })
export const searchResources = params => request({ url: '/feizhu/resources/search', method: 'get', params })
export const getResourceDetail = id => request({ url: '/feizhu/resources/detail', method: 'get', params: { id } })
