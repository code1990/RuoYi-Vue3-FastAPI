import stockMetadata from '@/assets/data/org_num.json'

export function getStockMetadata(stockCode) {
  return stockMetadata[String(stockCode || '').padStart(6, '0')] || {}
}

export function getStockConcept(stockCode) {
  return getStockMetadata(stockCode).concept || '-'
}

export function getStockIndustry(stockCode) {
  return getStockMetadata(stockCode).industry || '-'
}

export function getStockOrgNum(stockCode) {
  const value = getStockMetadata(stockCode).org_num
  return value === null || value === undefined ? '-' : Number(value).toFixed(0)
}
