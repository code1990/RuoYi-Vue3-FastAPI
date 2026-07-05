<template>
  <el-menu
    :default-active="activeMenu"
    mode="horizontal"
    @select="handleSelect"
    :ellipsis="false"
    :class="{ 'topnav-mixed': isMixedMenu }"
  >
    <template v-for="(item, index) in topMenus" :key="`${item.path}-${index}`">
      <el-menu-item
        v-if="isMixedMenu && index < visibleNumber"
        :index="item.path"
        :style="{ '--theme': theme }"
      >
        <svg-icon
          v-if="item.meta && item.meta.icon && item.meta.icon !== '#'"
          :icon-class="item.meta.icon"
        />
        <span>{{ item.meta?.title }}</span>
      </el-menu-item>
      <top-nav-item
        v-else-if="index < visibleNumber"
        :item="item"
        :theme="theme"
      />
    </template>

    <el-sub-menu
      v-if="topMenus.length > visibleNumber"
      index="more"
      :style="{ '--theme': theme }"
    >
      <template #title>{{ moreLabel }}</template>
      <template v-for="(item, index) in topMenus" :key="`${item.path}-more-${index}`">
        <el-menu-item
          v-if="isMixedMenu && index >= visibleNumber"
          :index="item.path"
          :style="{ '--theme': theme }"
        >
          <svg-icon
            v-if="item.meta && item.meta.icon && item.meta.icon !== '#'"
            :icon-class="item.meta.icon"
          />
          <span>{{ item.meta?.title }}</span>
        </el-menu-item>
        <top-nav-item
          v-else-if="index >= visibleNumber"
          :item="item"
          :theme="theme"
        />
      </template>
    </el-sub-menu>
  </el-menu>
</template>

<script setup>
import { isHttp } from '@/utils/validate'
import useAppStore from '@/store/modules/app'
import useSettingsStore from '@/store/modules/settings'
import usePermissionStore from '@/store/modules/permission'
import TopNavItem from './TopNavItem.vue'

const visibleNumber = ref(1)
const hideList = ['/index', '/user/profile']

const appStore = useAppStore()
const settingsStore = useSettingsStore()
const permissionStore = usePermissionStore()
const route = useRoute()
const router = useRouter()

const theme = computed(() => settingsStore.theme)
const routers = computed(() => permissionStore.topbarRouters)
const isPureTopMenu = computed(() => settingsStore.navType === 3)
const isMixedMenu = computed(() => settingsStore.navType === 2)
const moreLabel = computed(() => (isMixedMenu.value ? '更多入口' : '更多菜单'))

const topMenus = computed(() => {
  const menus = []
  routers.value.forEach((menu) => {
    if (menu.hidden === true) return
    if (menu.path === '/' && menu.children?.length) {
      menus.push(normalizeMenu(menu.children[0], menu.path))
    } else {
      menus.push(normalizeMenu(menu))
    }
  })
  return menus
})

const flatMenus = computed(() => flattenMenus(topMenus.value))

const activeMenu = computed(() => {
  const currentPath = route.path
  if (currentPath === '/noRedirect' || currentPath === '/noredirect') {
    return topMenus.value[0]?.path || currentPath
  }
  const exact = flatMenus.value.find((item) => item.path === currentPath)
  if (exact?.topPath) {
    return exact.topPath
  }

  if (currentPath && currentPath.lastIndexOf('/') > 0 && !hideList.includes(currentPath)) {
    const topMatch = topMenus.value.find((item) => currentPath.startsWith(`${item.path}/`))
    if (topMatch) {
      return topMatch.path
    }
  }
  return currentPath
})

function setVisibleNumber() {
  const width = document.body.getBoundingClientRect().width / 3
  const itemWidth = isMixedMenu.value ? 108 : 95
  visibleNumber.value = Math.max(1, parseInt(width / itemWidth, 10))
}

function handleSelect(key) {
  const routeMenu = flatMenus.value.find((item) => item.path === key) || topMenus.value.find((item) => item.path === key)
  const target = resolveNavigationTarget(routeMenu)

  if (isHttp(target.path)) {
    window.open(target.path, '_blank')
    return
  }

  if (target.query) {
    router.push({ path: target.path, query: target.query })
  } else {
    router.push({ path: target.path })
  }

  if (isPureTopMenu.value) {
    appStore.toggleSideBarHide(true)
    permissionStore.setSidebarRouters(permissionStore.defaultRoutes)
    permissionStore.setSidebarParentTitle('')
    return
  }

  if (isMixedMenu.value) {
    ensureSidebarOpened()
    activeRoutes(routeMenu?.topPath || key)
    appStore.toggleSideBarHide(false)
    return
  }

  if (routeMenu?.topPath && routeMenu.topPath !== key) {
    activeRoutes(routeMenu.topPath)
    appStore.toggleSideBarHide(false)
    return
  }

  if (routeMenu?.children?.length) {
    activeRoutes(key)
    appStore.toggleSideBarHide(false)
  } else {
    appStore.toggleSideBarHide(true)
    permissionStore.setSidebarParentTitle(topMenus.value.find((item) => item.path === routeMenu?.topPath)?.meta?.title || '')
  }
}

function normalizeMenu(menu, parentPath = '') {
  const normalized = { ...menu }
  normalized.path = resolveFullPath(parentPath, menu.path)
  normalized.topPath = normalized.path
  if (menu.children?.length) {
    normalized.children = menu.children
      .filter((child) => !child.hidden)
      .map((child) => normalizeChildMenu(child, normalized.path, normalized.path))
  }
  return normalized
}

function normalizeChildMenu(menu, parentPath, topPath) {
  const normalized = { ...menu }
  normalized.path = resolveFullPath(parentPath, menu.path)
  normalized.parentPath = parentPath
  normalized.topPath = topPath
  if (menu.children?.length) {
    normalized.children = menu.children
      .filter((child) => !child.hidden)
      .map((child) => normalizeChildMenu(child, normalized.path, topPath))
  }
  return normalized
}

function resolveFullPath(parentPath, menuPath) {
  if (!menuPath) return parentPath || '/'
  if (isHttp(menuPath) || menuPath.startsWith('/')) return menuPath
  if (!parentPath || parentPath === '/') return `/${menuPath}`
  return `${parentPath}/${menuPath}`.replace(/\/+/g, '/')
}

function flattenMenus(menus = []) {
  const result = []
  menus.forEach((menu) => {
    result.push(menu)
    if (menu.children?.length) {
      result.push(...flattenMenus(menu.children))
    }
  })
  return result
}

function resolveNavigationTarget(menu) {
  if (!menu) {
    return { path: route.path, query: undefined }
  }

  const leaf = findFirstAvailableLeaf(menu)
  const targetMenu = shouldUseLeaf(menu) ? leaf || menu : menu
  const query = targetMenu?.query ? JSON.parse(targetMenu.query) : undefined
  return {
    path: targetMenu?.path || menu.path,
    query
  }
}

function ensureSidebarOpened() {
  if (!appStore.sidebar.opened) {
    appStore.toggleSideBar(false)
  }
}

function shouldUseLeaf(menu) {
  return menu?.redirect === 'noRedirect' || menu?.redirect === 'noredirect' || Array.isArray(menu?.children) && menu.children.length > 0
}

function findFirstAvailableLeaf(menu) {
  if (!menu) return null
  if (!Array.isArray(menu.children) || menu.children.length === 0) {
    return menu
  }

  for (const child of menu.children) {
    if (child.hidden) continue
    const target = findFirstAvailableLeaf(child)
    if (target) {
      return target
    }
  }
  return null
}

function activeRoutes(key) {
  const routes = []
  const currentTopMenu = topMenus.value.find((menu) => menu.path === key)
  const parentTitle = currentTopMenu?.meta?.title || ''
  flatMenus.value.forEach((item) => {
    if (item.topPath === key && item.path !== key) {
      routes.push(item)
    }
  })

  if (routes.length > 0) {
    permissionStore.setSidebarRouters(routes)
    permissionStore.setSidebarParentTitle(parentTitle)
  } else if (currentTopMenu && !isPureTopMenu.value) {
    permissionStore.setSidebarRouters([currentTopMenu])
    permissionStore.setSidebarParentTitle(parentTitle)
  } else if (!isPureTopMenu.value) {
    appStore.toggleSideBarHide(true)
    permissionStore.setSidebarParentTitle('')
  }
  return routes
}

watch(
  () => [route.path, settingsStore.navType],
  ([path]) => {
    if ((path === '/noRedirect' || path === '/noredirect') && topMenus.value.length > 0) {
      handleSelect(topMenus.value[0].path)
      return
    }

    if (isPureTopMenu.value) {
      appStore.toggleSideBarHide(true)
      permissionStore.setSidebarParentTitle('')
      return
    }

    const currentMenu = flatMenus.value.find((item) => item.path === path)
    const topKey = currentMenu?.topPath || activeMenu.value
    if (topKey && topKey !== path) {
      activeRoutes(topKey)
      appStore.toggleSideBarHide(false)
      return
    }

    if (path && path.lastIndexOf('/') > 0 && !hideList.includes(path) && !route.meta.link) {
      const topMatch = topMenus.value.find((item) => path.startsWith(`${item.path}/`))
      if (topMatch) {
        activeRoutes(topMatch.path)
        appStore.toggleSideBarHide(false)
        return
      }
    }

    if (isMixedMenu.value) {
      const topMatch = topMenus.value.find((item) => item.path === path)
      if (topMatch) {
        activeRoutes(topMatch.path)
        appStore.toggleSideBarHide(false)
        return
      }
    }

    appStore.toggleSideBarHide(true)
    permissionStore.setSidebarParentTitle('')
  },
  { immediate: true }
)

watch(
  () => settingsStore.navType,
  () => {
    setVisibleNumber()
  }
)

onMounted(() => {
  window.addEventListener('resize', setVisibleNumber)
  setVisibleNumber()

  if ((route.path === '/noRedirect' || route.path === '/noredirect') && topMenus.value.length > 0) {
    handleSelect(topMenus.value[0].path)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', setVisibleNumber)
})
</script>

<style lang="scss">
.topmenu-container.el-menu--horizontal > .el-menu-item {
  float: left;
  height: 50px !important;
  line-height: 50px !important;
  color: #303133 !important;
  padding: 0 12px !important;
  margin: 0 6px !important;
}

.topmenu-container.el-menu--horizontal > .el-menu-item.is-active,
.el-menu--horizontal > .el-sub-menu.is-active .el-submenu__title {
  border-bottom: 2px solid #{'var(--theme)'} !important;
  color: #303133;
}

.topmenu-container.el-menu--horizontal > .el-sub-menu .el-sub-menu__title {
  float: left;
  height: 50px !important;
  line-height: 50px !important;
  color: #303133 !important;
  padding: 0 12px !important;
  margin: 0 6px !important;
}

.topmenu-container.el-menu--horizontal > .el-menu-item:not(.is-disabled):focus,
.topmenu-container.el-menu--horizontal > .el-menu-item:not(.is-disabled):hover,
.topmenu-container.el-menu--horizontal > .el-submenu .el-submenu__title:hover {
  background-color: #ffffff;
}

.topmenu-container .svg-icon {
  margin-right: 4px;
}

.topmenu-container .el-sub-menu .el-sub-menu__icon-arrow {
  position: static;
  vertical-align: middle;
  margin-left: 8px;
  margin-top: 0;
}

.topmenu-container.topnav-mixed {
  display: flex;
  align-items: center;
  gap: 4px;
  border-bottom: none;
  padding: 0 4px;

  > .el-menu-item,
  > .el-sub-menu .el-submenu__title {
    height: 38px !important;
    line-height: 38px !important;
    margin: 0 4px !important;
    padding: 0 14px !important;
    border-radius: 10px 10px 0 0;
    border-bottom: none !important;
    font-size: 14px;
    font-weight: 600;
    color: #4b5563 !important;
    transition: background-color 0.2s ease, color 0.2s ease, transform 0.2s ease;
  }

  > .el-menu-item.is-active,
  > .el-sub-menu.is-active .el-submenu__title {
    color: var(--theme) !important;
    background: color-mix(in srgb, var(--theme) 10%, #ffffff 90%);
    box-shadow: inset 0 -2px 0 color-mix(in srgb, var(--theme) 55%, transparent 45%);
  }

  > .el-menu-item:not(.is-disabled):focus,
  > .el-menu-item:not(.is-disabled):hover,
  > .el-sub-menu .el-submenu__title:hover {
    color: #111827 !important;
    background: rgba(15, 23, 42, 0.05);
    transform: translateY(-1px);
  }

  .svg-icon {
    margin-right: 6px;
    opacity: 0.88;
  }
}
</style>
