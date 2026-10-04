<template>
  <div class="retina-welcome"><retina-art /><div><h2>关注糖尿病视网膜病变</h2><p>多模态采集 · 共识复核 · 持续随访</p></div></div>
</template>
<script>
import RetinaArt from '@/components/RetinaArt'
export default { name: 'HomeCarousel', components: { RetinaArt }}
</script>
<style scoped>
.retina-welcome { display: flex; align-items: center; gap: 24px; padding: 24px; background: var(--primary-soft); border-radius: 10px; }
.retina-welcome .retina-art { max-width: 220px; }
.retina-welcome h2 { font-size: 22px; margin: 0 0 10px; }
.retina-welcome p { color: var(--muted); margin: 0; }
</style>
