import request from '@/utils/request'

export const getFileDetailOptions = params => request({ url: '/feizhu/file-details/options', method: 'get', params })
export const listFileDetails = params => request({ url: '/feizhu/file-details', method: 'get', params })
