<template>
  <view class="page" @touchstart="startSwipe" @touchmove="cancelMultiTouchSwipe" @touchend="switchBySwipe" @touchcancel="cancelSwipe">
    <view v-for="item in contracts" :key="item.code" class="chart-card">
      <view class="chart-head"><text>{{ item.name }}</text><text>{{ item.code }}</text></view>
      <!-- #ifdef H5 --><div :id="`relation-chart-${item.key}`" class="chart"></div><!-- #endif -->
      <!-- #ifdef APP-PLUS --><FutureHQChart :ref="element => setAppChart(item.key, element)" :DefaultSymbol="hqSymbol(item.code)" :DefaultChart="{ Type: 'KLine' }" /><!-- #endif -->
      <text v-if="item.error" class="error">{{ item.error }}</text>
    </view>
  </view>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
// #ifdef H5
import HQChart from "@/vendor/hqchart/umychart.uniapp.h5";
// #endif
import FutureHQChart from "@/components/FutureHQChart.vue";
import { registerKdjSignals } from "@/utils/kdj9Signal";
import { getFutureKline } from "@/api/future/kline";
import { useTradingStore } from "@/store";
import { getFutureQuotes } from "@/api/future/paper-trading";
import { getFutureRelations } from "@/api/future/relation";

const contracts = ref([]); const relationPairs = ref([]); const relationIndex = ref(0); const charts = []; const appCharts = new Map(); const swipeStart = ref({ x: 0, y: 0 }); let swipeSingleTouch = false;
function setAppChart(key, element) { if (element) appCharts.set(key, element); else appCharts.delete(key); }
function returnChartData(callback, payload) {
  // #ifndef H5
  callback({ data: payload });
  // #endif
  // #ifdef H5
  callback(payload);
  // #endif
}
const hqSymbol = value => String(value || "").replace(/\.XSGE$/i, ".SHFE").replace(/\.XDCE$/i, ".DCE").replace(/\.XZCE$/i, ".CZCE").replace(/\.XGFE$/i, ".GZFE").replace(/\.XCFE$/i, ".CFFEX").replace(/\.SHGE$/i, ".SHFE");
const rowsForChart = rows => rows.map(item => { const value = String(item.time); return [Number(value.slice(0, 8)), item.open, item.open, item.high, item.low, item.close, item.volume || 0, item.turnover || 0]; });
function clearCharts() { charts.forEach(chart => chart?.ChartDestroy?.()); charts.length = 0; appCharts.forEach(control => control?.ClearChart?.()); appCharts.clear(); }
function syncCharts(sourceChart) {
  const source = sourceChart?.JSChartContainer; const sourceFrame = source?.Frame?.SubFrame?.[0]?.Frame; if (!sourceFrame?.Data) return;
  charts.forEach(chart => { if (chart === sourceChart) return; const target = chart?.JSChartContainer; const targetFrame = target?.Frame?.SubFrame?.[0]?.Frame; if (!targetFrame?.Data) return; targetFrame.ZoomIndex = sourceFrame.ZoomIndex; targetFrame.XPointCount = sourceFrame.XPointCount; targetFrame.DataWidth = sourceFrame.DataWidth; targetFrame.DistanceWidth = sourceFrame.DistanceWidth; targetFrame.Data.DataOffset = Math.min(sourceFrame.Data.DataOffset, Math.max(0, targetFrame.Data.Data.length - targetFrame.XPointCount)); target.UpdataDataoffset(); chart.Draw(); });
}
function createChart(item) {
  // #ifdef H5
  registerKdjSignals(HQChart.JSIndexScript);
  const target = document.getElementById(`relation-chart-${item.key}`); if (!target) return;
  const chart = HQChart.JSChart.Init(target); charts.push(chart); HQChart.JSChart.GetResource().FrameLogo.Text = null;
  chart.SetOption({ Type: "历史K线图", Symbol: hqSymbol(item.code), Windows: [{ Index: "MA" }, { Index: "KDJ9_SIGNAL" }, { Index: "KDJ90_SIGNAL" }], KLine: { Period: 0, PageSize: 15, RightSpaceCount: 0 }, Border: { Left: 0, Right: 0, Top: 0, Bottom: 38 }, Frame: [{ IsShowRightText: false }, { IsShowRightText: false }, { IsShowRightText: false }], EnableYDrag: { Left: false, Right: false, Wheel: false }, EnableResize: true, IsAutoUpdate: false, IsShowRightMenu: false, NetworkFilter: async (data, callback) => { data.PreventDefault = true; try { const response = await getFutureKline({ contractCode: item.code, period: "1d", count: 120 }); callback({ name: item.name, symbol: hqSymbol(item.code), data: rowsForChart(response.data.rows || []) }); } catch { item.error = "行情暂不可用"; callback({ name: item.name, symbol: hqSymbol(item.code), data: [] }); } } });
  ["touchend", "mouseup"].forEach(event => target.addEventListener(event, () => setTimeout(() => syncCharts(chart), 0), { passive: true }));
  // #endif
  // #ifdef APP-PLUS
  const control = appCharts.get(item.key); if (!control) return;
  const info = uni.getSystemInfoSync(); control.SetSize(info.windowWidth - uni.upx2px(40), Math.max(160, (info.windowHeight - uni.upx2px(96)) / 2 - uni.upx2px(45)));
  control.Symbol = hqSymbol(item.code);
  const network = async (data, callback) => { data.PreventDefault = true; try { const response = await getFutureKline({ contractCode: item.code, period: "1d", count: 120 }); returnChartData(callback, { name: item.name, symbol: hqSymbol(item.code), data: rowsForChart(response.data.rows || []) }); } catch { item.error = "行情暂不可用"; returnChartData(callback, { name: item.name, symbol: hqSymbol(item.code), data: [] }); } };
  // FutureHQChart 会将控制器的 NetworkFilter 写回 Option；两处必须使用同一个回调。
  control.NetworkFilter = network;
  control.KLine.Option = { Type: "历史K线图", Symbol: control.Symbol, Windows: [{ Index: "MA" }, { Index: "KDJ9_SIGNAL" }, { Index: "KDJ90_SIGNAL" }], KLine: { Period: 0, PageSize: 15, RightSpaceCount: 0 }, Border: { Left: 0, Right: 0, Top: 0, Bottom: 38 }, Frame: [{ IsShowRightText: false }, { IsShowRightText: false }, { IsShowRightText: false }], EnableYDrag: { Left: false, Right: false, Wheel: false }, IsAutoUpdate: false, IsShowRightMenu: false, NetworkFilter: network };
  control.ChartType = "KLine"; control.OnSize(); control.CreateHQChart();
  // #endif
}
function pairCodes(item) { const left = item.sourceContractCode || item.source_contract_code || item.sourceContract; const right = item.relatedContractCode || item.related_contract_code || item.relatedContract; return left && right ? [left, right] : null; }
async function loadPair(index) { const pair = relationPairs.value[index]; if (!pair) return; relationIndex.value = index; clearCharts(); contracts.value = pair.map((code, key) => ({ key, code, name: code, error: "" })); const store = useTradingStore(); const responses = await Promise.all(pair.map(code => getFutureQuotes({ scope: /\.(CBOT|CME|NYMEX|COMEX)$/i.test(code) ? "overseas" : "domestic", keyword: code, pageSize: 1 }).catch(() => ({ data: { rows: [] } })))); contracts.value = pair.map((code, key) => { const quote = responses[key].data.rows.find(item => item.contractCode === code) || store.quotes.find(item => item.code === code); return { key, code, name: quote?.contractName || quote?.name || code, error: "" }; }); await nextTick(); contracts.value.forEach(createChart); }
function startSwipe(event) { swipeSingleTouch = event.touches?.length === 1; if (swipeSingleTouch) { const touch = event.touches[0]; swipeStart.value = { x: touch.clientX, y: touch.clientY }; } }
function cancelMultiTouchSwipe(event) { if (event.touches?.length !== 1) swipeSingleTouch = false; }
function cancelSwipe() { swipeSingleTouch = false; }
function switchBySwipe(event) { if (!swipeSingleTouch || event.changedTouches?.length !== 1) return cancelSwipe(); swipeSingleTouch = false; const touch = event.changedTouches[0]; const distance = touch.clientX - swipeStart.value.x; if (Math.abs(distance) <= 60 || Math.abs(distance) <= Math.abs(touch.clientY - swipeStart.value.y) || relationPairs.value.length < 2) return; const next = (relationIndex.value + (distance < 0 ? 1 : -1) + relationPairs.value.length) % relationPairs.value.length; loadPair(next); }
onLoad(async query => { const store = useTradingStore(); const codes = [query.left, query.right].filter(Boolean); try { await store.refreshQuotes(); } catch {} const rows = (await getFutureRelations().catch(() => ({ data: [] }))).data || []; relationPairs.value = rows.filter(item => ["positive", "inverse"].includes(item.relationType)).map(pairCodes).filter(Boolean); const current = relationPairs.value.findIndex(pair => pair[0] === codes[0] && pair[1] === codes[1]); if (current >= 0) return loadPair(current); const responses = await Promise.all(codes.map(code => getFutureQuotes({ scope: /\.(CBOT|CME|NYMEX|COMEX)$/i.test(code) ? "overseas" : "domestic", keyword: code, pageSize: 1 }).catch(() => ({ data: { rows: [] } })))); contracts.value = codes.map((code, index) => { const quote = responses[index].data.rows.find(item => item.contractCode === code) || store.quotes.find(item => item.code === code); return { key: index, code, name: quote?.contractName || quote?.name || code, error: "" }; }); await nextTick(); contracts.value.forEach(createChart); });
onBeforeUnmount(clearCharts);
</script>

<style scoped>
.page{height:100vh;box-sizing:border-box;display:grid;grid-template-rows:minmax(0,1fr) minmax(0,1fr);gap:20rpx;background:#f5f7fb;padding:20rpx;overflow:hidden}.chart-card{position:relative;min-height:0;display:flex;flex-direction:column;background:#fff;border-radius:18rpx;overflow:hidden}.chart-head{display:flex;flex:none;justify-content:space-between;padding:20rpx 24rpx;border-bottom:1rpx solid #edf0f6;font-size:27rpx;color:#29364d}.chart-head text:last-child{font-size:21rpx;color:#8b96a8}.chart,.chart-card :deep(.kline2){width:100%;min-height:0;flex:1;overflow:hidden}.error{position:absolute;top:50%;left:0;right:0;text-align:center;color:#8b96a8;font-size:23rpx}
</style>
