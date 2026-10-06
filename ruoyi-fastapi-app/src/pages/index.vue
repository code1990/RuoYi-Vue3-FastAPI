<template>
  <view class="page">
    <view class="tabs"><text :class="trading.scope === 'domestic' ? 'active' : ''" @click="trading.setScope('domestic')">国内</text><text :class="trading.scope === 'overseas' ? 'active' : ''" @click="trading.setScope('overseas')">国际</text></view>
    <scroll-view scroll-x class="market-scroll" :show-scrollbar="false">
      <view class="market-table">
        <view class="table-row table-head"><text v-for="column in columns" :key="column.key" :class="column.class" @click="sort(column.key)">{{ column.label }}{{ sortKey === column.key ? (sortDesc ? ' ↓' : ' ↑') : '' }}</text></view>
        <view v-for="(quote, index) in sortedQuotes" :key="quote.code" class="table-row" @click="trade(quote.code)"><text class="rank">{{ index + 1 }}</text><text class="code">{{ quote.code }}</text><text class="name">{{ quote.name }}</text><text :class="['price', color(quote.change)]">{{ number(quote.price) }}</text><text :class="['number', color(quote.change)]">{{ signed(quote.change) }}%</text><text :class="['number', color(quote.speed)]">{{ signed(quote.speed) }}%</text><text :class="['number', color(quote.amount)]">{{ signed(quote.amount) }}</text><text class="number">{{ number(quote.open) }}</text><text class="number">{{ number(quote.high) }}</text><text class="number">{{ number(quote.low) }}</text><text class="number">{{ number(quote.prevClose) }}</text></view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { computed, ref } from "vue";
import { useTradingStore } from "@/store";
const trading = useTradingStore();
const columns = [{ key: "rank", label: "排名", class: "rank" }, { key: "code", label: "代码", class: "code" }, { key: "name", label: "名称", class: "name" }, { key: "price", label: "现价", class: "price" }, { key: "change", label: "涨幅%", class: "number" }, { key: "speed", label: "涨速%", class: "number" }, { key: "amount", label: "涨跌", class: "number" }, { key: "open", label: "今开", class: "number" }, { key: "high", label: "最高", class: "number" }, { key: "low", label: "最低", class: "number" }, { key: "prevClose", label: "昨收", class: "number" }];
const sortKey = ref("change"); const sortDesc = ref(true);
const numeric = (value) => Number(value || 0);
const sortedQuotes = computed(() => [...trading.quotes].sort((a, b) => { if (sortKey.value === "rank") return 0; const left = a[sortKey.value]; const right = b[sortKey.value]; const result = typeof left === "string" ? String(left).localeCompare(String(right)) : numeric(left) - numeric(right); return sortDesc.value ? -result : result; }));
const number = (value) => value === null || value === undefined ? "-" : numeric(value).toFixed(2);
const signed = (value) => value === null || value === undefined ? "-" : `${numeric(value) >= 0 ? "+" : ""}${numeric(value).toFixed(2)}`;
const color = (value) => numeric(value) > 0 ? "up" : numeric(value) < 0 ? "down" : "";
function sort(key) { if (sortKey.value === key) sortDesc.value = !sortDesc.value; else { sortKey.value = key; sortDesc.value = true; } }
function trade(code) { trading.selectContract(code); uni.switchTab({ url: "/pages/work/index" }); }
trading.sync();
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb;padding-top:18rpx}.tabs{display:flex;gap:48rpx;padding:0 30rpx;border-bottom:1rpx solid #e3e8f0}.tabs text{padding:14rpx 4rpx 18rpx;font-size:29rpx;color:#8793a5}.tabs .active{color:#294cc9;font-weight:700;border-bottom:4rpx solid #294cc9}.market-scroll{width:100%;white-space:nowrap}.market-table{min-width:1870rpx;background:#fff}.table-row{display:flex;align-items:center;min-height:78rpx;border-bottom:1rpx solid #edf0f6;font-size:23rpx;color:#344158}.table-row:active{background:#f1f5ff}.table-row text{padding:0 12rpx;box-sizing:border-box;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.table-head{position:sticky;left:0;background:#f8faff;color:#68778d;font-size:22rpx;font-weight:600}.rank{width:100rpx;text-align:center}.code{width:185rpx}.name{width:230rpx}.price{width:170rpx;text-align:right;font-weight:600}.number{width:170rpx;text-align:right}.up{color:#e44848}.down{color:#18a56c}
</style>
