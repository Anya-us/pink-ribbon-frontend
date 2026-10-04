<template>
  <div class="tags-view-container">
    <nav class="tags-view-wrapper" aria-label="已打开的页面">
      <div v-for="tag in visitedViews" :key="tag.path" class="tags-view-item" :class="{ active: tag.path === $route.path }">
        <router-link :to="{ path: tag.path, query: tag.query }" :aria-current="tag.path === $route.path ? 'page' : null">{{ tag.title }}</router-link>
        <button v-if="!tag.meta || !tag.meta.affix" type="button" :aria-label="'关闭' + tag.title + '页签'" @click="closeTag(tag)"><i class="el-icon-close" aria-hidden="true" /></button>
      </div>
    </nav>
  </div>
</template>
<script>
export default {
  name: 'TagsView',
  computed: { visitedViews() { return this.$store.state.tagsView.visitedViews } },
  watch: { $route() { this.addTag() } },
  mounted() {
    this.$store.dispatch('tagsView/addVisitedView', { path: '/dashboard', fullPath: '/dashboard', name: 'Dashboard', meta: { title: '诊疗工作台', affix: true }})
    this.addTag()
  },
  methods: {
    addTag() {
      if (this.$route.name) this.$store.dispatch('tagsView/addView', this.$route)
      this.$nextTick(() => {
        const active = this.$el.querySelector('.active')
        if (active) active.scrollIntoView({ block: 'nearest', inline: 'nearest' })
      })
    },
    closeTag(tag) {
      this.$store.dispatch('tagsView/delView', tag).then(({ visitedViews }) => {
        if (this.$route.path === tag.path) this.$router.push(visitedViews.length ? visitedViews[visitedViews.length - 1].fullPath : '/dashboard')
      })
    }
  }
}
</script>
<style scoped>
.tags-view-container { height: 38px; background: var(--panel); border-bottom: 1px solid var(--border); }
.tags-view-wrapper { display: flex; align-items: center; gap: 5px; height: 100%; padding: 0 24px; overflow-x: auto; scrollbar-width: thin; }
.tags-view-item { display: flex; align-items: center; flex-shrink: 0; border-radius: 4px; font-size: 12px; color: var(--muted); }
.tags-view-item a { padding: 4px 11px; }
.tags-view-item.active { color: var(--primary-hover); background: var(--primary-soft); font-weight: 500; }
.tags-view-item:hover { background: #EDF3F0; }
.tags-view-item button { background: transparent; border: none; padding: 4px; color: inherit; cursor: pointer; border-radius: 3px; margin-right: 4px; }
.tags-view-item button:hover { background: #D8E8E1; }
@media (max-width: 767px) { .tags-view-wrapper { padding: 0 16px; } }
@media print { .tags-view-container { display: none; } }
</style>
