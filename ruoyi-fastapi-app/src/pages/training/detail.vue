<template>
  <view class="page"><view class="head"><view><text class="name">{{ name }}</text><text class="code">{{ code }}</text></view><text>尾盘价决策</text></view><!-- #ifdef H5 --><div id="training-chart" class="chart"></div><!-- #endif --><!-- #ifdef APP-PLUS --><FutureHQChart ref="appChart" :DefaultSymbol="hqSymbol(code)" :DefaultChart="{ Type: 'KLine' }" /><!-- #endif --><view class="hint">请选择今日判断；提交后不可修改，也不会影响模拟交易账户。</view><view class="actions"><button class="long" @click="ask('多')">看多</button><button class="pass" @click="ask('放弃')">放弃机会</button><button class="short" @click="ask('空')">看空</button></view><view v-if="dialog" class="mask"><view class="reason-box"><text class="reason-title">为什么{{ labels[decision] }}？</text><textarea v-model="reason" maxlength="500" auto-height placeholder="请写下你的判断依据，例如指标信号、趋势或风险考虑" /><view class="reason-actions"><text @click="dialog = false">取消</text><button @click="submit">确认记录</button></view></view></view></view>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
// #ifdef H5
import HQChart from "@/vendor/hqchart/umychart.uniapp.h5";
// #endif
// #ifndef H5
import { JSIndexScript } from "@/vendor/hqchart/uniapp/umychart.index.data.wechat.js";
// #endif
import FutureHQChart from "@/components/FutureHQChart.vue";
import { getFutureKline } from "@/api/future/kline";
import { submitTrainingDecision } from "@/api/future/training";
const code = ref(""); const name = ref(""); const dialog = ref(false); const decision = ref(""); const reason = ref(""); const appChart = ref(null); const labels = { 多: "看多", 空: "看空", 放弃: "放弃机会" }; let chart;
const hqSymbol = value => String(value || "").replace(/\.XSGE$/i, ".SHFE").replace(/\.XDCE$/i, ".DCE").replace(/\.XZCE$/i, ".CZCE").replace(/\.XGFE$/i, ".GZFE").replace(/\.XCFE$/i, ".CFFEX").replace(/\.SHGE$/i, ".SHFE");
const hqRows = rows => rows.map(item => { const text = String(item.time); return [Number(text.slice(0, 8)), item.open, item.open, item.high, item.low, item.close, item.volume || 0, item.turnover || 0]; });
const trainingIndicators = [{ ID: "TRAIN_KDJ9", Name: "训练KDJ9", Description: "KDJ 9 日信号", IsMainIndex: false, Script: "RSV9:=(CLOSE-LLV(LOW,9))/(HHV(HIGH,9)-LLV(LOW,9))*100;\nK9:SMA(RSV9,3,1);\nD9:SMA(K9,3,1);\nJ9:3*K9-2*D9;\nK1:=CROSS(RSV9,K9);\nK2:=CROSS(RSV9,D9);\nDRAWICON(K1,10,1);\nDRAWICON(K2,30,1);\nK10:(CROSS(J9,K9) AND CROSS(J9,D9))*100;" }, { ID: "TRAIN_KDJ90", Name: "训练KDJ90", Description: "KDJ 90 日信号", IsMainIndex: false, Script: "RSV90:=(CLOSE-LLV(LOW,90))/(HHV(HIGH,90)-LLV(LOW,90))*100;\nK90:SMA(RSV90,3,1);\nD90:SMA(K90,3,1);\nJ90:3*K90-2*D90;\nK11:=CROSS(RSV90,K90);\nK22:=CROSS(RSV90,D90);\nDRAWICON(K11,50,1);\nDRAWICON(K22,55,1);\nK100:(CROSS(J90,K90) AND CROSS(J90,D90))*100;" }];
function registerIndicators() {
  // #ifdef H5
  HQChart.JSIndexScript.AddIndex(trainingIndicators);
  // #endif
  // #ifndef H5
  JSIndexScript.AddIndex(trainingIndicators);
  // #endif
}
function returnChartData(callback, payload) {
  // #ifndef H5
  callback({ data: payload });
  // #endif
  // #ifdef H5
  callback(payload);
  // #endif
}
const chartOption = network => ({ Type: "历史K线图", Symbol: hqSymbol(code.value), Windows: [{ Index: "MA" }, { Index: "TRAIN_KDJ9" }, { Index: "TRAIN_KDJ90" }], KLine: { Period: 0, PageSize: 180, DataWidth: 10, RightSpaceCount: 0 }, Border: { Left: 0, Right: 0, Top: 0, Bottom: 34 }, Frame: [{ IsShowRightText: false }, { IsShowRightText: false }, { IsShowRightText: false }], EnableResize: true, IsAutoUpdate: true, AutoUpdateFrequency: 10000, IsShowRightMenu: false, NetworkFilter: network });
const realtimeData = rows => { const current = rows[rows.length - 1] || {}; const previous = rows[rows.length - 2] || {}; return { LatestPointFlash: { FlashCount: 2 }, stock: [{ name: name.value, symbol: hqSymbol(code.value), date: Number(String(current.time || "").slice(0, 8)), price: current.close, open: current.open, high: current.high, low: current.low, vol: current.volume || 0, amount: current.turnover || 0, yclose: previous.close || current.open, yclearing: previous.close || current.open }] }; };
const network = async (data, callback) => { data.PreventDefault = true; const realtime = data.Name === "KLineChartContainer::RequestRealtimeData"; try { const response = await getFutureKline({ contractCode: code.value, period: "1d", count: realtime ? 2 : 180 }); const rows = response.data.rows || []; returnChartData(callback, realtime ? realtimeData(rows) : { name: name.value, symbol: hqSymbol(code.value), data: hqRows(rows) }); } catch { returnChartData(callback, realtime ? { stock: [] } : { name: name.value, symbol: hqSymbol(code.value), data: [] }); } };
function createChart() { registerIndicators();
  // #ifdef H5
  const target = document.getElementById("training-chart"); if (!target) return; HQChart.JSChart.GetResource().FrameLogo.Text = null; chart = HQChart.JSChart.Init(target); chart.SetOption(chartOption(network));
  // #endif
  // #ifdef APP-PLUS
  const control = appChart.value; if (!control) return; const info = uni.getSystemInfoSync(); control.SetSize(info.windowWidth, uni.upx2px(1050)); control.Symbol = hqSymbol(code.value); control.NetworkFilter = network; control.KLine.Option = chartOption(network); control.ChartType = "KLine"; control.OnSize(); control.CreateHQChart();
  // #endif
}
function ask(value) { decision.value = value; reason.value = ""; dialog.value = true; }
async function submit() { if (reason.value.trim().length < 2) return uni.showToast({ title: "请至少填写两个字的判断理由", icon: "none" }); try { await submitTrainingDecision({ contractCode: code.value, decision: decision.value, reason: reason.value.trim() }); dialog.value = false; uni.showToast({ title: "决策已记录", icon: "success" }); setTimeout(() => uni.navigateBack(), 500); } catch {} }
onLoad(async query => { code.value = query.code || ""; name.value = decodeURIComponent(query.name || code.value); uni.setNavigationBarTitle({ title: name.value }); await nextTick(); createChart(); }); onBeforeUnmount(() => { chart?.ChartDestroy?.(); appChart.value?.ClearChart?.(); });
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb}.head{display:flex;align-items:center;justify-content:space-between;padding:22rpx 30rpx;background:#fff;color:#8b96a8;font-size:21rpx}.name,.code{display:block}.name{font-size:29rpx;font-weight:650;color:#26324a}.code{margin-top:5rpx;color:#8b96a8;font-size:20rpx}.chart{height:1050rpx;background:#fff;width:100%}.hint{padding:20rpx 30rpx;color:#748196;font-size:21rpx}.actions{display:flex;gap:14rpx;padding:0 30rpx}.actions button{flex:1;height:82rpx;display:flex;align-items:center;justify-content:center;margin:0;color:#fff;border:0;border-radius:12rpx;font-size:25rpx;line-height:1}.long{background:#e44848}.pass{background:#64748b}.short{background:#18a56c}.mask{position:fixed;z-index:99;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(15,23,42,.45);padding:42rpx}.reason-box{width:100%;box-sizing:border-box;background:#fff;border-radius:20rpx;padding:30rpx}.reason-title{display:block;font-size:29rpx;color:#26324a;font-weight:650}.reason-box textarea{width:100%;min-height:180rpx;box-sizing:border-box;margin-top:22rpx;padding:16rpx;background:#f6f8fc;border-radius:10rpx;font-size:24rpx;color:#344158}.reason-actions{display:flex;align-items:center;justify-content:flex-end;gap:28rpx;margin-top:24rpx;font-size:25rpx;color:#7b8798}.reason-actions button{margin:0;background:#294cc9;color:#fff;border:0;border-radius:10rpx;font-size:24rpx}
</style>
