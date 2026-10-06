<template>
  <view class="page">
    <view class="tabs"><text :class="trading.scope === 'domestic' ? 'active' : ''" @click="trading.setScope('domestic')">国内行情</text><text :class="trading.scope === 'overseas' ? 'active' : ''" @click="trading.setScope('overseas')">国际行情</text></view>
    <view class="section-title"><text>{{ trading.scope === 'domestic' ? '国内主力合约' : '国际期货合约' }}</text><text class="sub">{{ trading.quotes.length }} 个合约</text></view>
    <view class="list">
      <view v-for="quote in trading.quotes" :key="quote.code" class="quote" @click="trade(quote.code)">
        <view><view class="contract">{{ quote.name }} <text>{{ quote.code }}</text></view><text class="muted">期货主力合约</text></view>
        <view class="quote-right"><view class="price" :class="quote.change >= 0 ? 'up' : 'down'">{{ quote.price }}</view><text :class="quote.change >= 0 ? 'up' : 'down'">{{ signed(quote.change) }}%</text></view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { useTradingStore } from "@/store";
const trading = useTradingStore();
const signed = (value) => `${value >= 0 ? "+" : ""}${Number(value).toFixed(2)}`;
function trade(code) { trading.selectContract(code); uni.switchTab({ url: "/pages/work/index" }); }
trading.sync();
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb;padding:30rpx}.section-title,.quote{display:flex;justify-content:space-between;align-items:center}.tabs{display:flex;gap:44rpx;border-bottom:1rpx solid #e3e8f0;margin-bottom:28rpx}.tabs text{padding:12rpx 4rpx 18rpx;font-size:30rpx;color:#8793a5}.tabs .active{color:#294cc9;font-weight:700;border-bottom:4rpx solid #294cc9}.section-title{font-size:32rpx;font-weight:700;color:#17233d;margin:0 0 20rpx}.sub,.muted{font-size:22rpx;color:#8a96aa;font-weight:400}.list{background:#fff;border-radius:24rpx;overflow:hidden}.quote{padding:30rpx;border-bottom:1rpx solid #edf0f6}.quote:last-child{border:0}.contract{font-size:30rpx;font-weight:600;color:#1e293b}.contract text{font-size:22rpx;color:#9aa5b5;font-weight:400;margin-left:8rpx}.quote-right{text-align:right}.price{font-size:34rpx;font-weight:700;margin-bottom:8rpx}.up{color:#e44848}.down{color:#18a56c}
</style>
