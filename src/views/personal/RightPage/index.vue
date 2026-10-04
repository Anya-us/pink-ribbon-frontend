<template><examination-timeline :examinations="examinations" @select="openExamination" /></template>
<script>
import ExaminationTimeline from '@/components/dr/ExaminationTimeline'
import { examinationHistory } from '@/services/dr/selectors'
import { demoState } from '@/data/retina-demo'
export default { name: 'ScreeningHistory', components: { ExaminationTimeline }, computed: { examinations() { return examinationHistory(demoState.patient.id) } }, methods: { openExamination(id) { this.$router.push({ path: '/screening/evidence', query: { patientId: demoState.patient.id, examinationId: id }}) } }}
</script>
