<template>
  <div class="sidebar-logo-container" :class="{ collapse }">
    <router-link class="sidebar-logo-link" to="/dashboard" aria-label="糖网诊疗工作台">
      <img :src="logo" class="sidebar-logo" alt="">
      <div v-if="!collapse"><span class="sidebar-title">糖网诊疗</span><span class="brand-caption">多模态筛查与管理</span></div>
    </router-link>
  </div>
</template>
<script>
export default {
  name: 'SidebarLogo',
  props: { collapse: { type: Boolean, required: true }},
  data() { return { logo: process.env.BASE_URL + 'retina-mark.svg' } }
}
</script>
<style scoped>
.sidebar-logo-container { height: 116px; padding: 32px 24px; }
.sidebar-logo-link { display: flex !important; align-items: center; gap: 11px; }
.sidebar-logo { width: 40px; height: 40px; flex-shrink: 0; }
.sidebar-title { font-size: 21px; font-weight: 650; color: var(--heading); letter-spacing: .06em; }
.brand-caption { display: block; font-size: 11px; color: var(--muted); margin-top: 1px; white-space: nowrap; }
.collapse { padding: 32px 12px; }
</style>
