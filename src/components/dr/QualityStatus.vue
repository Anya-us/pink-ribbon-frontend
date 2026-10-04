<template>
  <span class="dr-quality"><span class="status-pill" :class="info.tone">{{ info.label }}</span><span v-if="showReason && reason" class="quality-reason">{{ reason }}</span></span>
</template>
<script>
import { QUALITY_STATES } from '@/services/dr'
export default { name: 'DrQualityStatus', props: { status: { type: String, default: 'pending' }, reason: { type: String, default: '' }, showReason: Boolean }, computed: { info() { return QUALITY_STATES[this.status] || { label: '状态未知', tone: 'warning' } } }}
</script>
<style scoped>
.dr-quality { display: inline-flex; flex-wrap: wrap; align-items: baseline; gap: 6px; }
.quality-reason { color: var(--muted); font-size: 12px; line-height: 1.7; }
</style>
