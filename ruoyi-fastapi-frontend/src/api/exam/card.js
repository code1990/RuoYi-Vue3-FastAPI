import request from '@/utils/request'

export const listExamCategories = () => request({ url: '/exam/categories', method: 'get' })
export const listExamCards = categoryId => request({ url: '/exam/cards', method: 'get', params: categoryId ? { categoryId } : undefined })
export const getExamReviewOverview = year => request({ url: '/exam/review/overview', method: 'get', params: { year } })
export const listExamCardAiSummaryVersions = cardId => request({ url: `/exam/cards/${cardId}/ai-summary-versions`, method: 'get' })
export const addExamCardAiSummaryVersion = (cardId, data) => request({ url: `/exam/cards/${cardId}/ai-summary-versions`, method: 'post', data })
export const activateExamCardAiSummaryVersion = (cardId, versionId) => request({ url: `/exam/cards/${cardId}/ai-summary-versions/${versionId}/activate`, method: 'post' })
