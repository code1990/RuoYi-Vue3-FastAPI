<template>
  <view class="page"><view v-if="rows.length" class="list"><view v-for="row in rows" :key="`${row.tradeDate}-${row.stockCode}`" class="row"><view><text class="name">{{ row.stockName }} <i>{{ row.stockCode }}</i></text><text class="detail">{{ row.industryName || '--' }} · 融券压力 {{ percent(row.shortPressure) }}</text></view><view class="right"><text class="score">{{ Number(row.score || 0).toFixed(1) }}</text><text class="detail">净买 {{ percent(row.netBuyRatio) }}</text></view></view></view><view v-else class="empty">暂无融券模型数据</view></view>
</template>

<script setup>
import { ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import { listMarginModels } from "@/api/stock/margin";
const rows = ref([]);
const percent = value => value === null || value === undefined ? '--' : `${(Number(value) * 100).toFixed(2)}%`;
async function load() { try { rows.value = (await listMarginModels()).data?.rows || []; } catch { rows.value = []; } }
onShow(load);
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fb;padding:28rpx 30rpx}.list,.empty{background:#fff;border-radius:18rpx}.row{display:flex;align-items:center;justify-content:space-between;padding:25rpx;border-bottom:1rpx solid #edf0f6}.row:last-child{border:0}.name,.detail,.score{display:block}.name{font-size:27rpx;font-weight:600;color:#25324a}.name i{font-style:normal;font-size:20rpx;font-weight:400;color:#8b96a8}.detail{margin-top:8rpx;font-size:21rpx;color:#8b96a8}.right{text-align:right}.score{font-size:30rpx;font-weight:700;color:#315bd4}.empty{padding:54rpx;text-align:center;color:#8b96a8;font-size:24rpx}
</style>
