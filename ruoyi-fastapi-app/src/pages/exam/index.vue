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
          <view v-for="day in month.days" :key="day.key" :class="['heatmap-day', day.date ? heatLevel(day.count) : 'blank']">
            <text v-if="day.date" class="day-number">{{ day.day }}</text><text v-if="day.count" class="day-count">{{ day.count }}</text>
          </view>
        </view>
      </view>
    </view>
    <view v-if="card" class="card"><text class="progress">{{ card.progress.phase === 'review' ? `第 ${card.progress.round} 轮复习` : '学习进度' }} {{ card.progress.completed }} / {{ card.progress.required }} 次有效回忆</text><text class="question">{{ card.question }}</text><view v-if="showAnswer"><view class="points"><text v-for="point in keyPoints" :key="point">{{ point }}</text></view><view v-if="card.aiSummary" class="summary"><view v-for="section in summarySections" :key="section.title" class="summary-section"><text class="summary-title">{{ section.title }}：</text><text class="summary-content">{{ section.content }}</text></view></view></view></view>
    <view v-else class="empty">暂无待复习卡片，明天再来看看。</view>
    <view v-if="card" class="bottom-panel"><button v-if="!showAnswer" class="reveal" @click="showAnswer=true">显示答案</button><view v-else class="actions"><button class="again" @click="rate('again')">重来</button><button class="hard" @click="rate('hard')">困难</button><button class="good" @click="rate('good')">良好</button><button class="easy" @click="rate('easy')">简单</button></view></view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getNextReviewCard, getReviewOverview, rateReviewCard } from '@/api/exam/review'

const card = ref(null)
const showAnswer = ref(false)
const reviewOverview = ref({})
const weekdays = ['日', '一', '二', '三', '四', '五', '六']
const summarySections = computed(() => ['结论', '要点', '补充'].map(title => {
  const content = String(card.value?.aiSummary || '').match(new RegExp(`${title}：([\\s\\S]*?)(?=结论：|要点：|补充：|$)`))?.[1]?.trim() || ''
  return { title, content: title === '要点' ? content.replace(/；/g, '；\n') : content }
}).filter(section => section.content))
const keyPoints = computed(() => String(card.value?.keyPoints || '').split('；').filter(Boolean))
const completedToday = computed(() => reviewOverview.value.completedToday || 0)
const formatDate = day => `${day.getFullYear()}-${String(day.getMonth() + 1).padStart(2, '0')}-${String(day.getDate()).padStart(2, '0')}`
const heatLevel = count => count >= 30 ? 'max' : count >= 20 ? 'high' : count >= 10 ? 'mid' : count ? 'low' : ''
const heatmapMonths = computed(() => {
  const counts = Object.fromEntries((reviewOverview.value.heatmap || []).map(item => [item.date, item.count]))
  const now = new Date()
  return Array.from({ length: 3 }, (_, index) => {
    const month = new Date(now.getFullYear(), now.getMonth() - 2 + index, 1)
    const leading = month.getDay()
    const lastDay = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate()
    const days = Array.from({ length: Math.ceil((leading + lastDay) / 7) * 7 }, (_, cell) => {
      const day = cell - leading + 1
      const date = day > 0 && day <= lastDay ? new Date(month.getFullYear(), month.getMonth(), day) : null
      return { key: date ? formatDate(date) : `${month.getTime()}-${cell}`, date, day, count: date ? counts[formatDate(date)] || 0 : 0 }
    })
    return { key: `${month.getFullYear()}-${month.getMonth()}`, label: `${month.getFullYear()}年${month.getMonth() + 1}月`, days, total: days.reduce((sum, day) => sum + day.count, 0) }
  })
})

async function load() { card.value = (await getNextReviewCard()).data || null; showAnswer.value = false }
async function loadHeatmap() {
  const year = new Date().getFullYear()
  const [current, previous] = await Promise.all([getReviewOverview(year), getReviewOverview(year - 1)])
  const currentData = current.data || {}
  reviewOverview.value = { ...currentData, heatmap: [...(previous.data?.heatmap || []), ...(currentData.heatmap || [])] }
}
async function rate(value) { await rateReviewCard(card.value.cardId, value); await Promise.all([load(), loadHeatmap()]) }
onShow(() => { load().catch(() => {}); loadHeatmap().catch(() => {}) })
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb;padding:28rpx 30rpx 190rpx}.heatmap-card,.card,.empty{background:#fff;border-radius:22rpx;padding:30rpx}.heatmap-card{margin-bottom:24rpx}.heatmap-header,.month-header{display:flex;align-items:center;justify-content:space-between}.heatmap-title{display:block;color:#25324a;font-size:30rpx;font-weight:700}.heatmap-subtitle,.month-header{color:#7f8ba0;font-size:22rpx}.today-count{padding:8rpx 12rpx;border-radius:10rpx;background:#eef3ff;color:#315bd4;font-size:22rpx}.heatmap-month{margin-top:26rpx}.month-header{padding-bottom:12rpx}.weekdays,.day-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:8rpx}.weekdays{margin-bottom:8rpx;text-align:center;color:#9aa5b5;font-size:20rpx}.heatmap-day{position:relative;aspect-ratio:1;border-radius:8rpx;background:#ebedf0;color:#5d6b80}.heatmap-day.low{background:#9be9a8}.heatmap-day.mid{background:#40c463;color:#fff}.heatmap-day.high{background:#30a14e;color:#fff}.heatmap-day.max{background:#216e39;color:#fff}.heatmap-day.blank{background:transparent}.day-number{position:absolute;top:6rpx;left:8rpx;font-size:19rpx}.day-count{position:absolute;right:7rpx;bottom:5rpx;font-size:18rpx;font-weight:600}.progress{display:block;color:#748198;font-size:22rpx;margin-bottom:22rpx}.question{display:block;color:#25324a;line-height:1.6;font-size:34rpx;font-weight:700}.summary{margin-top:28rpx}.summary-section{margin-bottom:24rpx}.summary-title,.summary-content{display:block;color:#344158;font-size:25rpx;line-height:1.8}.summary-title{font-weight:700;color:#1f4c7c}.summary-content{margin-top:4rpx;white-space:pre-line}.points{display:flex;flex-wrap:wrap;gap:12rpx;margin-top:24rpx}.points text{padding:10rpx 16rpx;border-radius:10rpx;background:#e8f3ff;color:#3b78aa;font-size:22rpx}.bottom-panel{position:fixed;left:0;right:0;bottom:0;padding:18rpx 30rpx 20rpx;background:#fff;box-shadow:0 -6rpx 20rpx rgba(38,57,84,.1)}.reveal,.actions button{height:90rpx;line-height:90rpx;font-size:30rpx}.reveal{width:100%;margin:0;background:#2979ff;color:#fff}.actions{display:flex;gap:10rpx}.actions button{flex:1;margin:0;border:0}.actions .again{background:#f56c6c;color:#fff}.actions .hard{background:#e6a23c;color:#fff}.actions .good{background:#f2c94c;color:#594400}.actions .easy{background:#e8f7ea;color:#2e7d32}.empty{text-align:center;color:#8b96a8;margin-top:24rpx}
</style>
