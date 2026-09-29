<template>
  <div class="market-page">
    <el-empty description="BTC 行情与策略可视化待接入">
      <template #image><el-icon :size="72"><Coin /></el-icon></template>
      <p>后续接入独立的数字货币数据、回测和模拟交易，不与 A 股数据混用。</p>
    </el-empty>
  </div>
</template>

<script setup>
import { Coin } from '@element-plus/icons-vue'
</script>

<style scoped>
.market-page { padding: 40px; }
</style>
