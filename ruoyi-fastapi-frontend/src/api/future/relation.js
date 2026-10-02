import request from '@/utils/request'

export function listFutureRelations() {
  return request({ url: '/future/relation/list', method: 'get' })
}
