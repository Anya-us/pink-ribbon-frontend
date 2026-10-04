<template>
  <nav class="sidebar-container" aria-label="主要导航">
    <logo :collapse="isCollapse" />
    <div v-if="!isCollapse" class="sidebar-section-label">诊疗工作空间</div>
    <el-scrollbar wrap-class="scrollbar-wrapper">
      <el-menu :default-active="activeMenu" :collapse="isCollapse" :text-color="variables.menuText" :active-text-color="variables.menuActiveText" background-color="transparent" :unique-opened="true" :collapse-transition="false" mode="vertical">
        <sidebar-item v-for="route in permission_routes" :key="route.path" :item="route" :base-path="route.path" />
      </el-menu>
    </el-scrollbar>
    <div v-if="!isCollapse" class="sidebar-foot"><i class="el-icon-connection" aria-hidden="true" /><div>多智能体共识<span>采集 · 复核 · 随访</span></div></div>
  </nav>
</template>
<script>
import { mapGetters } from 'vuex'
import SidebarItem from './SidebarItem'
import Logo from './Logo'
import variables from '@/styles/variables.scss'
export default {
  components: { SidebarItem, Logo },
  computed: {
    ...mapGetters(['permission_routes', 'sidebar']),
    variables() { return variables },
    activeMenu() { return this.$route.meta.activeMenu || this.$route.path },
    isCollapse() { return !this.sidebar.opened }
  }
}
</script>
<style scoped>
.sidebar-section-label { padding: 10px 24px 14px; color: var(--muted); font-size: 12px; }
.sidebar-foot { display: flex; align-items: center; gap: 12px; position: absolute; bottom: 0; left: 0; width: 100%; padding: 24px; border-top: 1px solid var(--border); color: var(--primary); font-size: 12px; }
.sidebar-foot i { font-size: 24px; }
.sidebar-foot span { display: block; color: var(--muted); margin-top: 3px; font-size: 11px; }
</style>
