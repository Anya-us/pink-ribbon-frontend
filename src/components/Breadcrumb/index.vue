<template>
  <nav class="app-breadcrumb" aria-label="当前位置">
    <ol><li v-for="(item, index) in levelList" :key="item.path"><span v-if="index === levelList.length - 1" aria-current="page">{{ item.meta.title }}</span><router-link v-else :to="item.redirect && item.redirect !== 'noRedirect' ? item.redirect : item.path">{{ item.meta.title }}</router-link><span v-if="index < levelList.length - 1" class="breadcrumb-separator" aria-hidden="true">/</span></li></ol>
  </nav>
</template>
<script>
export default {
  name: 'Breadcrumb',
  computed: {
    levelList() {
      const matched = this.$route.matched.filter(item => item.meta && item.meta.title && item.meta.breadcrumb !== false)
      if (matched[0] && matched[0].name === 'Dashboard') return matched
      return [{ path: '/dashboard', meta: { title: '工作台' }}].concat(matched)
    }
  }
}
</script>
<style scoped>
.app-breadcrumb { font-size: 13px; line-height: 1.6; color: var(--muted); }
.app-breadcrumb ol { list-style: none; display: flex; align-items: center; margin: 0; padding: 0; flex-wrap: wrap; }
.app-breadcrumb li { display: flex; align-items: center; }
.app-breadcrumb a { color: var(--primary); }
.app-breadcrumb a:hover { text-decoration: underline; }
.breadcrumb-separator { margin: 0 10px; color: var(--input-border); }
@media (max-width: 767px) { .app-breadcrumb li:not(:last-child) { display: none; } }
</style>
