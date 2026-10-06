<template>
  <view class="page">
    <view class="header">
      <view><text class="eyebrow">MARKET CENTER</text><view class="title">期货行情</view></view>
      <view class="refresh" @click="refresh"><text class="i-mdi-refresh"></text></view>
    </view>
    <view class="notice">服务器实时行情 · 点击合约进入模拟训练</view>
    <view class="section-title"><text>国内主力合约</text><text class="sub">{{ trading.quotes.length }} 个合约</text></view>
    <view class="list">
      <view v-for="quote in trading.quotes" :key="quote.code" class="quote" @click="trade(quote.code)">
        <view><view class="contract">{{ quote.name }} <text>{{ quote.code }}</text></view><text class="muted">期货主力合约</text></view>
        <view class="quote-right"><view class="price" :class="quote.change >= 0 ? 'up' : 'down'">{{ quote.price }}</view><text :class="quote.change >= 0 ? 'up' : 'down'">{{ signed(quote.change) }}%</text></view>
      </view>
    </view>
    <view class="tip"><text class="i-mdi-information-outline"></text> 模拟训练采用全额资金占用，不使用杠杆。</view>
  </view>
</template>

<script setup>
import { useTradingStore } from "@/store";
const trading = useTradingStore();
const signed = (value) => `${value >= 0 ? "+" : ""}${Number(value).toFixed(2)}`;
async function refresh() { await trading.refreshQuotes(); uni.showToast({ title: "账户已刷新", icon: "none" }); }
function trade(code) { trading.selectContract(code); uni.switchTab({ url: "/pages/work/index" }); }
trading.sync();
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb;padding:58rpx 30rpx}.header,.section-title,.quote{display:flex;justify-content:space-between;align-items:center}.eyebrow{font-size:20rpx;letter-spacing:3rpx;color:#7c8aa5}.title{font-size:48rpx;font-weight:700;color:#14213d;margin-top:8rpx}.refresh{width:68rpx;height:68rpx;border-radius:34rpx;background:#fff;display:flex;align-items:center;justify-content:center;color:#3454d1;font-size:36rpx}.notice{font-size:22rpx;color:#53647e;background:#eaf0ff;padding:16rpx 20rpx;border-radius:12rpx;margin:28rpx 0}.section-title{font-size:32rpx;font-weight:700;color:#17233d;margin:34rpx 0 20rpx}.sub,.muted{font-size:22rpx;color:#8a96aa;font-weight:400}.list{background:#fff;border-radius:24rpx;overflow:hidden}.quote{padding:30rpx;border-bottom:1rpx solid #edf0f6}.quote:last-child{border:0}.contract{font-size:30rpx;font-weight:600;color:#1e293b}.contract text{font-size:22rpx;color:#9aa5b5;font-weight:400;margin-left:8rpx}.quote-right{text-align:right}.price{font-size:34rpx;font-weight:700;margin-bottom:8rpx}.up{color:#e44848}.down{color:#18a56c}.tip{margin-top:28rpx;color:#7d899d;font-size:23rpx;line-height:1.7}.tip text{margin-right:8rpx}
</style>
