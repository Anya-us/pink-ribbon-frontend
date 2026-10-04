<template><span class="status-pill" :class="info.tone">{{ info.label }}</span></template>
<script>
import { TASK_STATES } from '@/services/dr'
export default { name: 'DrTaskStatus', props: { status: { type: String, required: true }}, computed: { info() { return TASK_STATES[this.status] || { label: '状态未知', tone: 'warning' } } }}
</script>
