<template>
  <view class="page">
    <view class="contract"><text>{{ name || code }}</text><text>{{ code }}</text></view>
    <scroll-view scroll-x class="tabs" :show-scrollbar="false"><text v-for="item in periods" :key="item.value" :class="period === item.value ? 'active' : ''" @click="changePeriod(item.value)">{{ item.label }}</text></scroll-view>
    <scroll-view scroll-x class="tabs indicators" :show-scrollbar="false"><text v-for="item in indicators" :key="item" :class="indicator === item ? 'active' : ''" @click="changeIndicator(item)">{{ item }}</text></scroll-view>
    <view class="chart"><!-- #ifdef H5 --><canvas id="future-kline-canvas"></canvas><!-- #endif --><!-- #ifndef H5 --><text>技术分析仅在 H5 版提供</text><!-- #endif --><text v-if="error" class="error">{{ error }}</text></view>
    <view class="footer"><button size="mini" @click="trade">模拟交易</button><text>数据：新华财经</text></view>
  </view>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { getFutureKline } from "@/api/future/kline";

const code = ref(""); const name = ref(""); const period = ref("1d"); const indicator = ref("MACD"); const error = ref("");
const rows = ref([]); let resizeHandler;
const periods = [{ label: "1分", value: "1m" }, { label: "5分", value: "5m" }, { label: "15分", value: "15m" }, { label: "30分", value: "30m" }, { label: "60分", value: "60m" }, { label: "日", value: "1d" }, { label: "周", value: "1w" }, { label: "月", value: "1mo" }];
const indicators = ["MA", "BOLL", "MACD", "KDJ", "RSI"];
const average = (values, count, index) => index + 1 < count ? null : values.slice(index - count + 1, index + 1).reduce((total, item) => total + item, 0) / count;
const line = (ctx, points, color, width = 1) => { ctx.beginPath(); points.forEach((point, index) => index ? ctx.lineTo(point.x, point.y) : ctx.moveTo(point.x, point.y)); ctx.strokeStyle = color; ctx.lineWidth = width; ctx.stroke(); };

function render() {
  // #ifdef H5
  const canvas = document.getElementById("future-kline-canvas"); if (!canvas || !rows.value.length) return;
  const rect = canvas.getBoundingClientRect(); const ratio = window.devicePixelRatio || 1; const width = rect.width; const height = rect.height;
  canvas.width = width * ratio; canvas.height = height * ratio; const ctx = canvas.getContext("2d"); ctx.scale(ratio, ratio); ctx.clearRect(0, 0, width, height);
  const data = rows.value.slice(-100); const closes = data.map(item => Number(item.close)); const left = 8; const right = 46; const top = 12; const mainBottom = height * .67; const bottom = height - 22;
  const min = Math.min(...data.map(item => Number(item.low))); const max = Math.max(...data.map(item => Number(item.high))); const range = max - min || 1;
  const x = index => left + (width - left - right) * (index + .5) / data.length; const y = value => mainBottom - (Number(value) - min) / range * (mainBottom - top);
  ctx.font = "11px sans-serif"; ctx.fillStyle = "#8b97a8"; ctx.strokeStyle = "#edf0f4"; ctx.lineWidth = 1;
  for (let i = 0; i < 5; i++) { const py = top + (mainBottom - top) * i / 4; ctx.beginPath(); ctx.moveTo(left, py); ctx.lineTo(width - right, py); ctx.stroke(); ctx.fillText((max - range * i / 4).toFixed(2), width - right + 3, py + 3); }
  const body = Math.max(2, (width - left - right) / data.length * .62);
  data.forEach((item, index) => { const up = Number(item.close) >= Number(item.open); const color = up ? "#e34d59" : "#20a162"; const px = x(index); ctx.strokeStyle = color; ctx.beginPath(); ctx.moveTo(px, y(item.high)); ctx.lineTo(px, y(item.low)); ctx.stroke(); ctx.fillStyle = color; const openY = y(item.open); const closeY = y(item.close); ctx.fillRect(px - body / 2, Math.min(openY, closeY), body, Math.max(1, Math.abs(closeY - openY))); });
  if (indicator.value === "MA" || indicator.value === "BOLL") {
    const series = indicator.value === "MA" ? [[5, "#f2a93b"], [10, "#5886f0"], [20, "#9b59b6"]] : [[20, "#5886f0"]];
    series.forEach(([count, color]) => line(ctx, closes.map((_, index) => ({ x: x(index), y: y(average(closes, count, index) ?? closes[index]) })), color));
  }
  const values = indicator.value === "MACD" ? closes.map((value, index) => value - (average(closes, 12, index) ?? value)) : indicator.value === "KDJ" ? closes.map((value, index) => { const sample = closes.slice(Math.max(0, index - 8), index + 1); return (value - Math.min(...sample)) / ((Math.max(...sample) - Math.min(...sample)) || 1) * 100; }) : closes.map((value, index) => { const previous = closes[index - 1] ?? value; return 50 + (value - previous) / (Math.abs(value - previous) || 1) * 20; });
  const subTop = mainBottom + 16; const subMin = Math.min(...values); const subRange = Math.max(...values) - subMin || 1; const subY = value => bottom - (value - subMin) / subRange * (bottom - subTop);
  ctx.fillStyle = "#8b97a8"; ctx.fillText(indicator.value, left, subTop - 4); line(ctx, values.map((value, index) => ({ x: x(index), y: subY(value) })), "#5886f0", 1.2);
  ctx.fillText(String(data[0].time).slice(4, 8), left, height - 5); ctx.fillText(String(data[data.length - 1].time).slice(4, 8), width - right - 22, height - 5);
  // #endif
}
async function load() { error.value = ""; try { const response = await getFutureKline({ contractCode: code.value, period: period.value, count: 300 }); rows.value = response.data.rows || []; await nextTick(); render(); } catch { error.value = "行情暂不可用，请稍后重试"; } }
function changePeriod(value) { period.value = value; load(); }
function changeIndicator(value) { indicator.value = value; render(); }
function trade() { uni.switchTab({ url: "/pages/work/index" }); }
onLoad(async query => { code.value = query.code || ""; name.value = query.name || ""; await nextTick(); load(); // #ifdef H5
  resizeHandler = render; window.addEventListener("resize", resizeHandler); // #endif
});
onBeforeUnmount(() => { // #ifdef H5
  window.removeEventListener("resize", resizeHandler); // #endif
});
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb}.contract{display:flex;justify-content:space-between;padding:24rpx 28rpx;background:#fff;color:#25334b;font-size:32rpx;font-weight:700}.contract text:last-child{font-size:23rpx;color:#8b97a8;font-weight:400}.tabs{white-space:nowrap;background:#fff;border-top:1rpx solid #eef1f5;padding:14rpx 22rpx;box-sizing:border-box}.tabs text{display:inline-block;margin-right:28rpx;padding:10rpx 4rpx;color:#7e8b9c;font-size:26rpx}.tabs .active{color:#294cc9;border-bottom:4rpx solid #294cc9;font-weight:700}.indicators{border-top:0}.chart{position:relative;height:760rpx;background:#fff;margin-top:16rpx}.chart canvas{width:100%;height:100%;display:block}.error{position:absolute;top:45%;left:0;right:0;text-align:center;color:#8b97a8;font-size:26rpx}.footer{display:flex;align-items:center;justify-content:space-between;padding:24rpx 28rpx;color:#8b97a8;font-size:22rpx}.footer button{margin:0;background:#294cc9;color:#fff;border:0}
</style>
