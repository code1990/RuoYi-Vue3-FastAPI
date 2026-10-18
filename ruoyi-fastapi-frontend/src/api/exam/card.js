import request from '@/utils/request'

export const listExamCategories = () => request({ url: '/exam/categories', method: 'get' })
export const listExamCards = categoryId => request({ url: '/exam/cards', method: 'get', params: categoryId ? { categoryId } : undefined })
export const getExamReviewOverview = year => request({ url: '/exam/review/overview', method: 'get', params: { year } })
