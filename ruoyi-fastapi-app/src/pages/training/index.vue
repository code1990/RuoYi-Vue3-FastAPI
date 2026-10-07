<template>
  <view class="page">
    <view class="intro"><text class="title">盘感训练</text><text>每日尾盘选择看多、看空或放弃；不计入模拟账户。</text></view>
    <view class="section">待决策合约 <text>{{ pending.length }} 个</text></view>
    <view v-if="pending.length" class="list"><view v-for="item in pending" :key="item.contract_code" class="row" @tap.stop="open(item)"><view><text class="name">{{ item.contract_name }}</text><text class="code">{{ item.contract_code }}</text></view><view class="right"><text :class="Number(item.px_change_rate) >= 0 ? 'up' : 'down'">{{ price(item.last_px) }}</text><text>进入训练 ›</text></view></view></view>
    <view v-else class="empty">今日已无待决策合约</view>
    <view class="section">最近决策</view>
    <view v-if="history.length" class="list"><view v-for="item in history.slice(0, 5)" :key="item.decision_id || item.decisionId" class="row"><view><text class="name">{{ item.contract_name || item.contractName }}</text><text class="code">{{ item.trade_date || item.tradeDate }} · {{ item.decision }}</text></view><view class="right"><text :class="Number(item.pnl_rate ?? item.pnlRate) >= 0 ? 'up' : 'down'">{{ result(item) }}</text><text>{{ item.status === 'settled' ? '已结算' : '待结算' }}</text></view></view></view>
    <view v-else class="empty">尚无训练记录</view>
  </view>
</template>

<script setup>
import { computed, ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import { getTrainingHistory, getTrainingList } from "@/api/future/training";
const rows = ref([]); const history = ref([]); const pending = computed(() => rows.value.filter(item => !item.submitted));
const price = value => Number(value || 0).toFixed(2); const result = item => { const value = item.pnl_rate ?? item.pnlRate; return value === null || value === undefined ? "--" : `${Number(value) >= 0 ? "+" : ""}${Number(value).toFixed(2)}%`; };
function open(item) { const code = item.contract_code || item.contractCode; const name = item.contract_name || item.contractName || code; if (!code) return uni.showToast({ title: "合约代码缺失", icon: "none" }); uni.navigateTo({ url: `/pages/training/detail?code=${encodeURIComponent(code)}&name=${encodeURIComponent(name)}` }); }
async function load() { try { rows.value = (await getTrainingList()).data || []; history.value = (await getTrainingHistory()).data || []; } catch { rows.value = []; } }
onShow(load);
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb;padding:28rpx 30rpx}.intro{display:flex;flex-direction:column;gap:12rpx;padding:30rpx;background:linear-gradient(135deg,#17275e,#4b70e6);border-radius:22rpx;color:#dce5ff;font-size:23rpx}.title{color:#fff;font-size:36rpx;font-weight:700}.section{margin:34rpx 0 15rpx;color:#26324a;font-size:28rpx;font-weight:700}.section text{font-size:21rpx;color:#8b96a8;font-weight:400}.list{background:#fff;border-radius:18rpx;overflow:hidden}.row{display:flex;align-items:center;justify-content:space-between;padding:23rpx 25rpx;border-bottom:1rpx solid #edf0f6}.row:last-child{border-bottom:0}.name,.code,.right text{display:block}.name{font-size:27rpx;color:#25324a;font-weight:600}.code,.right text:last-child{margin-top:7rpx;font-size:20rpx;color:#8b96a8}.right{text-align:right;font-size:25rpx}.up{color:#e44848!important}.down{color:#18a56c!important}.empty{padding:48rpx;text-align:center;background:#fff;border-radius:18rpx;color:#9aa5b5;font-size:24rpx}
</style>
