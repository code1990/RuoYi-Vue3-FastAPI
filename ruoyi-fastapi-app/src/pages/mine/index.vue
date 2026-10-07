<template>
  <view class="page">
    <view class="hero"><text class="eyebrow">PAPER ACCOUNT</text><view class="label">模拟账户权益</view><view class="equity">¥ {{ format(trading.equity) }}</view><view class="funds"><view><text>可用资金</text><b>¥ {{ format(trading.cash) }}</b></view><view><text>浮动盈亏</text><b :class="trading.unrealizedPnl >= 0 ? 'up' : 'down'">{{ signed(trading.unrealizedPnl) }}</b></view></view></view>
    <view class="warning"><text class="i-mdi-shield-check-outline"></text> 仅供交易学习和策略演练，所有资产均为虚拟数据。</view>
    <view class="section">本月浮盈日历</view>
    <view class="calendar card"><view class="calendar-head"><text v-for="day in ['日','一','二','三','四','五','六']" :key="day">{{ day }}</text></view><view class="calendar-grid"><view v-for="cell in calendarDays" :key="cell.key" :class="['calendar-day', cell.value > 0 ? 'up' : cell.value < 0 ? 'down' : '']"><text>{{ cell.day }}</text><text v-if="cell.value !== null" class="calendar-value">{{ signed(cell.value) }}</text><text v-if="cell.estimated" class="calendar-estimate">预估</text></view></view></view>
    <view class="section">持仓明细</view>
    <view v-if="trading.positions.length" class="card"><view v-for="item in trading.positions" :key="item.id" class="position"><view><view class="contract">{{ item.name || item.code }} <text v-if="item.name">{{ item.code }}</text></view><text :class="item.side === '多' ? 'up' : 'down'">{{ item.side }} {{ item.quantity }} 手　开仓 {{ format(item.avgPrice) }}　最新 {{ format(item.lastPrice) }}</text><text class="detail">占用 ¥{{ format(item.margin) }}　浮盈 <text :class="item.unrealizedPnl >= 0 ? 'up' : 'down'">{{ signed(item.unrealizedPnl) }}</text></text><text v-if="!item.tradable" class="detail">{{ item.reason }}</text></view><button :disabled="!item.tradable" @click="close(item.id)">平仓</button></view></view>
    <view v-else class="empty">暂无持仓</view>
    <view class="section">最近成交</view>
    <view v-if="trading.orders.length" class="card history"><view v-for="item in trading.orders.slice(0, 6)" :key="item.id" class="order"><view><text class="contract">{{ item.name || item.code }} <text v-if="item.name">{{ item.code }}</text></text><text class="time">{{ item.time }} · {{ item.action }}{{ item.side === '多' ? '做多' : '做空' }}</text></view><view class="right"><text>{{ item.quantity }} 手 · ¥ {{ format(item.price) }}</text><text>手续费 ¥ {{ format(item.fee) }}</text><text class="time">交易所 ¥{{ format(item.exchangeFee) }} + 公司 ¥{{ format(item.brokerFee) }}</text><text v-if="item.pnl !== undefined" :class="item.pnl >= 0 ? 'up' : 'down'">已实现 {{ signed(item.pnl) }}</text></view></view></view>
    <view v-else class="empty">暂无成交记录</view>
  </view>
</template>

<script setup>
import { computed, ref } from "vue";
import { useTradingStore } from "@/store";
import { getPaperFloatingCalendar } from "@/api/future/paper-trading";
const trading = useTradingStore();
const month = new Date().toISOString().slice(0, 7); const calendarRows = ref([]);
const format = (value) => Number(value).toLocaleString("zh-CN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const signed = (value) => `${value >= 0 ? "+" : ""}${Number(value).toFixed(2)}`;
const calendarDays = computed(() => { const [year, mon] = month.split("-").map(Number); const first = new Date(year, mon - 1, 1).getDay(); const count = new Date(year, mon, 0).getDate(); const values = Object.fromEntries(calendarRows.value.map((item) => [Number(item.tradeDate.slice(-2)), item])); return Array.from({ length: first + count }, (_, index) => { const day = index - first + 1; const item = values[day]; return index < first ? { key: `blank-${index}`, day: "", value: null } : { key: day, day, value: item?.floatingPnl ?? null, estimated: item?.estimated }; }); });
async function close(id) { await trading.closePosition(id); uni.showToast({ title: "已模拟平仓", icon: "none" }); }
async function load() { await trading.sync(); try { calendarRows.value = (await getPaperFloatingCalendar(month)).data; } catch { calendarRows.value = []; } }
load();
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb;padding:30rpx}.hero{background:linear-gradient(135deg,#17275e,#4b70e6);color:#fff;padding:38rpx 34rpx;border-radius:28rpx}.eyebrow{font-size:20rpx;letter-spacing:3rpx;color:#bfcdfc}.label{font-size:26rpx;margin-top:15rpx;color:#dce5ff}.equity{font-size:56rpx;font-weight:700;margin:12rpx 0 35rpx}.funds{display:flex;border-top:1rpx solid #8197e6;padding-top:24rpx}.funds view{width:50%;display:flex;flex-direction:column;font-size:22rpx;color:#cbd7ff}.funds b{margin-top:10rpx;color:#fff;font-size:27rpx}.funds .up{color:#ffb4b4}.funds .down{color:#9cf0cd}.warning{font-size:22rpx;line-height:1.5;color:#63708a;background:#fff;padding:20rpx;border-radius:16rpx;margin-top:22rpx}.section{font-size:30rpx;font-weight:700;color:#17233d;margin:38rpx 0 18rpx}.card{background:#fff;border-radius:22rpx;overflow:hidden}.calendar{padding:18rpx}.calendar-head,.calendar-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:8rpx}.calendar-head text{text-align:center;font-size:20rpx;color:#8b96a8}.calendar-day{min-height:82rpx;padding:8rpx;box-sizing:border-box;background:#f8faff;border-radius:8rpx;font-size:20rpx;color:#69778c}.calendar-value,.calendar-estimate{display:block;margin-top:6rpx;font-size:17rpx}.calendar-estimate{color:#9aa5b5}.position,.order{display:flex;justify-content:space-between;align-items:center;padding:26rpx;border-bottom:1rpx solid #edf0f6}.position:last-child,.order:last-child{border:0}.contract{font-size:27rpx;font-weight:600;color:#25324a}.contract text,.time{font-size:21rpx;font-weight:400;color:#94a0b2}.position view>text,.detail{display:block;font-size:22rpx;margin-top:10rpx}.detail{color:#8290a5}.up{color:#e44848!important}.down{color:#18a56c!important}.position button{font-size:23rpx;color:#3659d6;background:#edf1ff;border:0;border-radius:10rpx;padding:8rpx 18rpx}.position button[disabled]{background:#c9d0dc;color:#fff}.empty{text-align:center;color:#9aa5b5;font-size:25rpx;background:#fff;border-radius:20rpx;padding:52rpx}.order{font-size:22rpx;color:#68778d}.time{display:block;margin-top:9rpx}.right{display:flex;flex-direction:column;text-align:right;gap:9rpx}
</style>
