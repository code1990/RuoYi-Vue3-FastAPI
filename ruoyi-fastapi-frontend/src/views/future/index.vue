<template>
  <div class="market-page">
    <el-empty description="期货行情与策略可视化待接入">
      <template #image><el-icon :size="72"><TrendCharts /></el-icon></template>
      <p>后续接入独立的合约、交易时段、保证金和风控数据。</p>
    </el-empty>
  </div>
</template>

<script setup>
import { TrendCharts } from '@element-plus/icons-vue'
</script>

<style scoped>
.market-page { padding: 40px; }
</style>
