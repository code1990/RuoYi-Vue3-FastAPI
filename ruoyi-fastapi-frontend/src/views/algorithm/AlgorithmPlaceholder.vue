<template>
  <div class="algorithm-page"><el-empty :description="`${title}算法模块待开发`" /></div>
</template>

<script setup>
defineProps({ title: { type: String, required: true } })
</script>

<style scoped>
.algorithm-page { padding: 40px; }
</style>
