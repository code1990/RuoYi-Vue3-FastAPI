import request from '@/utils/request'

export function getNightSuperCards(params) {
  return request({
    url: '/stock/xg/night-super/cards',
    method: 'get',
    params
  })
}
