<template>
  <view class="page">
    <view class="card quote-card">
      <view class="contract">{{ quote.name }} <text>{{ quote.code }}</text></view>
      <view class="price" :class="quote.change >= 0 ? 'up' : 'down'">{{ quote.price }}</view>
      <text :class="quote.change >= 0 ? 'up' : 'down'">{{ signed(quote.change) }}%</text>
      <view class="picker"><text v-for="item in trading.quotes" :key="item.code" :class="item.code === quote.code ? 'active' : ''" @click="selectContract(item.code)">{{ item.code }}</text></view>
    </view>
    <view class="card lightning lightning-page"><text class="margin">1 手保证金 ¥ {{ format(oneMargin) }}</text><view class="quick-controls"><view class="price-mode"><text>−</text><b>对手价</b><text>＋</text></view><view class="stepper"><text @click="change(-1)">−</text><b>{{ quantity }} 手</b><text @click="change(1)">＋</text></view></view><view class="limits"><text>跌停 {{ format(quote.limitDown) }}</text><text>价格 {{ format(quote.price) }}</text><text>涨停 {{ format(quote.limitUp) }}</text><text>最多 {{ maxLots }} 手</text></view><text v-if="!canTrade" class="trade-disabled">{{ tradeStatus.reason }}</text><view class="lightning-actions"><button class="long" :disabled="!canTrade" @click="submit('多')"><text>{{ format(quote.price) }}</text><text>加多</text></button><button class="short" :disabled="!canTrade || !activePositions.length" @click="lock"><text>{{ format(quote.price) }}</text><text>锁单</text></button><button class="close" :disabled="!canTrade || !activePositions.length" @click="closeCurrent"><text>{{ format(quote.price) }}</text><text>平仓</text></button></view></view>
    <view class="section"><text>当前持仓</text><text class="sub">可用 ¥ {{ format(trading.cash) }}</text></view>
    <view v-if="trading.positions.length" class="card positions"><view v-for="item in trading.positions" :key="item.id" class="position"><view><view class="contract">{{ item.name || item.code }} <text v-if="item.name">{{ item.code }}</text></view><text class="side" :class="item.side === '多' ? 'up' : 'down'">{{ item.side }} {{ item.quantity }} 手</text><text class="detail">开仓 {{ format(item.avgPrice) }}　最新 {{ format(item.lastPrice) }}</text><text class="detail">占用 ¥{{ format(item.margin) }}　浮盈 <text :class="item.unrealizedPnl >= 0 ? 'up' : 'down'">{{ signed(item.unrealizedPnl) }}</text></text><text v-if="!item.tradable" class="detail">{{ item.reason }}</text></view><button :disabled="!item.tradable" @click="close(item.id)">平仓</button></view></view>
    <view v-else class="empty">暂无持仓，选择合约后开始模拟交易</view>
  </view>
</template>

<script setup>
import { computed, ref } from "vue";
import { useTradingStore } from "@/store";
import { getPaperTradingStatus } from "@/api/future/paper-trading";
const trading = useTradingStore();
const quantity = ref(1);
const quote = computed(() => trading.selectedQuote);
const activePositions = computed(() => trading.positions.filter((item) => item.code === quote.value?.code));
const tradeStatus = ref({ tradable: false, reason: "正在读取交易状态" });
const canTrade = computed(() => tradeStatus.value.tradable);
const margin = computed(() => quote.value.price * quote.value.multiplier * Number(quantity.value || 0));
const oneMargin = computed(() => quote.value.price * quote.value.multiplier);
const maxLots = computed(() => Math.floor(trading.cash / (oneMargin.value || 1)));
const format = (value) => value === null || value === undefined ? "--" : Number(value).toLocaleString("zh-CN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const signed = (value) => `${value >= 0 ? "+" : ""}${Number(value).toFixed(2)}`;
function change(delta) { quantity.value = Math.max(1, Number(quantity.value || 1) + delta); }
async function refreshStatus() { if (!quote.value?.code) return; try { tradeStatus.value = (await getPaperTradingStatus(quote.value.code)).data; } catch { tradeStatus.value = { tradable: false, reason: "交易状态暂不可用" }; } }
function selectContract(code) { trading.selectContract(code); refreshStatus(); }
function confirmOpen(side) { const action = side === "多" ? "买入开多" : "卖出开空"; return new Promise((resolve) => uni.showModal({ title: "确认模拟开仓", content: `${quote.value.name} ${quote.value.code}\n${action} ${quantity.value} 手\n占用 ¥ ${format(margin.value)}`, confirmText: "确认开仓", success: ({ confirm }) => resolve(confirm), fail: () => resolve(false) })); }
async function submit(side) { if (!canTrade.value || !await confirmOpen(side)) return; await trading.openPosition(side, quantity.value); await refreshStatus(); uni.showToast({ title: `已模拟开${side}`, icon: "success" }); }
async function lock() { const position = activePositions.value[0]; if (position) await submit(position.side === "多" ? "空" : "多"); }
async function closeCurrent() { for (const position of activePositions.value) await close(position.id); }
async function close(id) { await trading.closePosition(id); uni.showToast({ title: "已模拟平仓", icon: "none" }); }
trading.sync().then(refreshStatus);
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb;padding:28rpx 30rpx}.card{background:#fff;border-radius:24rpx;padding:30rpx;margin-bottom:28rpx}.quote-card{position:relative}.contract{font-size:30rpx;font-weight:650;color:#1e293b}.contract text{font-size:22rpx;color:#9aa5b5;font-weight:400}.price{font-size:54rpx;font-weight:700;margin:22rpx 0 8rpx}.up{color:#e44848}.down{color:#18a56c}.picker{display:flex;gap:14rpx;margin-top:30rpx;overflow:auto}.picker text{font-size:21rpx;background:#f1f4f9;padding:10rpx 15rpx;border-radius:10rpx;color:#718097;white-space:nowrap}.picker .active{background:#e8edff;color:#3556d4}.margin{display:block;font-size:22rpx;color:#68778d}.quick-controls,.limits,.lightning-actions{display:flex;gap:12rpx;margin-top:14rpx}.price-mode,.stepper{flex:1;display:flex;justify-content:space-between;align-items:center;background:#f4f6fa;border-radius:10rpx;padding:10rpx 16rpx;font-size:22rpx}.price-mode text,.stepper text{font-size:30rpx;color:#3556d4}.limits{justify-content:space-between;font-size:19rpx;color:#69778c}.lightning-actions button{flex:1;height:92rpx;color:#fff;border:0;border-radius:10rpx;font-size:24rpx}.lightning-actions button text{display:block;font-size:20rpx;line-height:1.5}.lightning-actions button[disabled]{opacity:.55}.lightning-actions button[disabled].long{background:#e44848}.lightning-actions button[disabled].short{background:#18a56c}.lightning-actions button[disabled].close{background:#3556d4}.short{background:#18a56c}.long{background:#e44848}.close{background:#3556d4}.trade-disabled{display:block;font-size:22rpx;color:#8b96a8;margin-top:8rpx}.section{display:flex;justify-content:space-between;align-items:center;font-size:30rpx;font-weight:700;color:#17233d;margin:38rpx 0 18rpx}.sub{font-size:22rpx;color:#8290a5;font-weight:400}.positions{padding:0}.position{display:flex;justify-content:space-between;align-items:center;padding:27rpx 30rpx;border-bottom:1rpx solid #edf0f6}.side,.detail{font-size:22rpx;display:block;margin-top:9rpx}.detail{color:#8290a5}.position button{font-size:23rpx;color:#3659d6;background:#edf1ff;border:0;border-radius:10rpx;padding:8rpx 18rpx}.position button[disabled]{background:#c9d0dc;color:#fff}.empty{color:#9aa5b5;text-align:center;font-size:25rpx;padding:75rpx 0}
</style>
