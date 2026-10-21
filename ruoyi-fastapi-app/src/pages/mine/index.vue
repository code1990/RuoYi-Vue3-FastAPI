<template>
  <view class="page">
    <view class="grid">
      <view v-for="item in entries" :key="item.title" class="entry" hover-class="entry-hover" @click="open(item)">
        <view :class="['icon', item.tone]"><text :class="item.icon"></text></view>
        <text class="entry-title">{{ item.title }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
const entries = [
  { title: "个人", icon: "i-mdi-account-circle-outline", tone: "orange", url: "/pages/account/index" },
  { title: "资金", icon: "i-mdi-currency-usd", tone: "green", url: "/pages/dde/index" },
  { title: "融券", icon: "i-mdi-chart-timeline-variant", tone: "blue", url: "/pages/margin/index" }
];
function open(item) { uni.navigateTo({ url: item.url }); }
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb;padding:30rpx}.grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:18rpx}.entry{display:flex;flex-direction:column;align-items:center;min-width:0;padding:12rpx 0}.icon{width:76rpx;height:76rpx;display:flex;align-items:center;justify-content:center;border-radius:22rpx;font-size:43rpx}.orange{background:#fff0df;color:#d87918}.green{background:#e4f7ee;color:#16885c}.blue{background:#e8edff;color:#315bd4}.entry-title{margin-top:10rpx;font-size:20rpx;color:#536177;white-space:nowrap}
</style>
