<template>
  <view class="page">
    <view class="hero"><text class="eyebrow">PAPER ACCOUNT</text><view class="label">模拟账户权益</view><view class="equity">¥ {{ format(trading.equity) }}</view><view class="funds"><view><text>可用资金</text><b>¥ {{ format(trading.cash) }}</b></view><view><text>浮动盈亏</text><b :class="trading.unrealizedPnl >= 0 ? 'up' : 'down'">{{ signed(trading.unrealizedPnl) }}</b></view></view></view>
    <view class="warning"><text class="i-mdi-shield-check-outline"></text> 仅供交易学习和策略演练，所有资产均为虚拟数据。</view>
    <view class="section">持仓明细</view>
    <view v-if="trading.positions.length" class="card"><view v-for="item in trading.positions" :key="item.id" class="position"><view><view class="contract">{{ item.name }} <text>{{ item.code }}</text></view><text :class="item.side === '多' ? 'up' : 'down'">{{ item.side }} {{ item.quantity }} 手　均价 {{ item.avgPrice.toFixed(2) }}</text></view><button @click="close(item.id)">平仓</button></view></view>
    <view v-else class="empty">暂无持仓</view>
    <view class="section">最近成交</view>
    <view v-if="trading.orders.length" class="card history"><view v-for="item in trading.orders.slice(0, 6)" :key="item.id" class="order"><view><text class="contract">{{ item.type }} {{ item.name }}</text><text class="time">{{ item.time }}</text></view><view class="right"><text>{{ item.quantity }} 手 · {{ item.price }}</text><text v-if="item.pnl !== undefined" :class="item.pnl >= 0 ? 'up' : 'down'">{{ signed(item.pnl) }}</text></view></view></view>
    <view v-else class="empty">暂无成交记录</view>
    <button class="reset" @click="confirmReset">重置模拟账户</button>
  </view>
</template>

<script setup>
import { useTradingStore } from "@/store";
const trading = useTradingStore();
const format = (value) => Number(value).toLocaleString("zh-CN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const signed = (value) => `${value >= 0 ? "+" : ""}${Number(value).toFixed(2)}`;
async function close(id) { await trading.closePosition(id); uni.showToast({ title: "已模拟平仓", icon: "none" }); }
function confirmReset() { uni.showToast({ title: "线上账户不支持客户端重置", icon: "none" }); }
trading.sync();
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb;padding:30rpx}.hero{background:linear-gradient(135deg,#17275e,#4b70e6);color:#fff;padding:38rpx 34rpx;border-radius:28rpx}.eyebrow{font-size:20rpx;letter-spacing:3rpx;color:#bfcdfc}.label{font-size:26rpx;margin-top:15rpx;color:#dce5ff}.equity{font-size:56rpx;font-weight:700;margin:12rpx 0 35rpx}.funds{display:flex;border-top:1rpx solid #8197e6;padding-top:24rpx}.funds view{width:50%;display:flex;flex-direction:column;font-size:22rpx;color:#cbd7ff}.funds b{margin-top:10rpx;color:#fff;font-size:27rpx}.funds .up{color:#ffb4b4}.funds .down{color:#9cf0cd}.warning{font-size:22rpx;line-height:1.5;color:#63708a;background:#fff;padding:20rpx;border-radius:16rpx;margin-top:22rpx}.section{font-size:30rpx;font-weight:700;color:#17233d;margin:38rpx 0 18rpx}.card{background:#fff;border-radius:22rpx;overflow:hidden}.position,.order{display:flex;justify-content:space-between;align-items:center;padding:26rpx;border-bottom:1rpx solid #edf0f6}.position:last-child,.order:last-child{border:0}.contract{font-size:27rpx;font-weight:600;color:#25324a}.contract text,.time{font-size:21rpx;font-weight:400;color:#94a0b2}.position view>text{display:block;font-size:22rpx;margin-top:10rpx}.up{color:#e44848!important}.down{color:#18a56c!important}.position button{font-size:23rpx;color:#3659d6;background:#edf1ff;border:0;border-radius:10rpx;padding:8rpx 18rpx}.empty{text-align:center;color:#9aa5b5;font-size:25rpx;background:#fff;border-radius:20rpx;padding:52rpx}.order{font-size:22rpx;color:#68778d}.time{display:block;margin-top:9rpx}.right{display:flex;flex-direction:column;text-align:right;gap:9rpx}.reset{margin:42rpx 0 25rpx;background:#fff;color:#d35c5c;border:1rpx solid #f1cccc;border-radius:14rpx;font-size:26rpx}
</style>
