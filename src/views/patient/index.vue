<template>
  <main class="clinical-page">
    <clinical-header title="患者服务" description="查看已签发报告和已确认计划，准备复查所需资料。"><router-link class="text-link" :to="{ path: '/patient/help', query: $route.query }">了解筛查与报告流程 <i class="el-icon-right" /></router-link></clinical-header>
    <demo-notice text="本页为合成患者服务示例，只展示当前患者已签发的报告与关联计划。" />
    <patient-bar />
    <section v-if="!portal.reports.length" class="panel empty-state"><i class="el-icon-document" /><h3>暂无已签发报告</h3><p>完成医生审核后，签发报告和确认计划将显示在这里。</p><p>候选草稿不会出现在患者服务页。</p></section>
    <section v-for="report in portal.reports" :key="report.id" class="panel section-gap"><div class="panel-heading"><div><h2>已签发报告</h2><p>{{ report.signedAt.slice(0, 10) }} · {{ report.examinationId }}</p></div><span class="status-pill success">合成签发示例</span></div><div class="panel-body"><dl class="detail-grid"><div><dt>右眼 OD</dt><dd>{{ gradeInfo(report.eyeResults.OD.drGrade).label }}</dd></div><div><dt>左眼 OS</dt><dd>{{ gradeInfo(report.eyeResults.OS.drGrade).label }}</dd></div><div><dt>黄斑水肿</dt><dd>未评估</dd></div><div><dt>报告编号</dt><dd>{{ report.id }}</dd></div><div><dt>签发人</dt><dd>{{ report.signedBy }}</dd></div><div><dt>版本</dt><dd>{{ report.version }}</dd></div></dl><p class="patient-conclusion">{{ report.conclusion }}</p><p class="muted">{{ report.plan }}</p></div></section>
    <section v-if="portal.tasks.length" class="panel section-gap"><div class="panel-heading"><h2>已确认的随访计划</h2><span class="muted small-text">{{ portal.tasks.length }} 项</span></div><ul class="patient-plans"><li v-for="task in portal.tasks" :key="task.id"><div><h3>{{ task.title }}</h3><p>{{ task.dueAt || '日期待确认' }} · {{ task.reportId }}</p></div><task-status :status="task.status" /></li></ul></section>
  </main>
</template>
<script>
import ClinicalHeader from '@/components/ClinicalHeader'
import DemoNotice from '@/components/DemoNotice'
import PatientBar from '@/components/dr/PatientBar'
import TaskStatus from '@/components/dr/TaskStatus'
import { portalView } from '@/services/dr/selectors'
import { demoState, gradeInfo } from '@/data/retina-demo'
export default { name: 'PatientService', components: { ClinicalHeader, DemoNotice, PatientBar, TaskStatus }, computed: { portal() { return portalView(demoState.patient.id) } }, methods: { gradeInfo }}
</script>
<style scoped>
.detail-grid dd { overflow-wrap: anywhere; }
.patient-conclusion { margin: 24px 0 8px; }
.patient-plans { list-style: none; padding: 0 24px; margin: 0; }
.patient-plans li { display: flex; justify-content: space-between; align-items: center; gap: 16px; padding: 20px 0; border-bottom: 1px solid var(--border); }
.patient-plans li:last-child { border: 0; }
.patient-plans h3 { font-size: 15px; margin: 0 0 7px; }
.patient-plans p { font-size: 12px; color: var(--muted); margin: 0; overflow-wrap: anywhere; }
@media (max-width: 767px) { .patient-plans li { align-items: flex-start; flex-direction: column; } }
</style>
