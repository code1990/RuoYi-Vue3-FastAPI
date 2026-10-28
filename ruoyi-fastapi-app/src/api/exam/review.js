import request from '@/utils/request'
export const getReviewOverview = year => request({ url: '/exam/review/overview', method: 'get', params: year ? { year } : undefined })
export const getReviewProgress = () => request({ url: '/exam/review/progress', method: 'get' })
export const getNextReviewCard = () => request({ url: '/exam/review/next', method: 'get' })
export const rateReviewCard = (cardId, rating) => request({ url: `/exam/review/${cardId}/rate`, method: 'post', data: { rating } })
