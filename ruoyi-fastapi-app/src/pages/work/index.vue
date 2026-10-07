<template>
  <view class="page">
    <view class="card quote-card">
      <view class="contract">{{ quote.name }} <text>{{ quote.code }}</text></view>
      <view class="price" :class="quote.change >= 0 ? 'up' : 'down'">{{ quote.price }}</view>
      <text :class="quote.change >= 0 ? 'up' : 'down'">{{ signed(quote.change) }}%</text>
      <view class="picker"><text v-for="item in trading.quotes" :key="item.code" :class="item.code === quote.code ? 'active' : ''" @click="selectContract(item.code)">{{ item.code }}</text></view>
    </view>
    <view class="card order">
      <view class="label">下单手数</view>
      <view class="quantity"><text @click="change(-1)">−</text><input v-model="quantity" type="number" /><text @click="change(1)">＋</text></view>
      <view class="estimate">预计占用资金 ¥ {{ format(margin) }}　·　无杠杆训练</view>
      <text v-if="!canTrade" class="trade-disabled">{{ tradeStatus.reason }}</text><view class="actions"><button class="short" :disabled="!canTrade" @click="submit('空')">卖出开空</button><button class="long" :disabled="!canTrade" @click="submit('多')">买入开多</button></view>
    </view>
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
const tradeStatus = ref({ tradable: false, reason: "正在读取交易状态" });
const canTrade = computed(() => tradeStatus.value.tradable);
const margin = computed(() => quote.value.price * quote.value.multiplier * Number(quantity.value || 0));
const format = (value) => Number(value).toLocaleString("zh-CN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const signed = (value) => `${value >= 0 ? "+" : ""}${Number(value).toFixed(2)}`;
function change(delta) { quantity.value = Math.max(1, Number(quantity.value || 1) + delta); }
async function refreshStatus() { if (!quote.value?.code) return; try { tradeStatus.value = (await getPaperTradingStatus(quote.value.code)).data; } catch { tradeStatus.value = { tradable: false, reason: "交易状态暂不可用" }; } }
function selectContract(code) { trading.selectContract(code); refreshStatus(); }
function confirmOpen(side) { const action = side === "多" ? "买入开多" : "卖出开空"; return new Promise((resolve) => uni.showModal({ title: "确认模拟开仓", content: `${quote.value.name} ${quote.value.code}\n${action} ${quantity.value} 手\n占用 ¥ ${format(margin.value)}`, confirmText: "确认开仓", success: ({ confirm }) => resolve(confirm), fail: () => resolve(false) })); }
async function submit(side) { if (!canTrade.value || !await confirmOpen(side)) return; await trading.openPosition(side, quantity.value); await refreshStatus(); uni.showToast({ title: `已模拟开${side}`, icon: "success" }); }
async function close(id) { await trading.closePosition(id); uni.showToast({ title: "已模拟平仓", icon: "none" }); }
trading.sync().then(refreshStatus);
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb;padding:28rpx 30rpx}.card{background:#fff;border-radius:24rpx;padding:30rpx;margin-bottom:28rpx}.quote-card{position:relative}.contract{font-size:30rpx;font-weight:650;color:#1e293b}.contract text{font-size:22rpx;color:#9aa5b5;font-weight:400}.price{font-size:54rpx;font-weight:700;margin:22rpx 0 8rpx}.up{color:#e44848}.down{color:#18a56c}.picker{display:flex;gap:14rpx;margin-top:30rpx;overflow:auto}.picker text{font-size:21rpx;background:#f1f4f9;padding:10rpx 15rpx;border-radius:10rpx;color:#718097;white-space:nowrap}.picker .active{background:#e8edff;color:#3556d4}.label{font-size:26rpx;color:#4a5568}.quantity{display:flex;align-items:center;justify-content:space-between;border:1rpx solid #e5eaf2;border-radius:14rpx;margin:18rpx 0;padding:0 22rpx;height:82rpx}.quantity text{font-size:42rpx;color:#3659d6}.quantity input{text-align:center;font-size:32rpx;font-weight:600}.estimate{font-size:22rpx;color:#8b96a8;margin-bottom:26rpx}.trade-disabled{display:block;margin:-8rpx 0 18rpx;color:#98a2b3;font-size:22rpx}.actions{display:flex;gap:18rpx}.actions button{flex:1;color:white;border:0;border-radius:14rpx;font-size:28rpx}.actions button[disabled],.position button[disabled]{background:#c9d0dc;color:#fff}.short{background:#1fa76d}.long{background:#e44848}.section{display:flex;justify-content:space-between;align-items:center;font-size:30rpx;font-weight:700;color:#17233d;margin:38rpx 0 18rpx}.sub{font-size:22rpx;color:#8290a5;font-weight:400}.positions{padding:0}.position{display:flex;justify-content:space-between;align-items:center;padding:27rpx 30rpx;border-bottom:1rpx solid #edf0f6}.side,.detail{font-size:22rpx;display:block;margin-top:9rpx}.detail{color:#8290a5}.position button{font-size:23rpx;color:#3659d6;background:#edf1ff;border:0;border-radius:10rpx;padding:8rpx 18rpx}.empty{color:#9aa5b5;text-align:center;font-size:25rpx;padding:75rpx 0}
</style>
