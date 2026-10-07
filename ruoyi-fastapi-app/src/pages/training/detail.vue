<template>
  <view class="page"><view class="head"><view><text class="name">{{ name }}</text><text class="code">{{ code }}</text></view><text>尾盘价决策</text></view><!-- #ifdef H5 --><div id="training-chart" class="chart"></div><!-- #endif --><view class="hint">请选择今日判断；提交后不可修改，也不会影响模拟交易账户。</view><view class="actions"><button class="long" @click="submit('多')">看多</button><button class="pass" @click="submit('放弃')">放弃机会</button><button class="short" @click="submit('空')">看空</button></view></view>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import HQChart from "@/vendor/hqchart/umychart.uniapp.h5";
import { getFutureKline } from "@/api/future/kline";
import { submitTrainingDecision } from "@/api/future/training";
const code = ref(""); const name = ref(""); let chart;
const hqSymbol = value => String(value || "").replace(/\.XSGE$/i, ".SHFE").replace(/\.XDCE$/i, ".DCE").replace(/\.XZCE$/i, ".CZCE").replace(/\.XGFE$/i, ".GZFE").replace(/\.XCFE$/i, ".CFFEX").replace(/\.SHGE$/i, ".SHFE");
const hqRows = rows => rows.map(item => { const text = String(item.time); return [Number(text.slice(0, 8)), item.open, item.open, item.high, item.low, item.close, item.volume || 0, item.turnover || 0]; });
function registerIndicators() { HQChart.JSIndexScript.AddIndex([{ ID: "TRAIN_KDJ9", Name: "训练KDJ9", Description: "KDJ 9 日信号", IsMainIndex: false, Script: "RSV9:=(CLOSE-LLV(LOW,9))/(HHV(HIGH,9)-LLV(LOW,9))*100;\nK9:SMA(RSV9,3,1);\nD9:SMA(K9,3,1);\nJ9:3*K9-2*D9;\nK1:=CROSS(RSV9,K9);\nK2:=CROSS(RSV9,D9);\nDRAWICON(K1,10,1);\nDRAWICON(K2,30,1);\nK10:(CROSS(J9,K9) AND CROSS(J9,D9))*100;" }, { ID: "TRAIN_KDJ90", Name: "训练KDJ90", Description: "KDJ 90 日信号", IsMainIndex: false, Script: "RSV90:=(CLOSE-LLV(LOW,90))/(HHV(HIGH,90)-LLV(LOW,90))*100;\nK90:SMA(RSV90,3,1);\nD90:SMA(K90,3,1);\nJ90:3*K90-2*D90;\nK11:=CROSS(RSV90,K90);\nK22:=CROSS(RSV90,D90);\nDRAWICON(K11,50,1);\nDRAWICON(K22,55,1);\nK100:(CROSS(J90,K90) AND CROSS(J90,D90))*100;" }]); }
function createChart() { // #ifdef H5
  const target = document.getElementById("training-chart"); if (!target) return; registerIndicators(); HQChart.JSChart.GetResource().FrameLogo.Text = null; chart = HQChart.JSChart.Init(target); chart.SetOption({ Type: "历史K线图", Symbol: hqSymbol(code.value), Windows: [{ Index: "MA" }, { Index: "TRAIN_KDJ9" }, { Index: "TRAIN_KDJ90" }], KLine: { Period: 0, PageSize: 80, RightSpaceCount: 0 }, Border: { Left: 0, Right: 0, Top: 0, Bottom: 34 }, Frame: [{ IsShowRightText: false }, { IsShowRightText: false }, { IsShowRightText: false }], EnableResize: true, IsAutoUpdate: false, IsShowRightMenu: false, NetworkFilter: async (data, callback) => { data.PreventDefault = true; try { const response = await getFutureKline({ contractCode: code.value, period: "1d", count: 180 }); callback({ name: name.value, symbol: hqSymbol(code.value), data: hqRows(response.data.rows || []) }); } catch { callback({ name: name.value, symbol: hqSymbol(code.value), data: [] }); } } }); // #endif
}
async function submit(decision) { const labels = { 多: "看多", 空: "看空", 放弃: "放弃机会" }; uni.showModal({ title: "确认训练决策", content: `${name.value}：${labels[decision]}\n将按尾盘价格记录，提交后不可修改。`, success: async ({ confirm }) => { if (!confirm) return; try { await submitTrainingDecision({ contractCode: code.value, decision }); uni.showToast({ title: "决策已记录", icon: "success" }); setTimeout(() => uni.navigateBack(), 500); } catch {} } }); }
onLoad(async query => { code.value = query.code || ""; name.value = query.name || code.value; uni.setNavigationBarTitle({ title: name.value }); await nextTick(); createChart(); }); onBeforeUnmount(() => chart?.ChartDestroy?.());
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb}.head{display:flex;align-items:center;justify-content:space-between;padding:22rpx 30rpx;background:#fff;color:#8b96a8;font-size:21rpx}.name,.code{display:block}.name{font-size:29rpx;font-weight:650;color:#26324a}.code{margin-top:5rpx;color:#8b96a8;font-size:20rpx}.chart{height:1050rpx;background:#fff;width:100%}.hint{padding:20rpx 30rpx;color:#748196;font-size:21rpx}.actions{display:flex;gap:14rpx;padding:0 30rpx}.actions button{flex:1;height:82rpx;display:flex;align-items:center;justify-content:center;margin:0;color:#fff;border:0;border-radius:12rpx;font-size:25rpx;line-height:1}.long{background:#e44848}.pass{background:#64748b}.short{background:#18a56c}
</style>
