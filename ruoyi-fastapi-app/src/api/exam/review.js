import request from '@/utils/request'
export const getReviewOverview = () => request({ url: '/exam/review/overview', method: 'get' })
export const getNextReviewCard = () => request({ url: '/exam/review/next', method: 'get' })
export const rateReviewCard = (cardId, rating) => request({ url: `/exam/review/${cardId}/rate`, method: 'post', data: { rating } })
