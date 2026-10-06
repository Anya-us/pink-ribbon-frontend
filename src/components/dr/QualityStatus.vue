<template>
  <span class="dr-quality"><span class="status-pill" :class="info.tone">{{ info.label }}</span><span v-if="showReason && reason" class="quality-reason">{{ reason }}</span><span v-if="showNextStep && nextStep" class="quality-next">下一步：{{ nextStep }}</span></span>
</template>
<script>
import { QUALITY_STATES } from '@/services/dr'
export default {
  name: 'DrQualityStatus',
  props: { status: { type: String, default: 'pending' }, reason: { type: String, default: '' }, showReason: Boolean, showNextStep: Boolean },
  computed: {
    info() { return QUALITY_STATES[this.status] || { label: '状态未知', tone: 'warning' } },
    nextStep() {
      return {
        passed: '进入医生审核。',
        retake: '调整对焦与视野后重新采集。',
        ungradable: '转人工确认后重新采集，暂不出具分级。',
        unknown_device: '补录设备信息并重新进行质控。',
        missing: '补充该眼相应模态后再评估。',
        pending: '等待质控完成。',
        error: '联系工作人员处理采集服务故障。'
      }[this.status] || ''
    }
  }
}
</script>
<style scoped>
.dr-quality { display: inline-flex; flex-wrap: wrap; align-items: baseline; gap: 6px; }
.quality-reason { color: var(--muted); font-size: 12px; line-height: 1.7; }
.quality-next { color: var(--heading); font-size: 12px; line-height: 1.7; }
</style>
