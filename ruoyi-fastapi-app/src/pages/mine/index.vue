<template>
  <view class="page">
    <view class="hero">
      <text class="eyebrow">MARKETPLACE</text>
      <text class="title">商城</text>
      <text class="subtitle">把常用的模拟交易功能放在一起</text>
    </view>

    <view class="section-title">功能入口</view>
    <view class="grid">
      <view v-for="item in entries" :key="item.title" class="entry" @click="open(item)">
        <view :class="['icon', item.tone]"><text :class="item.icon"></text></view>
        <text class="entry-title">{{ item.title }}</text>
        <text class="entry-desc">{{ item.desc }}</text>
      </view>
    </view>

    <view class="tip"><text class="i-mdi-information-outline"></text> 商城目前用于集中入口，所有功能仍使用原有模拟交易数据。</view>
  </view>
</template>

<script setup>
const entries = [
  { title: "模拟下单", desc: "快速开仓与平仓", icon: "i-mdi-flash-outline", tone: "blue", tab: "/pages/work/index" },
  { title: "资产总览", desc: "权益、持仓与盈亏", icon: "i-mdi-wallet-outline", tone: "orange", url: "/pages/account/index" },
  { title: "盘感训练", desc: "每日交易决策练习", icon: "i-mdi-brain", tone: "purple", tab: "/pages/training/index" },
  { title: "考试复习", desc: "复习交易知识点", icon: "i-mdi-notebook-outline", tone: "green", tab: "/pages/exam/index" },
  { title: "行情分析", desc: "选择合约查看 K 线", icon: "i-mdi-chart-line", tone: "red", tab: "/pages/index" }
];
function open(item) { item.tab ? uni.switchTab({ url: item.tab }) : uni.navigateTo({ url: item.url }); }
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb;padding:30rpx}.hero{padding:40rpx 36rpx;border-radius:28rpx;background:#173b8f;color:#fff}.eyebrow{display:block;font-size:20rpx;letter-spacing:3rpx;color:#adc8ff}.title{display:block;margin-top:12rpx;font-size:54rpx;font-weight:700}.subtitle{display:block;margin-top:14rpx;font-size:25rpx;color:#d9e6ff}.section-title{margin:38rpx 0 18rpx;font-size:30rpx;font-weight:700;color:#17233d}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18rpx}.entry{min-height:220rpx;box-sizing:border-box;padding:26rpx;background:#fff;border-radius:22rpx}.entry:active{background:#eef3ff}.icon{width:68rpx;height:68rpx;display:flex;align-items:center;justify-content:center;border-radius:20rpx;font-size:38rpx}.blue{background:#e8efff;color:#2856c7}.orange{background:#fff0df;color:#d87918}.purple{background:#f0eaff;color:#7551c8}.green{background:#e4f7ee;color:#16885c}.red{background:#ffe8e8;color:#d64b4b}.entry-title,.entry-desc{display:block}.entry-title{margin-top:20rpx;font-size:28rpx;font-weight:650;color:#26334d}.entry-desc{margin-top:8rpx;font-size:21rpx;color:#8a96a8;line-height:1.4}.tip{margin-top:26rpx;padding:20rpx;border-radius:16rpx;background:#fff;color:#718097;font-size:22rpx;line-height:1.5}.tip text{color:#3556d4}
</style>
