<template>
  <view class="page">
    <view class="section">
      <text class="section-title">学习</text>
      <view class="review-entry" hover-class="entry-hover" @tap="open(reviewEntry)">
        <view :class="['icon', reviewEntry.tone]"><text :class="reviewEntry.icon"></text></view>
        <view class="review-copy"><text class="review-title">今日复习</text><text class="review-hint">{{ dueCount === null ? '查看今日学习任务' : dueCount ? `待复习 ${dueCount} 题` : '今日复习已完成' }}</text></view>
        <text class="chevron">›</text>
      </view>
      <view class="learning-tools">
        <view v-for="item in learningEntries" :key="item.title" class="entry" hover-class="entry-hover" @tap="open(item)">
          <view :class="['icon', item.tone]"><text :class="item.icon"></text></view>
          <text class="entry-title">{{ item.title }}</text>
        </view>
      </view>
    </view>
    <view class="section">
      <text class="section-title">期货工具</text>
      <view class="grid">
        <view v-for="item in entries" :key="item.title" class="entry" hover-class="entry-hover" @tap="open(item)">
          <view :class="['icon', item.tone]"><text :class="item.icon"></text></view>
          <text class="entry-title">{{ item.title }}</text>
        </view>
      </view>
    </view>
    <view class="section">
      <text class="section-title">账户与设置</text>
      <view class="grid account-grid">
        <view v-for="item in accountEntries" :key="item.title" class="entry" hover-class="entry-hover" @tap="open(item)">
          <view :class="['icon', item.tone]"><text :class="item.icon"></text></view>
          <text class="entry-title">{{ item.title }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getReviewOverview } from '@/api/exam/review'

const dueCount = ref(null)
const reviewEntry = { title: "今日复习", icon: "i-mdi-school-outline", tone: "purple", url: "/pages/exam/index" };
const learningEntries = [
  { title: "学习进度", icon: "i-mdi-chart-line", tone: "purple", url: "/pages/review/index" }
];
const entries = [
  { title: "资金", icon: "i-mdi-currency-usd", tone: "green", url: "/pages/dde/index" },
  { title: "融券", icon: "i-mdi-chart-timeline-variant", tone: "blue", url: "/pages/margin/index" },
  { title: "合约关联", icon: "i-mdi-link-variant", tone: "blue", url: "/pages/index", tab: true, market: "relation" },
  { title: "盘感训练", icon: "i-mdi-target", tone: "green", url: "/pages/training/index" }
];
const accountEntries = [
  { title: "个人", icon: "i-mdi-account-circle-outline", tone: "orange", url: "/pages/account/index" }
];
function open(item) { if (item.market) uni.setStorageSync("market-tab", item.market); (item.tab ? uni.switchTab : uni.navigateTo)({ url: item.url }); }
onShow(async () => { try { dueCount.value = (await getReviewOverview()).data?.dueCount || 0 } catch {} })
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb;padding:30rpx}.section{margin-bottom:34rpx}.section-title{display:block;margin:0 0 12rpx 4rpx;color:#25324a;font-size:25rpx;font-weight:700}.grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:18rpx}.entry{display:flex;flex-direction:column;align-items:center;min-width:0;padding:12rpx 0}.review-entry{display:flex;align-items:center;padding:24rpx;border-radius:20rpx;background:#fff}.review-copy{display:flex;flex:1;flex-direction:column;margin-left:18rpx}.review-title{color:#25324a;font-size:29rpx;font-weight:700}.review-hint{margin-top:5rpx;color:#7f8ba0;font-size:22rpx}.chevron{color:#9aa5b5;font-size:42rpx}.learning-tools{display:flex;margin-top:8rpx}.learning-tools .entry{min-width:112rpx}.account-grid{grid-template-columns:repeat(5,minmax(0,1fr));justify-items:start}.icon{width:76rpx;height:76rpx;display:flex;align-items:center;justify-content:center;border-radius:22rpx;font-size:43rpx}.orange{background:#fff0df;color:#d87918}.green{background:#e4f7ee;color:#16885c}.blue{background:#e8edff;color:#315bd4}.purple{background:#f2ebff;color:#7a4dc7}.entry-title{margin-top:10rpx;font-size:20rpx;color:#536177;white-space:nowrap}
</style>
