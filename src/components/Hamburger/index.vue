<template>
  <button class="navigation-toggle" type="button" :aria-expanded="String(isActive)" :aria-label="isActive ? '收起导航' : '展开导航'" @click="toggleClick">
    <i class="el-icon-s-fold" :class="{ collapsed: !isActive }" aria-hidden="true" />
  </button>
</template>
<script>
export default {
  name: 'Hamburger',
  props: { isActive: { type: Boolean, default: false }},
  methods: { toggleClick() { this.$emit('toggleClick') } }
}
</script>
<style scoped>
.navigation-toggle { border: none; background: var(--page); color: var(--muted); cursor: pointer; width: 40px; height: 40px; font-size: 19px; border-radius: 50%; margin: 0; flex-shrink: 0; }
.navigation-toggle:hover { background: var(--primary-soft); color: var(--primary); }
.collapsed { transform: rotate(180deg); }
</style>
