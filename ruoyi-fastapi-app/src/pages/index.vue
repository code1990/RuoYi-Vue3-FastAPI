<template>
  <view class="page">
    <scroll-view scroll-x class="tabs" :show-scrollbar="false"><view class="tab-list"><text v-for="market in markets" :key="market.code" :class="selectedMarket === market.code ? 'active' : ''" @click="selectMarket(market)">{{ market.label }}</text></view></scroll-view>
    <view class="market-body">
      <view class="fixed-table"><view class="table-row table-head"><text class="rank" @click="sort('rank')">排名{{ sortKey === 'rank' ? (sortDesc ? ' ↓' : ' ↑') : '' }}</text><text class="contract" @click="sort('name')">名称{{ sortKey === 'name' ? (sortDesc ? ' ↓' : ' ↑') : '' }}</text></view><view v-for="(quote, index) in sortedQuotes" :key="quote.code" class="table-row" @click="trade(quote.code)"><text class="rank">{{ index + 1 }}</text><view class="contract"><text>{{ quote.name }}</text><text class="code">{{ quote.code }}</text></view></view></view>
      <scroll-view scroll-x class="market-scroll" :show-scrollbar="false"><view class="market-table"><view class="table-row table-head"><text v-for="column in columns" :key="column.key" @click="sort(column.key)">{{ column.label }}{{ sortKey === column.key ? (sortDesc ? ' ↓' : ' ↑') : '' }}</text></view><view v-for="quote in sortedQuotes" :key="quote.code" class="table-row" @click="trade(quote.code)"><text :class="color(quote.change)">{{ number(quote.price) }}</text><text :class="color(quote.change)">{{ signed(quote.change) }}%</text><text :class="color(quote.speed)">{{ signed(quote.speed) }}%</text><text :class="color(quote.amount)">{{ signed(quote.amount) }}</text><text>{{ number(quote.open) }}</text><text>{{ number(quote.high) }}</text><text>{{ number(quote.low) }}</text><text>{{ number(quote.prevClose) }}</text></view></view></scroll-view>
    </view>
  </view>
</template>

<script setup>
import { computed, ref } from "vue";
import { useTradingStore } from "@/store";
const trading = useTradingStore();
const columns = [{ key: "price", label: "现价" }, { key: "change", label: "涨幅%" }, { key: "speed", label: "涨速%" }, { key: "amount", label: "涨跌" }, { key: "open", label: "今开" }, { key: "high", label: "最高" }, { key: "low", label: "最低" }, { key: "prevClose", label: "昨收" }];
const markets = [{ code: "domestic", label: "国内", scope: "domestic" }, { code: "overseas", label: "国际", scope: "overseas" }, { code: "XSGE", label: "上期", scope: "domestic" }, { code: "XDCE", label: "大商", scope: "domestic" }, { code: "XZCE", label: "郑商", scope: "domestic" }, { code: "XGFE", label: "广期", scope: "domestic" }, { code: "SHGE", label: "上金", scope: "domestic" }, { code: "CBOT", label: "CBOT", scope: "overseas" }, { code: "CME", label: "CME", scope: "overseas" }, { code: "NYMEX", label: "NYMEX", scope: "overseas" }, { code: "COMEX", label: "COMEX", scope: "overseas" }];
const selectedMarket = ref("domestic");
const sortKey = ref("change"); const sortDesc = ref(true); const numeric = (value) => Number(value || 0);
const sortedQuotes = computed(() => trading.quotes.filter((item) => ["domestic", "overseas"].includes(selectedMarket.value) || item.market === selectedMarket.value).sort((a, b) => { if (sortKey.value === "rank") return 0; const left = a[sortKey.value]; const right = b[sortKey.value]; const result = typeof left === "string" ? String(left).localeCompare(String(right)) : numeric(left) - numeric(right); return sortDesc.value ? -result : result; }));
const number = (value) => value === null || value === undefined ? "-" : numeric(value).toFixed(2); const signed = (value) => value === null || value === undefined ? "-" : `${numeric(value) >= 0 ? "+" : ""}${numeric(value).toFixed(2)}`; const color = (value) => numeric(value) > 0 ? "up" : numeric(value) < 0 ? "down" : "";
function sort(key) { if (sortKey.value === key) sortDesc.value = !sortDesc.value; else { sortKey.value = key; sortDesc.value = true; } } async function selectMarket(market) { selectedMarket.value = market.code; await trading.setScope(market.scope); } function trade(code) { trading.selectContract(code); uni.switchTab({ url: "/pages/work/index" }); }
trading.sync();
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb;padding-top:18rpx}.tabs{width:100%;white-space:nowrap;border-bottom:1rpx solid #e3e8f0}.tab-list{display:flex;gap:42rpx;padding:0 30rpx}.tabs text{padding:14rpx 4rpx 18rpx;font-size:29rpx;color:#8793a5}.tabs .active{color:#294cc9;font-weight:700;border-bottom:4rpx solid #294cc9}.market-body{display:flex;background:#fff}.fixed-table{width:300rpx;flex:none;z-index:2;box-shadow:8rpx 0 14rpx rgba(30,45,80,.06)}.market-scroll{flex:1;min-width:0;white-space:nowrap}.market-table{min-width:1360rpx}.table-row{display:flex;align-items:center;height:88rpx;border-bottom:1rpx solid #edf0f6;font-size:23rpx;color:#344158}.table-row:active{background:#f1f5ff}.table-head{height:72rpx;background:#f8faff;color:#68778d;font-size:22rpx;font-weight:600}.rank{width:92rpx;padding-left:16rpx;box-sizing:border-box;text-align:left}.contract{width:208rpx;display:flex;flex-direction:column;overflow:hidden;white-space:nowrap}.contract text:first-child{overflow:hidden;text-overflow:ellipsis}.code{font-size:19rpx;color:#9aa5b5;margin-top:3rpx}.market-table text{width:170rpx;padding:0 12rpx;box-sizing:border-box;text-align:left;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.up{color:#e44848}.down{color:#18a56c}
</style>
