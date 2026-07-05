<template>
  <el-sub-menu
    v-if="hasChildren"
    :index="item.path"
    :style="{ '--theme': theme }"
  >
    <template #title>
      <svg-icon
        v-if="item.meta && item.meta.icon && item.meta.icon !== '#'"
        :icon-class="item.meta.icon"
      />
      <span>{{ item.meta?.title }}</span>
    </template>
    <top-nav-item
      v-for="(child, childIndex) in item.children"
      :key="`${child.path}-${childIndex}`"
      :item="child"
      :theme="theme"
    />
  </el-sub-menu>
  <el-menu-item
    v-else
    :index="item.path"
    :style="{ '--theme': theme }"
  >
    <svg-icon
      v-if="item.meta && item.meta.icon && item.meta.icon !== '#'"
      :icon-class="item.meta.icon"
    />
    <span>{{ item.meta?.title }}</span>
  </el-menu-item>
</template>

<script setup>
const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  theme: {
    type: String,
    required: true
  }
})

const hasChildren = computed(() => Array.isArray(props.item.children) && props.item.children.length > 0)
</script>
