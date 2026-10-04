<template>
  <span class="dr-source-device"><span>{{ sourceLabel }}</span><span v-if="institution">{{ institution }}</span><span>{{ device ? device.name : '设备未登记' }}</span></span>
</template>
<script>
export default { name: 'DrSourceDeviceTag', props: { source: { type: String, default: 'synthetic' }, device: { type: Object, default: null }, institution: { type: String, default: '' }}, computed: { sourceLabel() { return this.source === 'local' ? '本地选择' : this.source === 'synthetic' ? '合成演示资料' : '来源未登记' } }}
</script>
<style scoped>
.dr-source-device { display: inline-flex; flex-wrap: wrap; gap: 6px 12px; color: var(--muted); font-size: 12px; }
.dr-source-device span + span::before { content: '·'; margin-right: 12px; color: var(--input-border); }
</style>
