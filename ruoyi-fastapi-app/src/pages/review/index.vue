<template>
  <view class="page">
    <view class="heatmap-card">
      <view class="heatmap-header">
        <view><text class="heatmap-title">复习热力图</text><text class="heatmap-subtitle">最近三个月</text></view>
        <text class="today-count">今日 {{ completedToday }} 次</text>
      </view>
      <view v-for="month in heatmapMonths" :key="month.key" class="heatmap-month">
        <view class="month-header"><text>{{ month.label }}</text><text>{{ month.total }} 次</text></view>
        <view class="weekdays"><text v-for="day in weekdays" :key="day">{{ day }}</text></view>
        <view class="day-grid">
          <view v-for="day in month.days" :key="day.key" :class="['heatmap-day', day.date ? day.level : 'blank']">
            <text v-if="day.date" class="day-number">{{ day.day }}</text><text v-if="day.count || day.plannedCount" class="day-count">{{ day.count || day.plannedCount }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getReviewOverview } from '@/api/exam/review'

const reviewOverview = ref({})
const weekdays = ['日', '一', '二', '三', '四', '五', '六']
const completedToday = computed(() => reviewOverview.value.completedToday || 0)
const formatDate = day => `${day.getFullYear()}-${String(day.getMonth() + 1).padStart(2, '0')}-${String(day.getDate()).padStart(2, '0')}`
const heatLevel = count => count >= 30 ? 'max' : count >= 20 ? 'high' : count >= 10 ? 'mid' : count ? 'low' : ''
const heatmapMonths = computed(() => {
  const counts = Object.fromEntries((reviewOverview.value.heatmap || []).map(item => [item.date, item.count]))
  const plannedCounts = Object.fromEntries((reviewOverview.value.plannedReviews || []).map(item => [item.date, item.count]))
  const now = new Date()
  const today = formatDate(now)
  return Array.from({ length: 3 }, (_, index) => {
    const month = new Date(now.getFullYear(), now.getMonth() - 2 + index, 1)
    const leading = month.getDay()
    const lastDay = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate()
    const days = Array.from({ length: Math.ceil((leading + lastDay) / 7) * 7 }, (_, cell) => {
      const day = cell - leading + 1
      const date = day > 0 && day <= lastDay ? new Date(month.getFullYear(), month.getMonth(), day) : null
      const key = date && formatDate(date)
      const count = key ? counts[key] || 0 : 0
      const plannedCount = key ? plannedCounts[key] || 0 : 0
      return { key: key || `${month.getTime()}-${cell}`, date, day, count, plannedCount, level: key > today && plannedCount ? 'planned' : heatLevel(count) }
    })
    return { key: `${month.getFullYear()}-${month.getMonth()}`, label: `${month.getFullYear()}年${month.getMonth() + 1}月`, days, total: days.reduce((sum, day) => sum + day.count, 0) }
  })
})

async function load() {
  const year = new Date().getFullYear()
  const [current, previous] = await Promise.all([getReviewOverview(year), getReviewOverview(year - 1)])
  const currentData = current.data || {}
  reviewOverview.value = { ...currentData, heatmap: [...(previous.data?.heatmap || []), ...(currentData.heatmap || [])], plannedReviews: currentData.plannedReviews || [] }
}

onShow(() => { load().catch(() => {}) })
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb;padding:28rpx 30rpx}.heatmap-card{background:#fff;border-radius:22rpx;padding:30rpx}.heatmap-header,.month-header{display:flex;align-items:center;justify-content:space-between}.heatmap-title{display:block;color:#25324a;font-size:30rpx;font-weight:700}.heatmap-subtitle,.month-header{color:#7f8ba0;font-size:22rpx}.today-count{padding:8rpx 12rpx;border-radius:10rpx;background:#eef3ff;color:#315bd4;font-size:22rpx}.heatmap-month{margin-top:26rpx}.month-header{padding-bottom:12rpx}.weekdays,.day-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:8rpx}.weekdays{margin-bottom:8rpx;text-align:center;color:#9aa5b5;font-size:20rpx}.heatmap-day{position:relative;aspect-ratio:1;border-radius:8rpx;background:#ebedf0;color:#5d6b80}.heatmap-day.low{background:#9be9a8}.heatmap-day.mid{background:#40c463;color:#fff}.heatmap-day.high{background:#30a14e;color:#fff}.heatmap-day.max{background:#216e39;color:#fff}.heatmap-day.planned{background:#f7bfd3;color:#963b5c}.heatmap-day.blank{background:transparent}.day-number{position:absolute;top:6rpx;left:8rpx;font-size:19rpx}.day-count{position:absolute;right:7rpx;bottom:5rpx;font-size:18rpx;font-weight:600}
</style>
