<template>
  <view class="page">
    <view class="card overview">
      <view><text class="title">题库学习进度</text><text class="subtitle">按题目统计，同题当天多次评级只算 1 题</text></view>
      <text class="percent">{{ bank.progressPercent || 0 }}%</text>
    </view>

    <view class="card depth-card">
      <view class="section-title"><text>题库复习深度</text><text>{{ bank.started || 0 }} / {{ total }} 题已开始学习</text></view>
      <view class="depth-content">
        <view class="donut" :style="donutStyle"><view class="donut-hole"><text>{{ total }}</text><small>题库总数</small></view></view>
        <view class="legend"><view v-for="item in levels" :key="item.key" class="legend-row"><i :style="{ background: item.color }" /><text>{{ item.label }}</text><b>{{ item.count }} 题</b></view></view>
      </view>
    </view>

    <view class="card">
      <view class="section-title"><text>最近 30 天学习量</text><text>日均 {{ recent.averageDailyStudied || 0 }} 题</text></view>
      <view class="summary"><view><b>{{ recent.newCards || 0 }}</b><small>新学题数</small></view><view><b>{{ recent.reviewedCards || 0 }}</b><small>复习题数</small></view><view><b>{{ recent.studiedCards || 0 }}</b><small>学习题数</small></view></view>
      <view class="estimate"><text>完成首轮覆盖</text><b v-if="recent.estimatedCoverageDays !== null && recent.estimatedCoverageDays !== undefined">约 {{ recent.estimatedCoverageDays }} 天</b><text v-else>完成更多新题后估算</text></view>
    </view>

    <view class="card daily-card">
      <view class="section-title"><text>每天学习了多少题</text><text>新学 + 复习 = 合计</text></view>
      <view v-for="day in dailyDays" :key="day.date" class="daily-row"><text>{{ day.date.slice(5) }}</text><text>新学 {{ day.newCards }} 题</text><text>复习 {{ day.reviewedCards }} 题</text><b>{{ day.studiedCards }} 题</b></view>
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
const dailyDays = computed(() => [...(recent.value.days || [])].reverse())

async function load() { progress.value = (await getReviewProgress()).data || {} }

onShow(() => { load().catch(() => {}) })
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb;padding:28rpx 30rpx}.card{margin-bottom:20rpx;padding:28rpx;background:#fff;border-radius:22rpx}.overview,.section-title,.summary,.estimate,.daily-row{display:flex;align-items:center;justify-content:space-between}.title{display:block;color:#25324a;font-size:32rpx;font-weight:700}.subtitle,.section-title,.estimate,.daily-row{color:#7f8ba0;font-size:22rpx}.percent{color:#315bd4;font-size:44rpx;font-weight:700}.section-title{padding-bottom:22rpx}.section-title>text:first-child{color:#25324a;font-size:28rpx;font-weight:700}.depth-content{display:flex;align-items:center;gap:30rpx}.donut{position:relative;flex:none;width:210rpx;height:210rpx;border-radius:50%}.donut-hole{position:absolute;inset:35rpx;display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:50%;background:#fff;color:#25324a}.donut-hole text{font-size:34rpx;font-weight:700}.donut-hole small,.summary small{margin-top:4rpx;color:#8d98aa;font-size:19rpx}.legend{flex:1}.legend-row{display:flex;align-items:center;gap:10rpx;margin:10rpx 0;font-size:22rpx;color:#59677e}.legend-row i{width:16rpx;height:16rpx;border-radius:50%}.legend-row b{margin-left:auto;color:#25324a;font-weight:600}.summary{gap:10rpx}.summary view{flex:1;display:flex;flex-direction:column;align-items:center;padding:16rpx 4rpx;border-radius:12rpx;background:#f6f8fc}.summary b{color:#25324a;font-size:34rpx}.estimate{margin-top:20rpx;padding:18rpx 20rpx;border-radius:12rpx;background:#edf2ff;color:#536177}.estimate b{color:#315bd4;font-size:26rpx}.daily-card{padding-bottom:8rpx}.daily-row{min-height:70rpx;border-top:1rpx solid #edf0f6}.daily-row text:nth-child(2){color:#b87919}.daily-row text:nth-child(3){color:#27866e}.daily-row b{color:#25324a;font-size:24rpx}
</style>
