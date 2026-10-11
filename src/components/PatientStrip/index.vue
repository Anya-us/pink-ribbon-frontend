<template><patient-bar><template v-if="$slots.tools" slot="tools"><slot name="tools" /></template></patient-bar></template>
<script>
import PatientBar from '@/components/dr/PatientBar'
export default { name: 'PatientStrip', components: { PatientBar }}
</script>
