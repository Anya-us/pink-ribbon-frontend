<template>
  <nav class="sidebar-container" aria-label="主要导航">
    <div class="sidebar-body">
      <logo :collapse="isCollapse" />
      <div v-if="!isCollapse" class="sidebar-section-label">诊疗工作空间</div>
      <el-scrollbar wrap-class="scrollbar-wrapper">
        <el-menu :default-active="activeMenu" :collapse="isCollapse" :text-color="variables.menuText" :active-text-color="variables.menuActiveText" background-color="transparent" :unique-opened="true" :collapse-transition="false" mode="vertical">
          <sidebar-item v-for="route in permission_routes" :key="route.path" :item="route" :base-path="route.path" />
        </el-menu>
      </el-scrollbar>
      <div v-if="!isCollapse" class="sidebar-foot"><i class="el-icon-connection" aria-hidden="true" /><div>多智能体共识<span>采集 · 复核 · 随访</span></div></div>
    </div>
    <button class="sidebar-edge-toggle" type="button" :aria-label="isCollapse ? '展开导航' : '收起导航'" :aria-expanded="String(!isCollapse)" @click="toggleSideBar"><i :class="isCollapse ? 'el-icon-arrow-right' : 'el-icon-arrow-left'" aria-hidden="true" /></button>
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
  },
  methods: {
    toggleSideBar() { this.$store.dispatch('app/toggleSideBar') }
  }
}
</script>
<style scoped>
.sidebar-body { position: relative; height: 100%; overflow: hidden; }
.sidebar-section-label { padding: 10px 24px 14px; color: var(--muted); font-size: 14px; }
.sidebar-foot { display: flex; align-items: center; gap: 12px; position: absolute; bottom: 0; left: 0; width: 100%; padding: 24px; border-top: 1px solid var(--border); color: var(--primary); font-size: 14px; }
.sidebar-foot i { font-size: 24px; }
.sidebar-foot span { display: block; color: var(--muted); margin-top: 3px; font-size: 13px; }
.sidebar-edge-toggle { position: absolute; z-index: 4; top: 50%; right: -16px; display: grid; width: 30px; height: 52px; padding: 0; place-items: center; border: 1px solid #d7e5ec; border-left: 0; border-radius: 0 13px 13px 0; color: #6f8ca1; background: #fff; box-shadow: 5px 3px 12px rgba(49, 91, 121, .08); cursor: pointer; opacity: 0; transform: translate(8px, -50%); transition: opacity .2s ease, transform .2s ease, color .2s ease, background .2s ease; }
.sidebar-edge-toggle:hover, .sidebar-edge-toggle:focus-visible { color: #337fae; background: #edf8ff; }
.sidebar-edge-toggle:focus-visible { opacity: 1; transform: translate(0, -50%); }
</style>
