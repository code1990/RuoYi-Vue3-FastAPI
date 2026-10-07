<template>
  <view class="page">
    <view class="quote-summary">
      <view class="quote-main"><text :class="priceClass">{{ number(quote.price) }}</text><text :class="priceClass">{{ signed(quote.change) }}%</text></view>
      <view class="quote-grid"><view><text>今开</text><b>{{ number(quote.open) }}</b></view><view><text>最高</text><b>{{ number(quote.high) }}</b></view><view><text>最低</text><b>{{ number(quote.low) }}</b></view><view><text>涨跌</text><b :class="priceClass">{{ signed(quote.amount) }}</b></view><view><text>5分涨速</text><b :class="priceClass">{{ signed(quote.speed) }}%</b></view><view><text>昨结</text><b>{{ number(quote.prevClose) }}</b></view></view>
    </view>
    <view class="contract-switch"><text @click="switchContract(-1)">‹ 上一合约</text><text>{{ code }}</text><text @click="switchContract(1)">下一合约 ›</text></view>
    <scroll-view scroll-x class="tabs" :show-scrollbar="false"><text v-for="item in periods" :key="item.value" :class="period === item.value ? 'active' : ''" @click="changePeriod(item.value)">{{ item.label }}</text></scroll-view>
    <view class="chart"><!-- #ifdef H5 --><div id="future-hqchart"></div><!-- #endif --><text v-if="error" class="error">{{ error }}</text></view>
    <scroll-view scroll-x class="tabs indicators" :show-scrollbar="false"><text v-for="item in activeIndicators" :key="item" :class="indicator === item ? 'active' : ''" @click="changeIndicator(item)">{{ item }}</text></scroll-view>
    <view class="footer"><button size="mini" @click="trade">闪电下单</button><text>数据：新华财经</text></view>
  </view>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import HQChart from "@/vendor/hqchart/umychart.uniapp.h5";
import { getFutureKline } from "@/api/future/kline";
import { useTradingStore } from "@/store";

const code = ref(""); const name = ref(""); const period = ref("1d"); const indicator = ref("MACD"); const error = ref(""); let chart;
const trading = useTradingStore(); const quote = computed(() => trading.quotes.find(item => item.code === code.value) || { name: name.value, code: code.value });
const periods = [{ label: "分时", value: "minute" }, { label: "五日", value: "5d" }, { label: "日线", value: "1d" }, { label: "周线", value: "1w" }, { label: "月线", value: "1mo" }, { label: "年线", value: "1y" }, { label: "1分", value: "1m" }, { label: "5分", value: "5m" }, { label: "15分", value: "15m" }, { label: "30分", value: "30m" }, { label: "60分", value: "60m" }];
const indicators = ["MA", "BOLL", "MACD", "KDJ", "RSI"];
const minuteIndicators = ["MACD", "KDJ", "RSI"];
const hqPeriod = { "1m": 4, "5m": 5, "15m": 6, "30m": 7, "60m": 8, "1d": 0, "1w": 1, "1mo": 2, "1y": 3 };
const apiPeriod = { 0: "1d", 1: "1w", 2: "1mo", 3: "1y", 4: "1m", 5: "5m", 6: "15m", 7: "30m", 8: "60m" };
const hqSymbol = value => String(value || "").replace(/\.XSGE$/i, ".SHFE").replace(/\.XDCE$/i, ".DCE").replace(/\.XZCE$/i, ".CZCE").replace(/\.XGFE$/i, ".GZFE").replace(/\.XCFE$/i, ".CFFEX").replace(/\.SHGE$/i, ".SHFE");
const isMinuteView = computed(() => period.value === "minute" || period.value === "5d");
const activeIndicators = computed(() => isMinuteView.value ? minuteIndicators : indicators);
function hqRows(rows) { let previous; return rows.map(item => { const text = String(item.time); const row = [Number(text.slice(0, 8)), previous ?? item.open, item.open, item.high, item.low, item.close, item.volume || 0, item.turnover || 0]; if (text.length > 8) row.push(Number(text.slice(8))); previous = item.close; return row; }); }
function fillMinuteRows(rows) {
  const byDate = new Map();
  rows.forEach(item => { const value = String(item.time); const date = value.slice(0, 8); if (!byDate.has(date)) byDate.set(date, []); byDate.get(date).push(item); });
  return [...byDate.values()].flatMap(items => {
    items.sort((left, right) => Number(left.time) - Number(right.time));
    const toMinute = value => { const time = Number(String(value).slice(8)); return Math.floor(time / 100) * 60 + time % 100; };
    const daytime = items.filter(item => toMinute(item.time) >= 540 && toMinute(item.time) <= 900);
    if (!daytime.length) return items;
    const points = new Map(daytime.map(item => [toMinute(item.time), item])); const date = String(daytime[0].time).slice(0, 8); let previous = daytime[0]; const filled = [];
    // 与新华财经及 HQChart 线材时间表一致：09:00–10:15、10:31–11:30、13:31–15:00。
    [[540, 615], [631, 690], [811, 900]].forEach(([start, end]) => { for (let minute = start; minute <= end; minute += 1) { const current = points.get(minute); if (current) previous = current; else { const hour = String(Math.floor(minute / 60)).padStart(2, "0"); const second = String(minute % 60).padStart(2, "0"); previous = { ...previous, time: Number(`${date}${hour}${second}`), open: previous.close, high: previous.close, low: previous.close, volume: 0, turnover: 0 }; } filled.push(previous); } });
    return [...items.filter(item => toMinute(item.time) < 540 || toMinute(item.time) > 900), ...filled].sort((left, right) => Number(left.time) - Number(right.time));
  });
}
function minuteData(rows) { const last = rows[rows.length - 1] || {}; const text = String(last.time || ""); return { code: 0, stock: [{ name: name.value || code.value, symbol: hqSymbol(code.value), date: Number(text.slice(0, 8)) || 0, time: Number(text.slice(8)) || 0, price: last.close || 0, open: last.open || 0, high: last.high || 0, low: last.low || 0, vol: last.volume || 0, amount: last.turnover || 0, yclose: rows[0]?.open || 0, yclearing: rows[0]?.open || 0, minute: rows.map(item => { const value = String(item.time); return { date: Number(value.slice(0, 8)), time: Number(value.slice(8)), price: item.close, open: item.open, high: item.high, low: item.low, vol: item.volume || 0, amount: item.turnover || 0, avprice: item.close }; }) }] }; }
function emptyMinute() { return minuteData([]); }
function emptyHistoryMinute() { return { code: 0, name: name.value || code.value, symbol: hqSymbol(code.value), data: [{ date: 0, close: 0, yclose: 0, yclearing: 0, minute: [] }] }; }
async function network(data, callback) {
  data.PreventDefault = true;
  const requestedPeriod = isMinuteView.value ? period.value : (apiPeriod[data?.Request?.Data?.period] || period.value);
  try { const response = await getFutureKline({ contractCode: code.value, period: requestedPeriod, count: 500 }); const rows = response.data.rows || []; if (!rows.length && data.Name === "MinuteChartContainer::RequestMinuteData") { callback(emptyMinute()); return; } if (!rows.length && data.Name === "MinuteChartContainer::RequestHistoryMinuteData") { callback(emptyHistoryMinute()); return; }
    if (data.Name === "MinuteChartContainer::RequestMinuteData") { callback(minuteData(fillMinuteRows(rows))); return; }
    if (data.Name === "MinuteChartContainer::RequestHistoryMinuteData") { const groups = new Map(); fillMinuteRows(rows).forEach(item => { const text = String(item.time); const date = Number(text.slice(0, 8)); if (!groups.has(date)) groups.set(date, []); groups.get(date).push([Number(text.slice(8)), item.open, item.close, item.high, item.low, item.volume || 0, item.turnover || 0, item.close]); }); const days = [...groups].sort(([left], [right]) => left - right).slice(-5); callback({ code: 0, name: name.value || code.value, symbol: hqSymbol(code.value), data: days.map(([date, minute]) => ({ date, close: minute[minute.length - 1][2], yclose: minute[0][1], yclearing: minute[0][1], minute })).reverse() }); return; }
    const result = { name: name.value || code.value, symbol: hqSymbol(code.value), data: hqRows(rows) }; if (requestedPeriod.endsWith("m")) result.ver = 2.0; callback(result); }
  catch { error.value = "行情暂不可用，请稍后重试"; if (data.Name === "MinuteChartContainer::RequestMinuteData") callback(emptyMinute()); else if (data.Name === "MinuteChartContainer::RequestHistoryMinuteData") callback(emptyHistoryMinute()); else callback({ name: code.value, symbol: hqSymbol(code.value), data: [] }); }
}
function windows() { return [{ Index: indicator.value === "MA" || indicator.value === "BOLL" ? indicator.value : "MA" }, { Index: indicator.value === "MA" || indicator.value === "BOLL" ? "VOL" : indicator.value }]; }
function clearChart() { chart?.ChartDestroy?.(); chart = null; // #ifdef H5
  const target = document.getElementById("future-hqchart"); while (target?.hasChildNodes()) target.removeChild(target.lastChild); // #endif
}
function createChart() {
  // #ifdef H5
  const target = document.getElementById("future-hqchart"); if (!target || chart) return; target.innerHTML = "";
  HQChart.JSChart.GetResource().FrameLogo.Text = null;
  chart = HQChart.JSChart.Init(target); const option = isMinuteView.value ? { Type: "分钟走势图", Symbol: hqSymbol(code.value), DayCount: period.value === "5d" ? 5 : 1, Windows: [{ Index: minuteIndicators.includes(indicator.value) ? indicator.value : "MACD" }], MinuteVol: { BarColorType: 0 }, Border: { Left: 0, Right: 0, Top: 0, Bottom: 20 }, IsAutoUpdate: false, IsShowRightMenu: false, NetworkFilter: network } : { Type: "历史K线图", Symbol: hqSymbol(code.value), Windows: windows(), KLine: { Period: hqPeriod[period.value], PageSize: 60, RightSpaceCount: 0 }, Border: { Left: 0, Right: 0, Top: 0, Bottom: 20 }, Frame: [{ IsShowRightText: false }, { IsShowRightText: false }], CorssCursorInfo: { Left: 0, Right: 0 }, IsAutoUpdate: false, IsShowRightMenu: false, NetworkFilter: network }; chart.SetOption(option);
  // #endif
}
function changePeriod(value) {
  period.value = value;
  if (isMinuteView.value && !minuteIndicators.includes(indicator.value)) indicator.value = "MACD";
  // ChangeDayCount 会保留旧的多日数据；切换周期必须用独立实例，防止五日图混入旧日期。
  clearChart();
  nextTick(createChart);
}
function changeIndicator(value) { indicator.value = value; if (!chart) return; if (isMinuteView.value) { chart.ChangeIndex?.(2, value); return; } chart.ChangeIndex?.(0, value === "MA" || value === "BOLL" ? value : "MA"); chart.ChangeIndex?.(1, value === "MA" || value === "BOLL" ? "VOL" : value); }
const number = value => value === null || value === undefined ? "--" : Number(value).toFixed(2);
const signed = value => value === null || value === undefined ? "--" : `${Number(value) >= 0 ? "+" : ""}${Number(value).toFixed(2)}`;
const priceClass = computed(() => Number(quote.value.change) >= 0 ? "up" : "down");
function switchContract(direction) { const contracts = trading.quotes; if (!contracts.length) return; const index = Math.max(0, contracts.findIndex(item => item.code === code.value)); const next = contracts[(index + direction + contracts.length) % contracts.length]; code.value = next.code; name.value = next.name; uni.setNavigationBarTitle({ title: next.name || next.code }); chart?.ChangeSymbol?.(hqSymbol(next.code)); }
function trade() { trading.selectContract(code.value); trading.openLightning(); uni.switchTab({ url: "/pages/work/index" }); }
onLoad(async query => { code.value = query.code || ""; name.value = query.name || ""; uni.setNavigationBarTitle({ title: name.value || code.value }); try { await trading.refreshQuotes(); } catch {} await nextTick(); createChart(); });
onBeforeUnmount(clearChart);
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb}.quote-summary{display:flex;align-items:center;background:#fff;padding:26rpx 30rpx;gap:24rpx}.quote-main{width:25%;flex:none;display:flex;flex-direction:column;gap:7rpx}.quote-main text:first-child{font-size:49rpx;font-weight:700;line-height:1}.quote-main text:last-child{font-size:25rpx;font-weight:600}.quote-grid{flex:1;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15rpx 22rpx}.quote-grid view{display:flex;justify-content:space-between;gap:8rpx;min-width:0}.quote-grid text{font-size:21rpx;color:#8b97a8;white-space:nowrap}.quote-grid b{font-size:22rpx;color:#344158;font-weight:500;text-align:right;white-space:nowrap}.quote-grid b.up,.quote-grid b.down{font-weight:600}.contract-switch{display:flex;justify-content:space-between;align-items:center;padding:12rpx 30rpx;background:#fff;border-top:1rpx solid #eef1f5;color:#8b97a8;font-size:21rpx}.contract-switch text:first-child,.contract-switch text:last-child{color:#526bba}.tabs{white-space:nowrap;background:#fff;border-top:1rpx solid #eef1f5;padding:14rpx 22rpx;box-sizing:border-box}.tabs text{display:inline-block;margin-right:28rpx;padding:10rpx 4rpx;color:#7e8b9c;font-size:26rpx}.tabs .active{color:#294cc9;border-bottom:4rpx solid #294cc9;font-weight:700}.indicators{margin-top:16rpx;border-top:0}.chart{position:relative;height:760rpx;background:#fff}.chart>div{width:100%;height:100%}.error{position:absolute;top:45%;left:0;right:0;text-align:center;color:#8b97a8;font-size:26rpx}.footer{display:flex;align-items:center;justify-content:space-between;padding:24rpx 28rpx;color:#8b97a8;font-size:22rpx}.footer button{margin:0;background:#294cc9;color:#fff;border:0}.up{color:#e44848!important}.down{color:#18a56c!important}
</style>
