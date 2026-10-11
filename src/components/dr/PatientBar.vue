<template>
  <section class="patient-strip" aria-label="当前患者与检查">
    <div class="patient-monogram" aria-hidden="true"><i class="el-icon-user" /></div>
    <div class="patient-context"><h2>{{ patient.name }} <span class="muted small-text">{{ patient.sex }} · {{ patient.age }} 岁</span></h2><p>{{ patient.id }} · {{ examination.id }}<br>{{ examination.performedAt.slice(0, 10) }} · {{ institution.name }}</p></div>
    <div v-if="$slots.tools" class="patient-tools"><slot name="tools" /></div>
    <div class="patient-selector"><label for="dr-patient-selector" class="sr-only">切换患者</label><el-select id="dr-patient-selector" :value="patient.id" size="small" aria-label="切换患者" @change="changePatient"><el-option v-for="item in patients" :key="item.id" :value="item.id" :label="item.name + ' · ' + item.id" /></el-select></div>
  </section>
</template>
<script>
import { demoState, patients, currentBundle, selectPatient } from '@/data/retina-demo'
export default {
  name: 'DrPatientBar',
  computed: { patients() { return patients }, patient() { return demoState.patient }, examination() { return currentBundle().examination }, institution() { return currentBundle().institution } },
  methods: { changePatient(id) { const patient = patients.find(item => item.id === id); selectPatient(patient); this.$router.replace({ path: this.$route.path, query: { ...this.$route.query, patientId: id, examinationId: patient.currentExaminationId }}) } }
}
</script>
<style scoped>
.patient-context { flex: 1; min-width: 180px; }
.patient-context p { overflow-wrap: anywhere; }
.patient-tools { display: flex; align-items: center; flex-wrap: wrap; justify-content: flex-end; gap: 10px; margin-left: auto; padding: 0 16px; }
.patient-selector { display: flex; align-items: center; flex-wrap: wrap; gap: 12px; }
.patient-selector .el-select { width: 245px; }
.patient-selector .status-pill { margin-left: 0; }
@media (max-width: 1050px) { .patient-tools { order: 3; width: 100%; justify-content: flex-end; padding: 0; } }
@media (max-width: 767px) { .patient-tools { justify-content: flex-start; } .patient-selector { width: 100%; } .patient-selector .el-select { width: 100%; } }
</style>
