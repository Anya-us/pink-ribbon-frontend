<template>
  <div class="sidebar-container">
    <div class="menu-wrapper">
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        text-color="#555"
        active-text-color="#fff"
        background-color="transparent"
        :unique-opened="false"
        :collapse-transition="false"
        mode="vertical">
        <sidebar-item
          v-for="route in permission_routes"
          :key="route.path"
          :item="route"
          :base-path="route.path"/>
      </el-menu>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import SidebarItem from './SidebarItem'

export default {
  components: { SidebarItem },
  computed: {
    ...mapGetters(['permission_routes', 'sidebar']),
    activeMenu() {
      const route = this.$route
      const { meta, path } = route
      if (meta.activeMenu) return meta.activeMenu
      return path
    },
    isCollapse() {
      return !this.sidebar.opened
    }
  }
}
</script>

<style>
/* 整体背景 */
.sidebar-container {
  background: linear-gradient(180deg, #f1f7f7 0%, #fde5d9 100%) !important;
  min-height: 100vh;
  padding-top: 10px;
}

/* 去掉 el-scrollbar 残余滚动样式 */
.menu-wrapper {
  overflow-y: hidden !important;
  overflow-x: hidden !important;
}

/* 每个菜单项的基础样式 */
.el-menu-item {
  background-color: #fdf4f4 !important; /* 柔和统一底色 */
  color: #555 !important;
  margin: 6px 10px;
  border-radius: 10px;
  transition: all 0.3s ease;
}

/* hover 效果 */
.el-menu-item:hover {
  color: #fff !important;
  transform: translateX(2px);
}

/* active效果 */
.el-menu-item.is-active {
  background-color: #f5adb8 !important;
  color: #fff !important;
  box-shadow: 0 2px 6px rgba(245, 173, 184, 0.4);
  transform: translateX(2px);
}

/* 子菜单标题风格 */
.el-submenu__title {
  color: #555 !important;
  border-radius: 10px;
  margin: 6px 10px;
  transition: all 0.3s ease;
}

.el-submenu__title:hover {
  background-color: #f5adb8 !important;
  color: #fff !important;
}

/* 折叠状态下的圆角修饰 */
.el-menu--collapse .el-menu-item,
.el-menu--collapse .el-submenu__title {
  border-radius: 50%;
  margin: 8px auto;
}

/* 去掉子菜单底部空白 */
.el-submenu .el-menu {
  background-color: transparent !important;
}

/* 去掉滚动条 */
::-webkit-scrollbar {
  display: none;
}
</style>
