import request from '@/utils/request'

export const listFunction = query => request({ url: '/function/manage/list', method: 'get', params: query })
export const addFunction = data => request({ url: '/function/manage', method: 'post', data })
export const updateFunction = data => request({ url: '/function/manage', method: 'put', data })
export const delFunction = id => request({ url: '/function/manage/' + id, method: 'delete' })
