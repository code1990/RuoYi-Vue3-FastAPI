import request from '@/utils/request'

export const getFileDetailOptions = params => request({ url: '/feizhu/file-details/options', method: 'get', params })
export const listFileDetails = params => request({ url: '/feizhu/file-details', method: 'get', params })
export const listFileKeywords = () => request({ url: '/feizhu/file-details/keywords', method: 'get' })
export const deleteFileKeywordTopic = (keywordId, topic) => request({ url: `/feizhu/file-details/keywords/${keywordId}/topics`, method: 'delete', params: { topic } })
