<template>
  <view class="page">
    <view class="month"><text @click="changeMonth(-1)">‹</text><view><b>{{ monthLabel }}</b><small>当前月在前，仅可回看历史交易日</small></view><text :class="{ disabled: !canNext }" @click="changeMonth(1)">›</text></view>
    <view class="week"><text v-for="day in ['日','一','二','三','四','五','六']" :key="day">{{ day }}</text></view>
    <view class="calendar"><view v-for="cell in days" :key="cell.key" :class="['day', { active: selectedDate === cell.date, marked: cell.count }]" @click="selectDate(cell.date)"><text>{{ cell.day }}</text><small v-if="cell.count">{{ cell.count }} 个信号</small></view></view>
    <view class="headline"><text>{{ selectedDate ? `${selectedDate.slice(4, 6)}月${selectedDate.slice(6)}日 DDE` : '请选择信号日' }}</text><button v-if="selectedDate" @click="loadDetail">刷新</button></view>
    <view v-if="loading" class="empty">正在读取 DDE 信号…</view>
    <view v-else-if="selectedDate && !rows.length" class="empty">该日暂无可展示的 DDE 信号</view>
    <view v-else class="list"><view v-for="row in rows" :key="`${row.stockCode}-${row.signalSlot}`" class="row"><view><text class="name">{{ row.stockName }}</text><text class="code">{{ row.stockCode }} · {{ slot(row.signalSlot) }} · 信号价 {{ price(row.entryPrice) }}</text></view><view class="right"><text :class="['return', value(row) >= 0 ? 'up' : 'down']">{{ percent(value(row)) }}</text><small>{{ liveRows.get(row.stockCode) || 'T+1 收益' }}</small></view></view></view>
    <view v-if="selectedDate && rows.length" class="note">实时收益按最新行情价计算，仅覆盖上一个交易日的 DDE 信号。</view>
  </view>
</template>

<script setup>
import { computed, ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import { getDdeCalendar, getDdeQuotes, listDdeSignals } from "@/api/stock/dde";
const now = new Date(); const cursor = ref(new Date(now.getFullYear(), now.getMonth(), 1)); const calendar = ref([]); const selectedDate = ref(""); const rows = ref([]); const liveRows = ref(new Map()); const loading = ref(false);
const monthKey = computed(() => `${cursor.value.getFullYear()}${String(cursor.value.getMonth() + 1).padStart(2, "0")}`); const monthLabel = computed(() => `${cursor.value.getFullYear()} 年 ${cursor.value.getMonth() + 1} 月`);
const today = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, "0")}${String(now.getDate()).padStart(2, "0")}`; const canNext = computed(() => cursor.value.getFullYear() < now.getFullYear() || cursor.value.getMonth() < now.getMonth());
const days = computed(() => { const first = new Date(cursor.value.getFullYear(), cursor.value.getMonth(), 1).getDay(); const count = new Date(cursor.value.getFullYear(), cursor.value.getMonth() + 1, 0).getDate(); const signals = new Map(calendar.value.map(item => [item.tradeDate, item.signalCount])); return Array.from({ length: first + count }, (_, i) => { const day = i - first + 1; const date = i < first ? "" : `${monthKey.value}${String(day).padStart(2, "0")}`; return { key: date || i, day: i < first ? "" : day, date, count: signals.get(date) || 0 }; }); });
const price = value => Number(value || 0).toFixed(2); const percent = value => value === null || value === undefined ? "--" : `${Number(value) >= 0 ? "+" : ""}${Number(value).toFixed(2)}%`; const slot = value => ({ morning: "早盘", noon: "午盘", close: "尾盘" })[value] || value;
function value(row) { return row.liveT1 ?? row.t1MaxReturnPct; }
async function loadCalendar() { const response = await getDdeCalendar(monthKey.value); calendar.value = response.data || []; if (!selectedDate.value && calendar.value.length) await selectDate(calendar.value[calendar.value.length - 1].tradeDate); }
async function selectDate(date) { if (!date || date > today || !calendar.value.some(item => item.tradeDate === date)) return; selectedDate.value = date; await loadDetail(); }
async function loadDetail() { if (!selectedDate.value) return; loading.value = true; try { const response = await listDdeSignals(selectedDate.value); rows.value = response.data.rows || []; liveRows.value = new Map(); if (!rows.value.length) return; const quotes = (await getDdeQuotes(rows.value.map(row => row.stockCode))).data || []; const quoteByCode = new Map(quotes.map(item => [item.stockCode, item])); const currentDate = quotes[0]?.marketDate; if (!currentDate || selectedDate.value > currentDate) return; rows.value = rows.value.map(row => { const quote = quoteByCode.get(row.stockCode); if (!quote || !row.entryPrice) return row; liveRows.value.set(row.stockCode, selectedDate.value === currentDate ? '实时收益' : 'T+1 实时收益'); return { ...row, liveT1: (Number(quote.lastPrice) / Number(row.entryPrice) - 1) * 100 }; }); } finally { loading.value = false; } }
async function changeMonth(offset) { if (offset > 0 && !canNext.value) return; cursor.value = new Date(cursor.value.getFullYear(), cursor.value.getMonth() + offset, 1); selectedDate.value = ""; rows.value = []; await loadCalendar(); }
onShow(loadCalendar);
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb;padding:28rpx 30rpx}.month{display:flex;justify-content:space-between;align-items:center;background:#fff;border-radius:22rpx;padding:24rpx 30rpx;color:#264fc4}.month>text{font-size:50rpx}.month>text.disabled{color:#cbd3df}.month view{display:flex;flex-direction:column;align-items:center;color:#25324a}.month b{font-size:30rpx}.month small{font-size:20rpx;color:#8b96a8;margin-top:8rpx}.week,.calendar{display:grid;grid-template-columns:repeat(7,1fr);gap:8rpx}.week{margin:26rpx 0 12rpx}.week text{text-align:center;font-size:20rpx;color:#8b96a8}.day{min-height:105rpx;padding:12rpx 8rpx;box-sizing:border-box;background:#fff;border-radius:12rpx;font-size:23rpx;color:#8a96a8}.day.marked{color:#25324a;background:#eaf0ff}.day.active{background:#315bd4;color:#fff}.day small{display:block;margin-top:10rpx;font-size:17rpx}.headline{display:flex;justify-content:space-between;align-items:center;margin:34rpx 0 16rpx;font-size:30rpx;font-weight:700;color:#17233d}.headline button{margin:0;background:#edf1ff;color:#315bd4;border:0;font-size:22rpx}.row{display:flex;justify-content:space-between;align-items:center;padding:26rpx;background:#fff;border-radius:18rpx;margin-bottom:14rpx}.name,.code,.right small{display:block}.name{font-size:28rpx;font-weight:650;color:#25324a}.code,.right small{font-size:20rpx;color:#8b96a8;margin-top:9rpx}.right{text-align:right}.return{font-size:35rpx;font-weight:700}.up{color:#e44848}.down{color:#18a56c}.empty,.note{padding:48rpx 20rpx;text-align:center;border-radius:18rpx;background:#fff;color:#8b96a8;font-size:24rpx}.note{margin-top:18rpx;padding:20rpx;font-size:20rpx;line-height:1.5}
</style>
