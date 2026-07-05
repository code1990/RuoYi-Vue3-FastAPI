<template>
  <div :class="{ 'has-logo': showLogo }" class="sidebar-container">
    <logo v-if="showLogo" :collapse="isCollapse" />
    <div v-if="showModuleHeader" class="sidebar-module-header">
      <span class="module-title">{{ sidebarParentTitle }}</span>
    </div>
    <el-scrollbar wrap-class="scrollbar-wrapper">
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :background-color="getMenuBackground"
        :text-color="getMenuTextColor"
        :unique-opened="true"
        :active-text-color="theme"
        :collapse-transition="false"
        mode="vertical"
        :class="sideTheme"
      >
        <sidebar-item
          v-for="(route, index) in sidebarRouters"
          :key="route.path + index"
          :item="route"
          :base-path="route.path"
        />
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script setup>
import Logo from './Logo'
import SidebarItem from './SidebarItem'
import variables from '@/assets/styles/variables.module.scss'
import useAppStore from '@/store/modules/app'
import useSettingsStore from '@/store/modules/settings'
import usePermissionStore from '@/store/modules/permission'

const route = useRoute()
const appStore = useAppStore()
const settingsStore = useSettingsStore()
const permissionStore = usePermissionStore()

const sidebarRouters = computed(() => permissionStore.sidebarRouters)
const sidebarParentTitle = computed(() => permissionStore.sidebarParentTitle)
const showLogo = computed(() => settingsStore.sidebarLogo)
const sideTheme = computed(() => settingsStore.sideTheme)
const theme = computed(() => settingsStore.theme)
const isCollapse = computed(() => !appStore.sidebar.opened)
const showModuleHeader = computed(() => settingsStore.navType === 2 && !isCollapse.value && !!sidebarParentTitle.value)
const isMixedNav = computed(() => settingsStore.navType === 2)
const mixedMenuBackground = computed(() => '#ffffff')
const mixedMenuTextColor = computed(() => '#1f2937')

const getMenuBackground = computed(() => {
  if (isMixedNav.value) {
    return mixedMenuBackground.value
  }
  if (settingsStore.isDark) {
    return 'var(--sidebar-bg)'
  }
  return sideTheme.value === 'theme-dark' ? variables.menuBg : variables.menuLightBg
})

const getMenuTextColor = computed(() => {
  if (isMixedNav.value) {
    return mixedMenuTextColor.value
  }
  if (settingsStore.isDark) {
    return 'var(--sidebar-text)'
  }
  return sideTheme.value === 'theme-dark' ? variables.menuText : variables.menuLightText
})

const activeMenu = computed(() => {
  const { meta, path } = route
  if (meta.activeMenu) {
    return meta.activeMenu
  }
  return path
})
</script>

<style lang="scss" scoped>
.sidebar-container {
  background-color: v-bind(getMenuBackground);

  .sidebar-module-header {
    padding: 16px 18px 14px;
    border-bottom: 1px solid rgba(15, 23, 42, 0.08);
    background:
      linear-gradient(180deg, rgba(15, 23, 42, 0.04), rgba(255, 255, 255, 0)),
      color-mix(in srgb, #ffffff 96%, #f3f4f6 4%);

    .module-title {
      display: block;
      color: #111827;
      font-size: 16px;
      font-weight: 700;
      line-height: 1.35;
    }
  }

  .scrollbar-wrapper {
    background-color: v-bind(getMenuBackground);
  }

  .el-menu {
    border: none;
    height: 100%;
    width: 100% !important;
    padding: 10px 8px 18px;
    background-color: transparent;

    :deep(.el-menu-item),
    :deep(.el-sub-menu__title) {
      height: 42px;
      line-height: 42px;
      margin: 4px 0;
      border-radius: 10px;
      transition: background-color 0.2s ease, color 0.2s ease;
    }

    :deep(.el-menu-item) {
      padding-left: 14px !important;
      color: #1f2937 !important;

      &:hover {
        background: #f3f4f6 !important;
      }

      &.is-active {
        color: var(--menu-active-text, #409eff) !important;
        font-weight: 600;
        background: color-mix(in srgb, var(--menu-active-text, #409eff) 12%, #ffffff 88%) !important;
        box-shadow: inset 3px 0 0 var(--menu-active-text, #409eff);
      }
    }

    :deep(.el-sub-menu__title) {
      padding-left: 14px !important;
      color: #111827 !important;
      font-weight: 600;

      &:hover {
        background: #f3f4f6 !important;
      }
    }

    :deep(.el-sub-menu .el-menu-item) {
      margin-left: 10px;
      padding-left: 18px !important;
      opacity: 0.96;
    }

    :deep(.svg-icon) {
      margin-right: 10px !important;
      opacity: 0.88;
    }
  }
}
</style>
