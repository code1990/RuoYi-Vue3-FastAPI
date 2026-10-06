<template>
  <view class="page"><view class="contract"><text>{{ name || code }}</text><text>{{ code }}</text></view><scroll-view scroll-x class="tabs" :show-scrollbar="false"><text v-for="item in periods" :key="item.value" :class="period === item.value ? 'active' : ''" @click="changePeriod(item.value)">{{ item.label }}</text></scroll-view><scroll-view scroll-x class="tabs indicators" :show-scrollbar="false"><text v-for="item in indicators" :key="item" :class="indicator === item ? 'active' : ''" @click="changeIndicator(item)">{{ item }}</text></scroll-view><view class="chart"><!-- #ifdef H5 --><div id="future-hqchart"></div><!-- #endif --><!-- #ifndef H5 --><text>技术分析仅在 H5 版提供</text><!-- #endif --></view><view class="footer"><button size="mini" @click="trade">模拟交易</button><text>数据：新华财经</text></view></view>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { getFutureKline } from "@/api/future/kline";
const code = ref(""); const name = ref(""); const period = ref("1d"); const indicator = ref("MACD"); let chart; let JSCommon;
const periods = [{ label: "1分", value: "1m" }, { label: "5分", value: "5m" }, { label: "15分", value: "15m" }, { label: "30分", value: "30m" }, { label: "60分", value: "60m" }, { label: "日", value: "1d" }, { label: "周", value: "1w" }, { label: "月", value: "1mo" }];
const indicators = ["MA", "BOLL", "MACD", "KDJ", "RSI"];
const hqPeriod = { "1m": 4, "5m": 5, "15m": 6, "30m": 7, "60m": 8, "1d": 0, "1w": 1, "1mo": 2 };
function hqRows(rows) { let previous; return rows.map((item) => { const date = Number(String(item.time).slice(0, 8)); const time = Number(String(item.time).slice(8) || 0); const row = [date, previous ?? item.open, item.open, item.high, item.low, item.close, item.volume || 0, item.turnover || 0]; if (time) row.push(time); previous = item.close; return row; }); }
async function network(data, callback) { data.PreventDefault = true; try { const response = await getFutureKline({ contractCode: code.value, period: period.value, count: 300 }); callback({ name: name.value || code.value, symbol: code.value, data: hqRows(response.data.rows || []), ver: 2.0 }); } catch { callback({ name: code.value, symbol: code.value, data: [], ver: 2.0 }); } }
async function createChart() {
  // #ifdef H5
  const module = await import("hqchart"); const HQChart = module.default || module; JSCommon = HQChart.Chart; const target = document.getElementById("future-hqchart"); if (!target || chart) return; chart = JSCommon.JSChart.Init(target); chart.SetOption({ Type: "历史K线图", Symbol: code.value, Windows: [{ Index: indicator.value === "MA" || indicator.value === "BOLL" ? indicator.value : "MA", Overlay: true }, { Index: indicator.value === "MA" || indicator.value === "BOLL" ? "VOL" : indicator.value }], KLine: { Period: hqPeriod[period.value], PageSize: 60, IsShowTooltip: true }, IsShowRightMenu: false, NetworkFilter: network });
  // #endif
}
function redraw() { if (!chart) return; chart.ChangePeriod(hqPeriod[period.value]); chart.ChangeIndex(0, indicator.value === "MA" || indicator.value === "BOLL" ? indicator.value : "MA"); chart.ChangeIndex(1, indicator.value === "MA" || indicator.value === "BOLL" ? "VOL" : indicator.value); }
function changePeriod(value) { period.value = value; redraw(); }
function changeIndicator(value) { indicator.value = value; redraw(); }
function trade() { uni.switchTab({ url: "/pages/work/index" }); }
onLoad(async (query) => { code.value = query.code || ""; name.value = query.name || ""; await nextTick(); createChart(); });
onBeforeUnmount(() => { chart?.Destroy?.(); chart = null; });
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb}.contract{display:flex;justify-content:space-between;padding:24rpx 28rpx;background:#fff;color:#25334b;font-size:32rpx;font-weight:700}.contract text:last-child{font-size:23rpx;color:#8b97a8;font-weight:400}.tabs{white-space:nowrap;background:#fff;border-top:1rpx solid #eef1f5;padding:14rpx 22rpx;box-sizing:border-box}.tabs text{display:inline-block;margin-right:28rpx;padding:10rpx 4rpx;color:#7e8b9c;font-size:26rpx}.tabs .active{color:#294cc9;border-bottom:4rpx solid #294cc9;font-weight:700}.indicators{border-top:0}.chart{height:760rpx;background:#fff;margin-top:16rpx}.chart>div{width:100%;height:100%}.footer{display:flex;align-items:center;justify-content:space-between;padding:24rpx 28rpx;color:#8b97a8;font-size:22rpx}.footer button{margin:0;background:#294cc9;color:#fff;border:0}
</style>
