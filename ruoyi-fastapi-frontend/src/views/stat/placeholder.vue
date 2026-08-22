<template>
  <div class="stat-placeholder">
    <el-empty :description="`${title}正在筹备统计指标`" />
  </div>
</template>

<script setup>
const route = useRoute()
const title = computed(() => String(route.query.title || '量化统计'))
</script>

<style scoped>
.stat-placeholder { padding: 40px; }
</style>
