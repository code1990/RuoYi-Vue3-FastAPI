<template>
  <view class="page">
    <view class="card overview">
      <view class="overview-header"><view><text class="title">题库学习进度</text><text class="subtitle">按题目统计，同题当天多次评级只算 1 题</text></view><text class="percent">{{ bank.progressPercent || 0 }}%</text></view>
      <view class="progress-summary"><view><b>{{ recent.newCards || 0 }}</b><small>近30天新学</small></view><view><b>{{ recent.reviewedCards || 0 }}</b><small>近30天复习</small></view><view><b>{{ recent.studiedCards || 0 }}</b><small>近30天学习</small></view></view>
      <view class="estimate"><text>完成首轮覆盖</text><b v-if="recent.estimatedCoverageDays !== null && recent.estimatedCoverageDays !== undefined">约 {{ recent.estimatedCoverageDays }} 天</b><text v-else>完成更多新题后估算</text></view>
    </view>

    <view class="card depth-card">
      <view class="section-title"><text>题库复习深度</text><text>{{ bank.started || 0 }} / {{ total }} 题已开始学习</text></view>
      <view class="depth-content">
        <view class="donut" :style="donutStyle"><view class="donut-hole"><text>{{ total }}</text><small>题库总数</small></view></view>
        <view class="legend"><view v-for="item in levels" :key="item.key" class="legend-row"><i :style="{ background: item.color }" /><text>{{ item.label }}</text><b>{{ item.count }} 题</b></view></view>
      </view>
    </view>

    <view v-for="month in calendarMonths" :key="month.key" class="card heatmap-card">
      <view class="section-title"><text>{{ month.label }}学习热力图</text><text>{{ month.total }} 题</text></view>
      <view class="weekdays"><text v-for="weekday in weekdays" :key="weekday">{{ weekday }}</text></view>
      <view class="day-grid">
        <view v-for="day in month.days" :key="day.key" :class="['heatmap-day', day.date ? day.level : 'blank']">
          <text v-if="day.date" class="day-number">{{ day.day }}</text><text v-if="day.count || day.plannedCards" class="day-count">{{ day.count || day.plannedCards }}</text>
        </view>
      </view>
      <text class="heatmap-note">{{ month.current ? '数字为当天去重学习题数' : '数字为计划复习题数' }}</text>
    </view>

  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getReviewProgress } from '@/api/exam/review'

const progress = ref({})
const bank = computed(() => progress.value.questionBank || {})
const recent = computed(() => progress.value.recent30Days || {})
const weekdays = ['日', '一', '二', '三', '四', '五', '六']
const total = computed(() => ['unlearned', 'learning', 'initialReview', 'consolidating', 'mastered'].reduce((sum, key) => sum + (bank.value[key] || 0), 0))
const levels = computed(() => [
  { key: 'unlearned', label: '未学习', color: '#dce2ea', count: bank.value.unlearned || 0 },
  { key: 'learning', label: '学习中', color: '#f6b75a', count: bank.value.learning || 0 },
  { key: 'initialReview', label: '初次巩固', color: '#7ba9f7', count: bank.value.initialReview || 0 },
  { key: 'consolidating', label: '反复巩固', color: '#48b99b', count: bank.value.consolidating || 0 },
  { key: 'mastered', label: '稳定掌握', color: '#315bd4', count: bank.value.mastered || 0 },
])
const donutStyle = computed(() => {
  if (!total.value) return { background: '#dce2ea' }
  let degree = 0
  const stops = levels.value.map(item => { const next = degree + item.count / total.value * 360; const part = `${item.color} ${degree}deg ${next}deg`; degree = next; return part })
  return { background: `conic-gradient(${stops.join(',')})` }
})
const formatDate = day => `${day.getFullYear()}-${String(day.getMonth() + 1).padStart(2, '0')}-${String(day.getDate()).padStart(2, '0')}`
const heatLevel = count => count >= 20 ? 'max' : count >= 12 ? 'high' : count >= 6 ? 'mid' : count ? 'low' : ''
const calendarMonths = computed(() => {
  const calendar = Object.fromEntries((progress.value.calendar || []).map(item => [item.date, item]))
  const now = new Date(); const today = formatDate(now)
  return [0, 1].map(offset => {
    const month = new Date(now.getFullYear(), now.getMonth() + offset, 1)
    const leading = month.getDay(); const lastDay = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate()
    const days = Array.from({ length: Math.ceil((leading + lastDay) / 7) * 7 }, (_, cell) => {
      const day = cell - leading + 1; const date = day > 0 && day <= lastDay ? new Date(month.getFullYear(), month.getMonth(), day) : null; const key = date && formatDate(date); const item = key ? calendar[key] || {} : {}
      return { key: key || `${month.getTime()}-${cell}`, date, day, count: item.studiedCards || 0, plannedCards: item.plannedCards || 0, level: key > today && item.plannedCards ? 'planned' : heatLevel(item.studiedCards || 0) }
    })
    return { key: `${month.getFullYear()}-${month.getMonth()}`, label: `${month.getFullYear()}年${month.getMonth() + 1}月`, current: offset === 0, days, total: days.reduce((sum, day) => sum + day.count, 0) }
  })
})

async function load() { progress.value = (await getReviewProgress()).data || {} }

onShow(() => { load().catch(() => {}) })
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb;padding:28rpx 30rpx}.card{margin-bottom:20rpx;padding:28rpx;background:#fff;border-radius:22rpx}.overview-header,.section-title,.progress-summary,.estimate{display:flex;align-items:center;justify-content:space-between}.title{display:block;color:#25324a;font-size:32rpx;font-weight:700}.subtitle,.section-title,.estimate{color:#7f8ba0;font-size:22rpx}.percent{color:#315bd4;font-size:44rpx;font-weight:700}.progress-summary{gap:10rpx;margin-top:22rpx}.progress-summary view{flex:1;display:flex;flex-direction:column;align-items:center;padding:16rpx 4rpx;border-radius:12rpx;background:#f6f8fc}.progress-summary b{color:#25324a;font-size:34rpx}.progress-summary small,.donut-hole small{margin-top:4rpx;color:#8d98aa;font-size:19rpx}.section-title{padding-bottom:22rpx}.section-title>text:first-child{color:#25324a;font-size:28rpx;font-weight:700}.depth-content{display:flex;align-items:center;gap:30rpx}.donut{position:relative;flex:none;width:210rpx;height:210rpx;border-radius:50%}.donut-hole{position:absolute;inset:35rpx;display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:50%;background:#fff;color:#25324a}.donut-hole text{font-size:34rpx;font-weight:700}.legend{flex:1}.legend-row{display:flex;align-items:center;gap:10rpx;margin:10rpx 0;font-size:22rpx;color:#59677e}.legend-row i{width:16rpx;height:16rpx;border-radius:50%}.legend-row b{margin-left:auto;color:#25324a;font-weight:600}.weekdays,.day-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:8rpx}.weekdays{margin-bottom:8rpx;text-align:center;color:#9aa5b5;font-size:20rpx}.heatmap-day{position:relative;aspect-ratio:1;border-radius:8rpx;background:#ebedf0;color:#5d6b80}.heatmap-day.low{background:#9be9a8}.heatmap-day.mid{background:#40c463;color:#fff}.heatmap-day.high{background:#30a14e;color:#fff}.heatmap-day.max{background:#216e39;color:#fff}.heatmap-day.planned{background:#f7bfd3;color:#963b5c}.heatmap-day.blank{background:transparent}.day-number{position:absolute;top:6rpx;left:8rpx;font-size:19rpx}.day-count{position:absolute;right:7rpx;bottom:5rpx;font-size:18rpx;font-weight:600}.heatmap-note{display:block;margin-top:14rpx;color:#8d98aa;font-size:20rpx}.estimate{margin-top:20rpx;padding:18rpx 20rpx;border-radius:12rpx;background:#edf2ff;color:#536177}.estimate b{color:#315bd4;font-size:26rpx}
</style>
