import request from '@/utils/request'

export const listProject = query => request({ url: '/project/manage/list', method: 'get', params: query })
export const addProject = data => request({ url: '/project/manage', method: 'post', data })
export const updateProject = data => request({ url: '/project/manage', method: 'put', data })
export const delProject = id => request({ url: '/project/manage/' + id, method: 'delete' })
