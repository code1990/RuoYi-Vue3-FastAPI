import request from '@/utils/request'

export function listFutureProfitEffect() {
  return request({ url: '/future/profit-effect/list', method: 'get' })
}
