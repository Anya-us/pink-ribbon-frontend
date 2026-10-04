<template>
  <section class="app-main">
    <transition name="fade-transform" mode="out-in">
      <keep-alive :include="cachedViews">
        <router-view :key="key" />
      </keep-alive>
    </transition>
  </section>
</template>

<script>
export default {
  name: 'AppMain',
  computed: {
    cachedViews() {
      return this.$store.state.settings.tagsView ? this.$store.state.tagsView.cachedViews : undefined
    },
    key() {
      return this.$route.path
    }
  }
}
</script>

<style lang="scss" scoped>
.app-main {
  min-height: calc(100vh - var(--navbar-height));
  width: 100%;
  position: relative;
  overflow: clip;
}

.fixed-header+.app-main {
  padding-top: var(--navbar-height);
}

.hasTagsView {
  .app-main {
    min-height: calc(100vh - var(--navbar-height) - 38px);
  }

  .fixed-header+.app-main {
    padding-top: calc(var(--navbar-height) + 38px);
  }
}
</style>

<style lang="scss">
// fix css style bug in open el-dialog
.el-popup-parent--hidden {
  .fixed-header {
    padding-right: 15px;
  }
}
</style>
