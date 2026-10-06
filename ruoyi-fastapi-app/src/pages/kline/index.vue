<template>
  <view class="page">
    <view class="contract">
      <text class="switch" @click="switchContract(-1)">‹</text><view class="contract-name"><text>{{ quote.name || name || code }}</text><text>{{ code }}</text></view><text class="switch" @click="switchContract(1)">›</text>
    </view>
    <view class="quote-summary">
      <view class="quote-main"><text :class="priceClass">{{ number(quote.price) }}</text><text :class="priceClass">{{ signed(quote.change) }}%</text></view>
      <view class="quote-grid"><view><text>今开</text><b>{{ number(quote.open) }}</b></view><view><text>最高</text><b>{{ number(quote.high) }}</b></view><view><text>最低</text><b>{{ number(quote.low) }}</b></view><view><text>涨跌</text><b :class="priceClass">{{ signed(quote.amount) }}</b></view><view><text>5分涨速</text><b :class="priceClass">{{ signed(quote.speed) }}%</b></view><view><text>昨结</text><b>{{ number(quote.prevClose) }}</b></view></view>
    </view>
    <scroll-view scroll-x class="tabs" :show-scrollbar="false"><text v-for="item in periods" :key="item.value" :class="period === item.value ? 'active' : ''" @click="changePeriod(item.value)">{{ item.label }}</text></scroll-view>
    <view class="chart"><!-- #ifdef H5 --><div id="future-hqchart"></div><!-- #endif --><text v-if="error" class="error">{{ error }}</text></view>
    <scroll-view scroll-x class="tabs indicators" :show-scrollbar="false"><text v-for="item in indicators" :key="item" :class="indicator === item ? 'active' : ''" @click="changeIndicator(item)">{{ item }}</text></scroll-view>
    <view class="footer"><button size="mini" @click="trade">模拟交易</button><text>数据：新华财经</text></view>
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
const periods = [{ label: "1分", value: "1m" }, { label: "5分", value: "5m" }, { label: "15分", value: "15m" }, { label: "30分", value: "30m" }, { label: "60分", value: "60m" }, { label: "日", value: "1d" }, { label: "周", value: "1w" }, { label: "月", value: "1mo" }];
const indicators = ["MA", "BOLL", "MACD", "KDJ", "RSI"];
const hqPeriod = { "1m": 4, "5m": 5, "15m": 6, "30m": 7, "60m": 8, "1d": 0, "1w": 1, "1mo": 2 };
function hqRows(rows) { let previous; return rows.map(item => { const text = String(item.time); const row = [Number(text.slice(0, 8)), previous ?? item.open, item.open, item.high, item.low, item.close, item.volume || 0, item.turnover || 0]; if (text.length > 8) row.push(Number(text.slice(8))); previous = item.close; return row; }); }
async function network(data, callback) {
  data.PreventDefault = true;
  try { const response = await getFutureKline({ contractCode: code.value, period: period.value, count: 300 }); callback({ name: name.value || code.value, symbol: code.value, data: hqRows(response.data.rows || []) }); }
  catch { error.value = "行情暂不可用，请稍后重试"; callback({ name: code.value, symbol: code.value, data: [] }); }
}
function windows() { return [{ Index: indicator.value === "MA" || indicator.value === "BOLL" ? indicator.value : "MA" }, { Index: indicator.value === "MA" || indicator.value === "BOLL" ? "VOL" : indicator.value }]; }
function createChart() {
  // #ifdef H5
  const target = document.getElementById("future-hqchart"); if (!target || chart) return;
  chart = HQChart.JSChart.Init(target); chart.SetOption({ Type: "历史K线图", Symbol: code.value, Windows: windows(), KLine: { Period: hqPeriod[period.value], PageSize: 60 }, IsAutoUpdate: false, IsShowRightMenu: false, NetworkFilter: network });
  // #endif
}
function changePeriod(value) { period.value = value; chart?.ChangePeriod?.(hqPeriod[value]); }
function changeIndicator(value) { indicator.value = value; if (!chart) return; chart.ChangeIndex?.(0, value === "MA" || value === "BOLL" ? value : "MA"); chart.ChangeIndex?.(1, value === "MA" || value === "BOLL" ? "VOL" : value); }
const number = value => value === null || value === undefined ? "--" : Number(value).toFixed(2);
const signed = value => value === null || value === undefined ? "--" : `${Number(value) >= 0 ? "+" : ""}${Number(value).toFixed(2)}`;
const priceClass = computed(() => Number(quote.value.change) >= 0 ? "up" : "down");
function switchContract(direction) { const contracts = trading.quotes; if (!contracts.length) return; const index = Math.max(0, contracts.findIndex(item => item.code === code.value)); const next = contracts[(index + direction + contracts.length) % contracts.length]; code.value = next.code; name.value = next.name; uni.setNavigationBarTitle({ title: next.name || next.code }); chart?.ChangeSymbol?.(next.code); }
function trade() { uni.switchTab({ url: "/pages/work/index" }); }
onLoad(async query => { code.value = query.code || ""; name.value = query.name || ""; uni.setNavigationBarTitle({ title: name.value || code.value }); try { await trading.refreshQuotes(); } catch {} await nextTick(); createChart(); });
onBeforeUnmount(() => { chart?.Destroy?.(); chart = null; });
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb}.contract{display:flex;align-items:center;justify-content:space-between;padding:18rpx 28rpx;background:#fff;color:#25334b}.contract-name{display:flex;flex-direction:column;align-items:center;gap:5rpx;font-size:31rpx;font-weight:700}.contract-name text:last-child{font-size:20rpx;color:#8b97a8;font-weight:400}.switch{width:64rpx;text-align:center;font-size:52rpx;color:#5c6d82;line-height:54rpx}.quote-summary{background:#fff;padding:4rpx 34rpx 24rpx}.quote-main{display:flex;align-items:baseline;gap:18rpx}.quote-main text:first-child{font-size:58rpx;font-weight:700}.quote-main text:last-child{font-size:27rpx;font-weight:600}.quote-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20rpx 12rpx;margin-top:20rpx}.quote-grid view{display:flex;flex-direction:column;gap:5rpx}.quote-grid text{font-size:20rpx;color:#8b97a8}.quote-grid b{font-size:24rpx;color:#344158;font-weight:500}.quote-grid b.up,.quote-grid b.down{font-weight:600}.tabs{white-space:nowrap;background:#fff;border-top:1rpx solid #eef1f5;padding:14rpx 22rpx;box-sizing:border-box}.tabs text{display:inline-block;margin-right:28rpx;padding:10rpx 4rpx;color:#7e8b9c;font-size:26rpx}.tabs .active{color:#294cc9;border-bottom:4rpx solid #294cc9;font-weight:700}.indicators{margin-top:16rpx;border-top:0}.chart{position:relative;height:760rpx;background:#fff}.chart>div{width:100%;height:100%}.error{position:absolute;top:45%;left:0;right:0;text-align:center;color:#8b97a8;font-size:26rpx}.footer{display:flex;align-items:center;justify-content:space-between;padding:24rpx 28rpx;color:#8b97a8;font-size:22rpx}.footer button{margin:0;background:#294cc9;color:#fff;border:0}.up{color:#e44848!important}.down{color:#18a56c!important}
</style>
