<template>
  <view class="page">
    <view v-for="item in contracts" :key="item.code" class="chart-card">
      <view class="chart-head"><text>{{ item.name }}</text><text>{{ item.code }}</text></view>
      <!-- #ifdef H5 --><div :id="`relation-chart-${item.key}`" class="chart"></div><!-- #endif -->
      <text v-if="item.error" class="error">{{ item.error }}</text>
    </view>
  </view>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import HQChart from "@/vendor/hqchart/umychart.uniapp.h5";
import { getFutureKline } from "@/api/future/kline";
import { useTradingStore } from "@/store";

const contracts = ref([]); const charts = [];
const hqSymbol = value => String(value || "").replace(/\.XSGE$/i, ".SHFE").replace(/\.XDCE$/i, ".DCE").replace(/\.XZCE$/i, ".CZCE").replace(/\.XGFE$/i, ".GZFE").replace(/\.XCFE$/i, ".CFFEX").replace(/\.SHGE$/i, ".SHFE");
const rowsForChart = rows => rows.map(item => { const value = String(item.time); return [Number(value.slice(0, 8)), item.open, item.open, item.high, item.low, item.close, item.volume || 0, item.turnover || 0]; });
function clearCharts() { charts.forEach(chart => chart?.ChartDestroy?.()); charts.length = 0; }
function createChart(item) {
  // #ifdef H5
  const target = document.getElementById(`relation-chart-${item.key}`); if (!target) return;
  const chart = HQChart.JSChart.Init(target); charts.push(chart); HQChart.JSChart.GetResource().FrameLogo.Text = null;
  chart.SetOption({ Type: "历史K线图", Symbol: hqSymbol(item.code), Windows: [{ Index: "MA" }, { Index: "VOL" }], KLine: { Period: 0, PageSize: 45, RightSpaceCount: 0 }, Border: { Left: 0, Right: 0, Top: 0, Bottom: 16 }, Frame: [{ IsShowRightText: false }, { IsShowRightText: false }], IsAutoUpdate: false, IsShowRightMenu: false, NetworkFilter: async (data, callback) => { data.PreventDefault = true; try { const response = await getFutureKline({ contractCode: item.code, period: "1d", count: 120 }); callback({ name: item.name, symbol: hqSymbol(item.code), data: rowsForChart(response.data.rows || []) }); } catch { item.error = "行情暂不可用"; callback({ name: item.name, symbol: hqSymbol(item.code), data: [] }); } } });
  // #endif
}
onLoad(async query => { const store = useTradingStore(); try { await store.refreshQuotes(); } catch {} const codes = [query.left, query.right].filter((code, index, array) => code && array.indexOf(code) === index); contracts.value = codes.map((code, index) => { const quote = store.quotes.find(item => item.code === code); return { key: index, code, name: quote?.name || code, error: "" }; }); await nextTick(); contracts.value.forEach(createChart); });
onBeforeUnmount(clearCharts);
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb;padding:20rpx}.chart-card{position:relative;background:#fff;border-radius:18rpx;overflow:hidden;margin-bottom:20rpx}.chart-head{display:flex;justify-content:space-between;padding:20rpx 24rpx;border-bottom:1rpx solid #edf0f6;font-size:27rpx;color:#29364d}.chart-head text:last-child{font-size:21rpx;color:#8b96a8}.chart{height:560rpx;width:100%}.error{position:absolute;top:50%;left:0;right:0;text-align:center;color:#8b96a8;font-size:23rpx}
</style>
